#!/usr/bin/env bash
# Three-path screening launcher. Hardware path is a mask/architecture gate only.
# F3 uses frozen real network traces, F7 uses exact digital field baseline.
# No historical single-column read currents are loaded or fitted.
set -euo pipefail
umask 077
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export ATEN_CPU_CAPABILITY=default

PRIVATE="$HOME/mram_private/E02_256x256"
MANIFEST="$PRIVATE/config/E02_256x256_connectivity_PROPOSAL.csv"
if [[ ! -f "$MANIFEST" ]]; then
    echo "Missing fresh E02 proposal manifest: $MANIFEST" >&2
    exit 2
fi
PY="${MRAM_RUN_PYTHON:-$HOME/venvs/mram-stage4a/bin/python}"
[[ -x "$PY" ]] || PY="$(command -v python3)"
"$PY" -c 'import numpy; print("NumPy",numpy.__version__)'
python3 -m py_compile experiments/e02_three_path_masks.py experiments/e09_digital_competitor_screen.py

RUN="$(mktemp -d "$PRIVATE/logs/threepath_$(date -u +%Y%m%d)_XXXXXXXX")"
echo "NEW SCREEN RUN: $RUN"
echo "Evidence categories: E02 proposed test vectors; F3 real workload only; F7 exact digital only."
git rev-parse HEAD > "$RUN/git_revision.txt"
printf '%s\n' "$RUN" > "$PRIVATE/logs/last_threepath_run.txt"

# Longest task starts first; leaving it running does not imply completion.
MRAM_RUN_PYTHON="$PY" bash scripts/run_first_experiment.sh > "$RUN/F3_workload.log" 2>&1 &
F3_PID=$!
printf '%s\n' "$F3_PID" > "$RUN/F3.pid"
echo "F3 E01 frozen-network workload started (PID $F3_PID); results NOT yet confirmed."

if python3 experiments/e02_three_path_masks.py \
    --manifest "$MANIFEST" --out "$RUN/E02_matched_masks.json" \
    > "$RUN/E02_mask_gate.log" 2>&1; then
    echo "H1 structural/mask gate: completed (not Spectre)"
else
    echo "H1 structural/mask gate: FAILED; inspect $RUN/E02_mask_gate.log"
fi
tail -n 5 "$RUN/E02_mask_gate.log"

if "$PY" -m experiments.e09_digital_competitor_screen \
    --out "$RUN/E09_exact_digital.json" --restarts 20 --sweeps 12 \
    > "$RUN/E09_exact_digital.log" 2>&1; then
    echo "F7 exact-digital competitor: completed (not MRAM hardware)"
else
    echo "F7 exact-digital competitor: FAILED; inspect $RUN/E09_exact_digital.log"
fi
tail -n 35 "$RUN/E09_exact_digital.log"

if kill -0 "$F3_PID" 2>/dev/null; then
    echo "F3 frozen-network workload still running; keep Singularity shell open."
else
    set +e
    wait "$F3_PID"
    RC=$?
    set -e
    echo "F3 process exited with status $RC; review log/packet."
fi
tail -n 18 "$RUN/F3_workload.log"
echo "RUN_DIR=$RUN"
echo "Review all logs. Do NOT label any H1/F3/F7 result as new target Spectre data."
