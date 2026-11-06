#!/usr/bin/env bash
# One pre-placement mapped-area comparison of the INTEGRATED row+tracker.
# Same public/authorized library and Yosys logic as m2_yosys_mapped_area.sh.
# No MRAM macro, DAC, stochastic MTJ, scheduler, coefficient memory, STA.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${M2_LIBERTY:?Set M2_LIBERTY to the Liberty file}"
: "${M2_OUTPUT:?Set M2_OUTPUT to a fresh results folder}"
M2_N="${M2_N:-128}"
case "$M2_N" in 16|64|128) ;; *) echo "Invalid M2_N" >&2; exit 2;; esac
command -v yosys >/dev/null || { echo "yosys unavailable" >&2; exit 2; }
test -f "$M2_LIBERTY" || { echo "Missing Liberty: $M2_LIBERTY" >&2; exit 2; }
case "$M2_OUTPUT" in /*) ;; *) M2_OUTPUT="$PWD/$M2_OUTPUT";; esac
test ! -e "$M2_OUTPUT" || { echo "Output already exists: $M2_OUTPUT" >&2; exit 2; }
mkdir -p "$M2_OUTPUT"
printf '%s\n' \
 "Design=pbit_row_best_state_system" \
 "N_SPINS=$M2_N" \
 "LIBERTY=$M2_LIBERTY" \
 "LIBERTY_SHA256=$(sha256sum "$M2_LIBERTY" | awk '{print $1}')" \
 "YOSYS=$(yosys -V)" \
 "SCOPE=pre-placement cell area; external coefficient streamer, state scheduler, pbit, DAC, and memory excluded" \
 > "$M2_OUTPUT/run_manifest.txt"
for MODE in 0 1 2; do
    LOG="$M2_OUTPUT/mode${MODE}_yosys.log"
    NET="$M2_OUTPUT/mode${MODE}_mapped.v"
    echo "========== INTEGRATED MODE=$MODE N=$M2_N =========="
    yosys -Q -T -l "$LOG" -p "read_verilog -sv \
      rtl/pbit_local_field_row.sv \
      rtl/pbit_best_energy_tracker.sv \
      rtl/pbit_row_best_state_system.sv; \
      chparam -set N_SPINS $M2_N -set MODE $MODE pbit_row_best_state_system; \
      hierarchy -check -top pbit_row_best_state_system; \
      synth -flatten -top pbit_row_best_state_system; \
      dfflibmap -liberty $M2_LIBERTY; \
      abc -liberty $M2_LIBERTY; \
      clean; \
      stat -liberty $M2_LIBERTY; \
      write_verilog -noattr $NET" \
      > "$M2_OUTPUT/mode${MODE}_stdout.txt" 2>&1 || {
        tail -80 "$M2_OUTPUT/mode${MODE}_stdout.txt" >&2
        exit 1
      }
    grep -E 'Chip area for module|of which used for sequential' "$LOG" | tail -3
done
echo "========== M2 INTEGRATED MAPPED AREA COMPLETE =========="
echo "$M2_OUTPUT"
