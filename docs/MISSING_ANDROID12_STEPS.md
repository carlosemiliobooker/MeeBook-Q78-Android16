# Missing evidence for a reproducible stock Q78 → permanent Android 16 guide

**Status:** The Android 16 `system_a` installation on the *already prepared* MeeBook Q78 is confirmed. The earlier Android 11 → temporary Android 12 DSU/rooted-ADB sequence is also confirmed, but the complete **vendor-build process** and original Android 12 flash console output are missing from the preserved transcript. The original Android 12 flash *commands and image paths* have now been recovered from Mac history; see [Android 12 flash history](ANDROID12_FLASH_HISTORY.md).

| Gap | Evidence we have | Evidence not recovered |
| --- | --- | --- |
| Bootloader scope (not a missing step) | Stock Android 11 reported `ro.boot.flash.locked=0`, `ro.boot.verifiedbootstate=orange`; later fastbootd reported `unlocked: yes`. | **Factory-locked Q78s are not covered.** There is no unlock procedure in this project and none will be supplied as a step. |
| Custom ARM32 `libheif.so` | The saved 1,632-byte ARM32 shim was **recovered and hash-matched to the file inside the patched vendor image** (`53c1892c87efb863cf2e78ac548188771d90c65625ca9b45e60a247a3a6640eb`). Its `createHeifDecoder()` export returns null and has no shared-library dependencies. | Original source and exact compile command/NDK; whether the original historically flashed bytes match the current saved image. Binary hash and ELF symbols **are verified**. |
| Final compatible `vendor_a` | A 335,544,320 B patched image **was found and hashed** (`fa468f4f…`); it includes Skia, shim, `libmedia.so`, ICU, Rockchip HWC and correct selected on-disk SELinux xattrs. | Original vendor rebuild procedure, complete file/SELinux manifest and historical binary hash. The command *path* to the patched image and its currently measured SHA-256 are recovered. |
| Android 12 permanent fastbootd flash | Original history now gives **both exact paths**, size checks, logical-partition checks, `resize-logical-partition` for `system_a`/`vendor_a`, then `-S 16M flash vendor_a` and `flash system_a`. Later working A12 verified. | Contemporaneous image hashes and the fastboot `OKAY` stdout; validated recovery for a different stock unit. |
| Android 12 AVB / userdata | **After the A12 flash block**, original history records `fastboot -w` and `fastboot reboot`. The stock bootloader was already unlocked. | Wipe output; whether AVB/vbmeta was ever changed earlier; whether the wipe was strictly required. |
| Backup/recovery status (not a procedure) | Attempts were made but **no verified backups were successfully completed**. Rockchip Loader returned plausible data only for the first ~32 MiB. | Readback after ~32 MiB produced repeated `0xCC`; the apparent large backup was invalid. There is **no tested rollback/unbrick method** in this project. |

## Historical search completed

The original Mac was scanned using the evidence inventory and targeted filename/Terminal-history searches. These recovered the compiled HEIF shim, working patched-vendor image candidate, image hashes, selected library labels and the exact Android 12 permanent flash command block. **No `q78_heif_stub.c`, HEIF build script, or vendor image-construction script was found.**

The project's final publishable state therefore treats the patched vendor image as an **external prerequisite**, not a binary bundled in the repository or an image reproducibly built by the supplied code. There are **no further required artifact-search tasks**. See [project scope](PROJECT_SCOPE.md) and [the verified vendor comparison](VENDOR_IMAGE_VERIFICATION.md).

## Evidence notes

The longer [research findings](RESEARCH_FINDINGS.md) preserve Rockchip Loader observations, the original 32 MiB/`0xCC` backup failure, exact confirmed Android 16 fastboot results, and more detailed recovery-oriented read-only inspection steps. The research is **not** a tested unbrick or from-stock firmware recipe.

Do not add a bootloader-unlocking procedure, an untested vbmeta patch, a full-`super` flash, a generic replacement vendor partition, or an invented permanent A12 wipe instruction to cover the gaps. In particular, the Android 12 `fastboot -w` is **independently recorded** in the recovered Mac history, after the A12 flash block; do not infer any additional Android 12 `vbmeta` changes from the later Android 16 work.
