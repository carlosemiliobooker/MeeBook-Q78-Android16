# Stock Android 11 to rooted Android 12 staging — recorded MeeBook Q78 procedure

> **Read this status before following the commands.** This document reconstructs the **verified early-stage steps** from the separate Android 11 → Android 12 troubleshooting transcript. That transcript ends with **Android 12 running in DSU with root ADB but without a working graphical UI**. A *later* Q78 project record confirms Android 12 was subsequently installed permanently and booted with working E Ink graphics, and the intervening **vendor repair/build details were not retained**; the original permanent Android 12 flash *commands* were subsequently recovered from macOS history, without their console output. Thus this is **not yet a standalone, from-stock, known-good Android 12 installer**. Do not substitute any proposed operation for a verified step.

This record is included so contributors can reproduce the verified Android 11 hardware inspection and the **non-permanent Android 12 DSU/rooted-ADB staging** and help fill the missing link. The working Android 16 permanent-install procedure is in the [main README](../README.md); it requires a compatible, previously modified E Ink vendor partition.

## At-a-glance verification and outcomes

| Phase | Verified state |
|---|---|
| Original firmware | MeeBook Q78, RK3566, `rk3566_eink`, Android 11, firmware `MEEBOOK-V1.0.0-2022011811` |
| Bootloader | Device already reported `ro.boot.flash.locked=0` and verified boot `orange`; **no bootloader unlock command was recorded** |
| ADB root on stock Android 11 | **No**. `adb root` reported production build; `uid=2000(shell)` |
| GSI architecture | **ARM32 Binder64**: `arm32_binder64-ab` / A64; not generic `arm64` |
| Android 12 | Phh Treble AOSP 12.1 v416, vanilla, `system-squeak-arm32_binder64-ab-vanilla.img.xz` |
| Android 12 via DSU | Installed; ADB showed Android `12` and `Phh_Treble_vanilla`; **UI/boot-complete failed** at this recorded stage |
| ADB root on Android 12 DSU | **Yes**, `uid=0(root)` and context `u:r:su:s0` |
| Stock system and libraries | Read-only dm-linear mount of original Android 11 system; original `libskia.so` found |
| Graphics development | Temporary RAM-backed vendor library staging took effect; SurfaceFlinger still crashed |
| Permanent Android 12 | **Succeeded later according to the separate Android 16 handoff**, but the full original setup commands/files aren't in this early transcript |

## 1. Install tools on your Mac and confirm hardware

Download [Google Android Platform Tools](https://developer.android.com/tools/releases/platform-tools) and extract into `~/Downloads/platform-tools/`. The recorded commands used the following locations:

```bash
ADB="$HOME/Downloads/platform-tools/adb"
FB="$HOME/Downloads/platform-tools/fastboot"
BASE="$HOME/Q78-GSI"
mkdir -p "$BASE"
"$ADB" devices -l
"$ADB" shell 'getprop ro.build.version.release; getprop ro.product.device; getprop ro.boot.slot_suffix; getprop ro.boot.flash.locked; getprop ro.boot.verifiedbootstate; getprop ro.treble.enabled; getprop ro.boot.dynamic_partitions'
```

The recorded stock Q78 reported:

```text
Android release: 11
ro.boot.slot_suffix=_a
ro.boot.flash.locked=0
ro.boot.verifiedbootstate=orange
ro.treble.enabled=true
ro.boot.dynamic_partitions=true
```

**Bootloader prerequisite:** This specific device was already unlocked. **This guide does not include unlocking instructions and does not support factory-locked devices.** Do not attempt unrelated-device unlocking instructions.

## 2. Check root status on stock Android 11

The exact diagnostic sequence attempted:

```bash
"$ADB" root
"$ADB" wait-for-device
"$ADB" shell id
```

The original Android 11 answered `adbd cannot run as root in production builds` and provided shell UID `2000`. **These commands do not root stock Android.** No verified Magisk method exists in this project record.

## 3. Download Android 12 v416 and DSU Sideloader 2.03

These are the original download URLs and commands, with home-relative paths only:

```bash
mkdir -p "$HOME/Q78-GSI"
cd "$HOME/Q78-GSI"

curl -fL --retry 3 -o android12.img.xz \
  'https://github.com/phhusson/treble_experimentations/releases/download/v416/system-squeak-arm32_binder64-ab-vanilla.img.xz'

curl -fL --retry 3 -o dsu-sideloader.apk \
  'https://github.com/VegaBobo/DSU-Sideloader/releases/download/2.03/app-release.apk'

ls -lh android12.img.xz dsu-sideloader.apk
shasum -a 256 android12.img.xz dsu-sideloader.apk
```

**Hashes were not captured in the earlier transcript.** Record hashes for your own downloaded files; don't use guessed expected values. Release sources: [Phh v416](https://github.com/phhusson/treble_experimentations/releases/tag/v416), [DSU Sideloader 2.03](https://github.com/VegaBobo/DSU-Sideloader/releases/tag/2.03).

## 4. Install Android 12 temporarily through DSU

With USB debugging authorized on stock Android 11:

```bash
ADB="$HOME/Downloads/platform-tools/adb"
"$ADB" install -r "$HOME/Q78-GSI/dsu-sideloader.apk"
"$ADB" push "$HOME/Q78-GSI/android12.img.xz" /sdcard/Download/android12.img.xz
```

On the tablet, open **DSU Sideloader**. Grant its requested folder access, choose the transferred `android12.img.xz`, and provision a temporary Android 12 environment. A **4 GB DSU userdata size** was selected/recommended during the recorded test. The app prepared an Android 12 gzip image and a local installation helper.

The **exact helper command** used in the old session was:

```bash
"$ADB" shell sh '/storage/emulated/0/Android/data/vegabobo.dsusideloader/files/install'
```

The observed installer response:

```text
Starting: Intent { act=android.os.image.action.START_INSTALL dat=file:///storage/emulated/0/WifiTransfer/workspace_dsuhelper/android12.img.gz cmp=com.android.dynsystem/.VerificationActivity (has extras) }
DSU installation activity has been started!
```

Android subsequently displayed **“Dynamic system installed, to use it restart device.”** Select **Restart** from the DSU notification/UI. DSU does not overwrite the stock `system_a`; this was a temporary boot for root-capable diagnostics. If your DSU Sideloader version generates a different helper path, use the path actually shown by the app rather than assuming this historical one.

## 5. Verify Android 12 identity and rooted ADB

After the Android 12 DSU starts:

```bash
ADB="$HOME/Downloads/platform-tools/adb"
"$ADB" devices -l
"$ADB" shell getprop ro.build.version.release
"$ADB" root
"$ADB" wait-for-device
"$ADB" shell id
```

Recorded results:

```text
product:treble_a64_bvS model:Phh_Treble_vanilla device:phhgsi_a64_ab
12
restarting adbd as root
uid=0(root) gid=0(root) ... context=u:r:su:s0
```

**This establishes root ADB in the temporary Phh GSI only.** It is not a Magisk root of Android 11 or Android 16. Importantly, the old session's **graphical boot was not successful**; `sys.boot_completed` stayed blank.

## 6. Inspect the original Android 11 system and E Ink libraries — read-only

The original physical super partition was `/dev/block/by-name/super` → `/dev/block/mmcblk2p18`. The stock `system_a` extent recorded by `lpdump` was **2,341,184 sectors** starting **2,048 sectors** into physical super, using 512-byte sectors. These are historical measurements **for the original stock layout only**. Don't reuse them after repartitioning or on another device without checking `lpdump` first.

The following is the *successful historical* read-only mapper/mount operation. It assumes the exact **stock** layout above and the **root-capable Android 12 DSU**, and must not be run blindly on a current Android 16 installation:

```bash
"$ADB" shell '
set -e
NAME=q78_stock_system_ro
MP=/data/local/tmp/q78-stock
mkdir -p "$MP"
if ! dmctl getpath "$NAME" >/dev/null 2>&1; then
  dmctl create "$NAME" -ro linear 0 2341184 /dev/block/by-name/super 2048
fi
DEV=$(dmctl getpath "$NAME")
echo "Original Android 11 system partition: $DEV"
if ! grep -q " $MP " /proc/mounts; then
  mount -t ext4 -o ro,noload "$DEV" "$MP"
fi
find "$MP" -name "libskia*.so" 2>/dev/null
'
```

It found:

```text
/data/local/tmp/q78-stock/system/lib/libskia.so
```

The original library was **4,732,784 bytes**. The observed system image contained `libdng_sdk.so` and several additional ELF dependencies. See the [remaining missing material](MISSING_ANDROID12_STEPS.md) for why this does not by itself make an Android 12 display work.

### What the graphics work established, and what it didn't

The stock vendor's `/vendor/lib/hw/hwcomposer.rk30board.so` required Android 11's `libskia.so`. The team temporarily exposed stock libraries from a **tmpfs layer** and then bind-mounted a combined vendor library directory over `/vendor/lib`, adding additional APEX ICU dependencies where available. Those read/write operations affected the **running DSU mount namespace and RAM**, not the original flash.

One verified graphics-staging command (useful historical evidence, **not a permanent repair script**) was:

```bash
"$ADB" shell '
set -eu
RAM=/data/local/tmp/q78-vendor-complete
STOCK=/data/local/tmp/q78-stock/system/lib
NEED=$(du -sm /vendor/lib | awk "{print \$1}")
AVAILABLE=$(awk "/MemAvailable:/ {print int(\$2/1024)}" /proc/meminfo)
SIZE=$((NEED + 128))
if [ "$((SIZE + 256))" -ge "$AVAILABLE" ]; then
  echo "Not enough free RAM for this method"; exit 1
fi
mkdir -p "$RAM"
mount -t tmpfs -o "size=${SIZE}m,mode=0755" tmpfs "$RAM"
cp -a /vendor/lib/. "$RAM/"
for LIB in libdng_sdk.so libpiex.so libheif.so libjpeg.so libpng.so libft2.so libexpat.so; do
  if [ ! -e "$RAM/$LIB" ] && [ -f "$STOCK/$LIB" ]; then
    cp "$STOCK/$LIB" "$RAM/$LIB"
    chmod 644 "$RAM/$LIB"
  fi
done
chcon -R u:object_r:vendor_file:s0 "$RAM"
mount -o bind "$RAM" /vendor/lib
'
```

The later APEX ICU repair used `libandroidicu.so` from `/apex/com.android.i18n/lib` and sought `libicuuc.so`, `libicui18n.so`, and `libicudata.so` under `/apex/com.android.i18n/lib` and `/apex/com.android.art/lib`.

**Result:** This temporary method changed the dynamic linker's errors, confirming that library injection took effect, but did **not** produce a stable usable E Ink graphical UI. A subsequent `libheif.so` required an unavailable `libmedia.so`; SurfaceFlinger also crashed with `SIGABRT`. The original transcript ended there. No full permanent vendor patch-build commands can be inferred from these experiments. The **later working vendor stack** eventually used a **custom 32-bit ARM `libheif.so` shim**, Rockchip Mali/mapper libraries, and correct SELinux contexts; the shim's complete source/build and final vendor assembly commands remain missing.

## 7. The later permanent Android 12 milestone — partially evidenced

A *separate, later project handoff* records a working, permanently installed Android 12 Phh v416 system, with boot properties including `sys.boot_completed=1`, running SurfaceFlinger and Zygote, and good E Ink graphics. It also records these **historical post-flash logical allocations**:

```text
system_a: 1309229056 bytes
vendor_a:  335544320 bytes
```

It confirms that **userspace fastbootd** was used with `fastboot -S 16M flash system_a ...` and `fastboot -S 16M flash vendor_a ...`. A **subsequently recovered Mac Terminal history extract** now supplies the ordered Android 12 resize/flash commands and points `VENDOR` to the verified patched vendor-image candidate. See [Android 12 flash history](ANDROID12_FLASH_HISTORY.md). The longer history excerpt shows `SYSTEM="$BASE/android12.img"` and `VENDOR="$BASE/flash-staging/vendor_android12_patched.img"`, verifies image sizes, checks logical partition types, performs both resizes and flashes, and then records `fastboot -w` and `fastboot reboot`. It does **not** contain the commands' original `OKAY` output. The record still lacks the original system-image hash, contemporaneous vendor-image hash, the source/build command for the `libheif.so` shim, and evidence of any earlier `vbmeta` modifications.

**Consequently, we have an original historical command sequence, but not a fully reproducible, validated from-stock → permanent working Android 12 flash procedure.** Replaying a generic erase/flash recipe would be unsafe. Readers who already possess a matching *working* vendor image and functioning rooted Android 12 staging system can continue with the field-tested [Android 16 permanent flashing procedure](../README.md#8-permanent-flash-exact-operations-that-worked).

## 8. Continue safely

- If you are still on factory Android 11: **the verified path in this file takes you only to temporary DSU/rooted ADB**, not a working Android 12 user interface or a permanent Android 12 flash.
- If you already have working, permanently installed Phh v416 Android 12 and a verified compatible E Ink vendor stack: use the [main Android 16 guide](../README.md).
- **No verified backups or low-level recovery procedure were completed.** The retained vendor/GSI files are not a full-device restore image. Permanent flashing without such a recovery path carries a significant brick risk.

See [PROJECT_SCOPE.md](PROJECT_SCOPE.md) for the final documented limitations. The original vendor shim source and image-building scripts were not found; the repository will not substitute an untested rebuild.

### References

- [Phh Android 12 v416](https://github.com/phhusson/treble_experimentations/releases/tag/v416)
- [DSU Sideloader 2.03](https://github.com/VegaBobo/DSU-Sideloader/releases/tag/2.03)
- [Android Platform Tools](https://developer.android.com/tools/releases/platform-tools)
- [AOSP DSU](https://source.android.com/docs/core/ota/dynamic-system-updates)
- [AOSP userspace fastboot](https://source.android.com/docs/core/architecture/bootloader/fastbootd)
