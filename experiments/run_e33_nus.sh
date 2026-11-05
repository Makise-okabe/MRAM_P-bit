#!/usr/bin/env bash
# E33 offline fixed-range ideal-ADC bit-depth / failure-boundary test.
# Actual GF Spectre currents; ASSUMED BL/SL R; NOT a physical ADC or 1T1 PEX.
set -euo pipefail
umask 077
cd "$HOME/MRAM_Path_Finding"
E30="$HOME/mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30_RESULTS.json"
E31="$HOME/mram_private/E31_1T1/E31_256x4_20261105T033721Z_2792/E31_RESULTS.json"
RUN="$HOME/mram_private/E33_1T1/E33_$(date -u +%Y%m%dT%H%M%SZ)_$$"
mkdir -p "$RUN"
LOG="$RUN/E33_run.log"
echo "E33_PRIVATE_RUN=$RUN"
{
    echo "========== GIT COMMIT AND INPUT CHECK =========="
    git rev-parse HEAD
    test -s "$E30"
    test -s "$E31"
    sha256sum "$E30" "$E31"
    echo "========== SYNTAX / SELFTEST =========="
    python3 -m py_compile experiments/e33_adc_precision_frozen_gf.py
    python3 experiments/e33_adc_precision_frozen_gf.py selftest
    echo "========== E33 ADC PRECISION STUDY =========="
    python3 -u experiments/e33_adc_precision_frozen_gf.py run \
        --e30 "$E30" --e31 "$E31" --outdir "$RUN"
    echo "========== PROFESSOR BRIEF =========="
    cat "$RUN/E33_FOR_PROF_FONG.md"
    echo "E33_FINISHED_NO_NEW_SPECTRE_NO_PEX"
} 2>&1 | tee "$LOG"
