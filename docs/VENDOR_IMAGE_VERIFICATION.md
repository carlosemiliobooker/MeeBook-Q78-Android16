# Q78 Android 12 vendor image: read-only verification (2026-10-24)

**Status:** Local filesystem evidence identifies the only one of three saved vendor images that contains the recovered custom ARM32 `libheif.so` shim and the essential stock Skia dependency. **It does not yet prove the image was the exact one flashed to the device**, and this document is not an instruction to reflash the currently working Q78.

The observations below come from a read-only `debugfs` extraction/hash comparison run by the Q78 owner on the original Mac. The full proprietary firmware images remain on that Mac and are **not included** in this public repository.

## Candidate vendor images

| Local file in `~/Q78-GSI/flash-staging/` | Bytes | SHA-256 | Shim and Skia found? |
| --- | ---: | --- | --- |
| `vendor_a.img` | 121,528,320 | `eb5bf65dd55b665ca631eb53c825b65df543106b8998d5f8607e28337072d88c` | Neither found |
| `vendor_android12.img` | 335,544,320 | `87546836759e96cfb33ae2f592f299bbe814ff9b5c89aa9712c1d22ce9f2e79f` | Neither found |
| **`vendor_android12_patched.img`** | **335,544,320** | **`fa468f4ff1767aecfabb51e4148c7edb0f1aae978b1cc32735382e5c0d029d06`** | **Both present; saved shim exact match** |

The `file` command reports Linux ext-family filesystem data for all three. `vendor_android12_patched.img` is the **strongest known-good vendor candidate**, not a proven on-device partition dump. The previously confirmed permanent vendor logical-partition allocation is also 335,544,320 bytes.

## Selected files verified inside `vendor_android12_patched.img`

| Path within vendor filesystem | Bytes | SHA-256 |
| --- | ---: | --- |
| `lib/libheif.so` | 1,632 | `53c1892c87efb863cf2e78ac548188771d90c65625ca9b45e60a247a3a6640eb` |
| `lib/libskia.so` | 4,732,784 | `a62c4b1973fd1aff82e89a80b3b7f2050a151b4219577f0d9db40ad9d7a99dfb` |
| `lib/libmedia.so` | 349,520 | `b2a81c3cedc0a55440c58e688e38f91db3849fba3011b528c3ebf7b10eae8797` |
| `lib/libandroidicu.so` | 19,524 | `cf881341653a84a8d12d20040617910d3dcee1b78d5556db8164fd076d4118e3` |
| `lib/hw/hwcomposer.rk30board.so` | 102,564 | `9bca6bcfbe5283aff71e85b3193b9c0463ae42db4f8e467b9fecfa31431f4bda` |
| `lib/egl/libGLES_mali.so` | 28,003,584 | `0148bf72afc6b9017510f0fc4483801c9494752d85b00a86a205456263a7ce1e` |
| `lib/hw/android.hardware.graphics.mapper@4.0-impl-bifrost.so` | 112,284 | `54e67c54bb636df9b89a4b4c719cd02485dd94ab791d2adda4018d5a28d9f714` |

The HWC, Mali, and Bifrost mapper files had identical hashes in all three images. The decisive difference in this comparison is the added compatibility libraries in the patched image.

## Verified on-disk SELinux extended attributes

`debugfs` reported the following **inside the patched vendor filesystem**, beyond the separately saved live-file-tree manifest:

```text
/lib/libheif.so
    security.selinux = u:object_r:vendor_file:s0
/lib/egl/libGLES_mali.so
    security.selinux = u:object_r:same_process_hal_file:s0
/lib/hw/android.hardware.graphics.mapper@4.0-impl-bifrost.so
    security.selinux = u:object_r:same_process_hal_file:s0
```

These specific labels were verified; **not every file context in the image has yet been inventoried**.

## What we know about the HEIF shim

The independent saved 1,632-byte `libheif.so` has **exactly the same SHA-256 as the file extracted from the patched image**. ELF analysis found a 32-bit ARM EABI5 shared object named `libheif.so`, exporting `_Z17createHeifDecoderv` (`createHeifDecoder()`). Its instruction sequence returns a null pointer and it has no `DT_NEEDED` shared-library dependencies. The original source was reportedly named `q78_heif_stub.c` and was compiled with Clang 17.0.0; the exact original source and command have not been recovered.

This shim is not a HEIF decoder replacement, and a recompiled version is **not** automatically equivalent to the tested binary.

## Safe repeat of the local hash check (macOS)

```bash
ROOT="$HOME/Q78-GSI/flash-staging"
shasum -a 256 "$ROOT/vendor_android12_patched.img"
stat -f%z "$ROOT/vendor_android12_patched.img"
```

Expected: `fa468f4ff1767aecfabb51e4148c7edb0f1aae978b1cc32735382e5c0d029d06`, 335,544,320 bytes. These commands only read local files. If the hash is different, **do not use the image as though it were the verified candidate**.

### Final documentation limits

The final local search did not recover the original `q78_heif_stub.c` or vendor-build scripts. The exact historical `vendor_a` bytes and all relevant SELinux contexts cannot be proved from the preserved logs. The Android 12 flash **command block** has been recovered and is recorded in [Android 12 flash history](ANDROID12_FLASH_HISTORY.md), including `fastboot -w` and reboot; the individual fastboot output was not preserved.

No bootloader unlock, full-device backup, or unbrick procedure was performed or verified. See [project scope](PROJECT_SCOPE.md).

**Do not distribute extracted Rockchip/MeeBook binaries without permission, or overwrite the currently working Android 16 vendor partition solely to complete this documentation.**
