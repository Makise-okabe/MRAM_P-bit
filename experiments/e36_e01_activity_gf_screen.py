#!/usr/bin/env python3
"""E36: E01-activity-anchored GF 256x4 1T1-like current screening.

Reads the FROZEN E01 256-row occupancy histogram; chooses real observed
active-row counts m, but uses synthetic, predeclared spatial masks.
Reuses E30's verified GF NFET + student static MTJ generator and E28S
topology check. These are DC reads with ASSUMED 0.25-ohm BL segment
and shared return; NOT PEX, mismatch, actual ADC or MNIST inference.
Does not modify frozen E30/E31, and keeps all licensed decks private.
Python 3.6+ stdlib only.
"""
from __future__ import print_function
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil

import e30_large_1t1_gf_cim as e30
from e28s_shared_sl_four_column_gf import rewire

E01_SHA = "400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a"
E30_SHA = "f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52"
E01_PATH = Path.home() / "MRAM_Path_Finding/experiments/runs/E01_MNIST_20261104T085558Z_038af9/review_packet.zip"
E30_PATH = Path.home() / "mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30_RESULTS.json"
ARMS = ("ideal_independent", "assumed_BL_independent", "assumed_BL_shared_SL")
REGIONS = {
    "NEAR_BIASED_192": list(range(0, 192)),
    "FAR_BIASED_192": list(range(64, 256)),
    "FULL_DISTRIBUTED": list(range(256)),
}

def die(message):
    raise SystemExit("E36_BLOCKED: " + str(message))

def read_e01(path):
    import zipfile
    if not path.is_file() or e30.sha(path) != E01_SHA:
        die("Frozen E01 packet missing or SHA mismatch")
    total = [0] * 257
    with zipfile.ZipFile(str(path)) as z:
        members = sorted(n for n in z.namelist() if n.endswith("/screen.json"))
        if len(members) != 8:
            die("Expected eight frozen E01 array screen files")
        for member in members:
            screen = json.loads(z.read(member).decode("utf-8"))
            ev = screen["runs"][28]["evaluation"]
            hist = ev["occupancy_histogram"]
            if ev["proposed_group_rows"] != 256 or not isinstance(hist, list) or len(hist) != 257:
                die("E01 group-256 histogram is not the expected list")
            if any(type(n) is not int or n < 0 for n in hist):
                die("E01 histogram contains invalid bin counts")
            if sum(hist[1:]) != ev["nonempty_group_reads"]:
                die("E01 nonempty total inconsistent")
            if sum(hist) != ev["potential_group_reads"]:
                die("E01 total potential reads inconsistent")
            if sum(i * n for i, n in enumerate(hist)) != ev["active_rows_total_invariant"]:
                die("E01 active-row sum inconsistent")
            for i in range(257):
                total[i] += hist[i]
    if (sum(total[1:]), sum(total[25:]), sum(total[64:]),
        sum(total[110:]), max(i for i in range(257) if total[i])) != (12316, 7354, 804, 22, 128):
        die("Frozen E01 global occupancy check disagrees with previous NUS output")
    return total

def resident_weights(source_path):
    if not source_path.is_file() or e30.sha(source_path) != E30_SHA:
        die("Frozen E30 SHA mismatch or missing results")
    doc = json.loads(source_path.read_text(encoding="utf-8"))
    if doc.get("state") != "FINISHED" or doc.get("rows") != 256 or doc.get("columns") != 4:
        die("Frozen source is not completed E30 256x4")
    weights = []
    for c in range(4):
        p = doc["source_profiles"][c]
        if p["col"] != c or p["scenario_id"] != 0:
            die("Unexpected E30 first-scenario profile order")
        w = set(p["weight_P_rows_0based"])
        if len(w) != 128 or min(w) < 0 or max(w) > 255:
            die("Invalid resident E30 P-state weights")
        weights.append(w)
    return weights

def make_scenarios(weights, hist, m_values, repeats, seed):
    rng = random.Random(seed)
    scenarios = []
    used = set()
    for m in m_values:
        if m < 1 or m > 128 or hist[m] == 0:
            die("Requested m={} not observed in frozen E01".format(m))
        for area, pool in REGIONS.items():
            if len(pool) < m:
                die("Spatial region smaller than activity {}".format(m))
            for rep in range(repeats):
                for attempt in range(10000):
                    mask = tuple(sorted(rng.sample(pool, m)))
                    if mask not in used:
                        break
                else:
                    die("Could not draw a unique mask")
                used.add(mask)
                sid = len(scenarios)
                split = "CAL" if rep == 0 else "DEV"
                n = len(set(mask) & weights[0])
                scenarios.append({
                    "scenario_id": sid,
                    "label": "{}_m{}_rep{}".format(area, m, rep),
                    "spatial_group": area,
                    "split": split,
                    "selected_rows": list(mask),
                    "C0_true_n": n,
                    "m": m,
                    "E01_observed_count_at_m": hist[m],
                })
    return scenarios

def selftest():
    weights = [set(range(0,256,2))] * 4
    hist = [0] * 257
    for m in (24,29,56,89,128):
        hist[m] = 3
    scenarios = make_scenarios(weights, hist, (24,29,56,89,128), 2, 1701)
    assert len(scenarios) == 30
    assert len(set(tuple(s["selected_rows"]) for s in scenarios)) == 30
    profiles = e30.build_profiles(256,4,weights,scenarios)
    assert len(profiles) == 120
    for s in scenarios:
        chunk = profiles[s["scenario_id"]*4:s["scenario_id"]*4+4]
        assert len(chunk) == 4
        assert all(p["m"] == s["m"] for p in chunk)
        assert all(len(p["active_rows_0based"]) == s["m"] for p in chunk)
        assert chunk[0]["true_n"] == s["C0_true_n"]
    assert all(len(set(s["selected_rows"])) == s["m"] for s in scenarios)
    print("E36_SELFTEST_PASS: 5 activity levels, 3 spatial pools, 2 masks each, 4 fixed columns")
    print("E36_SELFTEST_NO_GF_NO_PEX_NO_REAL_E01_MASK_REPLAY")

def parse_levels(s):
    try:
        vals = tuple(int(x.strip()) for x in s.split(","))
    except ValueError:
        die("Use comma-separated integer m values")
    if not vals or len(vals) != len(set(vals)):
        die("Empty or duplicate m")
    if any(x < 1 or x > 128 for x in vals):
        die("m must lie in 1..128")
    return vals

def calculate_metrics(scenarios, output):
    results = {}
    for m in sorted({s["m"] for s in scenarios}):
        records = []
        for s in scenarios:
            if s["m"] != m:
                continue
            key = str(s["scenario_id"])
            ideal = output["ideal_independent"][key]
            bl = output["assumed_BL_independent"][key]
            shared = output["assumed_BL_shared_SL"][key]
            for c in range(4):
                records.append({
                    "scenario_id": s["scenario_id"], "column": c,
                    "true_P_count": len(set(s["selected_rows"]) & set(
                        output["_resident_weights"][c])),
                    "I_ideal_uA": ideal[c]*1e6,
                    "I_BL_uA": bl[c]*1e6,
                    "I_BL_SL_uA": shared[c]*1e6,
                    "BL_minus_ideal_uA": (bl[c]-ideal[c])*1e6,
                    "sharedSL_minus_BL_nA": (shared[c]-bl[c])*1e9,
                })
        results[str(m)] = {
            "n_column_observations": len(records),
            "ideal_current_range_uA": [min(r["I_ideal_uA"] for r in records),
                                      max(r["I_ideal_uA"] for r in records)],
            "bl_current_range_uA": [min(r["I_BL_uA"] for r in records),
                                   max(r["I_BL_uA"] for r in records)],
            "shared_current_range_uA": [min(r["I_BL_SL_uA"] for r in records),
                                       max(r["I_BL_SL_uA"] for r in records)],
            "mean_abs_BL_shift_uA": sum(abs(r["BL_minus_ideal_uA"]) for r in records)/len(records),
            "max_abs_BL_shift_uA": max(abs(r["BL_minus_ideal_uA"]) for r in records),
            "max_abs_shared_SL_increment_nA": max(abs(r["sharedSL_minus_BL_nA"]) for r in records),
            "details": records,
        }
    return results

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("selftest","preview","run"))
    p.add_argument("--m-values", default="24,29,56,89,128")
    p.add_argument("--repeats", type=int, default=2)
    p.add_argument("--seed", type=int, default=20261107)
    p.add_argument("--chunk-scenarios", type=int, default=2)
    p.add_argument("--timeout-sec", type=int, default=480)
    p.add_argument("--private", type=Path,
                   default=Path.home()/"mram_private/E36_activity_GF")
    args = p.parse_args()
    selftest()
    if args.mode == "selftest":
        return
    if args.repeats < 2 or args.repeats > 4:
        die("2..4 repeats required, first CAL and remaining DEV")
    if args.chunk_scenarios < 1 or args.chunk_scenarios > 3:
        die("chunk-scenarios must be 1..3")
    m_values = parse_levels(args.m_values)
    hist = read_e01(E01_PATH)
    weights = resident_weights(E30_PATH)
    scenarios = make_scenarios(weights, hist, m_values, args.repeats, args.seed)
    profiles = e30.build_profiles(256,4,weights,scenarios)
    if len(profiles) != len(scenarios)*4:
        die("Profile count incorrect")
    print("E36_FROZEN_E01_SHA", E01_SHA, flush=True)
    print("E36_FROZEN_E30_SHA", E30_SHA, flush=True)
    print("E36_M_VALUES", list(m_values), flush=True)
    print("E36_SCENARIOS", len(scenarios), "GF_PROFILE_COUNT", len(profiles), flush=True)
    print("E36_ACTIVITY_HISTOGRAM_COUNTS", {str(m):hist[m] for m in m_values}, flush=True)
    print("E36_MASKS_SYNTHETIC_ACTIVITY_MATCHED_NOT_TRUE_MNIST_TRACES", flush=True)
    if args.mode == "preview":
        for s in scenarios:
            print("E36_MASK", s["label"], "C0_P", s["C0_true_n"],
                  "m", s["m"], "SHA", hashlib.sha256(
                      repr(s["selected_rows"]).encode("ascii")).hexdigest()[:12])
        print("E36_PREVIEW_ONLY_NO_DECK_NO_SPECTRE", flush=True)
        return
    if not shutil.which("spectre"):
        die("Spectre unavailable; enter GF-licensed Singularity environment")
    e19, e19path, model, template_path, template = e30.verified_e19()
    root = args.private.expanduser().resolve()
    root.mkdir(parents=True,exist_ok=True)
    work = root / ("E36_256x4_" + dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                   + "_" + str(os.getpid()))
    work.mkdir(mode=0o700)
    manifest = {
        "experiment": "E36_GF_256x4_E01_ACTIVITY_MATCHED_SYNTHETIC_MASKS",
        "status": "INCOMPLETE",
        "frozen_E01_SHA": E01_SHA,
        "frozen_E30_SHA": E30_SHA,
        "frozen_E19_SHA": e30.sha(e19path),
        "static_student_MTJ_SHA": e30.sha(model),
        "GF_template_SHA": e30.sha(template_path),
        "rows": 256, "columns": 4,
        "E01_256row_histogram": hist,
        "activity_m_values": list(m_values),
        "synthetic_spatial_masks_NOT_true_neural_input_masks": True,
        "assumed_bl_R_per_row_segment_ohms": 0.25,
        "assumed_common_sl_R_ohms": 0.25,
        "physical_1T1_PEX": False,
        "physical_ADC": False,
        "mismatch_noise_and_transient": False,
        "shared_physical_WL_network": False,
        "bias_provisional_V": {"read":0.05,"WL":0.8},
        "resident_P_weights_by_column": [sorted(w) for w in weights],
        "scenarios": scenarios,
        "profiles": profiles,
        "results": {},
    }
    (work/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print("E36_PRIVATE_ROOT",work,flush=True)
    output={a:{} for a in ARMS}
    for part_num, sub in enumerate(e30.chunked(scenarios,args.chunk_scenarios)):
        ids={s["scenario_id"] for s in sub}
        chunk=[x for x in profiles if x["scenario_id"] in ids]
        group_by={x["id"]:x["scenario_id"] for x in chunk}
        folder=work/("part_%02d"%part_num)
        folder.mkdir(mode=0o700)
        for arm,rseg,shared in (
            ("ideal_independent",0.,False),
            ("assumed_BL_independent",.25,False),
            ("assumed_BL_shared_SL",.25,True)):
            generated=folder/("_gen_"+arm)
            text,deck_sha=e30.make_deck(generated,256,sub[0]["m"],chunk,
                                        rseg,e19,template,model,args)
            if len({s["m"] for s in sub}) > 1:
                die("Chunk must contain only one m; use --chunk-scenarios 1 or sorted m-aligned chunks")
            topology=None
            if shared:
                text,topology=rewire(text,group_by,.25,
                    expected_rows=256,expected_sources=len(chunk))
            vals,meta=e30.spectre_run(text,folder/arm,chunk,e19,args.timeout_sec)
            for j,pf in enumerate(chunk):
                sid=str(pf["scenario_id"])
                if sid not in output[arm]:
                    output[arm][sid]=[None]*4
                output[arm][sid][pf["col"]]=vals[j]
            meta["part"]=part_num
            if topology:
                meta["shared_return_topology_validation"]=topology
            manifest["results"].setdefault(arm,{"receipts":[]})["receipts"].append(meta)
            manifest["results"][arm]["currents_by_scenario_A"]=output[arm]
            (work/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
            print("E36_GF_DONE",arm,"PART",part_num,
                  "m",sub[0]["m"],"SCENARIOS",len(sub),
                  "CURRENT_RANGE_uA",
                  [round(min(vals)*1e6,4),round(max(vals)*1e6,4)],flush=True)
    for arm in ARMS:
        if len(output[arm]) != len(scenarios):
            die("Incomplete "+arm)
        if any(len(v)!=4 or any(x is None or not math.isfinite(x) for x in v)
               for v in output[arm].values()):
            die("Nonfinite/missing GF read current in "+arm)
    output["_resident_weights"]=[sorted(w) for w in weights]
    manifest["activity_analysis"]=calculate_metrics(scenarios,output)
    for m, data in sorted(manifest["activity_analysis"].items(),key=lambda x:int(x[0])):
        print("E36_ACTIVITY_RESULT","m",m,
              "N",data["n_column_observations"],
              "MEAN_ABS_BL_SHIFT_uA",data["mean_abs_BL_shift_uA"],
              "MAX_ABS_BL_SHIFT_uA",data["max_abs_BL_shift_uA"],
              "MAX_SHARED_SL_DIFF_nA",data["max_abs_shared_SL_increment_nA"],
              flush=True)
    manifest["status"]="FINISHED"
    dest=work/"E36_RESULTS.json"
    dest.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("E36_RESULT_PRIVATE",dest,flush=True)
    print("E36_NO_PEX_NO_PHYSICAL_ADC_NO_MISMATCH_NO_NEURAL_ACCURACY",flush=True)

if __name__ == "__main__":
    main()
