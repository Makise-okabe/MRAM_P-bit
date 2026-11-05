#!/usr/bin/env bash
# E31: NUS 256x4 fresh GF read masks, frozen E30 calibration, OOD spatial tests.
# Requires E30 source private JSON (SHA pinned). No PDK exports.
# GF transistor model + static student MTJ; assumed .25ohm/BL segment and SL.
# Not extracted 1T1 PEX; no physical BER or NN reliability claims.
set -euo pipefail
umask 077
cd "$HOME/MRAM_Path_Finding"
OUT="$HOME/mram_private/E31_1T1"
SRC="$HOME/mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30_RESULTS.json"
mkdir -p "$OUT"
LOG="$OUT/E31_FROZEN_CAL_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
echo "E31_LOG=$LOG"
{
  echo "========== E31 SOURCE + PYTHON GATE =========="
  git rev-parse HEAD
  test -s "$SRC"
  python3 -m py_compile \
    experiments/e30_large_1t1_gf_cim.py \
    experiments/e30p_offline_strong_baselines.py \
    experiments/e31_frozen_cal_unseen_masks.py
  python3 -u experiments/e31_frozen_cal_unseen_masks.py selftest

  echo "========== E31 36 NEW DEV MASKS x 256x4 GF CIRCUITS =========="
  echo "Original nine E30 CAL points stay frozen; no new CAL or retuning."
  echo "DEV: three known spatial families plus three OOD families."
  echo "Wire R values are ASSUMED NOT PEX (0.25ohm/BL segment, 0.25ohm shared SL)."
  python3 -u experiments/e31_frozen_cal_unseen_masks.py run \
    --source "$SRC" \
    --repeats 2 \
    --seed 20261106 \
    --chunk-scenarios 2 \
    --timeout-sec 480 \
    --private "$OUT"

  echo "========== COMPLETED E31 JSON =========="
  find "$OUT" -maxdepth 2 -type f -name E31_RESULTS.json -print
  echo "E31_BATCH_FINISHED_NOT_1T1_PEX"
} 2>&1 | tee "$LOG"
