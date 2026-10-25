# Android 12 permanent fastbootd installation — recovered Mac history

**Evidence update: 2026-10-24.** This chapter transcribes the **actual Android 12 flash command block** and following wipe/reboot commands recovered from the owner's original macOS `.zsh_history`. Unlike the earlier grep-only extract, the longer excerpt establishes the full `$SYSTEM`, `$VENDOR`, `$FB`, and `$BASE` assignments. Later work independently established that this Q78 successfully ran permanently installed Android 12 with a working Rockchip E Ink compositor before its Android 16 upgrade.

> [!WARNING]
> **Historical evidence, not a universal stock-Q78 installer.** Flashing these partitions permanently overwrites the Android system and the modified E Ink vendor stack; `fastboot -w` erases user data. The original Q78 was already bootloader-unlocked. A factory-locked Q78, a different firmware revision, or one lacking the compatible vendor image is **not** a validated starting point. A tested full-device restore process was never established. Do not run this block on a functioning Android 16 Q78.

## Files and sizes identified in the original flash block

| Item | Exact historical path on Mac | Verified size in script |
| --- | --- | ---: |
| Android 12 system image | `~/Q78-GSI/android12.img` | 1,309,229,056 bytes |
| Q78 patched E Ink vendor image | `~/Q78-GSI/flash-staging/vendor_android12_patched.img` | 335,544,320 bytes |
| `fastboot` binary | `~/Downloads/platform-tools/fastboot` | — |

The Android 12 GSI was **Phh-Treble AOSP 12.1 v416**, from the `system-squeak-arm32_binder64-ab-vanilla.img.xz` release. The original separate image-extraction command is not in this excerpt, so the compressed download must not be treated as directly flashable. An extracted raw image of the exact size above was present according to the script's required size check.

The surviving patched vendor file has a **later measured** SHA-256:

```text
fa468f4ff1767aecfabb51e4148c7edb0f1aae978b1cc32735382e5c0d029d06
```

A read-only image examination shows this file includes the 1,632-byte ARM32 `libheif.so` shim (SHA-256 `53c1892c87efb863cf2e78ac548188771d90c65625ca9b45e60a247a3a6640eb`), `libskia.so`, `libmedia.so`, `libandroidicu.so`, Rockchip HWC, Mali EGL, mapper, and appropriate selected SELinux xattrs. See [Vendor image verification](VENDOR_IMAGE_VERIFICATION.md). **The evidence does not establish that the bytes in today's saved vendor image are byte-for-byte identical to those flashed back then**, since no contemporaneous hash was preserved.

## Recovered historical command block

The original `.zsh_history` contained a `bash <<'BASH'` here-document with `set -euo pipefail`; its history representation included escaped newlines. The following is the same command block *formatted for readability*, not a newly tested installation run:

```bash
# HISTORICAL, DESTRUCTIVE COMMANDS — NOT FOR A CURRENTLY WORKING Q78
bash <<'BASH'
set -euo pipefail

FB="$HOME/Downloads/platform-tools/fastboot"
BASE="$HOME/Q78-GSI"

SYSTEM="$BASE/android12.img"
VENDOR="$BASE/flash-staging/vendor_android12_patched.img"

echo "=== VERIFY IMAGE SIZES ==="
test "$(stat -f %z "$SYSTEM")" = "1309229056"
test "$(stat -f %z "$VENDOR")" = "335544320"

echo "=== VERIFY LOGICAL PARTITIONS ==="
for PART in system_a vendor_a; do
  RESULT=$("$FB" getvar "is-logical:$PART" 2>&1)
  echo "$RESULT"
  echo "$RESULT" | grep -q "is-logical:$PART: yes"
done

echo "=== RESIZE SYSTEM_A ==="
"$FB" resize-logical-partition system_a 1309229056

echo "=== RESIZE VENDOR_A ==="
"$FB" resize-logical-partition vendor_a 335544320

echo "=== FLASH PATCHED E INK VENDOR ==="
"$FB" -S 16M flash vendor_a "$VENDOR"

echo "=== FLASH ANDROID 12 SYSTEM ==="
"$FB" -S 16M flash system_a "$SYSTEM"

echo "=== BOTH PARTITIONS FLASHED SUCCESSFULLY ==="
BASH
```

The `=== BOTH PARTITIONS FLASHED SUCCESSFULLY ===` line is **part of the submitted script**, not a preserved line of console output. Since the block used `set -e`, a *successful execution reaching that line* would imply the preceding operations succeeded; however, the shell history **does not contain the operation-by-operation `OKAY` responses or confirm that the marker was printed**.

The saved excerpt does **not** include the original transition into fastbootd or the original `getvar is-userspace` response for this Android 12 flash. Userspace fastbootd and the expected `_a` partition layout were independently confirmed in subsequent Q78 work, including the successful Android 16 flash, but those observations are not a substitute for verifying a new device before writing.

## Recorded wipe and first reboot

Immediately after the `BASH` block the original shell history recorded these commands:

```bash
FB=~/Downloads/platform-tools/fastboot
$FB -w
~/Downloads/platform-tools/fastboot reboot
```

**This directly fills the historical userdata gap:** a wipe command and reboot command were entered after the Android 12 flash script. It does **not** prove what their stdout/stderr said, the exact partitions wiped, or whether the wipe was required to boot. The later, separately documented Android 12 system was working permanently with stable SurfaceFlinger and the Q78's E Ink graphics.

There is **no `vbmeta` command in this recovered excerpt**. That is not proof that no `vbmeta` or verified-boot adjustments occurred earlier in the project. Do not invent an AVB modification based on generic GSI instructions.

## What remains unverified

- Bootloader unlocking is **out of scope**. The examined Q78 already reported unlocked (`ro.boot.flash.locked=0`, verified-boot state `orange`); these commands are **not** for a factory-locked device.
- The complete original source and build command for the ARM32 `libheif.so` shim, and a fully reproducible construction process for the **patched vendor image** from unmodified stock files.
- SHA-256 of the exact 1,309,229,056-byte Android 12 `system.img` at the time of flashing, contemporaneous hash of `vendor_android12_patched.img`, and `OKAY` stdout for each Android 12 flash/wipe command.
- Whether `vbmeta` had been changed earlier. **No verified full-device backup, rollback, or unbrick procedure was ever completed.**

**Current status:** The original Android 12 flash image paths, preflight size tests, logical partition checks, resize and flash order, and `fastboot -w`/reboot commands are **all recovered**. Remaining work is on **vendor-image reproducibility**, original stdout, and factory-locked/recovery cases—not on guessing the flash sequence.
