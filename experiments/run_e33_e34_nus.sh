#!/usr/bin/env bash
# One-call E33 + E34: two independent OFFLINE experiments on existing NUS
# E30/E31 actual GF-transistor current vectors with ASSUMED BL/SL R.
# No Spectre reruns, proprietary foundry model export or false PEX claims.
set -euo pipefail
umask 077
cd "$HOME/MRAM_Path_Finding"
E30="$HOME/mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30_RESULTS.json"
E31="$HOME/mram_private/E31_1T1/E31_256x4_20261105T033721Z_2792/E31_RESULTS.json"
ROOT="$HOME/mram_private/E33_E34_OFFLINE"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)_$$"
WORK="$ROOT/$STAMP"
mkdir -p "$WORK/E33" "$WORK/E34"
LOG="$WORK/E33_E34.log"
echo "E33_E34_PRIVATE_ROOT=$WORK"
{
    echo "========== FROZEN SOURCE HASHES =========="
    git rev-parse HEAD
    test -s "$E30"
    test -s "$E31"
    sha256sum "$E30" "$E31"
    echo "========== PYTHON COMPILE + LOGICAL SELFTESTS =========="
    python3 -m py_compile \
        experiments/e30p_offline_strong_baselines.py \
        experiments/e33_adc_precision_frozen_gf.py \
        experiments/e34_four_column_gf_generalization.py
    python3 -u experiments/e33_adc_precision_frozen_gf.py selftest
    python3 -u experiments/e34_four_column_gf_generalization.py selftest
    echo "========== E33: ADC PRECISION vs SPATIAL BASELINES =========="
    python3 -u experiments/e33_adc_precision_frozen_gf.py run \
        --e30 "$E30" --e31 "$E31" --outdir "$WORK/E33"
    echo "========== E34: FOUR COLUMN GENERALIZATION =========="
    python3 -u experiments/e34_four_column_gf_generalization.py run \
        --e30 "$E30" --e31 "$E31" --outdir "$WORK/E34"
    echo "========== PROFESSOR READY SUMMARIES =========="
    cat "$WORK/E33/E33_FOR_PROF_FONG.md"
    cat "$WORK/E34/E34_FOR_PROF_FONG.md"
    echo "========== COMPLETE =========="
    echo "E33_JSON=$WORK/E33/E33_ADC_SWEEP.json"
    echo "E34_JSON=$WORK/E34/E34_RESULTS.json"
    echo "LOG=$LOG"
    echo "E33_E34_COMPLETE_NOT_PEX_NOT_ADC_CIRCUIT_NOT_DNN"
} 2>&1 | tee "$LOG"
