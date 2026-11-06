#!/usr/bin/env bash
# M2: one controlled mapped-area comparison of FP4/FP6, INT4/INT6, BFP6.
# Pre-placement cell area ONLY; no MRAM, DAC, p-bit, output retention, STA.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${M2_LIBERTY:?Set M2_LIBERTY to a standard-cell Liberty file}"
: "${M2_OUTPUT:?Set M2_OUTPUT to a fresh output directory}"
M2_N="${M2_N:-128}"
case "$M2_N" in 16|64|128) ;; *) echo "M2_N must be 16, 64 or 128" >&2; exit 2;; esac
command -v yosys >/dev/null || { echo "yosys unavailable" >&2; exit 2; }
test -f "$M2_LIBERTY" || { echo "Liberty not found: $M2_LIBERTY" >&2; exit 2; }
case "$M2_OUTPUT" in /*) ;; *) M2_OUTPUT="$PWD/$M2_OUTPUT";; esac
test ! -e "$M2_OUTPUT" || { echo "Output exists: $M2_OUTPUT" >&2; exit 2; }
mkdir -p "$M2_OUTPUT"
printf '%s\n' \
 "Library=$M2_LIBERTY" \
 "N_SPINS=$M2_N" \
 "Library_SHA256=$(sha256sum "$M2_LIBERTY" | awk '{print $1}')" \
 "RTL_SHA256=$(sha256sum rtl/pbit_local_field_row.sv | awk '{print $1}')" \
 "Yosys=$(yosys -V)" \
 "Scope=pre-placement cell area of serial local-field row, excludes MRAM/DAC/p-bit/controller/timing" \
 > "$M2_OUTPUT/run_manifest.txt"
for MODE in 0 1 2; do
  echo "========== Mapping MODE=$MODE N=$M2_N =========="
  LOG="$M2_OUTPUT/mode${MODE}_yosys.log"
  NET="$M2_OUTPUT/mode${MODE}_mapped.v"
  yosys -Q -T -l "$LOG" -p "read_verilog -sv rtl/pbit_local_field_row.sv; \
    chparam -set N_SPINS $M2_N -set MODE $MODE pbit_local_field_row; \
    hierarchy -check -top pbit_local_field_row; \
    synth -top pbit_local_field_row; \
    dfflibmap -liberty $M2_LIBERTY; \
    abc -liberty $M2_LIBERTY; \
    clean; \
    stat -liberty $M2_LIBERTY; \
    write_verilog -noattr $NET" \
    > "$M2_OUTPUT/mode${MODE}_stdout.txt" 2>&1 || {
      tail -70 "$M2_OUTPUT/mode${MODE}_stdout.txt" >&2
      echo "FAIL MODE=$MODE; see $LOG" >&2
      exit 1
    }
  echo "========== MODE=$MODE area lines =========="
  grep -Ei 'Chip area|total cell area|Number of cells' "$LOG" | tail -12 || true
done
echo "========== M2 TECHNOLOGY-MAPPED AREA COMPLETE =========="
echo "$M2_OUTPUT"
