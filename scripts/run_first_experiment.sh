#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export ATEN_CPU_CAPABILITY=default

# Prefer the already documented NUS environment; never install or retrain silently.
if [[ -n "${MRAM_RUN_PYTHON:-}" ]]; then
  experiment_python="$MRAM_RUN_PYTHON"
elif [[ -x "$HOME/venvs/mram-stage4a/bin/python" ]]; then
  experiment_python="$HOME/venvs/mram-stage4a/bin/python"
else
  experiment_python="$(command -v python3)"
fi

echo "Using Python: $experiment_python"
exec "$experiment_python" -u -m experiments.nus_first_run "$@"
