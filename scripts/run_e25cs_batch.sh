#!/usr/bin/env bash
# NUS software batch only. No Spectre, training, package installation or uploads.
set -euo pipefail

E25_SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
E25_PROGRAM="$E25_SOURCE_ROOT/experiments/e25_incremental_adc_mapping.py"
if [[ -n "${E25_PYTHON:-}" ]]; then
  E25_PY="$E25_PYTHON"
elif [[ -x "$HOME/venvs/mram-stage4a/bin/python" ]]; then
  E25_PY="$HOME/venvs/mram-stage4a/bin/python"
else
  E25_PY="$(command -v python3)"
fi
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export ATEN_CPU_CAPABILITY=default

E25_RUN_ROOT="$HOME/mram_private/E02_256x256/E25CS/E25CS_$(date -u +%Y%m%dT%H%M%S)_$$"
mkdir -p "$E25_RUN_ROOT"
trap 'printf "E25_OUTPUT_DIRECTORY=%s\n" "$E25_RUN_ROOT"' EXIT

"$E25_PY" -c 'import sys,numpy; print("PYTHON",sys.version); print("NUMPY",numpy.__version__)' \
  | tee "$E25_RUN_ROOT/runtime.txt"

if [[ -z "${E25_PACKET:-}" ]]; then
  E25_PACKET="$("$E25_PY" - <<'PY'
import hashlib, os
from pathlib import Path
root = Path.home()/'mram_private'
expected = '400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a'
direct = [root/'E02_256x256/E22_E23/review_packet.zip']
found = None
for p in direct:
    if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == expected:
        found = p
        break
if found is None and root.is_dir():
    for folder, dirs, names in os.walk(str(root)):
        relative = Path(folder).relative_to(root)
        dirs[:] = sorted(d for d in dirs if d not in
                         {'cases','simulations','psf','netlists','.git','__pycache__'})
        if len(relative.parts) >= 8:
            dirs[:] = []
        if 'review_packet.zip' in names:
            p = Path(folder)/'review_packet.zip'
            if p.stat().st_size < 10000000 and hashlib.sha256(p.read_bytes()).hexdigest() == expected:
                found = p
                break
if found is None:
    raise SystemExit('Frozen packet not found. Set E25_PACKET to your existing review_packet.zip path.')
print(str(found))
PY
)"
fi
export E25_PACKET

"$E25_PY" "$E25_PROGRAM" --selftest | tee "$E25_RUN_ROOT/selftest.txt"

E25_GF_SOURCE="$HOME/mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162140_178/e22_results.json"
if [[ -f "$E25_GF_SOURCE" && -f "$E25_SOURCE_ROOT/experiments/e23a_residual_spatial_diagnostic.py" ]]; then
  printf 'E25_STAGE=existing_GF_current_diagnostics_no_new_Spectre\n'
  "$E25_PY" "$E25_SOURCE_ROOT/experiments/e22c_spatial_feature_ablation.py" --selftest \
    | tee "$E25_RUN_ROOT/e22c_selftest.txt"
  "$E25_PY" -u "$E25_SOURCE_ROOT/experiments/e22c_spatial_feature_ablation.py" \
    "$E25_GF_SOURCE" --out "$E25_RUN_ROOT/e22c_spatial_ablation.json" \
    | tee "$E25_RUN_ROOT/e22c_spatial_ablation.log"
  "$E25_PY" "$E25_SOURCE_ROOT/experiments/e23a_residual_spatial_diagnostic.py" --selftest \
    | tee "$E25_RUN_ROOT/e23a_selftest.txt"
  "$E25_PY" -u "$E25_SOURCE_ROOT/experiments/e23a_residual_spatial_diagnostic.py" \
    "$E25_GF_SOURCE" --out "$E25_RUN_ROOT/e23a_residual_diagnostic.json" \
    | tee "$E25_RUN_ROOT/e23a_residual_diagnostic.log"
else
  printf 'EXISTING_GF_DIAGNOSTICS_SKIPPED: saved E22 data or scripts unavailable\n'
fi

printf 'E25_STAGE=synthetic_backend_benchmark\n'
"$E25_PY" -u "$E25_PROGRAM" --benchmark --events 2048 --proposals 96 \
  --out "$E25_RUN_ROOT/backend_benchmark.json" \
  | tee "$E25_RUN_ROOT/backend_benchmark.log"

printf 'E25_STAGE=paired_small_mapping_replication\n'
"$E25_PY" -u "$E25_PROGRAM" \
  --packet "$E25_PACKET" --out "$E25_RUN_ROOT/pilot" \
  --cal-parents 128 --dev-parents 256 \
  --row-starts 0 --outputs 8 --search-outputs 8 \
  --groupings zero_rate_sorted,car_alpha_0 \
  --proposals 96 --graph-passes 7 --seed 250511 \
  --train-r 5 --eval-rs 0,1,5,10 \
  --backends full,sparse,segment --task-auto \
  | tee "$E25_RUN_ROOT/pilot_console.log"

printf 'E25_STAGE=all_FC1_rows_and_128_outputs\n'
# Full output search uses the strong sparse-recursion backend: segment-tree
# superiority at B=32 is not assumed. Every arm sees the same read groups.
"$E25_PY" -u "$E25_PROGRAM" \
  --packet "$E25_PACKET" --out "$E25_RUN_ROOT/full_fc1" \
  --cal-parents 128 --dev-parents 256 \
  --row-starts 0,256,512,768 --outputs 128 --search-outputs 128 \
  --groupings zero_rate_sorted,car_alpha_0 \
  --proposals 96 --graph-passes 7 --seed 250511 \
  --train-r 5 --eval-rs 0,1,5,10 \
  --backends sparse --task-auto \
  | tee "$E25_RUN_ROOT/full_fc1_console.log"

"$E25_PY" - "$E25_RUN_ROOT" <<'PY' | tee "$E25_RUN_ROOT/summary.txt"
import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1])
for label in ('pilot','full_fc1'):
    p=root/label/'results.json'
    result=json.loads(p.read_text())
    print('RESULT',label,'SHA256',hashlib.sha256(p.read_bytes()).hexdigest())
    print('TASK_STATUS',result['task_resources']['status'])
    for v in result['aggregate']:
        if v['r_assumed']==5:
            print(v['grouping'],v['method'],'DEV_MSE',round(v['dev_arithmetic_mse'],3),
                  'READS',v['dev_reads'],'NETWORK',v.get('network','NOT_RUN'))
print('Return summary.txt and the two console logs. Raw packet/checkpoint/netlists stay private.')
PY
