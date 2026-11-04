#!/usr/bin/env python3
"""E02 256x256 new-target structural mask gate. NO electrical physics measured.

Checks every proposed cell connection, creates a single globally fixed MTJ state
assignment and matched same-count spatial read masks for future Spectre runs.
The row 0 endpoint is NOT presumed to be physically near the sense amplifier.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        p.error("Refusing to overwrite a previous run")
    required = ["instance","row","column","BL","SL0","SL1","WLA","WLB","PW"]
    seen = set()
    with a.manifest.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != required:
            p.error("Unexpected manifest fields: " + str(reader.fieldnames))
        for entry in reader:
            r,c = int(entry["row"]),int(entry["column"])
            if not (0 <= r < 256 and 0 <= c < 256) or (r,c) in seen:
                p.error("Duplicate/out-of-range position")
            seen.add((r,c))
            expected = {
                "instance":f"X_R{r:03d}_C{c:03d}",
                "BL":f"BL_{c:03d}",
                "SL0":f"SL_{r:03d}",
                "SL1":f"SL_{r+1:03d}",
                "WLA":f"WLA_{r:03d}",
                "WLB":f"WLB_{r:03d}",
                "PW":"PW"
            }
            for k,v in expected.items():
                if entry[k] != v:
                    p.error(f"Connectivity mismatch {r},{c} {k}")
    if len(seen) != 256*256:
        p.error("Incomplete 256x256 manifest")
    # Fixed manufacturing-state bitmap, no old P/AP measurements or random model.
    states = bytes(1 if (r+c)%2 == 0 else 0
                   for r in range(256) for c in range(256))
    patterns = {
        "Z0": [],
        "LOW4": list(range(4)),
        "HIGH4": list(range(252,256)),
        "SPREAD4": [0,85,170,255],
        "LOW16": list(range(16)),
        "HIGH16": list(range(240,256)),
        "SPREAD16": [32*i+j for i in range(8) for j in (0,1)],
        "LOW32": list(range(32)),
        "HIGH32": list(range(224,256)),
        "SPREAD32": [16*i+j for i in range(16) for j in (0,1)]
    }
    cases = {}
    for name, rows in patterns.items():
        assert len(rows) == len(set(rows)) and all(0 <= x < 256 for x in rows)
        selected_p = sum(states[r*256] for r in rows) # sense_column=0
        selected_ap = len(rows)-selected_p
        if rows and selected_p != selected_ap:
            raise AssertionError(f"Unmatched P/AP: {name}")
        cases[name] = {
            "sense_column":0,"row_indices_zero_based":rows,
            "selected_P":selected_p,"selected_AP":selected_ap,
            "selected_state_by_row":{str(r):"P" if states[r*256] else "AP" for r in rows},
            "row_mask_sha256":sha(bytes(1 if r in rows else 0 for r in range(256)))
        }
    report = {
        "experiment":"E02A_mask_design",
        "evidence_class":"UNSIMULATED_TOPOLOGY_AND_VECTORS_ONLY",
        "full_256x256_connectivity_proposed":True,
        "full_array_physical_extraction":False,
        "target_spectre_run":False,
        "read_safety_verified":False,
        "sense_column":0,
        "row0_near_or_far":"UNRESOLVED",
        "global_initial_state_rule":"P if (row+column)%2 == 0 else AP; same for all runs",
        "global_state_bitmap_sha256":sha(states),
        "manifest_sha256":sha(a.manifest.read_bytes()),
        "historical_read_measurements_used":False,
        "warning":"No ADC, BL/SL/WL parasitics, read voltages, or sensor can be inferred from this file.",
        "cases":cases
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    print("PASS: all 65,536 proposed cell connections checked")
    print("PASS: Z0, 4/16/32 active-row matched masks, frozen P/AP assignments")
    print("NOT PASSED: electrical topology, timing, PEX, readout, or physical novelty")
    print("WROTE",a.out)

if __name__ == "__main__":
    main()
