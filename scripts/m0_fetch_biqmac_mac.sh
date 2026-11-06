#!/usr/bin/env bash
# First M0 import: 8 specified calibration graphs from the official Mac/Rudy directory.
# Raw files & E0 JSON remain local and ignored by git. No solver is run.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="data/biqmac/raw/rudy"
mkdir -p "$OUT"
for name in w01_100.0 pw01_100.0 w05_100.0 pw05_100.0 \
            w09_100.0 pw09_100.0 pm1s_100.0 pm1d_100.0; do
    echo "========== Official Mac/Rudy graph: $name =========="
    if [ ! -e "$OUT/$name" ]; then
        curl -fLsS --retry 3 \
          "https://biqmac.aau.at/library/mac/rudy/$name" \
          -o "$OUT/$name"
    fi
    test -s "$OUT/$name" || { echo "Empty graph: $name" >&2; exit 1; }
    if [ -e "$OUT/$name.E0.json" ]; then
        echo "Previous E0 report exists; preserve it and recheck on stdout."
        python -m experiments.biqmac_maxcut --file "$OUT/$name" \
          | grep -E '"status"|"sha256"|"n"|"raw_edge_count"|"effective_nonzero_edges"'
    else
        python -m experiments.biqmac_maxcut --file "$OUT/$name" \
          --output "$OUT/$name.E0.json"
    fi
done
echo "========== ORIGINAL FILE HASHES =========="
sha256sum "$OUT"/{w01,pw01,w05,pw05,w09,pw09,pm1s,pm1d}_100.0
echo "M0 E0 SOURCE-IDENTITY AND MATH AUDIT COMPLETE; NO OPTIMIZATION RUN."
