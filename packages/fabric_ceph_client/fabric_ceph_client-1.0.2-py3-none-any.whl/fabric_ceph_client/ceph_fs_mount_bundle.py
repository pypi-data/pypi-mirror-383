from __future__ import annotations
from pathlib import Path
import os
import re
import json
from typing import List, Tuple, Dict, Any, Optional

class CephFsMountBundle:
    """
    Prepare a local folder with ceph.conf, client key/secret, and a mount script
    that mounts EVERY CephFS path found in the exported keyring's MDS caps.

    Mount points are created under: /mnt/cephfs/<cluster>/<user>/<slug-of-path>
    so multiple clusters are clearly separated.
    """

    def __init__(
        self,
        cluster: str,
        ceph_conf_text: str,
        keyring_blob: str,
        *,
        out_base: Path | str = ".",
        mount_root_default: str = "/mnt/cephfs",
    ):
        self.cluster = str(cluster).strip()
        if not self.cluster:
            raise ValueError("cluster must be a non-empty string")

        self.ceph_conf_text = ceph_conf_text
        self.keyring_blob = keyring_blob
        self.out_base = Path(out_base).resolve()
        self.mount_root_default = mount_root_default

        # Filled by parse()
        self.entity: Optional[str] = None          # e.g. client.alice_123
        self.user_only: Optional[str] = None       # e.g. alice_123
        self.secret: Optional[str] = None          # base64 secret
        self.fs_paths: List[Tuple[str, str]] = []  # list of (fsname, path)

    # ---------- public API ----------

    def build(self) -> Dict[str, Any]:
        """
        Parse inputs and write files under ./<cluster>/.
        Returns a dict with file paths and the list of mounts that the script will attempt.
        """
        text = self._unescape_if_json(self.keyring_blob)
        self._parse_keyring(text)

        cluster_dir = self.out_base / self.cluster
        cluster_dir.mkdir(parents=True, exist_ok=True)

        conf_path = self._write_conf(cluster_dir)
        secret_path, keyring_path = self._write_secrets(cluster_dir, text)
        script_path = self._write_script(cluster_dir)

        return {
            "cluster_dir": str(cluster_dir),
            "ceph_conf": str(conf_path),
            "secret_file": str(secret_path),
            "keyring_file": str(keyring_path),
            "mount_script": str(script_path),
            "entity": self.entity,
            "user": self.user_only,
            "mounts": [
                {
                    "fsname": fs,
                    "path": p,
                    "mount_point": f"{self.mount_root_default}/{self.cluster}/{self.user_only}/{self._slug_from_path(p)}",
                }
                for fs, p in self.fs_paths
            ],
        }

    # ---------- helpers / parsing ----------

    @staticmethod
    def _unescape_if_json(s: str) -> str:
        # If the blob is JSON-escaped (e.g. starts/ends with quotes), decode it.
        try:
            return json.loads(s)
        except Exception:
            return s

    @staticmethod
    def _require_regex(regex: str, text: str, desc: str, flags=0) -> re.Match:
        m = re.search(regex, text, flags)
        if not m:
            raise ValueError(f"Could not find {desc} in keyring")
        return m

    def _parse_keyring(self, text: str) -> None:
        # [client.USER]
        m_ent = self._require_regex(r"\[(client\.[^\]]+)\]", text, "[client.<name>] stanza")
        self.entity = m_ent.group(1)
        self.user_only = self.entity.split(".", 1)[1]

        # key = <secret>
        m_key = self._require_regex(r"^\s*key\s*=\s*([A-Za-z0-9+/=]+)\s*$", text, "'key =' line", flags=re.M)
        self.secret = m_key.group(1)

        # caps mds = "allow rw fsname=FS path=/foo, allow rw fsname=FS path=/bar, ..."
        m_caps = re.search(r'caps\s+mds\s*=\s*"([^"]+)"', text)
        paths: List[Tuple[str, str]] = []
        if m_caps:
            body = m_caps.group(1)
            # Prefer explicit fsname/path pairs
            pairs = re.findall(r"fsname=([^,\s]+)\s+path=([^,\s]+)", body)
            if pairs:
                # de-dup, preserve order
                seen = set()
                for fp in pairs:
                    if fp not in seen:
                        seen.add(fp)
                        paths.append(fp)
            else:
                # Fallback: at least extract path=...; assume single-FS if not given
                for p in re.findall(r"path=([^,\s]+)", body):
                    paths.append(("CEPH-FS-01", p))

        if not paths:
            raise ValueError("No fsname/path entries found in MDS caps")

        self.fs_paths = paths

    # ---------- writers ----------

    def _write_conf(self, cluster_dir: Path) -> Path:
        conf_path = cluster_dir / "ceph.conf"
        conf_path.write_text(self.ceph_conf_text, encoding="utf-8")
        return conf_path

    def _write_secrets(self, cluster_dir: Path, keyring_text: str) -> tuple[Path, Path]:
        # secret file
        secret_path = cluster_dir / f"ceph.client.{self.user_only}.secret"
        secret_path.write_text(self.secret + "\n", encoding="utf-8")
        os.chmod(secret_path, 0o600)

        # full keyring (as-is)
        keyring_path = cluster_dir / f"ceph.client.{self.user_only}.keyring"
        keyring_path.write_text(keyring_text, encoding="utf-8")
        os.chmod(keyring_path, 0o600)

        return secret_path, keyring_path

    def _write_script(self, cluster_dir: Path) -> Path:
        script_name = f"mount_{self.user_only}.sh"
        script_path = cluster_dir / script_name

        lines = [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            "",
            '# Allow caller to override mount root:',
            f'MNT_BASE="${{MNT_BASE:-{self.mount_root_default}}}"',
            "",
            f'CLUSTER="{self.cluster}"',
            f'USER="{self.user_only}"',
            f'CLIENT="{self.entity}"',
            "",
            'BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"',
            'CONF="$BASE_DIR/ceph.conf"',
            f'SECRET="$BASE_DIR/ceph.client.{self.user_only}.secret"',
            "",
            'echo "Using cluster: $CLUSTER"',
            'echo "Using conf:    $CONF"',
            'echo "Mount root:    $MNT_BASE"',
            'sudo mkdir -p "$MNT_BASE/$CLUSTER/$USER"',
            "",
        ]

        for fsname, path in self.fs_paths:
            slug = self._slug_from_path(path)
            mnt = f'$MNT_BASE/$CLUSTER/$USER/{slug}'
            lines += [
                f'echo "Mounting fs={fsname} path={path} -> {mnt}"',
                f'sudo mkdir -p {mnt}',
                (
                    'sudo mount -t ceph ":' + path + f'" {mnt} '
                    f'-o name="$CLIENT",secretfile="$SECRET",conf="$CONF",fs="{fsname}",_netdev,noatime'
                ),
                "",
            ]

        lines += [
            'echo "All mounts attempted."',
            'echo "To unmount:"',
            'echo "  sudo umount -l $MNT_BASE/$CLUSTER/$USER/*"',
            "",
        ]

        script_path.write_text("\n".join(lines), encoding="utf-8")
        os.chmod(script_path, 0o750)
        return script_path

    # ---------- utils ----------

    @staticmethod
    def _slug_from_path(p: str) -> str:
        p = p.strip().lstrip("/")
        slug = re.sub(r"[^A-Za-z0-9._-]+", "_", p)
        return slug or "root"
