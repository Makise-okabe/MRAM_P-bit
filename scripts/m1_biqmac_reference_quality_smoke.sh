#!/usr/bin/env bash
# Stage M1: bounded reference-only solver-quality check on CALIBRATION graphs.
# Does NOT rerun six-bit pilot, sweep new formats, or simulate MTJ.
set -euo pipefail
cd "$(dirname "$0")/.."
for file in \
  data/biqmac/raw/rudy/w01_100.0 \
  data/biqmac/raw/rudy/pw01_100.0 \
  data/biqmac/raw/ising/t2g10_5555 \
  data/biqmac/raw/ising/ising2.5-100_5555; do
  test -s "$file" || { echo "MISSING audited graph: $file" >&2; exit 2; }
done
python -m unittest discover -s tests -p 'test_m1_biqmac_reference_quality_gate.py' -v
OUT="results/m1_fp64_reference_quality_$(date -u +%Y%m%dT%H%M%SZ)_$$"
python -m experiments.m1_biqmac_reference_quality_gate \
  --graph data/biqmac/raw/rudy/w01_100.0 \
  --graph data/biqmac/raw/rudy/pw01_100.0 \
  --graph data/biqmac/raw/ising/t2g10_5555 \
  --graph data/biqmac/raw/ising/ising2.5-100_5555 \
  --references docs/BIQMAC_OFFICIAL_OPTIMA_2007.json \
  --budgets 5000 20000 50000 \
  --schedules fixed linear \
  --seeds 6 \
  --seed 20261107 \
  --out "$OUT"
echo "====== FROZEN FP64 OPERATING-POINT PROBE ======"
echo "Output: $OUT"
head -5 "$OUT/reference_summary.csv"
echo "Do not pick a solver setting from held-out or quantized-format results."
