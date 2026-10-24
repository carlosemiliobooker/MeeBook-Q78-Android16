# File manifest and integrity notes

## Included, small, text/reproducible assets

| Path | Description |
| --- | --- |
| `README.md` | Public installation instructions based on one successful Q78 |
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
- Optional complete boot, dtbo, vbmeta, and super backup and a validated restore procedure.
- Factory firmware or vendor recovery material if available.

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

## Publishing large files

GitHub repositories should contain this documentation/scripts and small ABX configuration. If the owner chooses to distribute an independently authorized system image, upload it separately using the appropriate large-binary distribution mechanism and publish its exact SHA-256. Do **not** commit proprietary extracted vendor files without permission.
