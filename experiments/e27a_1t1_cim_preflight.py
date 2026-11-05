#!/usr/bin/env python3
"""E27A 1T1MTJ architecture + 4x4 paired-pattern physical-gate preparation.

READ ONLY with respect to existing NUS files. Writes ONLY a private JSON+CSV plan
under ~/mram_private/E27_1T1/. Does not run Spectre, create a PEX or assert a
GF-qualified 1T1MTJ layout. Does not print PDK/proprietary source text.
Python >=3.7, standard library only.
"""
import argparse
import csv
import datetime as dt
import glob
import hashlib
import json
import os
import pathlib
import re

HOME = pathlib.Path.home()
ROOT = HOME / "mram_fyp" / "cadence" / "CIM1_SINGLE_CELL"
E24 = (HOME / "mram_private" / "E02_256x256" / "E24" /
       "E24_ACTIVITY_20261104T173351_53" / "e24_activity_results.json")
OUTPUT = HOME / "mram_private" / "E27_1T1"
STATE_ROWS = [
    ["P","AP","P","AP"],
    ["AP","P","AP","P"],
    ["P","AP","P","AP"],
    ["AP","P","AP","P"],
]
MASKS = {
    "Z0_NONE": [],
    "S0_ROW0": [0],
    "S1_ROW1": [1],
    "S2_ROW2": [2],
    "S3_ROW3": [3],
    "N2_ROWS01": [0, 1],
    "F2_ROWS23": [2, 3],
    "D2_ROWS03": [0, 3],
    "D2_ROWS12": [1, 2],
    "ALL4": [0, 1, 2, 3],
}
COMPARED = [("N2_ROWS01","F2_ROWS23"),
            ("N2_ROWS01","D2_ROWS03"),
            ("F2_ROWS23","D2_ROWS12")]

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024*1024), b""):
            h.update(b)
    return h.hexdigest()

def info(path):
    path = pathlib.Path(path)
    if not path.is_file():
        return {"present":False}
    return {"present":True,"bytes":path.stat().st_size,"sha256":sha256(path)}

def make_cases():
    cases=[]
    for name, rows in MASKS.items():
        cols=[]
        for c in range(4):
            states=[STATE_ROWS[r][c] for r in rows]
            cols.append({"col":c, "selected_P":states.count("P"),
                         "selected_AP":states.count("AP")})
        cases.append({"case":name,"rows":rows,"m":len(rows),
                      "columns":cols,"fixed_states":STATE_ROWS,
                      "read_bias_status":"UNVERIFIED_1T1",
                      "evidence":"PLANNED_NO_PEX"})
    return cases

def selftest():
    by={x["case"]:x for x in make_cases()}
    assert len(by)==10
    for a,b in COMPARED:
        assert by[a]["m"]==by[b]["m"]==2
        assert [(x["selected_P"], x["selected_AP"]) for x in by[a]["columns"]] == \
               [(x["selected_P"], x["selected_AP"]) for x in by[b]["columns"]]
    assert all(x["selected_P"]+x["selected_AP"]==case["m"]
               for case in by.values() for x in case["columns"])
    print("E27A_SELFTEST_PASS: 10 case masks; near/far matched P/AP in all four columns")
    print("E27A_SELFTEST_NOT_PHYSICAL: no Spectre, no 1T1 PEX, no correlation measurement")

def inventory(root):
    print("E27A_BASELINE_ROOT", str(root))
    mtj=root/"models"/"mtj_read_v0.va"
    print("E27A_STUDENT_STATIC_MTJ", json.dumps(info(mtj),sort_keys=True))
    print("E27A_FROZEN_E24_DATA", json.dumps(info(E24),sort_keys=True))
    targets=[]
    # Use bounded globs only: do not crawl the legacy 4x4 2T1 PEX or huge PSF trees.
    for pat in (
        "models/*.va",
        "*.scs",
        "netlists/*.scs",
        "simulations/MC_CURRENT_REAL_*/cases/R01/m8/a00000/*.scs",
        "simulations/MC_CURRENT_REAL_*/cases/R01/m8/a00000/*/*.scs",
        "simulations/MC_CURRENT_REAL_*/cases/R01/m8/a00000/*/*/*.scs",
        "simulations/E2*/**/netlist",
    ):
        found=glob.glob(str(root/pat),recursive=False)
        targets.extend(p for p in found if os.path.isfile(p))
    # A selected subset is sufficient to find existing reusable deck structure.
    targets=sorted(set(targets))[:25]
    print("E27A_CANDIDATE_1T1_EXISTING_FILES",len(targets))
    for p in targets:
        print("  CANDIDATE",os.path.relpath(p,str(root)),
              "BYTES",os.path.getsize(p),"SHA256",sha256(p))
    return {"mtj_module":info(mtj), "frozen_e24":info(E24),
            "candidate_existing_files":[os.path.relpath(p,str(root)) for p in targets]}

def inspect_user_deck(path):
    print("E27A_OPTIONAL_DECK_AUDIT")
    p=pathlib.Path(path)
    if not p.is_file():
        print("E27A_DECK_MISSING",p)
        return None
    if p.stat().st_size>10_000_000:
        print("E27A_DECK_TOO_LARGE_FOR_AUDIT")
        return None
    # Count tokens without exposing licensed netlist/model text.
    patterns={
        "model_hvtnfet":r"\bhvtnfet\b",
        "mtj_read_model":r"\bmtj_read_v0\b",
        "other_mtj_token":r"\bmtj\w*\b",
        "WL_words":r"\b(?:wl|wll|wlr)\w*\b",
        "BL_words":r"\bbl\w*\b",
        "SL_words":r"\bsl\w*\b",
        "resistance_tokens":r"\b(?:rseg|rwire|rbl)\w*\b",
        "spectre_analysis":r"\b(?:dc|tran)\b",
    }
    txt=p.read_text(encoding="utf-8",errors="replace")
    counts={k:len(re.findall(v,txt,re.I)) for k,v in patterns.items()}
    result={"file_sha256":sha256(p),"bytes":p.stat().st_size,
            "token_counts":counts, "verdict":"MANUAL_PIN_AND_BIAS_VERIFICATION_REQUIRED"}
    print("E27A_DECK_METADATA",json.dumps(result,sort_keys=True))
    print("E27A_DECK_WARNING: token counts do NOT prove 1-FET-per-MTJ connectivity")
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--selftest",action="store_true")
    parser.add_argument("--root",default=str(ROOT))
    parser.add_argument("--private-out",default=str(OUTPUT))
    parser.add_argument("--inspect-deck",default="")
    args=parser.parse_args()
    if args.selftest:
        selftest()
        return
    selftest()
    root=pathlib.Path(args.root).expanduser()
    if not root.is_dir():
        raise SystemExit("E27A_BLOCKED_BASELINE_ROOT_NOT_FOUND: "+str(root))
    snapshot=inventory(root)
    deck=inspect_user_deck(args.inspect_deck) if args.inspect_deck else None
    cases=make_cases()
    out=pathlib.Path(args.private_out).expanduser()
    out.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(out,0o700)
    manifest={
        "experiment":"E27A",
        "timestamp_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "status":"1T1_CIM_PHYSICAL_PEX_AND_BIAS_GATE_PENDING",
        "topology":"one authorized GF access NFET + one authorized static MTJ per cell",
        "old_2T1_PEX_valid_for_target":False,
        "cell_design_note":"1T1 series BL-MTJ-NFET-SL example; exact terminal order and GF model pins must be verified on NUS",
        "model_scope":"existing E24 nominal single-FET model with ASSUMED interconnect is comparison only",
        "cell_read_bench_verified":False,
        "4x4_drc_lvs_pex_verified":False,
        "parallel_wordline_read_verified":False,
        "mixed_states_persistence_verified":False,
        "real_1T1_BL_SL_WL_RC_extracted":False,
        "read_disturb_checked":False,
        "joint_multi_column_error_tensor_available":False,
        "next_gate":"verify genuine 1T1 cell and multi-row current with actual physical parasitics, then extract new 4x4 layout",
        "requirements":[
            "one NFET and one MTJ in series, no legacy 2T1 local-floating-SL shortcuts",
            "legal read VBL/VSL/VWL and positive/negative current sign explicitly checked",
            "chosen gate/source/drain/MTJ top/bottom terminal order verified",
            "mixed P/AP state assignment persists across read cases",
            "same 4 columns and shared WL/SL/periphery present in every comparison",
            "all unselected BL/WL/SL nodes have defined safe impedances/biases",
            "match IDEAL vs PEX with identical active devices, drivers and sensing",
            "retain currents, voltages, state and KCL; compare nominal before mismatch",
            "do not fit/read true MAC count at runtime"
        ],
        "baseline_inventory":snapshot,
        "inspected_deck":deck,
        "state_by_row_column":STATE_ROWS,
        "matched_pair_cases":COMPARED,
        "cases":cases,
    }
    jpath=out/"E27A_1T1_4x4_preflight_manifest.json"
    cpath=out/"E27A_1T1_4x4_matched_masks.csv"
    jpath.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with cpath.open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["case","active_rows","m","col0_P","col0_AP","col1_P","col1_AP",
                         "col2_P","col2_AP","col3_P","col3_AP","evidence"])
        for case in cases:
            row=[case["case"]," ".join(str(x) for x in case["rows"]),case["m"]]
            for c in case["columns"]:
                row += [c["selected_P"],c["selected_AP"]]
            writer.writerow(row+[case["evidence"]])
    os.chmod(jpath,0o600)
    os.chmod(cpath,0o600)
    print("E27A_PRIVATE_MANIFEST",jpath)
    print("E27A_PRIVATE_MATCHED_MASKS",cpath)
    print("E27A_GATE_BLOCKED_PHYSICAL: new 1T1MTJ PEX, bias and legal multirow read unverified")
    print("E27A_NO_SPECTRE_RUN; NO_NEW_PEX; NO_PHYSICAL_CORRELATION_CLAIM")

if __name__=="__main__":
    main()
