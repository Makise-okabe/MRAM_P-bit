#!/usr/bin/env bash
# E1: first predeclared 4/5/6/8-bit global-scale precision plot on Biq Mac.
# 3 official CAL 100-spin graphs x 13 configurations x 24 paired NEW seeds
# = 936 solver runs, EVERY run 50k linear annealing attempted updates.
# NO stochastic-MTJ physics, RTL/circuit cost or post-hoc scales.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "========== FROZEN E1 PRECISION CODEBOOK TESTS =========="
python -m unittest discover -s tests -p 'test_m1_precision_global.py' -v
echo "========== SOURCE GRAPH PREFLIGHT =========="
for graph in data/biqmac/raw/rudy/w01_100.0 \
             data/biqmac/raw/ising/t2g10_5555 \
             data/biqmac/raw/ising/ising2.5-100_5555; do
  test -s "$graph" || { echo "MISSING official graph: $graph" >&2; exit 2; }
done
test -s docs/BIQMAC_OFFICIAL_OPTIMA_2007.json
OUT="results/m1_precision_global_$(date -u +%Y%m%dT%H%M%SZ)_$$"
echo "========== 50K LINEAR x 24 NEW PAIRED SEEDS =========="
python -m experiments.m1_biqmac_precision_sweep --out "$OUT"
echo "========== THREE SEPARATE PLOT PANELS =========="
python scripts/m1_precision_gap_plots.py \
   --csv "$OUT/precision_summary.csv" \
   --out-dir "$OUT/plots"
echo "========== OUTPUT HASHES =========="
sha256sum "$OUT/manifest.json" "$OUT/precision_paired_runs.csv" "$OUT/precision_summary.csv"
echo "========== FINAL E1 OUTPUT =========="
echo "$OUT"
echo "E1 GLOBAL PRECISION SWEEP COMPLETE — IDEAL MATHEMATICAL p-BIT ONLY"
