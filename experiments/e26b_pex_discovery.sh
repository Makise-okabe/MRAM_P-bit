#!/usr/bin/env bash
# E26B read-only audit of EXISTING NUS 4x4 2T1MTJ PEX and R1 four-BL deck.
# NO Spectre. NO foundry model/netlist contents printed. NO output files written.
set -euo pipefail

ROOT="$HOME/mram_fyp/cadence"
OVERLEAF="$HOME/MRAM_FYP_Overleaf"
PILOT="$ROOT/manual_cross5_runs/M047_READ_CIM_PILOT"

inspect() {
  label="$1"
  file="$2"
  if [ ! -f "$file" ]; then
    echo "E26B_MISSING $label $file"
    return
  fi
  echo "========== $label =========="
  echo "PATH: $file"
  echo "BYTES: $(wc -c < "$file")"
  echo "SHA256: $(sha256sum "$file" | awk '{print $1}')"
  echo "SUBCKT_HEADERS_COUNT: $(grep -Eic '^[[:space:]]*\.?subckt[[:space:]]' "$file" || true)"
  echo "BL_TOKEN_LINES: $(grep -Eic 'BL(\[|<|_|[0-9])' "$file" || true)"
  echo "WL_TOKEN_LINES: $(grep -Eic 'WL(\[|<|_|[0-9])' "$file" || true)"
  echo "SL_TOKEN_LINES: $(grep -Eic 'SL(\[|<|_|[0-9])' "$file" || true)"
  echo "R_ELEMENT_LINES_APPROX: $(grep -Eic '^[[:space:]]*R[^[:space:]]+[[:space:]]' "$file" || true)"
  echo "C_ELEMENT_LINES_APPROX: $(grep -Eic '^[[:space:]]*C[^[:space:]]+[[:space:]]' "$file" || true)"
}

echo "E26B_PREEXISTING_4x4_AUDIT_NOT_SPECTRE"
inspect XACT_4X4 "$ROOT/calibre/xact/M047_GF_4x4_TILE_TEST_PEX/M047_GF_4x4_TILE_TEST.pex.dspf"
inspect R1_4BL_DECK "$PILOT/R1_4BL_SIMULTANEOUS_READ/pex_R1_4BL_read.scs"
inspect R1_4X4_PEX "$PILOT/R1_4BL_SIMULTANEOUS_READ/M047_GF_4x4_TILE_TEST_initP.pex.dspf"
inspect R2_4X4_PEX "$PILOT/R2_MTJ_LOCAL_MC_PILOT/M047_GF_4x4_TILE_TEST_initP.pex.dspf"
inspect MC_P "$PILOT/MC1_CONTROLLED_READ_MARGIN_MC/M047_GF_4x4_MC1_initP.pex.dspf"
inspect MC_AP "$PILOT/MC1_CONTROLLED_READ_MARGIN_MC/M047_GF_4x4_MC1_initAP.pex.dspf"
inspect LVS_SOURCE "$ROOT/lvs_source/M047_GF_4x4_TILE_TEST/M047_GF_4x4_TILE_TEST_source.cdl"

echo "========== EXISTING R1/R2/MC RESULT FILENAMES =========="
for d in "$PILOT/R1_4BL_SIMULTANEOUS_READ" "$PILOT/R2_MTJ_LOCAL_MC_PILOT" "$PILOT/MC1_CONTROLLED_READ_MARGIN_MC"; do
  if [ ! -d "$d" ]; then
    continue
  fi
  echo "DIR: $d"
  find "$d" -maxdepth 2 -type f \
    \( -iname '*.csv' -o -iname '*.json' -o -iname '*.log' \
       -o -iname '*.out' -o -iname '*.md' -o -iname '*.raw' \
       -o -iname '*.npz' -o -iname '*.txt' \) \
    -printf '%P\n' | sort | head -35 || true
done

echo "========== CHECKPOINT PROVENANCE CANDIDATES =========="
for ckpt in \
  "$OVERLEAF/outputs/mnist_stage4a_v2/fp32_checkpoint.pt" \
  "$OVERLEAF/outputs/mnist_stage4a_v3_15ep/fp32_checkpoint.pt" \
  "$OVERLEAF/outputs/mnist_stage4a_v3_15ep/stage7b_W4A8_B6_FS31_pilot128train128dev_1epoch_v1.pt"
do
  if [ -f "$ckpt" ]; then
    echo "CKPT: $ckpt"
    echo "BYTES: $(wc -c < "$ckpt")"
    echo "SHA256: $(sha256sum "$ckpt" | awk '{print $1}')"
  fi
done
echo "E26B_COMPLETE_DISCOVERY_ONLY"
echo "NO actual joint error tensor, success or physical correlation inferred."
