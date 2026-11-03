#!/usr/bin/env bash
# PREPARATION ONLY. No licensed model is copied or physical result invented.
set -euo pipefail
umask 077
private="$HOME/mram_private/E02_256x256"
mkdir -p "$private/config" "$private/private_netlists" "$private/private_pex" "$private/raw" "$private/logs" "$private/postprocess"
chmod 700 "$private" "$private/config" "$private/private_netlists" "$private/private_pex" "$private/raw" "$private/logs" "$private/postprocess"
manifest="$private/logs/preflight_manifest.txt"
{
  printf 'UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf 'Host: %s\n' "$(hostname)"
  printf 'TARGET: 256 rows x 256 columns = 65536 cells\n'
  printf 'STATUS: preparation only, no electrical model or result\n'
  if command -v spectre >/dev/null 2>&1; then
    printf 'Spectre: available\n'
    spectre -W 2>&1 | head -n 5 || true
  else
    printf 'Spectre: NOT ON PATH; load authorized NUS Cadence environment\n'
  fi
  if command -v virtuoso >/dev/null 2>&1; then
    printf 'Virtuoso: available\n'
  else
    printf 'Virtuoso: NOT ON PATH; load authorized NUS Cadence environment\n'
  fi
  printf 'No technology or model files copied.\n'
} > "$manifest"
cat "$manifest"
printf '\nPRIVATE WORKSPACE (DO NOT COMMIT): %s\n' "$private"
