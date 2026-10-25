# Project scope and reproducibility status

This repository documents the successful **MeeBook Q78 RK3566 → permanently installed LineageOS 23.2 / Android 16** result from October 24, 2026. On the tested tablet, Android 16 booted, Rockchip E Ink graphics worked, and touch input was accurate. It also documents the earlier Android 11 → Android 12 DSU/rooted-ADB work and recovered Android 12 permanent flash history.

## Supported starting point

A **previously unlocked** MeeBook Q78 with the **already compatible, modified Rockchip E Ink vendor stack** is the tested starting point for the final Android 16 `system_a` flash. The Android 16 flash preserves that `vendor_a`; it does not build or fix a stock vendor image.

## Recovered Android 12 preparation

- Phh AOSP 12.1 v416 `arm32_binder64-ab-vanilla` was installed as a temporary DSU and enabled `adb root` (`uid=0`). The early DSU did **not** have a stable graphical interface.
- Original Mac shell history records the later permanent Android 12 image paths and preflight checks: `~/Q78-GSI/android12.img` (1,309,229,056 bytes) and `~/Q78-GSI/flash-staging/vendor_android12_patched.img` (335,544,320 bytes). It records `system_a` and `vendor_a` resizes, both `fastboot -S 16M flash` operations, `fastboot -w`, and `fastboot reboot`.
- The original fastboot `OKAY` outputs for **Android 12** were not preserved, but the later device was confirmed running Android 12 with working E Ink graphics before the Android 16 flash.

## Working patched vendor candidate

The saved `vendor_android12_patched.img` (335,544,320 bytes; SHA-256 `fa468f4ff1767aecfabb51e4148c7edb0f1aae978b1cc32735382e5c0d029d06`) contains the saved ARM32 HEIF shim, Skia, Rockchip hardware composer, Mali EGL and graphics mapper with sampled correct SELinux xattrs. This image matches the path used in the historical flash script, **but its exact bytes cannot be proved identical to what was originally flashed** without a contemporary hash or on-device readback. Proprietary vendor binaries are **not included**.

The custom `libheif.so` ELF was recovered and matched byte-for-byte to the file inside the patched vendor image, but its **original C source, compile invocation and complete image-building recipe were not recovered**. Final local filesystem/history searches found no matching source/build script. We are not substituting an invented or untested shim rebuild.

## Explicitly not included

- **Bootloader unlocking.** The tested device was already unlocked; no unlock transaction was performed or logged. Locked devices are outside scope.
- **Magisk/rooting stock Android or permanent Android 16.** The confirmed `root` refers to USB ADB on Android 12 (`uid=0`).
- **Complete verified backups or unbricking.** Backup attempts did not yield verified images. The Rockchip Loader USB readback beyond approximately 32 MiB was invalid. No complete tested recovery path exists.
- **A fully reproducible stock Android 11 → patched vendor build.** The complete build process and permissions/ABI validation for a new stock unit are unavailable.
- **Android 16 touchscreen troubleshooting experiments.** Only the final successful calibration-seed configuration is supplied.

**Read the README warning and do not flash a factory-stock vendor/device assuming the missing steps were tested.** No more historical-file searches are required to use this documentation as an honest record of the working device.
