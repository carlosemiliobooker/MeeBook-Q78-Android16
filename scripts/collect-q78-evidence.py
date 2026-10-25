#!/usr/bin/env python3
"""Read-only inventory of Q78 build artifacts on the *local Mac*.

Scans only the selected directory (default ~/Q78-GSI), without following
symlinks, running shell commands, reading credentials or uploading data.
Outputs *relative* candidate paths, file sizes and optional SHA-256 hashes.
Large files are not hashed by default; pass --hash-large to include them.
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import hashlib
import os
from pathlib import Path
import sys

CANDIDATES = (
    "libheif.so", "libskia.so", "libdng_sdk.so", "libGLES_mali.so",
    "hwcomposer.rk30board.so", "android.hardware.graphics.mapper*",
    "*heif*.c", "*heif*.cpp", "*shim*.c", "*shim*.cpp",
    "*vendor*.img", "*vendor*.img.gz", "*vendor*.sh",
    "*fastboot*.log", "*flash*.log", "*flash*.sh", "*build*.sh",
    "library-labels.txt", "SHA256SUMS*", "*manifest*.txt", "*manifest*.json",
    "Android.mk", "CMakeLists.txt", "*clang*.log", "*prepare*.sh",
)
SKIP_DIRS = {".git", "node_modules", "__pycache__", "transfer-parts", "recovery-backup"}
DEFAULT_MAX_BYTES = 128 * 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.home() / "Q78-GSI")
    parser.add_argument("--output", type=Path, default=Path("q78-evidence-inventory.csv"))
    parser.add_argument("--hash-large", action="store_true", help="also hash large images")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"No such directory: {root}")
    if args.output.exists():
        parser.error(f"Output already exists, refusing overwrite: {args.output}")
    found: list[tuple[str, int, str, str]] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not (Path(current) / d).is_symlink()]
        for name in files:
            if not any(fnmatch.fnmatch(name.lower(), pattern.lower()) for pattern in CANDIDATES):
                continue
            path = Path(current) / name
            if path.is_symlink() or not path.is_file():
                continue
            try:
                size = path.stat().st_size
                if size > DEFAULT_MAX_BYTES and not args.hash_large:
                    hashed = "SKIPPED (large; use --hash-large)"
                else:
                    hashed = sha256_file(path)
                found.append((str(path.relative_to(root)), size, hashed, ""))
            except OSError as exc:
                found.append((str(path.relative_to(root)), 0, "ERROR", str(exc)))

    with args.output.open("x", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(("relative_path", "size_bytes", "sha256_or_status", "error"))
        writer.writerows(sorted(found))
    print(f"Found {len(found)} candidate files in {root}")
    print(f"Wrote {args.output}; review the report before sharing or publishing.")
    print("No image, credential, source code, or file contents were copied to the CSV.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
