# MeeBook Q78 (RK3566): rooted-ADB staging and permanent Android 16 installation

**Device-specific, field-tested notes and files for running unofficial LineageOS 23.2 (Android 16) on the MeeBook Q78 E Ink reader.**

**Status:** The Q78 was successfully flashed on **2026-10-24**. The permanently installed Android 16 boots, E Ink rendering works, and touchscreen input is accurate. The active installation uses `system_a` and preserves the modified Rockchip E Ink `vendor_a` partition.

> [!WARNING]
> **Flashing is destructive and can brick your reader.** This guide applies **only to a Q78 whose bootloader is already unlocked**; it does **not** provide any bootloader-unlocking procedure. `fastboot -w` erases userdata. **No complete, verified backup or tested rollback/unbrick procedure was obtained during this project** despite attempts to make backups. The Rockchip USB readback was unusable beyond approximately 32 MiB, and later ADB backup attempts did not yield verified images. Slot `b` had empty logical partitions, so switching slots is **not** a fallback. Proceeding without a reliable restore path carries a real risk of permanent device loss.

> [!NOTE]
> **Reproducibility boundary:** This repository includes the proven Android 16 system-flashing procedure and files needed to prepare its touchscreen calibration. It **does not include a fully reproducible stock Android 11 → compatible E Ink vendor build**. The historical patched vendor image is an external, owner-supplied prerequisite: `vendor_android12_patched.img`, SHA-256 `fa468f4ff1767aecfabb51e4148c7edb0f1aae978b1cc32735382e5c0d029d06`. Its original source/build recipe was not recovered despite inspecting local files and shell history. Do not attempt the permanent installation on an unmodified stock-vendor Q78 based on this README alone. See [scope and limitations](docs/PROJECT_SCOPE.md).

> [!IMPORTANT]
> **What “root” means here:** We used **rooted USB ADB on an Android 12 staging GSI** (`adb root`, `id -u` → `0`). We **did not** establish Magisk, `su`, or rooted ADB on the final Android 16 OS. The unofficial Android 16 GSI has **no built-in root**. This is not a tested Magisk rooting tutorial or a from-stock bootloader-unlocking tutorial.

## Installation roadmap: stock Android 11 → Android 16

| Stage | Documentation | Status |
| --- | --- | --- |
| 1. Check original Q78 and bootloader status | [Android 11 → Android 12 guide](docs/ANDROID11_TO_ANDROID12.md#1-install-tools-on-your-mac-and-confirm-hardware) | Verified on a device already showing unlocked bootloader; **no unlock procedure recorded** |
| 2. Install temporary Phh Android 12 via DSU | [Android 11 → Android 12 guide](docs/ANDROID11_TO_ANDROID12.md#3-download-android-12-v416-and-dsu-sideloader-203) | Installed; Android 12 identified via ADB; original UI did not boot fully |
| 3. Obtain rooted USB ADB in Android 12 DSU | [Android 11 → Android 12 guide](docs/ANDROID11_TO_ANDROID12.md#5-verify-android-12-identity-and-rooted-adb) | **Confirmed UID 0** |
| 4. Make Rockchip E Ink vendor work; permanently install Android 12 | [Recorded evidence and gaps](docs/ANDROID11_TO_ANDROID12.md#7-the-later-permanent-android-12-milestone--partially-evidenced) | **Working A12 later confirmed; system/vendor image paths, checks, resize/flash sequence, and wipe/reboot now recovered; original output and vendor build still missing** |
| 5. Build touchscreen-calibrated Android 16 | [§5–6 below](#5-provision-the-calibration-no-trial-and-error-procedures) | Known-good image tested in DSU |
| 6. Permanently flash Android 16 in fastbootd | [§7–10 below](#8-permanent-flash-exact-operations-that-worked) | **Successfully completed on October 24, 2026** |

**Flash-history recovery (2026-10-24):** The original Mac Terminal history contains the Android 12 `resize-logical-partition system_a 1309229056`, `resize-logical-partition vendor_a 335544320`, `fastboot -S 16M flash vendor_a "$VENDOR"`, and `fastboot -S 16M flash system_a "$SYSTEM"` sequence. The original flash script defines `SYSTEM="$BASE/android12.img"` and `VENDOR="$BASE/flash-staging/vendor_android12_patched.img"`, checks both image sizes, and verifies both partitions are logical. The following shell history records `fastboot -w` and `fastboot reboot`. See [the recovered complete flash block and evidence limitations](docs/ANDROID12_FLASH_HISTORY.md). History still does **not** preserve flash `OKAY` output.

**Vendor evidence update (2026-10-24):** A read-only comparison of three saved vendor files found that [`vendor_android12_patched.img`](docs/VENDOR_IMAGE_VERIFICATION.md) (335,544,320 bytes, SHA-256 `fa468f4ff1767aecfabb51e4148c7edb0f1aae978b1cc32735382e5c0d029d06`) contains the exact saved ARM32 `libheif.so` compatibility shim, Skia, and verified graphics SELinux labels. **This is the strongest compatible vendor candidate, not yet a proven match to the live `vendor_a` partition.** Its proprietary binaries are not bundled.

**Evidence update (2026-10-24):** The recovered Android 11/12 chat documents the DSU and rooted-ADB preparation. Follow-up [research findings](docs/RESEARCH_FINDINGS.md) explain the missing proprietary/custom vendor build, historical Rockchip USB readback limitations, and how to locate relevant artifacts on the original Mac. The final local inventory and source searches did not find the original vendor-building script. **The full from-stock installation remains incomplete and factory-locked devices are outside this guide’s scope.** We recovered the original Android 12 `system_a`/`vendor_a` resize-and-flash commands, image paths, and wipe/reboot commands, but not the flash stdout or complete vendor-build recipe. No verified backup or stock restoration was completed.

## 1. Compatibility and prerequisites

This exact installation is **not a generic RK3566 guide**. It applies to the following hardware and *known-good starting configuration*:

| Item | Tested configuration |
| --- | --- |
| Reader | MeeBook Q78 |
| Board | `rk3566_eink` / Rockchip RK3566 |
| Display | 1404 × 1872 E Ink |
| ABI | **A64 / ARM32 userspace with 64-bit Binder** (`arm32_binder64`) |
| Partition layout | A/B dynamic partitions inside physical `super`; active slot `a` |
| Staging OS | Phh AOSP / Treble **12.1 v416** (`arm32_binder64-ab-vanilla`) |
| Final OS | Unofficial **LineageOS 23.2 / Android 16**, `a64-bvN`, release `2026-06-20` |
| Host | macOS Terminal with Android Platform Tools and Homebrew e2fsprogs |
| Required existing hardware stack | **Modified, known-good Q78 vendor partition containing Rockchip E Ink libraries** |

**Already-unlocked devices only:** The historical Android 11 → Android 12 transcript is included in [docs/ANDROID11_TO_ANDROID12.md](docs/ANDROID11_TO_ANDROID12.md). This Q78 **already reported unlocked** before our work. We do not provide an unlock procedure, and factory-locked devices are **not supported by this guide**. Android 12 via DSU enabled `adb root`, but the early transcript ended **before** graphical boot. The later successful permanent installation depended on a **known-good, modified E Ink vendor** and working Android 12. The complete vendor build procedure and Android 12 flash stdout are not preserved. A stock Android 11 vendor must not be assumed to work on Android 16.

### The working vendor stack must be preserved

The successful Q78 configuration included proprietary components such as:

```text
/vendor/lib/hw/hwcomposer.rk30board.so
/vendor/lib/egl/libGLES_mali.so
/vendor/lib/hw/android.hardware.graphics.mapper@4.0-impl-bifrost.so
Android 11 libskia.so
custom 32-bit ARM libheif.so shim
```

The owner recovered an exact-hash-matched [patched Android 12 vendor-image candidate](docs/VENDOR_IMAGE_VERIFICATION.md), including the 1,632-byte ARM32 HEIF shim. The image itself is not part of this repository.

Correct SELinux file labels also mattered (including `same_process_hal_file` on the relevant Mali and mapper files). These proprietary and custom binaries are **not** included in this public repository. The working project's local vendor materials were at:

```text
~/Q78-GSI/known-good/q78-vendor-complete/
~/Q78-GSI/known-good/q78-vendor-complete/library-labels.txt
```

The tested Android 16 flash **did not change `vendor_a`**.

## 2. Files you need

| File | Where to get it | Notes |
| --- | --- | --- |
| Android Platform Tools (`adb`, `fastboot`) | [Google Platform Tools](https://developer.android.com/tools/releases/platform-tools) | Use current binaries on macOS |
| Homebrew `e2fsprogs` (`debugfs`, `e2fsck`) | `brew install e2fsprogs` | Only needed to build a customized system image |
| `lineage-23.2-20260620-a64-bvN.tar.xz` | [A64 GSI release](https://github.com/Lost-Entrepreneur439/LineageOS-a64_gsi/releases/tag/2026-06-20) | **Correct ARM32/Binder64 A/B vanilla image**; do not use `arm64` |
| `system-squeak-arm32_binder64-ab-vanilla.img.xz` | [Phh Treble v416](https://github.com/phhusson/treble_experimentations/releases/tag/v416) | Android 12 staging image, needed only if establishing that baseline |
| Working Q78 modified `vendor_a` | **Owner-supplied previously patched image; build recipe unavailable** | Critical; not distributed here |
| `assets/q78-input-manager-state.abx` | **Included here** | 322-byte Android Binary XML calibration |
| `assets/q78-input-manager-state.xml` | **Included here** | Human-readable calibration source |
| `assets/q78-calibration-seed.rc` | **Included here** | Boot-time install of calibration |
| `scripts/build-abx.py` | **Included here** | Rebuilds the ABX from XML |
| `scripts/prepare-image.sh` | **Included here** | Injects both assets into a copy of ext4 Android 16 |
| `scripts/check-fastbootd.sh` | **Included here** | Read-only checks before flashing |

This repository intentionally does **not** embed 450 MB–1.9 GB operating-system images or private vendor dumps. Download the public image from its original publisher and keep any proprietary files extracted from your own hardware private. See [FILES.md](FILES.md) for integrity information and [PROJECT_SCOPE.md](docs/PROJECT_SCOPE.md) for the precise limits of reproducibility.

## 3. Prepare macOS

Install [Homebrew](https://brew.sh/) if needed, then:

```bash
brew install e2fsprogs xz

# Example: place platform-tools in ~/Downloads/platform-tools
ADB="$HOME/Downloads/platform-tools/adb"
FB="$HOME/Downloads/platform-tools/fastboot"
BASE="$HOME/Q78-GSI"
mkdir -p "$BASE/images" "$BASE/downloads"

"$ADB" version
"$FB" --version
```

Download the specific **A64** Android 16 release archive linked in §2 to `$BASE/downloads/`.

## 4. Get rooted ADB on the Android 12 staging OS

**For the tested stock Android 11 → Android 12 DSU/root sequence**, follow [this newly added chapter](docs/ANDROID11_TO_ANDROID12.md). **This section below applies to the later, proven working Phh Android 12.1 v416 system with the compatible vendor stack already installed.** Do not flash the A12 image or modify `vendor_a` blindly on a factory reader.

On the Q78, enable Developer Options and USB debugging. Connect by USB and authorize the Mac. Then:

```bash
ADB="$HOME/Downloads/platform-tools/adb"
"$ADB" devices -l
"$ADB" -d root
"$ADB" -d shell id -u
"$ADB" -d shell getprop ro.build.version.release
"$ADB" -d shell getprop ro.boot.slot_suffix
```

**Proven staging result:** `id -u` → `0`, OS → `12`, slot → `_a`. If the first command reports `adbd cannot run as root in production builds`, your current system is **not** the documented staging environment: these commands do **not** root arbitrary stock firmware.

The tested Q78 previously installed Phh v416 using **userspace fastbootd**, with the pre-existing compatible vendor stack:

```text
system_a: 1,309,229,056 bytes (historical Android 12 allocation)
vendor_a:   335,544,320 bytes
```

Those are **recorded results**, not universal flash settings. The [documented from-stock staging steps](docs/ANDROID11_TO_ANDROID12.md) stop at an Android 12 DSU with root ADB but nonfunctional UI; full permanent Android 12 installation instructions remain incomplete. Never overwrite a working Q78 vendor partition with a generic vendor image.

## 5. Provision the calibration (no trial-and-error procedures)

The known-good Q78 transform was recovered from Android 12's persisted input settings. We include the exact values and a regenerated ABX file in `assets/`; there is no need to redo the experimental touchscreen investigation.

For completeness, the **single proven Android 12 provisioning command** was:

```bash
"$ADB" -d shell service call input 11 \
  s16 a1cc21cba608c55d28d6dd2b1939004df0e0c756 \
  i32 0 i32 1 \
  f 0 f 1.3333333 f 0 \
  f -0.75 f 0 f 1404
```

This recorded the calibration in `/data/system/input-manager-state.xml` on the rooted Android 12 device. The tested file used **Android Binary XML** (`ABX\x00`). The bundled ABX is generated from the same XML calibration, is 322 bytes long, and follows [AOSP's binary XML serialization](https://android.googlesource.com/platform/frameworks/base/+/b6ad99651e5f/core/java/com/android/internal/util/BinaryXmlSerializer.java).

To regenerate the included binary on macOS:

```bash
python3 scripts/build-abx.py \
  assets/q78-input-manager-state.xml \
  assets/q78-input-manager-state.abx
```

The binary bundled here was reconstructed from the confirmed XML and matches the original **length**, but the original 322-byte extracted file was not available to byte-compare during repository packaging. This is stated rather than pretending it is a verified original dump.

## 6. Obtain and build the Android 16 image

### A. Verify the upstream archive

From the repository root:

```bash
BASE="$HOME/Q78-GSI"
ARCHIVE="$BASE/downloads/lineage-23.2-20260620-a64-bvN.tar.xz"

# Hash recorded from the tested 2026-06-20 upstream download:
EXPECTED=b942b856f7aa72d2f881c933a936a4bc9c438520fad43eebdd4287addc6f2889
ACTUAL="$(shasum -a 256 "$ARCHIVE" | awk '{print $1}')"
[[ "$ACTUAL" == "$EXPECTED" ]] || { echo 'STOP: archive SHA256 mismatch'; exit 1; }

echo 'PASS: upstream archive checksum'
tar -tJf "$ARCHIVE"
tar -xJf "$ARCHIVE" -C "$BASE/images"
```

The tar listing shows the actual extracted `.img` filename. Locate it:

```bash
find "$BASE/images" -type f -name '*.img' -print
```

### B. Prefer the previously validated raw image, if you have it

The **exact final device-tested image** is the local file:

```text
~/Q78-GSI/android16-test/q78-calibration-seed-v1/android16-calibration-seed.img
```

It was created from this intermediate, verified base image:

```text
~/Q78-GSI/android16-test/lineage-23.2-20260620-a64-bvN-debug.img
SHA256: 6cce1bb35958ba62b2d5a556f0838fbee04a34276be8c3b688fe506c86ba501c
```

That intermediate file differs from the upstream image by a `ro.debuggable` one-byte build-property change. **It did not establish working root on Android 16** and is not needed to encode touchscreen calibration, but the final system used this specific intermediate. If you possess the tested, calibration-seeded final image, use it directly and skip the rebuild.

### C. Rebuild an image from the public upstream release

**Reproduction path — prepared in this repository, but not separately DSU-tested from a pristine upstream image.** The proven success used the prepatched intermediate noted above. For exact replication, provide your own verified intermediate as input instead of the pristine image.

Use the path printed by `find` for `SOURCE_IMG`. Example:

```bash
SOURCE_IMG="$HOME/Q78-GSI/images/lineage-23.2-20260620-a64-bvN.img"
OUTPUT_IMG="$HOME/Q78-GSI/images/android16-calibration-seed.img"

./scripts/prepare-image.sh "$SOURCE_IMG" "$OUTPUT_IMG"
```

The script performs the same **necessary system-image changes** as the successful implementation:

```text
/system/etc/q78-input-manager-state.abx
/system/etc/init/q78-calibration-seed.rc
```

The `init` rule runs during `post-fs-data`, copies the ABX file into `/data/system/input-manager-state.xml`, assigns owner `system:system`, applies `0600`, and restores the SELinux context. The script writes the files into a **copy** of the ext4 GSI using `debugfs`, labels them `u:object_r:system_file:s0`, reads both files back, runs a read-only filesystem check, and writes a SHA-256 sidecar. This builder is supplied as a reproducibility aid, not falsely represented as having undergone the original on-device test.

**Required output image size:** `1880514560` bytes. The **known-good file** was confirmed this size and its raw and compressed variants passed local `SHA256SUMS.txt` verification before permanent flashing.

For a newly built image, **test it in DSU before permanent flashing**. The actual successful project used the stock DSU installer and a gzip of the prepared raw ext4 image:

```bash
IMG="$HOME/Q78-GSI/images/android16-calibration-seed.img"
gzip -n -c "$IMG" > "$IMG.gz"
"$ADB" -d push "$IMG.gz" /sdcard/Download/android16-calibration-seed.img.gz
"$ADB" -d shell am start-activity \
  -n com.android.dynsystem/com.android.dynsystem.VerificationActivity \
  -a android.os.image.action.START_INSTALL \
  -d file:///storage/emulated/0/Download/android16-calibration-seed.img.gz \
  --el KEY_SYSTEM_SIZE 1880514560 \
  --el KEY_USERDATA_SIZE 4294967296
```

Approve the DSU installation on the Android 12 device and test Android 16 boot, E Ink rendering, and input. The Android 16 DSU was tested successfully with these integrated calibration assets before the final system flash. A DSU install is a separate prerequisite validation, **not** a substitute for the permanent flash.

## 7. Inspect the Q78 partition layout before flashing

The successful unit had physical `super` size **5,372,903,424 bytes** and slot-A maximum dynamic-partition group size **2,682,257,408 bytes**. Its system needed to grow from `1,309,229,056` to `1,880,514,560` bytes (an increase of `571,285,504` bytes), with enough space left in the group. No other partitions needed shrinking or deleting.

While rooted Android 12 is still running, save the actual layout for **your** device:

```bash
"$ADB" -d shell lpdump > "$HOME/Q78-GSI/lpdump-before-flash.txt"
```

Compare your physical `super`, group maximum, currently allocated extents, and logical partition names with the figures above. **Do not apply this resize if your layout lacks the space**; this guide supplies no untested instructions for deleting other partitions. **We did not obtain verified partition backups or establish a recovery method.** This is a disclosure of a serious risk, not a claim that a working backup procedure exists.

## 8. Permanent flash: exact operations that worked

**Only proceed with a verified compatible vendor partition, an unlocked bootloader, correct slot/group geometry, and a prepared image previously booted successfully in DSU. This operation overwrites your currently installed Android system.**

### A. Reboot into *userspace* fastbootd

```bash
ADB="$HOME/Downloads/platform-tools/adb"
FB="$HOME/Downloads/platform-tools/fastboot"
IMG="$HOME/Q78-GSI/android16-test/q78-calibration-seed-v1/android16-calibration-seed.img"

# Or substitute your verified, DSU-tested output from §6C:
# IMG="$HOME/Q78-GSI/images/android16-calibration-seed.img"

"$ADB" -d reboot fastboot
"$FB" devices
"$FB" getvar is-userspace
"$FB" getvar current-slot
"$FB" getvar is-logical:system_a
"$FB" getvar unlocked
"$FB" getvar secure
"$FB" getvar partition-size:system_a
"$FB" getvar partition-size:vendor_a
```

**The confirmed outputs were:**

```text
is-userspace: yes
current-slot: a
is-logical:system_a: yes
unlocked: yes
secure: yes
partition-size:system_a: 0x4E094000  # BEFORE resize
partition-size:vendor_a: 0x14000000
```

`secure: yes` can coexist with `unlocked: yes`; it does not mean that the Android 16 user space is root-enabled. If slot is not `a`, bootloader is locked, or this is not fastbootd, **stop**. You may use `./scripts/check-fastbootd.sh` for the read-only checks.

### B. Verify the exact local image

```bash
stat -f%z "$IMG"            # Must print: 1880514560
shasum -a 256 "$IMG"        # Save this hash for your own records
```

If using the previously verified local package, its associated `SHA256SUMS.txt` was checked successfully in the field:

```bash
cd "$HOME/Q78-GSI/android16-test/q78-calibration-seed-v1"
shasum -a 256 -c SHA256SUMS.txt
```

Return to a shell with `FB` and `IMG` set if necessary.

### C. Resize `system_a`

**Destructive partition change:**

```bash
"$FB" resize-logical-partition system_a 1880514560
"$FB" getvar partition-size:system_a
```

Expected after resize:

```text
partition-size:system_a: 0x70166000
```

### D. Flash the customized Android 16 system

```bash
"$FB" -S 16M flash system_a "$IMG"
```

The original success used `-S 16M` and completed **109/109** sparse chunks:

```text
Sending sparse 'system_a' 109/109 (9580 KB)  OKAY
Writing 'system_a'                        OKAY
Finished. Total time: 90.621s
```

Fastboot may show `Resizing 'system_a'` even after the explicit resize; that appeared during the successful flash. **Do not interrupt it.**

### E. Check the final layout

```bash
"$FB" getvar partition-size:system_a
"$FB" getvar partition-size:vendor_a
"$FB" getvar current-slot
"$FB" getvar is-userspace
```

Confirmed successful outputs:

```text
partition-size:system_a: 0x70166000
partition-size:vendor_a: 0x14000000
current-slot: a
is-userspace: yes
```

**Do not flash** `vendor_a`, `boot_a`, `dtbo_a`, or `vbmeta_a` as part of this successful system-only sequence. The original successful boot did **not** require changing vbmeta, despite the bootloader reporting `secure: yes`.

## 9. Clean userdata and boot permanently into Android 16

> [!CAUTION]
> The next command **erases userdata** (applications, downloads, DSU images, encryption metadata as supported, settings). This is intentional for a clean Android 12 → 16 installation.

Optionally check userdata formatting support:

```bash
"$FB" getvar partition-type:userdata
"$FB" getvar partition-size:userdata
"$FB" getvar partition-type:metadata
```

Then perform the **user-approved clean wipe** and reboot:

```bash
"$FB" -w
"$FB" reboot
```

On the documented device, the user confirmed **“works good”** after the permanent boot. Android 16 and touchscreen input were operational. The clean wipe is part of the tested sequence; a data-preserving Android 12 → 16 upgrade was **not** tested.

## 10. Validate the installed result

On the device, without relying on Android 16 ADB root:

1. Confirm **Android 16 / LineageOS 23.2** boots normally from internal storage (not DSU).
2. Confirm E Ink screen draws setup and menus.
3. Tap through the interface and test touch at multiple points, including near the edges.
4. Reboot normally and confirm it boots again with touch.
5. Test sleep/wake, Wi-Fi, keyboard, and any target kiosk app before treating the installation as fully stable.

**Tested and confirmed by the original Q78 user:** first permanent Android 16 boot and working screen input. A full subsequent sleep/wake or repeated-reboot endurance run was not logged in the source record. Do not assume those unreported tests passed.

## 11. Root status and limitations

- **Android 12 staging:** USB `adb root` worked, with UID `0`.
- **Android 16 GSI:** does not include root; modifying `/system/build.prop` to say `ro.debuggable=1` did not demonstrate runtime rooted debugging in DSU.
- **No Magisk boot-image patching is included:** its success, AVB behavior, and rollback for this Q78 were not tested; guessing at a `boot_a` patch could break the working E Ink installation.
- **Calibration persistence:** The final image seeds `input-manager-state.xml` during each boot. It worked in permanent Android 16, but overwriting the entire input-manager state may replace other input preferences. Improving that behavior is a separate, future enhancement—not required to reproduce the successful flash.
- **Backups and rollback:** No verified partition backup or full recovery procedure was completed. Backup attempts were unsuccessful; in particular, the Rockchip USB dump was unreliable. The preserved vendor and GSI build files are *not* a device-level backup. No rollback or unbrick commands are offered. Do not relock the bootloader with a modified system installed.

## References and credits

- [Lost-Entrepreneur439's A64 LineageOS 23.2 GSI (2026-06-20)](https://github.com/Lost-Entrepreneur439/LineageOS-a64_gsi/releases/tag/2026-06-20) — unofficial third-party build, initial A64/arm32_binder64 release; no root included.
- [Phh Treble AOSP v416](https://github.com/phhusson/treble_experimentations/releases/tag/v416) — Android 12 staging GSI.
- [AOSP: fastbootd](https://source.android.com/docs/core/architecture/bootloader/fastbootd) — userspace fastboot and logical partition resizing.
- [AOSP: GSI flashing](https://source.android.com/docs/core/tests/vts/gsi) — GSI prerequisites, data wipe, and verified-boot considerations.
- [AOSP: Android Binary XML serializer](https://android.googlesource.com/platform/frameworks/base/+/b6ad99651e5f/core/java/com/android/internal/util/BinaryXmlSerializer.java) — format used to package calibration.
- [AOSP: PersistentDataStore](https://android.googlesource.com/platform/frameworks/base/+/master/services/core/java/com/android/server/input/PersistentDataStore.java) — touchscreen calibration store.
- [e2fsprogs debugfs documentation](https://android.googlesource.com/platform/external/e2fsprogs/+/62fe2f4df048d439f73d7442bb318db7d3a4882a/debugfs/debugfs.8.in) — offline ext4 writes, xattrs, and verification.

**Credits:** LineageOS, TrebleDroid, the A64 GSI maintainer and contributors, Phh's Treble work, and the original MeeBook Q78 hardware experiment/testing. All trademarks and third-party files remain with their respective owners.
