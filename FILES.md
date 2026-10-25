# File manifest and integrity notes

## Included, small, text/reproducible assets

| Path | Description |
| --- | --- |
| `README.md` | Public installation instructions based on one successful Q78 |
| `docs/ANDROID11_TO_ANDROID12.md` | Verified stock Android 11 → temporary Android 12 DSU/root-ADB setup; candid incomplete-stage notes |
| `docs/MISSING_ANDROID12_STEPS.md` | Remaining evidence limitations; the historical file search is complete |
| `docs/VENDOR_IMAGE_VERIFICATION.md` | Read-only comparison of three archived vendor images; shim/hash/context evidence |
| `docs/RESEARCH_FINDINGS.md` | Extended historical research dossier; not a tested recovery guide |
| `docs/PROJECT_SCOPE.md` | Final audited scope, working prerequisites and explicit unsupported procedures |
| `scripts/collect-q78-evidence.py` | Read-only local finder for shim, vendor and flash-log candidate files |
| `assets/q78-input-manager-state.xml` | Known-working 6-coefficient touch calibration in XML |
| `assets/q78-input-manager-state.abx` | 322-byte Android Binary XML calibration |
| `assets/q78-calibration-seed.rc` | The successful `post-fs-data` calibration seed logic |
| `scripts/build-abx.py` | Pure-Python ABX serializer for this simple calibration XML |
| `scripts/prepare-image.sh` | macOS ext4 GSI injector and verification, not separately field-tested |
| `scripts/check-fastbootd.sh` | Non-destructive fastbootd/slot check |
| `.gitignore` | Keeps personal dumps and large system images out of Git |

Included ABX SHA-256:

```text
2a6c9182d48b141b52c6f3e2d583d2cc748071cc0d1f76d2fdb6fdc87a7616e7  assets/q78-input-manager-state.abx
```

The ABX is regenerated from the recorded plaintext XML using AOSP-compatible protocol encoding. It is semantically based on the tested config and identical in size to the exported 322-byte ABX; the original binary was unavailable to compare its bytes.

## Early Android 12 staging files (external downloads)

- `system-squeak-arm32_binder64-ab-vanilla.img.xz`: [Phh v416](https://github.com/phhusson/treble_experimentations/releases/tag/v416), downloaded as `android12.img.xz`. Old-chat SHA-256 was not recorded.
- DSU Sideloader v2.03 `app-release.apk`: [release](https://github.com/VegaBobo/DSU-Sideloader/releases/tag/2.03), downloaded as `dsu-sideloader.apk`. Old-chat SHA-256 was not recorded.
- Android 11 stock system libraries and final modified vendor remain user-supplied; see `docs/ANDROID11_TO_ANDROID12.md`.

## Download from original sources (not included)

1. **Android 16 public release:** `lineage-23.2-20260620-a64-bvN.tar.xz`
   - Source: <https://github.com/Lost-Entrepreneur439/LineageOS-a64_gsi/releases/tag/2026-06-20>
   - Recorded SHA-256: `b942b856f7aa72d2f881c933a936a4bc9c438520fad43eebdd4287addc6f2889`
   - Extracted `.img` is the base for adding calibration. The exact successful final was built from a **separately debug-patched** copy of this base.
2. **Android 12 GSI used for staging:** `system-squeak-arm32_binder64-ab-vanilla.img.xz`
   - Source: <https://github.com/phhusson/treble_experimentations/releases/tag/v416>
3. **Android Platform Tools:** <https://developer.android.com/tools/releases/platform-tools>
4. **Homebrew `e2fsprogs`:** `brew install e2fsprogs`

## Must come from your own Q78

- Correctly modified E Ink `vendor_a` with its proprietary Rockchip graphics stack and proper SELinux labels.
- A compatible, already-unlocked Q78 with the known-good vendor stack. **This repository includes no bootloader-unlock instructions.**
- **No working full-device backup or tested recovery procedure was produced in this project.** The saved vendor/GSI images are build artifacts, not an assured device backup.

No private vendor binaries, bootloader images, or personal userdata are supplied here.

## Exact tested local files (not available in this upload)

```text
~/Q78-GSI/android16-test/lineage-23.2-20260620-a64-bvN-debug.img
SHA256 6cce1bb35958ba62b2d5a556f0838fbee04a34276be8c3b688fe506c86ba501c

~/Q78-GSI/android16-test/q78-calibration-seed-v1/android16-calibration-seed.img
Size 1880514560 bytes

~/Q78-GSI/android16-test/q78-calibration-seed-v1/android16-calibration-seed.img.gz
~/Q78-GSI/android16-test/q78-calibration-seed-v1/SHA256SUMS.txt
```

Both final image entries were verified using their local checksum list immediately before flashing. The final raw-image SHA-256 **was not copied into the project handoff**, so this repository deliberately does **not** invent a hash for it. Run `shasum -a 256` on the user's original locally preserved image.

## Matched vendor image (external, not distributed)

A local filesystem inspection established that **`~/Q78-GSI/flash-staging/vendor_android12_patched.img`** contains the shim, Skia, ICU, libmedia and Rockchip HALs, and the verified sampled `security.selinux` xattrs.

```text
vendor_android12_patched.img  335544320 bytes
SHA256 fa468f4ff1767aecfabb51e4148c7edb0f1aae978b1cc32735382e5c0d029d06
lib/libheif.so             1632 bytes
SHA256 53c1892c87efb863cf2e78ac548188771d90c65625ca9b45e60a247a3a6640eb
```

See [vendor verification](docs/VENDOR_IMAGE_VERIFICATION.md) for the full list of measured library hashes and contexts. Neither proprietary file is included in this GitHub repository. This is the **best local vendor candidate**, not yet proven to be identical to the installed `vendor_a` contents.

## Publishing large files

GitHub repositories should contain this documentation/scripts and small ABX configuration. If the owner chooses to distribute an independently authorized system image, upload it separately using the appropriate large-binary distribution mechanism and publish its exact SHA-256. Do **not** commit proprietary extracted vendor files without permission.

## Provenance of the research update

The included `docs/RESEARCH_FINDINGS.md` came from a later research handoff and should be treated as an **evidence ledger**, not a freshly executed successful installation. The non-destructive file-inventory utility was used on the original Mac; subsequent targeted searches did not recover the source/build script. It contains no private system files or credentials.

## Additional recovered installation evidence

- [`docs/ANDROID12_FLASH_HISTORY.md`](docs/ANDROID12_FLASH_HISTORY.md) documents the fully recovered Android 12 image paths, exact size and logical-partition checks, `system_a`/`vendor_a` resize and flash commands, and separately recorded `fastboot -w`/reboot. It also documents their evidence limits (the original fastboot `OKAY` output was not saved). The full shell-history file is deliberately **not included**, since it can contain private information.

## Completion status (2026-10-24)

The search for the original shim source and vendor build script is closed with **no matching source/build script found**. The compiled shim, patched vendor-image candidate, Android 12 flash command history, and working Android 16 image preparation/flash process are documented. This repository does **not** claim to be a complete factory-stock/locked-device installer. See [`docs/PROJECT_SCOPE.md`](docs/PROJECT_SCOPE.md).
