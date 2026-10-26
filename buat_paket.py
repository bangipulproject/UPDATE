#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buat paket update BIP untuk repo GitHub.

Output:
  update.json
  BIP-<versi>-<tanggal>.zip  (berpassword, isinya APK)

Jalankan:
  python buat_paket.py
  python buat_paket.py --apk "../ASDP BIP - git/dist/BIP-3.1.1-20261026.apk"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

import pyzipper

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent / "ASDP BIP - git"
GRADLE = PROJECT / "app" / "build.gradle.kts"
DIST = PROJECT / "dist"

REPO_RAW = "https://raw.githubusercontent.com/bangipulproject/UPDATE/main"
ZIP_PASSWORD = "@R00t12345"
PACKAGE_NAME = "com.asdp.bip"

FEATURES = {
    "monitor": {"enabled": True, "label": "FERIZY MONITOR"},
    "panel": {"enabled": True, "label": "FERIZY PANEL"},
    "vps": {"enabled": True, "label": "VPS MANAGER"},
    "mas": {"enabled": True, "label": "FERIZY MAS"},
    "vpn": {"enabled": True, "label": "PENGATARAN VPN"},
    "system": {"enabled": True, "label": "SISTEM"},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_version() -> tuple[str, int]:
    text = GRADLE.read_text(encoding="utf-8")
    name = re.search(r'versionName\s*=\s*"([^"]+)"', text)
    code = re.search(r"versionCode\s*=\s*(\d+)", text)
    if not name or not code:
        raise SystemExit("versionName/versionCode tidak ditemukan di app/build.gradle.kts")
    return name.group(1), int(code.group(1))


def find_apk(version: str, explicit: str | None) -> Path:
    if explicit:
        apk = Path(explicit).expanduser().resolve()
        if not apk.is_file():
            raise SystemExit(f"APK tidak ditemukan: {apk}")
        return apk
    candidates = sorted(DIST.glob(f"BIP-{version}-*.apk"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise SystemExit(f"APK BIP-{version}-*.apk tidak ditemukan di {DIST}")
    return candidates[0]


def make_zip(apk: Path) -> Path:
    zip_path = BASE / (apk.stem + ".zip")
    with pyzipper.AESZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        encryption=pyzipper.WZ_AES,
    ) as zf:
        zf.setpassword(ZIP_PASSWORD.encode("utf-8"))
        zf.write(apk, arcname=apk.name)
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", help="path APK release (default: dist terbaru)")
    args = parser.parse_args()

    if not GRADLE.is_file():
        raise SystemExit(f"Proyek tidak ditemukan: {PROJECT}")

    version, code = read_version()
    apk = find_apk(version, args.apk)
    zip_path = make_zip(apk)

    apk_hash = sha256(apk)
    zip_hash = sha256(zip_path)
    url = f"{REPO_RAW}/{zip_path.name}"

    manifest = {
        "app": "Ferizy BIP",
        "packageName": PACKAGE_NAME,
        "versionCode": code,
        "versionName": version,
        "minVersionCode": 14,
        "mandatory": False,
        "notes": f"Rilis {version} - update APK via GitHub (ZIP berpassword) atau server web, plus perbaikan stabilitas.",
        "changelog": [
            "Sumber update bisa dipilih: Git (GitHub) atau Web (bip.bangipul.my.id)",
            "Update APK dari GitHub memakai paket ZIP berpassword",
            "Verifikasi SHA-256 paket ZIP dan APK sebelum instalasi",
            "Installer VPS mode Web/Git: shebang di baris pertama dan preview user_data",
            f"Versi {version} (versionCode {code})",
        ],
        "apk": {
            "url": url,
            "size": zip_path.stat().st_size,
            "sha256": zip_hash,
            "apkSha256": apk_hash,
            "format": "zip",
            "name": apk.name,
        },
        "features": FEATURES,
        "values": {},
    }

    out = BASE / "update.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("APK      :", apk)
    print("ZIP      :", zip_path)
    print("Manifest :", out)
    print("Versi    :", version, f"({code})")
    print("ZIP size :", zip_path.stat().st_size)
    print("ZIP sha  :", zip_hash)
    print("APK sha  :", apk_hash)
    print("URL      :", url)
    print()
    print("Upload ke repo GitHub: update.json +", zip_path.name)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        sys.exit(130)
