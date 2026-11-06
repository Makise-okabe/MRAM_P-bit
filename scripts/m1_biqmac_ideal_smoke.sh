#!/usr/bin/env bash
# First E1 solver smoke pilot on *already verified* official Biq Mac graphs.
# Exactly four source graphs, same 100 vertices, paired seeds. No MTJ model.
# Uses 6-bit formats only and shared-beta ideal Gibbs; do not call final result.
set -euo pipefail
cd "$(dirname "$0")/.."
for file in data/biqmac/raw/rudy/w01_100.0 \
            data/biqmac/raw/rudy/pw01_100.0 \
            data/biqmac/raw/ising/t2g10_5555 \
            data/biqmac/raw/ising/ising2.5-100_5555; do
    test -s "$file" || { echo "MISSING verified source: $file" >&2; exit 1; }
done
OUT="results/m1_maxcut_ideal_$(date -u +%Y%m%dT%H%M%SZ)_$$"
python -m experiments.m1_biqmac_ideal_pilot \
   --graph data/biqmac/raw/rudy/w01_100.0 \
   --graph data/biqmac/raw/rudy/pw01_100.0 \
   --graph data/biqmac/raw/ising/t2g10_5555 \
   --graph data/biqmac/raw/ising/ising2.5-100_5555 \
   --formats fp6_fn,int6,bfp6 \
   --scale-policies fullscale,mse \
   --updates 5000 \
   --seeds 3 \
   --seed 20261107 \
   --output "$OUT"
echo "========== PROVENANCE =========="
cat "$OUT/e1_manifest.json"
echo "========== CSV HEADERS =========="
head -2 "$OUT/representation_audit.csv"
head -2 "$OUT/paired_returns.csv"
echo "========== OUTPUT =========="
echo "$OUT"
