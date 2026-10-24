#!/usr/bin/env bash
# Inject the verified Q78 input calibration into an A64/Binder64 Android 16 ext4 GSI.
# Run on macOS with Homebrew e2fsprogs; never run against a live block device.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 INPUT_EXT4_GSI.img OUTPUT_Q78_GSI.img" >&2
  exit 2
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$1"
DEST="$2"
CAL="$HERE/assets/q78-input-manager-state.abx"
RC="$HERE/assets/q78-calibration-seed.rc"

if ! command -v brew >/dev/null; then
  echo 'ERROR: Homebrew not found; install e2fsprogs (brew install e2fsprogs)' >&2
  exit 1
fi
BREW_E2FS="$(brew --prefix e2fsprogs)"
DBG="${DBG:-$BREW_E2FS/sbin/debugfs}"
FSCK="${FSCK:-$BREW_E2FS/sbin/e2fsck}"

[[ -f "$SRC" && -f "$CAL" && -f "$RC" ]] || { echo "ERROR: missing input or calibration asset" >&2; exit 1; }
[[ -x "$DBG" && -x "$FSCK" ]] || { echo "ERROR: install e2fsprogs: brew install e2fsprogs" >&2; exit 1; }
[[ "$SRC" != "$DEST" ]] || { echo "ERROR: output must differ from input" >&2; exit 1; }
[[ ! -e "$DEST" ]] || { echo "ERROR: output exists; refusing to overwrite $DEST" >&2; exit 1; }
[[ "$(stat -f%z "$SRC")" == "1880514560" ]] || { echo "ERROR: unexpected image size; expected 1880514560 bytes" >&2; exit 1; }
[[ "$(stat -f%z "$CAL")" == "322" ]] || { echo "ERROR: unexpected ABX asset size" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Ensure this is the expected GSI type/layout before any changes.
"$DBG" -R 'stat /system/build.prop' "$SRC" > "$TMP/source-stat" 2>"$TMP/source-err"
grep -q 'Inode:' "$TMP/source-stat" || { cat "$TMP/source-err" >&2; echo 'ERROR: unexpected system image layout' >&2; exit 1; }

echo 'Copying raw GSI (source is never modified)...'
cp -p "$SRC" "$DEST"

# Both files are new to the base image. debugfs supports ext4 offline writes and xattrs.
for SPEC in "$CAL|/system/etc/q78-input-manager-state.abx" "$RC|/system/etc/init/q78-calibration-seed.rc"; do
  LOCAL="${SPEC%%|*}"
  DEVICE="${SPEC#*|}"
  echo "Injecting $DEVICE"
  "$DBG" -w -R "write $LOCAL $DEVICE" "$DEST" > "$TMP/write-out" 2> "$TMP/write-err"
  grep -q 'Allocated inode:' "$TMP/write-out" || { cat "$TMP/write-out" "$TMP/write-err" >&2; echo "ERROR: failed to write $DEVICE" >&2; exit 1; }
  "$DBG" -w -R "ea_set $DEVICE security.selinux u:object_r:system_file:s0" "$DEST" > /dev/null
  "$DBG" -R "stat $DEVICE" "$DEST" > "$TMP/stat"
  grep -q 'Inode:' "$TMP/stat" || { echo "ERROR: missing injected inode $DEVICE" >&2; exit 1; }
  "$DBG" -R "dump $DEVICE $TMP/dump" "$DEST" > /dev/null
  cmp "$LOCAL" "$TMP/dump" || { echo "ERROR: image readback differs for $DEVICE" >&2; exit 1; }
  "$DBG" -R "ea_get $DEVICE security.selinux" "$DEST" > "$TMP/label" 2>/dev/null
  grep -q 'u:object_r:system_file:s0' "$TMP/label" || { echo "ERROR: incorrect SELinux label on $DEVICE" >&2; exit 1; }
  rm -f "$TMP/dump"
done

echo 'Checking ext4 filesystem (read-only check)...'
"$FSCK" -fn "$DEST"
[[ "$(stat -f%z "$DEST")" == '1880514560' ]] || { echo 'ERROR: resulting image has unexpected size' >&2; exit 1; }

shasum -a 256 "$DEST" > "$DEST.sha256"
echo "Prepared image: $DEST"
echo "SHA256 stored: $DEST.sha256"
echo 'NOTE: This script has not been validated end-to-end on a fresh public image; DSU-test newly built images before permanent flashing.'
