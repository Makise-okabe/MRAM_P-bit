#!/usr/bin/env bash
# M0/E0: first wide-dynamic-range pilot source audit, original Mac/ising.
# Calibration examples only (seed 5555), not held-out or solver quality.
# No overwrites of previously downloaded original files or audit JSON.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=data/biqmac/raw/ising
mkdir -p "$OUT"
for name in t2g10_5555 ising2.5-100_5555; do
    src="https://biqmac.aau.at/library/mac/ising/$name"
    file="$OUT/$name"
    echo "========== OFFICIAL WIDE-RANGE GRAPH: $name =========="
    if [ ! -e "$file" ]; then
        curl --fail --location --silent --show-error --retry 3 "$src" -o "$file"
    fi
    test -s "$file" || { echo "FAIL: missing or zero-byte $file" >&2; exit 1; }
    export M0_CHECK_FILE="$file"
    python - <<'PY'
import os
from decimal import Decimal
from experiments.biqmac_maxcut import load_rudy
p = os.environ["M0_CHECK_FILE"]
g = load_rudy(p)
stem = p.split("/")[-1]
expected = {"t2g10_5555": (100,200),
            "ising2.5-100_5555": (100,4950)}
assert (g.n,g.raw_edge_count) == expected[stem], (stem,g.n,g.raw_edge_count)
abs_weights = [abs(w) for _,_,w in g.edges]
if stem == "t2g10_5555":
    assert min(abs_weights)==Decimal(460), min(abs_weights)
    assert max(abs_weights)==Decimal(294541), max(abs_weights)
else:
    assert any(abs(w)==1 for _,_,w in g.edges)
    assert any(w==Decimal(-101237) for _,_,w in g.edges)
print("OFFICIAL GRAPH M0 STRUCTURE CHECK PASS:",stem,
      "n=",g.n,"m=",g.raw_edge_count,
      "sha256=",g.sha256)
PY
done
REPORT="$OUT/weight_audit_$(date -u +%Y%m%dT%H%M%SZ)_$$.json"
python -m experiments.biqmac_weight_audit \
 --file "$OUT/t2g10_5555" \
 --file "$OUT/ising2.5-100_5555" \
 --output "$REPORT"
echo "========== SOURCE FILE SHA256 =========="
sha256sum "$OUT/t2g10_5555" "$OUT/ising2.5-100_5555"
echo "M0 WIDE-RANGE ORIGINAL-SOURCE E0 AUDIT FINISHED; NO SOLVER RUN."
