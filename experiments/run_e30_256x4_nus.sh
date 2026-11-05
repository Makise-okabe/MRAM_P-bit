#!/usr/bin/env bash
# E30 real NUS large-row GF NFET + static-MTJ read-current experiment.
# 256 rows x 4 columns = 1024 actual GF NFET/MTJ branch pairs per scenario.
# Same active WL *mask*, independent ideal gate drivers. ASSUMED wire R, NOT PEX.
set -euo pipefail
umask 077
cd "$HOME/MRAM_Path_Finding"
ROOT="$HOME/mram_private/E30_1T1"
mkdir -p "$ROOT"
LOG="$ROOT/E30_256x4_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
echo "E30_LOG=$LOG"
{
  echo "========== CURRENT COMMIT =========="
  git rev-parse HEAD
  echo "========== COMPILE + 128/256-ROW LOGICAL CHECK =========="
  python3 -m py_compile experiments/e30_large_1t1_gf_cim.py
  python3 -u experiments/e30_large_1t1_gf_cim.py selftest
  echo "========== GF SPECTRE 256 ROW x 4 COL; 24 ACTIVE ROWS =========="
  echo "INTERCONNECT NOTE: --segment-ohms and --return-ohms are ILLUSTRATIVE hypotheses; NOT GF PEX"
  python3 -u experiments/e30_large_1t1_gf_cim.py run \
    --rows 256 \
    --columns 4 \
    --active 24 \
    --max-scenarios 18 \
    --chunk-scenarios 2 \
    --segment-ohms 0.25 \
    --return-ohms 0.25 \
    --timeout-sec 480 \
    --private "$ROOT"
  echo "========== E30 ACTUAL RESULT LOCATIONS =========="
  find "$ROOT" -maxdepth 2 -type f -name E30_RESULTS.json -print
  echo "E30_FINISHED_256x4_NOT_256x256_NO_PEX"
} 2>&1 | tee "$LOG"
