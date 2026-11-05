#!/usr/bin/env python3
"""E30: scalable GF 1T1-like 256-row multi-column CIM CURRENT experiment.

User-selected 1T1 architecture. Each simulated cell has one real GF access
NFET (compact model) plus a student-owned static 2-terminal MTJ model.
A column contains ALL rows, active or not. Each scenario applies the SAME row-activation mask across columns via
separately ideal-gate-driven NFETs (NOT a real shared-WL RC network);
stored P/AP weights remain resident.
4 or 16 columns are jointly simulated with an intentionally ASSUMED shared
source-return impedance, and compared to independent ground.

IMPORTANT: This is NOT actual 1T1MTJ layout PEX, NOT a 256x256 physical macro,
NOT read-disturb-certified, and DOES NOT establish four-plane neural accuracy.
Wire resistance is a sensitivity assumption (defaults from CLI ONLY); the
real GF transistor currents are solved by NUS Spectre. End-to-end claims await
actual interconnect geometry and signed-bitplane alignment.

Modes:
 selftest: unit-test scenario generation, no GF/NUS.
 generate: make a private circuit deck; no Spectre.
 run: execute a bounded 256x4 or 256x16 matched CAL/DEV campaign.
Python 3.6 stdlib only.
"""
from __future__ import print_function
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

E19_SHA="b6bec40bc234fac406d191229146354a5fe47c6969fb6db6a672e607ddf83e54"
MODEL_SHA="1d22984b7be5135c07bb5e392d73aa53e1ad42b7c4bdc6d2fc11bb3f313b9a88"

def die(msg):
    raise SystemExit("E30_BLOCKED: "+str(msg))

def sha(path):
    h=hashlib.sha256()
    with open(str(path),"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def specs(rows=256,cols=4,m=24,seed=20261105):
    if rows not in (128,256) or cols not in (4,16,256):
        raise ValueError("Only 128/256 rows and 4/16/256 columns")
    if m not in (16,24,32) or rows<4*m:
        raise ValueError("m must be 16/24/32 and rows >=4*m")
    rng=random.Random(seed)
    # C0 alternates P/AP to guarantee attainable matched count classes;
    # other columns hold independent resident weights, never changed per case.
    weights=[set(range(0,rows,2))]
    for c in range(1,cols):
        weights.append(set(rng.sample(list(range(rows)),rows//2)))
    region_len=max(2*m,64)
    if region_len>rows//2:
        raise ValueError("Need near/far spatially separated candidate pools")
    regions={
        "ROW_LO":list(range(region_len)),
        "ROW_HI":list(range(rows-region_len,rows)),
        "DISTRIBUTED":[int(i*rows/region_len)+(i%2) for i in range(region_len)]
    }
    if any(len(v)!=len(set(v)) or min(v)<0 or max(v)>=rows for v in regions.values()):
        raise AssertionError("Invalid row pool")
    scen=[]
    seen=set()
    for area,pool in regions.items():
        available_p=sorted(set(pool)&weights[0])
        available_ap=sorted(set(pool)-weights[0])
        for n in (m//2-1,m//2,m//2+1):
            for split in ("CAL","DEV"):
                for attempt in range(1000):
                    active=tuple(sorted(rng.sample(available_p,n)+
                                        rng.sample(available_ap,m-n)))
                    if active not in seen:break
                else:raise ValueError("Cannot draw distinct spatial masks")
                seen.add(active)
                sid=len(scen)
                scen.append({"scenario_id":sid,"label":"{}-n{}-{}".format(area,n,split),
                             "spatial_group":area,"split":split,
                             "selected_rows":list(active),"C0_true_n":n,
                             "m":m})
    return weights,scen

def build_profiles(rows,cols,weights,scenarios):
    out=[]
    for item in scenarios:
        active=set(item["selected_rows"])
        for col in range(cols):
            p=weights[col]
            n=len(active&p)
            out.append({
               "id":len(out),"scenario_id":item["scenario_id"],
               "label":item["label"],"split":item["split"],"col":col,
               "true_n":n,"m":item["m"],"k":len(p),
               "active_rows_0based":sorted(active),
               "weight_P_rows_0based":sorted(p),
               "mask_hash":hashlib.sha256(repr((item["scenario_id"],col,sorted(active),sorted(p))).encode("ascii")).hexdigest()[:16]
            })
    return out

def selftest():
    for rows in (128,256):
        w,sc=specs(rows,4,24,17)
        prof=build_profiles(rows,4,w,sc)
        assert len(sc)==18 and len(prof)==72
        assert len(set(tuple(s["selected_rows"]) for s in sc))==18
        for s in sc:
            chunk=prof[4*s["scenario_id"]:4*s["scenario_id"]+4]
            assert len({tuple(p["active_rows_0based"]) for p in chunk})==1
            assert all(len(p["active_rows_0based"])==24 and len(p["weight_P_rows_0based"])==rows//2 for p in chunk)
            assert chunk[0]["true_n"]==s["C0_true_n"]
        assert len(set(p["mask_hash"] for p in prof))==len(prof)
    w,s=specs(256,16,24,17)
    assert len(w)==16 and len(s)==18
    print("E30_SELFTEST_PASS: 128/256-row resident weights; 4/16 columns; 18 CAL/DEV spatial masks")
    print("E30_SELFTEST_MOCK_WORKLOAD_ONLY_NOT_GF_PEX_OR_COUNT_ERROR")

def verified_e19():
    try:
        import e19_gf_nfet_mtj_nonideal_count_gate_v2 as e19
    except ImportError:die("verified local E19 v2 must exist beside experiment")
    source=Path(e19.__file__).resolve()
    if sha(source)!=E19_SHA:die("E19 generator SHA changed: "+sha(source))
    model=Path.home()/e19.MODEL_REL
    if not model.is_file() or sha(model)!=MODEL_SHA or e19.MODEL_SHA!=MODEL_SHA:
        die("student MTJ fingerprint differs")
    template_path=Path(e19.choose_template(None)).resolve()
    template=e19.parse_template(template_path)
    return e19,source,model,template_path,template

def chunked(lst,n):
    for i in range(0,len(lst),n):yield lst[i:i+n]

def make_deck(work,rows,m,chunk,rseg,e19,template,model,args):
    work.mkdir(mode=0o700)
    opts=argparse.Namespace(**vars(args))
    opts.rows=rows;opts.m=m;opts.k=rows//2
    opts.vread=0.05;opts.vwl=0.8
    path=Path(e19.make_deck(work,chunk,rseg,template,model,opts))
    if not path.is_file():die("E19 did not create netlist")
    return path.read_text(),sha(path)

def current_vector(raw,profiles,e19):
    z=e19.parse_sources(raw)
    ans=[]
    for p in profiles:
        name="VC%04d:p"%p["id"]
        if name not in z:die("missing actual GF Spectre read source "+name)
        ans.append(float(z[name]))
    if not all(math.isfinite(x) for x in ans):die("nonfinite GF current")
    return ans

def spectre_run(text,work,profiles,e19,timeout):
    work.mkdir(mode=0o700)
    deck=work/"input.scs"
    deck.write_text(text)
    start=time.time()
    with (work/"stdout.log").open("w") as stream:
        try:
            code=subprocess.run(["spectre",str(deck),"+log",str(work/"spectre.log"),
                                 "-format","psfascii"],cwd=str(work),
                                 stdout=stream,stderr=subprocess.STDOUT,
                                 timeout=timeout).returncode
        except subprocess.TimeoutExpired:code=124
    if code:
        die("Spectre rc={} at {}. Private logs retained; no physical result.".format(code,work))
    result=work/"input.raw/dcOp.dc"
    if not result.is_file():die("missing DC current output "+str(result))
    values=current_vector(result,profiles,e19)
    return values,{"deck_sha256":sha(deck),"spectre_psf_sha256":sha(result),
                   "elapsed_sec":round(time.time()-start,2)}

def nearest(n,centres):
    return min(centres,key=lambda k:(abs(n-centres[k]),k))

def score_C0(scenarios,records,arm):
    vals=[]
    for s in scenarios:
        key=str(s["scenario_id"])
        if key not in records:die("Missing scenario id "+key+" in "+arm)
        vals.append({"scenario_id":s["scenario_id"],"area":s["spatial_group"],
                     "split":s["split"],"n":s["C0_true_n"],
                     "I":records[key][0]})
    cal=[r for r in vals if r["split"]=="CAL"]
    dev=[r for r in vals if r["split"]=="DEV"]
    centres={n:sum(x["I"] for x in cal if x["n"]==n)/
             len([x for x in cal if x["n"]==n])
             for n in sorted({x["n"] for x in cal})}
    if len(centres)!=3:die("need 3 CAL count classes in C0")
    means=list(centres.values())
    increasing=means[0]<means[-1]
    ordered=all((means[i]<means[i+1] if increasing else means[i]>means[i+1])
               for i in range(2))
    if not ordered:
        print("E30_CAL_NONMONOTONIC_COUNT_LEVELS",arm,flush=True)
    err=[]
    for r in dev:
        pred=nearest(r["I"],centres)
        err.append({"scenario_id":r["scenario_id"],"area":r["area"],
                    "true_n":r["n"],"decoded_n":pred,
                    "count_error":pred-r["n"],"I_uA":r["I"]*1e6})
    return {"CAL_centroids_uA":{str(k):v*1e6 for k,v in centres.items()},
            "CAL_strictly_monotonic":ordered,
            "DEV_wrong":sum(x["count_error"]!=0 for x in err),
            "DEV_total":len(err),"DEV_cases":err}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("selftest","generate","run"))
    p.add_argument("--rows",type=int,choices=(128,256),default=256)
    p.add_argument("--columns",type=int,choices=(4,16,256),default=4)
    p.add_argument("--active",type=int,choices=(16,24,32),default=24)
    p.add_argument("--segment-ohms",type=float,default=0.25,
                   help="ASSUMED BL resistor per row segment, NOT PEX")
    p.add_argument("--return-ohms",type=float,default=0.25,
                   help="ASSUMED shared SL return per simultaneous scenario, NOT PEX")
    p.add_argument("--seed",type=int,default=20261105)
    p.add_argument("--chunk-scenarios",type=int,default=2)
    p.add_argument("--max-scenarios",type=int,default=18)
    p.add_argument("--timeout-sec",type=int,default=480)
    p.add_argument("--private",default=str(Path.home()/"mram_private/E30_1T1"))
    args=p.parse_args()
    selftest()
    if args.mode=="selftest":return
    if not (math.isfinite(args.segment_ohms) and 0<args.segment_ohms<=1.0 and
            math.isfinite(args.return_ohms) and 0<args.return_ohms<=1.0):
        die("Assumed wire and SL return R must be >0 and <=1Ω; never invent PEX")
    if args.chunk_scenarios<1 or args.chunk_scenarios>4:
        die("chunk_scenarios must be 1..4")
    if args.mode=="run" and args.columns==256:
        die("No unverified full 256x256 Spectre run; generate one private deck first")
    if args.max_scenarios<1 or args.max_scenarios>18:
        die("max-scenarios must be 1..18")
    weights,scenarios=specs(args.rows,args.columns,args.active,args.seed)
    scenarios=scenarios[:args.max_scenarios]
    prof=build_profiles(args.rows,args.columns,weights,scenarios)
    e19,source,model,tpath,template=verified_e19()
    root=Path(args.private).expanduser().resolve()
    root.mkdir(parents=True,exist_ok=True)
    work=root/("E30_{}x{}_{}_{}".format(args.rows,args.columns,
         dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),os.getpid()))
    work.mkdir(mode=0o700)
    manifest={
       "experiment":"E30_GF_1T1_LARGE_ROW_ARRAY",
       "state":"INCOMPLETE","rows":args.rows,"columns":args.columns,
       "cells":args.rows*args.columns,
       "physical_1T1_PEX":False,"GF_compact_NFET":True,
       "student_static_MTJ":True,
       "model_mismatch_or_read_disturb":False,
       "shared_real_multi_column_Spectre":True,
       "physical_shared_WL_network":False,
       "NOT_FULL_1T1_256x256_EXTRACTED":True,
       "assumed_bl_R_per_segment_ohms":args.segment_ohms,
       "row_lo_hi_names":"indices only: electrical near/far order not verified",
       "assumed_sl_shared_return_ohms":args.return_ohms,
       "screening_bias_V":{"read":0.05,"WL":0.8},
       "runtime_weight_map_random_seed":args.seed,
       "cal_dev_separated_by_masks_NOT_chip":True,
       "frozen_E19_SHA":sha(source),"student_MTJ_SHA":sha(model),
       "historical_GF_template_SHA":sha(tpath),
       "scenarios":scenarios,
       "n_scenarios":len(scenarios),
       "source_profiles":prof,
       "results":{}}
    (work/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("E30_PRIVATE_ROOT",work,flush=True)
    print("E30_LARGE_GF_CIM",args.rows,args.columns,"CELLS",args.rows*args.columns,
          "ACTIVE_WL",args.active,"SCENARIOS",len(scenarios),flush=True)
    print("E30_ASSUMED_R_NOT_PEX",args.segment_ohms,args.return_ohms,flush=True)
    if args.mode=="run" and not shutil.which("spectre"):
        die("Spectre not on PATH")
    # Use local audited E28S rewiring with fail-closed terminal topology checks.
    try:
        from e28s_shared_sl_four_column_gf import rewire
    except ImportError:die("E28S return topology verifier missing")
    output={}
    for part_num,sub in enumerate(chunked(scenarios,args.chunk_scenarios)):
        ids=set(x["scenario_id"] for x in sub)
        chunk=[x for x in prof if x["scenario_id"] in ids]
        part=work/("part_%02d"%part_num)
        part.mkdir(mode=0o700)
        modes=[("ideal_independent",0.,False),
               ("assumed_BL_independent",args.segment_ohms,False),
               ("assumed_BL_shared_SL",args.segment_ohms,True)]
        if args.mode=="generate":modes=modes[:1]
        for arm,rseg,shared in modes:
            generated=part/("_gen_"+arm)
            raw,sourcehash=make_deck(generated,args.rows,args.active,chunk,
                                     rseg,e19,template,model,args)
            topology=None
            if shared:
                groups={x["id"]:x["scenario_id"] for x in chunk}
                raw,topology=rewire(raw,groups,args.return_ohms,
                      expected_rows=args.rows,expected_sources=len(chunk))
            if args.mode=="generate":
                print("E30_GENERATED_ONLY",generated/"input.scs",
                      "SHA256",sourcehash,flush=True)
                continue
            vals,meta=spectre_run(raw,part/arm,chunk,e19,args.timeout_sec)
            output.setdefault(arm,{})
            for i,pf in enumerate(chunk):
                sid=str(pf["scenario_id"])
                if sid not in output[arm]:output[arm][sid]=[None]*args.columns
                output[arm][sid][pf["col"]]=vals[i]
            if topology:meta["shared_return_topology_validation"]=topology
            meta["n_cells_in_deck"]=len(chunk)*args.rows
            manifest["results"].setdefault(arm,{"provenance":[]})["provenance"].append(meta)
            manifest["results"][arm]["currents_by_scenario_A"]=output[arm]
            print("E30_SPECTRE_DONE",arm,"PART",part_num,"CELL_DEVICES",len(chunk)*args.rows,
                  "CURRENT_uA_MIN_MAX",
                  [round(min(vals)*1e6,6),round(max(vals)*1e6,6)],flush=True)
            (work/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    if args.mode=="generate":
        print("E30_GENERATE_ONLY_NO_SPECTRE_NO_PEX",work,flush=True)
        return
    for name,rec in output.items():
        if len(rec)!=len(scenarios):die("Incomplete "+name)
        manifest["results"][name]["currents_by_scenario_A"]=rec
        if len(scenarios)==18:
            manifest["results"][name]["C0_cal_dev"]=score_C0(scenarios,rec,name)
            z=manifest["results"][name]["C0_cal_dev"]
            print("E30_C0_COUNT",name,"DEV_WRONG",z["DEV_wrong"],"/",z["DEV_total"],
                  "CAL_CENTROIDS_uA",z["CAL_centroids_uA"],flush=True)
    a=output["assumed_BL_independent"]
    b=output["assumed_BL_shared_SL"]
    for s in scenarios:
        sid=str(s["scenario_id"])
        diffs=[(b[sid][c]-a[sid][c])*1e9 for c in range(args.columns)]
        print("E30_CASE",s["label"],"C0_n",s["C0_true_n"],
              "C0_I_uA",b[sid][0]*1e6,
              "C0_SHARED_VS_INDEP_nA",diffs[0],
              "MAX_SHARED_EFFECT_nA",max(abs(v) for v in diffs),flush=True)
    manifest["state"]="FINISHED"
    path=work/"E30_RESULTS.json"
    path.write_text(json.dumps(manifest,indent=2)+"\n")
    print("E30_REAL_GF_LARGE_ARRAY_RESULTS",path,flush=True)
    print("E30_WARNING_NOT_PEX_NO_NEURAL_REPLAY_NO_1T1_256x256_PHYSICAL_MACRO",flush=True)

if __name__=="__main__":
    main()
