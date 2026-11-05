#!/usr/bin/env bash
# E28S one-shot: single coupled four-column Spectre DC deck per shared-SL arm.
# Results private; GF transistor + student MTJ, ASSUMED return R not actual PEX.
set -euo pipefail
umask 077
cd "$HOME/MRAM_Path_Finding"
OUT="$HOME/mram_private/E28_1T1"
mkdir -p "$OUT"
LOG="$OUT/E28S_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
echo "E28S_LOG=$LOG"
{
  echo "========== E28S RESEARCH GATE =========="
  git rev-parse HEAD
  echo "========== VERIFY SOURCE =========="
  python3 -m py_compile experiments/e28s_shared_sl_four_column_gf.py
  python3 -u experiments/e28s_shared_sl_four_column_gf.py selftest
  echo "========== GENUINELY COUPLED FOUR-COLUMN GF SPECTRE =========="
  python3 -u experiments/e28s_shared_sl_four_column_gf.py run --private "$OUT" --timeout-sec 300
  echo "========== E28S PRIVATE DELIVERABLE =========="
  find "$OUT" -maxdepth 2 -name E28S_RESULTS.json -type f -print
  echo "E28S_COMPLETE"
  echo "SCOPE=nominal GF transistor + student static MTJ, explicitly ASSUMED shared return resistor, no actual 1T1 PEX"
} 2>&1 | tee "$LOG"
