#!/usr/bin/env bash
# M4C exploratory Nangate45 Genus mapping. No sudo, iverilog or yosys.
# Run: bash scripts/m4c_run_genus_nus.sh
# Override library with: export FYP_NANGATE_LIB=/path/to/your/liberty.lib
set -euo pipefail
cd "$(dirname "$0")/.."
REPO=$(pwd -P)
LIB="$HOME/mram_open_libraries/nangate45/NangateOpenCellLibrary_typical.lib"
if [ -n "$(printenv FYP_NANGATE_LIB || true)" ]; then
    LIB="$FYP_NANGATE_LIB"
fi
GENUS=$(command -v genus || true)
if [ -z "$GENUS" ]; then
    echo "M4C ERROR: Genus not on PATH; load NUS cadence/genus module first" >&2
    exit 2
fi
if [ ! -r "$LIB" ]; then
    echo "M4C ERROR: Nangate45 Liberty not readable: $LIB" >&2
    exit 2
fi
LIB=$(realpath "$LIB")
RTL_DIR="$REPO/rtl"
SCRIPT="$REPO/scripts/m4c_genus_nangate45.tcl"
test -r "$SCRIPT"
test -r "$REPO/rtl/m3_local_field_row.v"
test -r "$REPO/rtl/m4_common_logit_row.v"
mkdir -p results
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
SHA=$(git rev-parse --short HEAD)
OUT="$REPO/results/m4c_genus_$STAMP"_"$SHA"
if [ -e "$OUT" ]; then
    echo "M4C ERROR: refusing overwrite $OUT" >&2
    exit 2
fi
mkdir -p "$OUT"
git rev-parse HEAD > "$OUT/git_sha.txt"
sha256sum "$LIB" > "$OUT/nangate45_lib_sha256.txt"
echo "M4C: library=$LIB"
echo "M4C: Genus=$GENUS"
echo "M4C: output=$OUT"
echo "M4C: illustrative 10ns clock for all three tops"

for family in fp6 int6 bfp6; do
    FYP_TOP="m4_$family""_logit"
    FYP_LIB="$LIB"
    FYP_RTL_DIR="$RTL_DIR"
    FYP_OUT="$OUT/$family"
    export FYP_TOP FYP_LIB FYP_RTL_DIR FYP_OUT
    mkdir -p "$FYP_OUT/work"
    printf '\n===== START %s =====\n' "$FYP_TOP"
    if ! (cd "$FYP_OUT/work" && "$GENUS" -f "$SCRIPT" > "$FYP_OUT/genus.log" 2>&1); then
        echo "M4C ERROR: Genus non-zero for $family; inspect $FYP_OUT/genus.log" >&2
        exit 3
    fi
    if ! grep -q "M4C_GENUS_MAPPED_PASS_TOP=$FYP_TOP" "$FYP_OUT/genus.log"; then
        echo "M4C ERROR: no Genus mapped-pass marker for $family" >&2
        exit 3
    fi
    if [ ! -s "$FYP_OUT/area.rpt" ]; then
        echo "M4C ERROR: missing mapped-area report for $family" >&2
        exit 3
    fi
    echo "M4C PASS: $FYP_TOP"
done
printf '\n========== THREE MAPPED AREA REPORTS ==========\n'
for family in fp6 int6 bfp6; do
    echo "===== $family ====="
    cat "$OUT/$family/area.rpt"
done
echo "M4C GENUS THREE-FORMAT RUN COMPLETE"
echo "RESULT DIRECTORY: $OUT"
echo "NOT measured: RAM macro, beta/gain generator, p-bit, GF22FDX, placed area, power and STA."
