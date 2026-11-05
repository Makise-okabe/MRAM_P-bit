#!/usr/bin/env bash
# One-shot E27B/C batch. Auto-select E19 ORIGINAL single-cell template; NEVER reuse a generated multi-instance input.scs.
# Physical 1T1MTJ layout PEX does not exist yet. No fake four-column coupling.
set -euo pipefail
umask 077
cd "$HOME/MRAM_Path_Finding"
PRIVATE="$HOME/mram_private/E27_1T1"
mkdir -p "$PRIVATE"
LOG="$PRIVATE/E27BC_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
echo "E27BC_LOG=$LOG"
{
  echo "========== GIT SHA / LOCAL STATE =========="
  git rev-parse HEAD
  git status --short
  echo "========== COMPILE + TEST =========="
  python3 -m py_compile experiments/e27a_1t1_cim_preflight.py experiments/e27b_1t1_reference_gf_spectre.py experiments/e27c_1t1_physical_handoff_audit.py
  python3 experiments/e27a_1t1_cim_preflight.py --selftest
  python3 experiments/e27b_1t1_reference_gf_spectre.py selftest
  python3 experiments/e27c_1t1_physical_handoff_audit.py --selftest
  echo "========== E27C EXISTING MODEL + DECK METADATA =========="
  python3 -u experiments/e27c_1t1_physical_handoff_audit.py
  echo "========== E27B 16 ACTUAL GF NFET READS; 4 INDEPENDENT COLUMN CIRCUITS =========="
  if [ ! -f experiments/e19_gf_nfet_mtj_nonideal_count_gate_v2.py ]; then
    echo "E27B_BLOCKED: local verified E19 v2 generator missing; NO SPECTRE"
  elif ! command -v spectre >/dev/null 2>&1; then
    echo "E27B_BLOCKED: Spectre not on PATH; NO SPECTRE"
  else
    echo "========== E27B VERIFIED TEMPLATE PREFLIGHT (NO SPECTRE) =========="
    python3 -u experiments/e27b_1t1_reference_gf_spectre.py preflight \
      --vread 0.05 --vwl 0.8
    echo "========== E27B LIMITED GF SPECTRE DC =========="
    python3 -u experiments/e27b_1t1_reference_gf_spectre.py run \
      --vread 0.05 --vwl 0.8 --timeout-sec 240
  fi
  echo "========== E27B/C COMPLETE =========="
  echo "E27B_REAL_GF_NFET_ONLY_IF_RESULT_FILE_PRINTED_NOT_1T1_LAYOUT_PEX"
  echo "E27C_NO_PHYSICAL_JOINT_CORRELATION_RESULT"
} 2>&1 | tee "$LOG"
