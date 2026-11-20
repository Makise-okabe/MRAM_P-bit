#!/usr/bin/env python3
"""Recover a completed artifact; stdlib verification only, no solver imports."""
import csv
from collections import defaultdict
import gzip
import hashlib
import json
import math
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"results/fyp_tail_probe_20261121"
PREFLIGHT=ROOT/"results/fyp_tail_preflight_20261121"
ARMS=("ref64","fp6","int6","fp6_mask","int6_tail","int6_keep")
FREEZE="54c06ff593c8acded95f7e4ce6f04a347c6164f7"

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    f=json.loads((ROOT/"docs/FYP_TAIL_FREEZE_20261121.json").read_text())
    for path,expected in f["file_sha256"].items():
        if sha(ROOT/path)!=expected:
            raise RuntimeError("Frozen source changed: "+path)
    deliverable=json.loads((BASE/"deliverable_manifest.json").read_text())
    for path,expected in deliverable["files"].items():
        if sha(BASE/path)!=expected["sha256"] or (BASE/path).stat().st_size!=expected["bytes"]:
            raise RuntimeError("Recovered artifact file mismatch: "+path)
    graph_table={}
    with (BASE/"analysis/graph_summary.csv").open() as handle:
        for row in csv.DictReader(handle):
            graph_table[row["family"],int(row["index"]),row["representation"]]=row
    total=0
    graphmeans={}
    allkeys=set()
    for family,name in enumerate(("ring","torus")):
        for g in range(24):
            folder=BASE/name/f"{g:03d}"
            m=json.loads((folder/"manifest.json").read_text())
            if m["freeze_commit"]!=FREEZE or m["records"]!=384:
                raise RuntimeError("Bundle identity mismatch.")
            source=ROOT/"data/fyp_tail_probe_20261121"/name/f"{g:03d}.rudy"
            if sha(source)!=m["graph_sha256"]:
                raise RuntimeError("Original source hash mismatch.")
            for path,expected in m["files"].items():
                if sha(folder/path)!=expected:
                    raise RuntimeError("Raw bundle hash mismatch.")
            with gzip.open(folder/"records.json.gz","rt") as handle:
                rows=json.load(handle)
            if len(rows)!=384:
                raise RuntimeError("Unexpected raw record count.")
            by={(r["representation"],int(r["seed"])):r for r in rows}
            expected={(a,4000000000000+100000*family+1000*g+s) for a in ARMS for s in range(64)}
            if len(by)!=len(rows) or set(by)!=expected:
                raise RuntimeError("Unexpected/duplicate raw keys.")
            b=max(0,max(r["V"] for r in rows if r["representation"] in ARMS[:3]))
            if b!=m["B_control"]:
                raise RuntimeError("Control reference mismatch.")
            for r in rows:
                key=(name,g,r["representation"],r["seed"])
                if key in allkeys:
                    raise RuntimeError("Global duplicate key.")
                allkeys.add(key)
                payload={k:v for k,v in r.items() if k!="record_sha256"}
                canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False)
                if hashlib.sha256(canonical.encode()).hexdigest()!=r["record_sha256"]:
                    raise RuntimeError("Record payload hash mismatch.")
                if r["gain"]!=1 or r["offset_logit"]!=0 or r["attempted_updates"]!=50000:
                    raise RuntimeError("Unregistered run condition.")
                if not r["V"]>=r["M"]>=r["R"]:
                    raise RuntimeError("Invalid trajectory accounting.")
            for a in ARMS:
                rr=[r for r in rows if r["representation"]==a]
                vals=defaultdict(list)
                for r in rr:
                    ref=by["ref64",r["seed"]]
                    vals["Rz_pp"].append(100*(r["V"]-r["R"])/b)
                    vals["A_pp"].append(100*(ref["V"]-r["V"])/b)
                    vals["extra_pp"].append(100*(ref["R"]-r["R"])/b)
                    vals["selection_pp"].append(100*(r["V"]-r["M"])/b)
                    vals["tie_pp"].append(100*(r["M"]-r["R"])/b)
                    vals["buffer_gain_pp"].append(100*(r["buffer_best_original_cut"]-r["R"])/b)
                for metric,v in vals.items():
                    mean=math.fsum(v)/64
                    expected_mean=float(graph_table[name,g,a][metric])
                    if not math.isclose(mean,expected_mean,rel_tol=0,abs_tol=1e-10):
                        raise RuntimeError("Independent graph mean mismatch.")
                    graphmeans[name,g,a,metric]=mean
            total+=len(rows)
    if total!=18432 or len(allkeys)!=18432:
        raise RuntimeError("Unique scientific record cap mismatch.")
    with (BASE/"analysis/confirmatory.csv").open() as handle:
        confirm=list(csv.DictReader(handle))
    for r in confirm:
        observed=math.fsum(graphmeans["ring",g,r["left"],"Rz_pp"]-graphmeans["ring",g,r["right"],"Rz_pp"] for g in range(24))/24
        if not math.isclose(observed,float(r["mean"]),abs_tol=1e-10,rel_tol=0):
            raise RuntimeError("Independent confirmatory mean mismatch.")
    evidence={"status":"PASS","source_artifact_id":14659628343,"source_run_id":44797500337,
              "archive_only_run_id":os.environ.get("GITHUB_RUN_ID"),"frozen_files":len(f["file_sha256"]),
              "verified_deliverable_files":len(deliverable["files"]),"unique_scientific_records":total,
              "independently_recomputed_graph_mean_cells":len(graphmeans),
              "confirmatory_point_estimates_recomputed":2,"solver_calls":0,
              "administrative_failure":"Original archive step omitted git add -f for ignored results directories.",
              "scientific_data_modified":False,"freeze_commit":FREEZE}
    (PREFLIGHT/"artifact_archive_recovery.json").write_text(json.dumps(evidence,sort_keys=True,indent=2)+"\n")
    readme=ROOT/"README.md"
    text=readme.read_text()
    marker="## Weak-tail mechanism checkpoint — 21 November 2026"
    if marker not in text:
        text+="\n\n"+marker+"\n\nThe frozen 2x2 mechanism experiment completed 18,432 unique trajectories on 48 fresh graphs. Both registered ring contrasts were supported: removing the accurate FP6 tail raised selection loss by 0.07562 pp (98.75% one-sided lower bound 0.04719), and restoring the tail to INT6 reduced it by 0.09132 pp (lower bound 0.06210). See [the full checkpoint report](results/fyp_tail_probe_20261121/RESULTS.md) and [registered contrasts](results/fyp_tail_probe_20261121/analysis/confirmatory.csv).\n\nThe workspace failure required a disclosed replay of the same fixed keys on GitHub Actions; inaccessible local outputs were not pooled. The subsequent ignored-directory archive error was repaired from the existing artifact with zero additional solver calls. All raw bundles and source hashes are archived. Offset, gain and hardware work remain stopped at the requested checkpoint.\n"
        readme.write_text(text)
    print(json.dumps(evidence,sort_keys=True))

if __name__=="__main__":
    main()
