#!/usr/bin/env bash
# E36: NUS GF 256-row x4-column CURRENT screen over real E01 activity percentiles.
# Activity m matches frozen E01; spatial masks are synthetic and NOT actual
# MNIST vectors. Interconnect resistances are E30's ASSUMED values, NOT PEX.
set -euo pipefail
umask 077
cd "$HOME/MRAM_Path_Finding"
ROOT="$HOME/mram_private/E36_activity_GF"
mkdir -p "$ROOT"
LOG="$ROOT/E36_pilot_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
echo "E36_LOG=$LOG"
{
  echo "========== REPOSITORY COMMIT =========="
  git rev-parse HEAD
  echo "========== COMPILE AND PURE-LOGIC SELFTEST =========="
  python3 -m py_compile experiments/e36_e01_activity_gf_screen.py
  python3 -u experiments/e36_e01_activity_gf_screen.py selftest
  echo "========== FROZEN E01 & E30 CHECK; PREVIEW MASKS =========="
  python3 -u experiments/e36_e01_activity_gf_screen.py preview \
      --m-values 24,56,128 --repeats 2
  echo "========== ACTUAL GF PILOT; 256 ROWS X 4 COLUMNS =========="
  python3 -u experiments/e36_e01_activity_gf_screen.py run \
      --m-values 24,56,128 \
      --repeats 2 \
      --chunk-scenarios 2 \
      --timeout-sec 480 \
      --private "$ROOT"
  echo "========== PRIVATE RESULTS =========="
  find "$ROOT" -maxdepth 2 -name E36_RESULTS.json -print
  echo "E36_COMPLETE_NOT_PEX_NOT_PHYSICAL_ADC_NOT_NEURAL_INFERENCE"
} 2>&1 | tee "$LOG"
