#!/usr/bin/env bash
# Read-only fastbootd sanity checks. No writes.
set -euo pipefail
FB="${FB:-$HOME/Downloads/platform-tools/fastboot}"
[[ -x "$FB" ]] || { echo "Missing fastboot binary: $FB" >&2; exit 1; }

check() {
  local name="$1" expect="$2" out
  out="$($FB getvar "$name" 2>&1)" || { echo "$out" >&2; exit 1; }
  printf '%s\n' "$out" | grep -F -- "$name: $expect" >/dev/null || {
    echo "Expected $name: $expect; got:" >&2
    echo "$out" >&2
    exit 1
  }
  printf 'PASS %-24s %s\n' "$name" "$expect"
}

check is-userspace yes
check current-slot a
check is-logical:system_a yes
check unlocked yes
printf '\nCurrent partition allocations (read-only):\n'
"$FB" getvar partition-size:system_a
"$FB" getvar partition-size:vendor_a
printf '\nCheck available super-group headroom independently before any resize.\n'
