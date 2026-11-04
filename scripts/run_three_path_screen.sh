#!/usr/bin/env bash
# Robust 3-path screening: H1 structural, F7 exact digital, F3 frozen workload.
# NO archived 8-cell current, ADC or physical error distribution is imported.
set -euo pipefail
umask 077
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export ATEN_CPU_CAPABILITY=default
PRIVATE="$HOME/mram_private/E02_256x256"
MANIFEST="$PRIVATE/config/E02_256x256_connectivity_PROPOSAL.csv"
if [[ ! -f "$MANIFEST" ]]; then
    echo "STOP: fresh 256x256 connectivity proposal missing: $MANIFEST" >&2
    exit 2
fi

mkdir -p "$PRIVATE/logs"
RUN="$(mktemp -d "$PRIVATE/logs/threepath_$(date -u +%Y%m%d)_XXXXXXXX")"
printf '%s\n' "$RUN" > "$PRIVATE/logs/last_threepath_run.txt"
git rev-parse HEAD > "$RUN/git_revision.txt"
echo "RUN_DIR=$RUN"
echo "No new target physical measurement is claimed by these screening scripts."
python3 -m py_compile experiments/e02_three_path_masks.py experiments/e09_digital_competitor_stdlib.py

echo "=== H1: 256x256 full connectivity/matched-mask structural gate ==="
if python3 experiments/e02_three_path_masks.py \
    --manifest "$MANIFEST" --out "$RUN/E02_matched_masks.json" \
    > "$RUN/E02_mask_gate.log" 2>&1; then
    echo "H1 PASS (STRUCTURAL ONLY, NOT SPECTRE)"
else
    echo "H1 FAIL: inspect $RUN/E02_mask_gate.log"
fi
tail -n 8 "$RUN/E02_mask_gate.log"

echo "=== F7: exact digital incremental Ising baseline, no numpy required ==="
if python3 experiments/e09_digital_competitor_stdlib.py \
    --out "$RUN/E09_exact_digital.json" --restarts 20 --sweeps 12 \
    > "$RUN/E09_exact_digital.log" 2>&1; then
    echo "F7 completed (EXACT DIGITAL SOFTWARE ONLY)"
else
    echo "F7 failed: inspect $RUN/E09_exact_digital.log"
fi
tail -n 32 "$RUN/E09_exact_digital.log"

echo "=== F3: discover Python with both numpy and torch ==="
PY=""
CANDIDATES=(
    "${MRAM_RUN_PYTHON:-}"
    "$HOME/venvs/mram-stage4a/bin/python"
    "$HOME"/venvs/*/bin/python
    "$HOME"/.conda/envs/*/bin/python
    "$HOME"/miniconda*/bin/python
    "$(command -v python3)"
    "$(command -v python || true)"
)
for candidate in "${CANDIDATES[@]}"; do
    if [[ -n "$candidate" && -x "$candidate" ]]; then
        if "$candidate" -c 'import numpy, torch' > /dev/null 2>&1; then
            PY="$candidate"
            echo "READY_PYTHON=$PY"
            break
        else
            echo "Missing numpy/torch in $candidate"
        fi
    fi
done
if [[ -n "$PY" ]]; then
    echo "F3: launching frozen-MNIST real-workload screen"
    if MRAM_RUN_PYTHON="$PY" bash scripts/run_first_experiment.sh \
       > "$RUN/F3_workload.log" 2>&1; then
       echo "F3 command finished successfully; inspect the run packet."
    else
       echo "F3 command failed; review exact issue in $RUN/F3_workload.log"
    fi
else
    echo "F3 BLOCKED: no available Python containing numpy AND torch." \
        | tee "$RUN/F3_workload.log"
    echo "Try the host's existing venv outside Singularity or a permitted Conda module."
fi
tail -n 28 "$RUN/F3_workload.log"

echo "=== EXPLICIT EVIDENCE STATUS ==="
if [[ -f "$RUN/E02_matched_masks.json" ]]; then
    echo "H1: proposal connectivity and matched mask ONLY"
else
    echo "H1: structural gate failed"
fi
if [[ -f "$RUN/E09_exact_digital.json" ]]; then
    echo "F7: exact digital algorithm competitor ONLY"
else
    echo "F7: comparator failed"
fi
echo "F3: review frozen-network log and output packet; never infer physical readout"
echo "Spectre electrical experiment remains outstanding for all 3 MRAM claims."
echo "RUN_DIR=$RUN"
