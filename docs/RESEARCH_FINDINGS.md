> **Root-status correction (owner-confirmed):** The Q78 with permanently installed Android 16 is rooted. This historical report does not document how it was rooted. Earlier DSU debugging observations should not be read as denying the final root status.

> **Historical research snapshot.** Later local file searches recovered the compiled HEIF shim, a matching patched vendor-image candidate and the Android 12 flash command block. The original shim source/build script was **not found**. For the final state, see [PROJECT_SCOPE.md](PROJECT_SCOPE.md) and [VENDOR_IMAGE_VERIFICATION.md](VENDOR_IMAGE_VERIFICATION.md). This research document is retained for provenance, not as current action items.

# MeeBook Q78: missing installation steps — evidence and recovery dossier

> **Scope decision (2026-10-24):** This is an archived research/evidence dossier, **not an unlock or unbrick guide**. The installation guide supports already-unlocked Q78s only. No verified full-device backups were completed and no recovery method was proven; exploratory Rockchip readbacks failed. Historical discussions below are not recommended actions.

> **Update after this research was written:** The full Android 12 flash command block, `SYSTEM=~/Q78-GSI/android12.img`, patched vendor image path, and subsequent `fastboot -w` / reboot were recovered from the owner's Terminal history. See [Android 12 flash history](ANDROID12_FLASH_HISTORY.md) for newer evidence. The original fastboot stdout and vendor-build recipe remain unavailable.


**Research date:** 2026-10-24  
**Scope:** The six gaps in `MISSING_ANDROID12_STEPS(1).md`, concerning a reproducible stock Android 11 → Android 12 staging → permanent Android 16 installation of the MeeBook Q78 (RK3566).  
**Status:** Detailed research and local-evidence recovery plan; **not** a complete, newly tested stock-to-Android-16 installation procedure.

> **Bottom line:** A Q78-specific public repository now documents the **successful Android 16 system-only fastbootd flash** with exact sizes and representative `OKAY` output. It **does not preserve** the original custom 32-bit `libheif.so` shim, the steps creating the modified E Ink vendor image, the stock bootloader-unlock process, or an Android 12 permanent-install transcript. Those missing artifacts **cannot be truthfully recreated from a library name or an outcome statement**. This dossier extracts everything that can be substantiated and gives actionable, read-only ways to locate the rest on the original Mac.

## Evidence levels used in this report

- **CONVERSATION-OBSERVED** — An exact command/result appears in the original Q78 Android 11 → DSU Android 12 conversation supplied here.
- **REPOSITORY-REPORTED** — A public project records a successful procedure, potentially retrospectively, but its underlying local artifacts / full console transcript were not provided to this analysis.
- **AOSP-DOCUMENTED** — The Android upstream documents the general mechanism; **not proof of success on this Q78**.
- **PROPOSED / READ-ONLY** — A reasonable inspection command or data-collection procedure that has **not been reported as tested** on the device.
- **NOT RECOVERED** — Required source, binary, hash, or successful log has not been located.

## Executive status of the six gaps

| # | Missing item | What has been found | What is still missing |
|---|---|---|---|
| 1 | Stock bootloader unlocking | Android 11 reported `ro.boot.flash.locked=0` and `ro.boot.verifiedbootstate=orange`; final Android 16 repository reports fastbootd `unlocked: yes`. | Any bootloader-unlock transaction on a **locked, factory-stock Q78**, or proof the tested Q78 was ever locked. |
| 2 | ARM32 `libheif.so` shim | Q78 graphics linker failure chain and a precise location where the **working proprietary/custom vendor files were retained locally**. | Actual shim source, exported symbols, compile invocation, build NDK version, ABI proof, binary and hash. |
| 3 | Modified `vendor.img` construction | Stock `super` geometry, stock lib extraction and temporary overlay experiments; final repo states a working 320 MiB `vendor_a` with specific Mali/mapper/Skia/shim components and labels. | Reproducible build from stock, all binaries, complete SELinux xattrs, image hash, exact successful `vendor_a` flash transcript. |
| 4 | Permanent **Android 12** fastbootd log | The **Android 16** success sequence is recorded in detail (section 4 below). The Android 12 **DSU** installation and `adb root` are directly observed. | Exact Android 12 permanent-flash commands, source images, first-boot log, any `vendor_a` flash and observed OKAY output. |
| 5 | Android 12 AVB and userdata treatment | Android 11 verified-boot state `orange`; final Android 16 flash reportedly **left vbmeta unchanged**, did `fastboot -w`, and booted. | Android **12** vbmeta/verity and userdata decision and corresponding first-boot evidence. |
| 6 | Tested rollback / unbrick | Rockchip USB Loader connection, GPT read, and confirmation of a 32 MiB `0xCC` readback boundary. | Tested full restore, verified stock recovery image, boot0/boot1 handling, Maskrom loader/test transcript. |

---

## 1. Bootloader unlocking — what the existing evidence establishes

**CONVERSATION-OBSERVED:** On stock Android 11 the Q78 returned:

```text
ro.boot.flash.locked=0
ro.boot.verifiedbootstate=orange
ro.oem_unlock_supported=1
ro.boot.slot_suffix=_a
ro.boot.dynamic_partitions=true
```

`adb root` **failed** on the production Android 11 build; that says nothing about its bootloader unlock state. The unit entered Rockchip Loader mode via ADB, and Rockchip reported USB `Vid=0x2207,Pid=0x350a`, **Loader**.

**REPOSITORY-REPORTED:** In the later successful fastbootd session, the public Q78 guide records:

```text
is-userspace: yes
current-slot: a
is-logical:system_a: yes
unlocked: yes
secure: yes
```

**Interpretation:** The tested unit was unlocked at both observed phases. None of these outputs establishes *how* it became unlocked. `secure: yes` coexisting with `unlocked: yes` is normal and does not mean the flashing lock was on. There is no evidence that the tester ran `fastboot flashing unlock`, `fastboot oem unlock`, or a Rockchip unlock command.

**What would close the gap:** Original purchase/factory-state note; OEM-unlocking switch state; full initial bootloader/fastboot session transcript; exact before/after output from an actual unlock, if one happened. For a new factory-locked unit, determine the supported OEM unlock procedure independently. **Do not insert an untested unlock command in a Q78 guide.**

**Read-only inspection, if the device currently exposes fastbootd:** 

```bash
FB="$HOME/Downloads/platform-tools/fastboot"
"$FB" devices
"$FB" getvar is-userspace
"$FB" getvar unlocked
"$FB" getvar current-slot
```

Do not reboot a working device into another mode solely to collect these values unless that disruption is wanted. Current unlocked status still cannot reconstruct the historical unlock sequence.

## 2. Custom ARM32 `libheif.so` shim — how to find and document the real artifact

### What actually happened in the Android 12 session

**CONVERSATION-OBSERVED:** The installed image was Phh-Treble v416 `system-squeak-arm32_binder64-ab-vanilla.img.xz`, a **32-bit userspace** (`armeabi-v7a` / A64 Binder64). DSU booted far enough for `adb shell getprop ro.build.version.release` to print `12`; `adb root` worked (`uid=0(root)`).

The stock Rockchip hardware composer was `/vendor/lib/hw/hwcomposer.rk30board.so`. The troubleshooting exposed this concrete sequence of missing/transitively needed framework libraries:

```text
hwcomposer.rk30board.so
  -> libskia.so       (initial dependency missing from A12)
     -> libandroidicu.so
     -> libdng_sdk.so
     -> libicuuc.so (via ICU)
     -> libheif.so
        -> libmedia.so (A11 libheif required this private A11 framework library)
```

The A11 `libskia.so` was recovered from a **read-only mapping** of the stock `system_a` logical partition at:

```text
/data/local/tmp/q78-stock/system/lib/libskia.so
```

A RAM-based tmpfs + OverlayFS / bind-mount experiment exposed libraries under `/vendor/lib`, but the **last error in this original conversation** was:

```text
dlopen failed: library "libmedia.so" not found:
needed by /vendor/lib/libheif.so in namespace (default)
```

At that point SurfaceFlinger also had a `SIGABRT`, so a definitive working Android 12 graphics fix **is not included in this chat**. The later public repository reports that a *custom 32-bit ARM `libheif.so` shim* was ultimately used in the working vendor stack, but **does not distribute its source or binary**.

### Most likely places to recover it — NOT VERIFIED PRESENT

The public Q78 project identifies local working materials at:

```text
~/Q78-GSI/known-good/q78-vendor-complete/
~/Q78-GSI/known-good/q78-vendor-complete/library-labels.txt
```

Look within the **original Mac's** `~/Q78-GSI/` directory for:

```text
libheif.so
*heif*.c
*heif*.cpp
*shim*.c
*shim*.cpp
*vendor*.img
*build*.sh
*clang*.log
```

The downloadable `collect_q78_evidence.py` included with this report automates a **read-only inventory** of likely files and hashes small candidates. It does not fetch files from the Q78, alter images, upload anything, or execute flash commands.

### How to identify the real shim if found

A valid reproduction needs all of the following:

1. **Source:** filename and complete C/C++ source, including any intentional exported `libheif` symbols and return behavior.
2. **Toolchain:** Android NDK revision, Clang binary, target triple / API (`armv7a-linux-androideabi<API>` if NDK-built), command-line flags, and linked dependencies.
3. **Output:** `file libheif.so` showing `ELF 32-bit`, ARM EABI; `readelf -h`, `readelf -d`, dynamic exports, `SONAME` and `NEEDED` entries.
4. **Deployment:** actual placement in the modified `/vendor/lib/`, file mode and SELinux xattr, and confirmation it was available to the vendor linker namespace.
5. **Integrity:** `shasum -a 256 libheif.so` and a hash of the final vendor image containing it.
6. **Functional test:** log showing the composer staying loaded and stable `surfaceflinger`, boot completion, real E Ink refresh, and working touch.

Inspect (example after finding the file):

```bash
file /path/to/libheif.so
shasum -a 256 /path/to/libheif.so
readelf -h /path/to/libheif.so
readelf -d /path/to/libheif.so
readelf -Ws /path/to/libheif.so | grep -E 'GLOBAL|WEAK' | head -n 60
```

`readelf` may be supplied by `llvm-readelf` from an Android NDK or Homebrew; macOS does not always ship GNU `readelf`.

**Important engineering limitation:** A random upstream desktop `libheif` binary is *not* a substitute for this shim, and the mere fact that a `.so` has the required filename says nothing about its ABI. Producing a tiny empty shared object could satisfy a `DT_NEEDED` name yet fail symbol resolution or corrupt behavior. **No tested shim source was found in the supplied record or public Q78 repository. Do not represent example code as the working source.**

## 3. Modified `vendor.img` — known components, actual geometry, and extraction procedure

### Stock partition geometry obtained from the device

**CONVERSATION-OBSERVED** via root ADB `lpdump --slot=0 /dev/block/by-name/super`:

| Logical partition | Start sector within `super` | Length (512-byte sectors) | Stock extent size |
|---|---:|---:|---:|
| `system_a` | 2,048 | 2,341,184 | 1,198,686,208 B |
| `system_ext_a` | 2,344,960 | 218,944 | 112,099,328 B |
| `vendor_a` | 2,564,096 | 237,360 | 121,528,320 B |
| `product_a` | 2,801,664 | 195,568 | 100,130,816 B |
| `odm_a` | 2,998,272 | 12,016 | 6,152,192 B |

The physical `super` partition was `/dev/block/mmcblk2p18`, and the stock `system_a` was exposed as `/dev/block/dm-7` using a read-only `dmctl` mapping. That is direct evidence of access to *real flash data* under root ADB, unlike Rockchip USB `rl` beyond 32 MiB.

**REPOSITORY-REPORTED** later successful staging allocation:

```text
Android 12 system_a = 1,309,229,056 bytes
Modified vendor_a   =   335,544,320 bytes (320 MiB)
```

Thus the successful modified vendor allocation was much larger than the older stock extent visible in the DSU log. **Do not mistake that old stock vendor extent for the known-good 320 MiB vendor image.** The record does not contain the resize and rebuild events that changed it.

### Working vendor stack named by the later repository

- `/vendor/lib/hw/hwcomposer.rk30board.so`
- `/vendor/lib/egl/libGLES_mali.so`
- `/vendor/lib/hw/android.hardware.graphics.mapper@4.0-impl-bifrost.so`
- Android 11 framework `libskia.so` and dependencies made vendor-accessible
- Custom ARM32 `libheif.so` shim
- File SELinux labels, notably `same_process_hal_file` for the relevant Mali/mapper HAL and dependent libraries

The exact complete `.so` manifest, modes, labels, working `vendor.img`, and source-to-output recipe are **not published**. The working directory is reported as:

`~/Q78-GSI/known-good/q78-vendor-complete/`

### Inspection of an actual known-good vendor image (do not modify it)

If the local Mac has a vendor image, capture:

```bash
IMG="/absolute/path/to/known-good-vendor.img"
file "$IMG"
stat -f%z "$IMG"
shasum -a 256 "$IMG"

# If it is a raw ext4 filesystem, e2fsprogs can inspect it read-only:
# brew install e2fsprogs
# brew --prefix e2fsprogs -> .../opt/e2fsprogs
DBG="$(brew --prefix e2fsprogs)/sbin/debugfs"
"$DBG" -R 'ls -l /lib/hw' "$IMG"
"$DBG" -R 'stat /lib/hw/hwcomposer.rk30board.so' "$IMG"
"$DBG" -R 'ea_list /lib/hw/hwcomposer.rk30board.so' "$IMG"
"$DBG" -R 'ea_list /lib/egl/libGLES_mali.so' "$IMG"
```

If `file` reports **Android sparse image**, convert a *copy* to raw with `simg2img` before attempting `debugfs`; do not treat sparse data as raw ext4. Ext4 images can also be inspected with `e2fsck -fn` (read-only and non-mutating flags).

The `security.selinux` extended attribute, not merely a text label list, is relevant when reproducing the vendor image. AOSP requires certain same-process HALs and dependencies to have `same_process_hal_file`; blindly labeling every file this way is incorrect. See AOSP SELinux references below.

### Potential acquisition paths

1. **Best:** locate the known-good completed `vendor.img` or the entire local `known-good/q78-vendor-complete` tree; enumerate and hash it.
2. If currently running rooted staging Android, **conditionally** use read-only extraction of its actual `vendor_a` device-mapper block mapping (do *not* assume `system_a` maps to stock when DSU is active). Verify size and ext4 contents with `file`, filesystem checks, and ELF metadata.
3. A surviving modified `super.img` may be parsed offline with Android `lpunpack`, `lpdump`, and related partition tools, as long as its data is genuinely readable.
4. Rebuild from factory-stock `vendor` **only after** retrieving the actual modifications, dependencies, SELinux labels, and tested image parameters.

No full, verified `lpmake`, resize, filesystem image-construction, and `vendor_a` flashing transcript was found for the first stock-to-A12 transition. There is **not enough evidence** to publish executable replacement commands for this part.

## 4. Fastbootd flash transcript — Android 16 found, Android 12 still missing

### Confirmed Android 12 staging (this conversation)

- GSI: `system-squeak-arm32_binder64-ab-vanilla.img.xz` / Phh v416.
- DSU Sideloader started Android's `com.android.dynsystem/.VerificationActivity` through ADB.
- User reported “dynamic system installed” and selected Restart.
- ADB detected `Phh_Treble_vanilla` and Android `12`.
- `adb root` worked and reported UID 0.
- **No complete successful permanent Android 12 fastbootd transcript exists in this supplied conversation.**

### Exact successful Android 16 sequence published by the Q78 project

**REPOSITORY-REPORTED**, dated **2026-10-24**. This is **not** an Android 12 transcript, and assumes a pre-existing **known-good modified vendor** and a verified, tested Android 16 image.

**Prerequisites observed:**

```text
is-userspace: yes
current-slot: a
is-logical:system_a: yes
unlocked: yes
secure: yes
partition-size:system_a: 0x4E094000  (1,309,229,056 bytes)
partition-size:vendor_a: 0x14000000  (335,544,320 bytes)
```

The existing `super` had 5,372,903,424 physical bytes, with slot-A dynamic partition group maximum 2,682,257,408 bytes. The target Android 16 raw `system_a` image size was **1,880,514,560 bytes**. The system required a growth of **571,285,504 bytes** and reportedly fit without deleting other logical partitions.

The published procedure, transcribed for evidence **rather than as an instruction to execute blindly**, was:

```bash
ADB="$HOME/Downloads/platform-tools/adb"
FB="$HOME/Downloads/platform-tools/fastboot"
IMG="$HOME/Q78-GSI/android16-test/q78-calibration-seed-v1/android16-calibration-seed.img"

# Starting in the known-good rooted Android 12 environment:
"$ADB" -d reboot fastboot
"$FB" devices
"$FB" getvar is-userspace
"$FB" getvar current-slot
"$FB" getvar is-logical:system_a
"$FB" getvar unlocked
"$FB" getvar secure
"$FB" getvar partition-size:system_a
"$FB" getvar partition-size:vendor_a

stat -f%z "$IMG"           # 1880514560
shasum -a 256 "$IMG"        # record device-tested file's hash

# DESTRUCTIVE — from the published success record:
"$FB" resize-logical-partition system_a 1880514560
"$FB" getvar partition-size:system_a
"$FB" -S 16M flash system_a "$IMG"

# Post-write status checks:
"$FB" getvar partition-size:system_a
"$FB" getvar partition-size:vendor_a
"$FB" getvar current-slot
"$FB" getvar is-userspace

# DESTRUCTIVE userdata wipe and reboot in the published success:
"$FB" -w
"$FB" reboot
```

The recorded successful transfer included:

```text
Sending sparse 'system_a' 109/109 (9580 KB)  OKAY
Writing 'system_a'                        OKAY
Finished. Total time: 90.621s
```

Post-resize:

```text
partition-size:system_a: 0x70166000  (1,880,514,560 bytes)
partition-size:vendor_a: 0x14000000  (unchanged)
current-slot: a
is-userspace: yes
```

The successful Android 16 procedure **did not** flash `vendor_a`, `boot_a`, `dtbo_a`, or `vbmeta_a`. It preserved the already-modified Rockchip E Ink vendor partition. The GSI had integrated touchscreen calibration data and was DSU-tested before permanent flashing.

Relevant local Android 16 artifacts reported by the project:

```text
~/Q78-GSI/android16-test/lineage-23.2-20260620-a64-bvN-debug.img
SHA256: 6cce1bb35958ba62b2d5a556f0838fbee04a34276be8c3b688fe506c86ba501c

~/Q78-GSI/android16-test/q78-calibration-seed-v1/android16-calibration-seed.img
Size: 1880514560 bytes
Exact SHA256: not preserved in the public record

~/Q78-GSI/android16-test/q78-calibration-seed-v1/SHA256SUMS.txt
```

Original upstream archive:

`lineage-23.2-20260620-a64-bvN.tar.xz`  
Recorded upstream SHA-256: `b942b856f7aa72d2f881c933a936a4bc9c438520fad43eebdd4287addc6f2889`

**Important:** These values describe **Android 16 on the post-modification Q78**, not factory-stock Android 11. The upstream archive and public project's image-preparation scripts are linked in the sources section. No new image was downloaded, built, or flashed during preparation of this dossier.

### What is still required for the Android 12 permanent flash

Retrieve the original Android 12 session's actual:

1. `fastboot getvar` state before first Android 12 flash.
2. Final Android 12 `system_a` image path, raw size, SHA-256.
3. Modified `vendor_a` image path, raw size, SHA-256.
4. Exact `resize-logical-partition` and `flash` commands and flags for **both** partitions (if both were flashed).
5. Flash `OKAY` output and post-flash `getvar` values.
6. AVB/vbmeta decision and userdata wipe.
7. First normal boot report: Android version, SurfaceFlinger stable, E Ink usable.

No Android 16 command should be relabeled as a proven Android 12 step.

## 5. AVB, vbmeta, and userdata — disentangle Android 11 / 12 / 16

| Phase | Evidence | Conclusion |
|---|---|---|
| Stock Android 11 | `ro.boot.flash.locked=0`; `ro.boot.verifiedbootstate=orange` | Device already reported unlocked; does not reveal how it was unlocked or whether vbmeta ever changed. |
| Android 12 **DSU test** | DSU installed and booted far enough for rooted ADB; its userdata was an approximately 3.7 GiB F2FS `/data` mount (`/dev/block/dm-5`). | DSU was demonstrated; nothing shows that stock AVB partitions had to be flashed or that normal userdata was wiped to create the DSU. |
| Permanent Android 12 | No flash/boot completion transcript present in source conversation. | **Unknown:** vbmeta flags, image hashes, userdata format/wipe, first normal boot. |
| Permanent Android 16 | Repository says no `vbmeta_a` write, no boot/dtbo write; `fastboot -w` followed by reboot; new OS booted. | **Recorded for this one already-unlocked, already-modified unit only.** |

**AOSP-DOCUMENTED:** General GSI docs describe a verified-boot disable procedure on *some* devices, and `fastboot -w` wipes userdata. This generic example is not authorization to change the Q78's vbmeta. The Q78's published Android 16 successful procedure made **no vbmeta change**. Keep these facts separate.

To investigate the original permanent Android 12 phase, search the local terminal history or installer logs for strings such as `--disable-verification`, `vbmeta`, `-w`, `format:`, `erase userdata`, `resize-logical-partition`, and successful `fastboot flash` reports. Because shell histories can contain credentials, review and redact before sharing. Do not upload your entire raw shell history.

## 6. Rollback and unbrick — what's real and what's not

**CONVERSATION-OBSERVED:** The Q78 entered Rockchip Loader:

```text
DevNo=1 Vid=0x2207,Pid=0x350a,LocationID=1 Loader
```

`rkdeveloptool rfi` reported 61,079,552 512-byte sectors (31,272,730,624 bytes = 29.125 GiB). `rkdeveloptool ppt` returned its full GPT partition names. A read of the first 32 MiB produced a legitimate GPT (`EFI PART`) and real board firmware signatures, including:

```text
DDR Version V1.09 20211103_resume
U-Boot SPL ... (Apr 13 2021)
RK3566-Q78-BYRead-116
```

**However:** The resulting 30-piece, 29.125 GiB USB backup was **not usable**. The ADB-obtained `boot_a.img` from Loader mode began with repeated `0xCC` instead of `ANDROID!`; a byte-by-byte scan found **zero non-`0xCC` bytes in at least chunks 01–13** and repeated `0xCC` sampled throughout every chunk. The common Rockchip USB Loader read cap at **absolute 32 MiB** explains this pattern. The files' correct sizes and SHA-256 checks only checked what the host wrote, not that the chip returned real flash contents.

**Not recovered:** A complete verified stock image; a Q78-compatible Maskrom RAM helper verified to read beyond 32 MiB; a successful restore transcript; eMMC boot0/boot1 extraction or reprogramming; a validated stock factory firmware package.

**Useful alternative demonstrated in the DSU session:** Root ADB accessed the real stock `super` block device via `/dev/block/by-name/super`, including an `lpdump` and a read-only mapped mount of stock `system_a`. If a comparable *rooted* environment is available, reading individual partitions using root ADB is a credible route to **genuine** image extraction without Rockchip Loader's 32 MiB restriction. This is an acquisition method, **not a tested full unbrick plan**.

**Official Rockchip tooling** distinguishes `db` (download temporary boot code), `rl` (read LBA), `wl` (write LBA), and `ef` (erase). Never claim full readback just because `rl` returns a 100% progress report. Never give a recovery-flash command until the source image, device mode, offsets, scope, and a tested restoration path are established.

Possible recovery components that must be checked for a complete plan: boot images, dtbo, vbmeta, trust/uboot, E Ink waveform and related calibration, dynamic `super` layout, userdata formatting, and possibly separate eMMC boot hardware regions. A `super.img` containing the wrong vendor or the wrong logical-partition geometry can make recovery worse.

**Practical conclusion:** The user has said recovery is lower priority than getting the OS working, so this dossier documents the limitation without demanding another 29 GiB backup attempt.

---

## 7. Exact local artifact recovery — recommended order

1. **Recover the known-good vendor folder first.** `~/Q78-GSI/known-good/q78-vendor-complete/` and `library-labels.txt` are named in the published guide. Look for `libheif.so`, `libskia.so`, a finalized `vendor.img`, an accompanying hash/manifest, and any install script or build log. This is the single biggest obstacle to a reproducible **from-stock** procedure.
2. **Recover shim source or compilation history.** Search the original `~/Q78-GSI` workspace for `*heif*.c`, `*shim*.c`, `Android.mk`, `CMakeLists.txt`, `.sh` build scripts, LLVM/Clang logs, and Make/Ninja command output. Search shell history manually only if source is absent.
3. **Recover fastboot transcripts.** Look in `~/Q78-GSI` for `*fastboot*.log`, `*flash*.log`, and text logs. Distinguish Android 12 from Android 16 before copying commands.
4. **Record final actual hashes.** Hash the shim and vendor files. If the Android 16 final image is present, hash it; the public record deliberately does not invent that hash.
5. **Recover any Android 12 AVB/wipe details.** Search logs for exact `vbmeta`, `fastboot -w`, and first-boot messages.
6. **Avoid publishing proprietary binaries by default.** A reproducibility document can publish names/hashes/build descriptions without redistributing MeeBook/Rockchip proprietary files.

Use the included `collect_q78_evidence.py` to create a targeted *local* inventory and SHA-256 manifest on the Mac. Review its report before sharing it. It does not find deleted files, recover hidden chats, or reconstruct files that do not exist on disk.

## 8. Verified public references

**Device-specific account (research findings are based on this source, not independently re-flashed):**

- Q78 Android 16 project README: https://github.com/carlosemiliobooker/MeeBook-Q78-Android16
- Q78 file manifest and missing binary disclosure: https://github.com/carlosemiliobooker/MeeBook-Q78-Android16/blob/main/FILES.md
- Public GSI A12 v416 release: https://github.com/phhusson/treble_experimentations/releases/tag/v416
- Android 16 A64 GSI release recorded in project: https://github.com/Lost-Entrepreneur439/LineageOS-a64_gsi/releases/tag/2026-06-20

**Platform technical references (general mechanisms, not Q78-tested instructions):**

- AOSP fastbootd architecture and logical partition operations: https://source.android.com/docs/core/architecture/bootloader/fastbootd
- AOSP dynamic partitions: https://source.android.com/docs/core/ota/dynamic_partitions/implement
- AOSP generic GSI flashing constraints: https://source.android.com/docs/core/tests/vts/gsi
- AOSP SELinux same-process HAL labeling: https://source.android.com/docs/core/architecture/vndk/dir-rules-sepolicy
- AOSP Android linker namespace rules: https://source.android.com/docs/core/architecture/vndk/linker-namespace
- Rockchip official USB utility: https://github.com/rockchip-linux/rkdeveloptool
- Reference investigation of the 32 MiB `0xCC` problem (different Rockchip device): https://github.com/wesbos/photo-frame-dashboard/blob/main/docs/loader-research.md
- AOSP logical partition tools: https://android.googlesource.com/platform/system/extras/+/refs/heads/android11-gsi/partition_tools/README.md
- `debugfs` filesystem extended-attribute inspection: https://android.googlesource.com/platform/external/e2fsprogs/+/844087a335bc940b2cbee91853a4c7b943596845/debugfs/debugfs.8.in

## 9. Deliverable integrity and next documentation milestone

This report is **an evidence ledger plus retrieval instructions**, not a runnable from-stock installer. The included inventory script is safe to run locally for evidence discovery but cannot fill gaps for missing binaries or undisclosed source.

**To make the original six missing rows truly reproducible, the critical minimum is:**

- Actual 32-bit shim source and SHA-256 of the produced `libheif.so`.
- A complete list, byte hashes, modes, and security labels for every change to stock vendor, with finalized `vendor.img` and proof it booted.
- Permanent Android 12 `fastbootd` transaction transcript with actual image hashes, AVB decision, and first normal boot.
- Device-specific bootloader unlock evidence if testing on a locked stock unit.
- A separate tested rollback/unbrick log if recovery is to be claimed.

Until recovered, label those steps **NOT DOCUMENTED** rather than manufacturing code, commands, or success claims. The Android 16 system-only flash **is** documented for the known-good premodified Q78; it does not close the earlier from-stock vendor and bootloader gaps.
