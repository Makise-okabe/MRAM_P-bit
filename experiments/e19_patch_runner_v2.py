#!/usr/bin/env python3
"""Create a corrected E19 v2 script from an EXACT verified original; Python 3.6."""
from __future__ import print_function
import hashlib
import subprocess
import sys
from pathlib import Path

EXPECTED = '1656e467139c2cd1ce9f1ceaf7673cb57cc3adbe78433f35022eb17793b2451b'
OUTPUT_SHA = 'b6bec40bc234fac406d191229146354a5fe47c6969fb6db6a672e607ddf83e54'
OLD = 'e19_gf_nfet_mtj_nonideal_count_gate.py'
NEW = 'e19_gf_nfet_mtj_nonideal_count_gate_v2.py'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def swap_once(data, previous, replacement):
    if data.count(previous) != 1:
        raise SystemExit('PATCH_ERROR: expected unique match missing: ' + previous[:65])
    return data.replace(previous, replacement, 1)

def main():
    directory = Path(__file__).resolve().parent
    src = directory / OLD
    dst = directory / NEW
    if not src.is_file():
        raise SystemExit('PATCH_ERROR: original E19 not found at ' + str(src))
    original_bytes = src.read_bytes()
    if digest(original_bytes) != EXPECTED:
        raise SystemExit('PATCH_ERROR: unknown original SHA256 ' + digest(original_bytes) +
                         '. Do NOT modify script manually; use verified patch.')
    if dst.exists():
        raise SystemExit('PATCH_ERROR: refuses overwrite ' + str(dst))
    s = original_bytes.decode('utf-8')
    s = swap_once(s,
        "    try: return path.read_text(errors='replace')",
        "    try: return Path(path).read_text(errors='replace')")
    s = swap_once(s,
        "    data=read_text(src)\n    lines=logical_lines(data)",
        "    src=Path(src)\n    data=read_text(src)\n    lines=logical_lines(data)")
    s = swap_once(s,
        "            try:return parse_template(p)['source']",
        "            try:\n                parse_template(p)\n                return p")
    s = swap_once(s,
        "        data=parse_template(fake)\n        assert len(data['includes'])==1",
        "        data=parse_template(fake)\n        assert choose_template(str(fake)) == fake.resolve()\n        assert isinstance(choose_template(str(fake)), Path)\n        assert len(data['includes'])==1")
    final = s.encode('utf-8')
    if digest(final) != OUTPUT_SHA:
        raise SystemExit('PATCH_ERROR: v2 hash mismatch; will not write')
    dst.write_bytes(final)
    print('E19_PATCH_V2_WRITTEN:', dst)
    print('E19_PATCH_V2_SHA256:', digest(final))
    print('E19_ORIGINAL_UNCHANGED:', src)
    print('E19_SELFTEST_BEFORE_NUS_SPECTRE:')
    rc = subprocess.call([sys.executable, str(dst), 'selftest'])
    if rc:
        raise SystemExit('PATCH_ERROR: v2 selftest failed rc=' + str(rc))
    print('E19_PATCH_COMPLETE: safe to run v2 run subcommand')

if __name__ == '__main__':
    main()
