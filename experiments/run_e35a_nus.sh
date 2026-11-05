#!/usr/bin/env bash
# E35A: strict read-only frozen E01 W4A8 activity-data schema/histogram audit.
# NO Spectre, NO physical 1T1 PEX. The E01 packet is not uploaded anywhere.
set -euo pipefail
umask 077
cd "$HOME/MRAM_Path_Finding"
PACKET="$HOME/MRAM_Path_Finding/experiments/runs/E01_MNIST_20261104T085558Z_038af9/review_packet.zip"
DIR="$HOME/mram_private/E35_E01_activity/E35A_$(date -u +%Y%m%dT%H%M%SZ)_$$"
mkdir -p "$DIR"
LOG="$DIR/E35A_run.log"
{
    echo "========== REPOSITORY COMMIT =========="
    git rev-parse HEAD
    echo "========== VERIFY E01 PACKET =========="
    test -s "$PACKET"
    sha256sum "$PACKET"
    echo "========== PYTHON SELFTEST =========="
    python3 -m py_compile experiments/e35a_frozen_e01_activity_audit.py
    python3 -u experiments/e35a_frozen_e01_activity_audit.py selftest
    echo "========== PRIVATE E01 HISTOGRAM DISCOVERY =========="
    python3 -u experiments/e35a_frozen_e01_activity_audit.py audit \
      --packet "$PACKET" \
      --out "$DIR/E35A_schema_audit.json"
    echo "========== PRIVATE RESULT =========="
    echo "$DIR/E35A_schema_audit.json"
    echo "E35A_COMPLETE_SOFTWARE_ACTIVITY_ONLY_NOT_GF_OR_PEX"
} 2>&1 | tee "$LOG"
