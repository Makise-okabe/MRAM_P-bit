#!/usr/bin/env python3
"""E31: fixed-E30-CAL generalization to NEW 256x4 GF Spectre read masks.

Actual licensed GF NFET compact-model currents + student's static MTJ model,
with the SAME ASSUMED BL/SL resistor values and device weight map as E30.
Never claims 1T1 PEX, measured chip BER, deployed ADC, or N2 recovery.

The E30 original 9 CAL masks fit all baseline coefficients. No new CAL,
no refitting/retuning using E31; the new DEV masks include in-distribution
spatial masks AND uncalibrated/OOD patterns. Four columns are solved jointly.
Uses e30_large_1t1_gf_cim.py and e30p_offline_strong_baselines.py.
Python 3.6 standard library only.
"""
from __future__ import print_function
import argparse, datetime as dt, hashlib, json, math, os
from pathlib import Path
import random, shutil, statistics

SEED_WEIGHT=20261105
DEFAULT_SOURCE=Path.home()/"mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30_RESULTS.json"
EXPECTED_SHA="f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52"
AREAS=("ROW_LO","ROW_HI","DISTRIBUTED","UNIFORM_OOD","DUAL_END_OOD","CENTER_OOD")
COUNTS=(11,12,13)
ARMS=("ideal_independent","assumed_BL_independent","assumed_BL_shared_SL")

def die(msg):
    raise SystemExit("E31_BLOCKED: "+str(msg))

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def region_pool(area):
    if area=="ROW_LO":return list(range(64))
    if area=="ROW_HI":return list(range(192,256))
    if area=="DISTRIBUTED":return [int(i*256/64)+(i%2) for i in range(64)]
    if area=="UNIFORM_OOD":return list(range(256))
    if area=="DUAL_END_OOD":return list(range(32))+list(range(224,256))
    if area=="CENTER_OOD":return list(range(96,160))
    raise ValueError("Unknown region "+str(area))

def new_masks(weights,original,repeats,seed):
    if repeats<1 or repeats>10:raise ValueError("repeats must be 1..10")
    rng=random.Random(seed)
    original_set={tuple(s["selected_rows"]) for s in original["scenarios"]}
    unique=set(original_set)
    profiles=[]
    idno=0
    for area in AREAS:
        pool=region_pool(area)
        if len(set(pool))!=len(pool):die("Duplicate row positions in "+area)
        available_P=sorted(set(pool)&weights[0])
        available_AP=sorted(set(pool)-weights[0])
        for n in COUNTS:
            for r in range(repeats):
                for attempt in range(10000):
                    active=tuple(sorted(rng.sample(available_P,n)+
                         rng.sample(available_AP,24-n)))
                    if active not in unique:break
                else:die("Mask sampling exhausted for "+area)
                unique.add(active)
                profiles.append({
                    "scenario_id":idno,
                    "label":"{}-n{}-DEV-{:02d}".format(area,n,r),
                    "spatial_group":area,
                    "split":"DEV",
                    "selected_rows":list(active),
                    "C0_true_n":n,"m":24,
                    "E31_new_unseen_mask":True
                })
                idno+=1
    assert len(profiles)==len(AREAS)*len(COUNTS)*repeats
    return profiles

def selftest():
    import e30_large_1t1_gf_cim as e30
    weights,original_sc=e30.specs(256,4,24,SEED_WEIGHT)
    fake={"scenarios":original_sc}
    cases=new_masks(weights,fake,2,771)
    assert len(cases)==36
    assert len(set(tuple(x["selected_rows"]) for x in cases))==36
    prof=e30.build_profiles(256,4,weights,cases)
    assert len(prof)==144
    for item in cases:
        group=prof[item["scenario_id"]*4:item["scenario_id"]*4+4]
        assert group[0]["true_n"]==item["C0_true_n"]
        assert all(p["m"]==24 and p["k"]==128 for p in group)
    print("E31_SELFTEST_PASS: 36 new DEV masks, 3 seen and 3 out-of-CAL spatial regimes, identical resident P/AP map")
    print("E31_SELFTEST_NO_GF_CURRENT_NO_PEX")

def check_source(path,allow_other):
    if not path.is_file():die("Missing E30 original private JSON")
    if not allow_other and sha(path)!=EXPECTED_SHA:
        die("E30 source SHA mismatch, freeze original E30 evidence")
    raw=json.loads(path.read_text())
    if raw.get("state")!="FINISHED" or raw.get("rows")!=256 or raw.get("columns")!=4 or raw.get("n_scenarios")!=18:
        die("E30 source is not completed 256x4 and 18 scenarios")
    if not math.isclose(float(raw["assumed_bl_R_per_segment_ohms"]),.25,abs_tol=1e-12):
        die("E30 BL hypothesis differs from frozen .25ohm")
    if not math.isclose(float(raw["assumed_sl_shared_return_ohms"]),.25,abs_tol=1e-12):
        die("E30 return hypothesis differs from frozen .25ohm")
    return raw

def fit_frozen_cal(raw,e30p):
    fit={}
    for arm in ARMS:
        orig=e30p.rows_for_arm(raw,arm)
        cal=[x for x in orig if x["split"]=="CAL"]
        g,off,bank,qfits,d=e30p.calibrated_models(cal)
        fit[arm]=(g,off,bank,qfits,d)
    return fit

def eval_new(new_scenarios,current,fit,arm,e30p):
    g,off,bank,qfits,d=fit
    qfit=qfits[d]
    records=[]
    names=("GLOBAL","AREA_OFFSET","AREA_COUNT_BANK","INPUT_Q")
    for scenario in new_scenarios:
        sid=str(scenario["scenario_id"])
        if sid not in current:die("Missing new current scenario "+sid)
        a=scenario["spatial_group"]
        val=current[sid][0]*1e6
        q=e30p.qscore(scenario["selected_rows"],256,d)
        options={"GLOBAL":g,
                 "AREA_OFFSET":{n:g[n]+off[a] if a in off else g[n] for n in COUNTS},
                 "AREA_COUNT_BANK":{n:bank[(a,n)] if a in off else g[n] for n in COUNTS},
                 "INPUT_Q":{n:qfit["intercepts"][n]+qfit["beta"]*q for n in COUNTS}}
        pred={name:e30p.decode(val,options[name]) for name in names}
        records.append({"scenario_id":sid,"area":a,"in_CAL_spatial_family":a in off,
                        "n":scenario["C0_true_n"],"current_C0_uA":val,
                        "Q_"+d:q,"prediction":pred})
    summary={}
    for group in ("SEEN_SPATIAL_FAMILIES","UNSEEN_SPATIAL_FAMILIES","ALL"):
        subset=([x for x in records if x["in_CAL_spatial_family"]==(group=="SEEN_SPATIAL_FAMILIES")]
                if group!="ALL" else records)
        summary[group]={}
        for name in names:
            err=[x["prediction"][name]-x["n"] for x in subset]
            summary[group][name]={"wrong":sum(e!=0 for e in err),
                                  "total":len(err),
                                  "mae_count":sum(abs(e) for e in err)/len(err)}
    return {"arm":arm,"CAL_model_locked":True,"CAL_Q_direction":d,
            "new_DEV":records,"summary":summary,
            "area_unknown_policy":"GLOBAL fallback, zero tuning for unseen region"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("selftest","run"))
    p.add_argument("--source",type=Path,default=DEFAULT_SOURCE)
    p.add_argument("--repeats",type=int,default=2)
    p.add_argument("--seed",type=int,default=20261106)
    p.add_argument("--chunk-scenarios",type=int,default=2)
    p.add_argument("--timeout-sec",type=int,default=480)
    p.add_argument("--private",type=Path,default=Path.home()/"mram_private/E31_1T1")
    p.add_argument("--allow-other-source",action="store_true",help="Explicit, separately audited experiment only")
    args=p.parse_args()
    selftest()
    if args.mode=="selftest":return
    if args.chunk_scenarios<1 or args.chunk_scenarios>3:die("chunk scenarios must be 1..3")
    if not shutil.which("spectre"):die("Spectre not on PATH")
    import e30_large_1t1_gf_cim as e30
    import e30p_offline_strong_baselines as e30p
    from e28s_shared_sl_four_column_gf import rewire
    raw=check_source(args.source,args.allow_other_source)
    source_sha=sha(args.source)
    weights,orig_sc=e30.specs(256,4,24,SEED_WEIGHT)
    for c in range(4):
        reported=set(raw["source_profiles"][c]["weight_P_rows_0based"])
        if reported!=weights[c]:die("E31 resident weight state mismatch for C"+str(c))
    known={(s["spatial_group"],s["C0_true_n"],s["split"]) for s in raw["scenarios"]}
    if len(known)!=18:die("E30 source training design changed")
    scenarios=new_masks(weights,raw,args.repeats,args.seed)
    profiles=e30.build_profiles(256,4,weights,scenarios)
    cal_models=fit_frozen_cal(raw,e30p)
    e19,src,model,tpath,template=e30.verified_e19()
    root=args.private.expanduser().resolve()
    root.mkdir(parents=True,exist_ok=True)
    stamp="E31_256x4_"+dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")+"_"+str(os.getpid())
    work=root/stamp
    work.mkdir(mode=0o700)
    manifest={
        "experiment":"E31_NEW_MASKS_FROZEN_E30_CAL",
        "status":"INCOMPLETE","source_e30_sha256":source_sha,
        "resident_weights_identical":True,
        "full_1T1_PEX":False,"GF_compact_model":True,
        "MTJ":"student static two-state",
        "assumed_BL_R_per_segment_ohms":.25,
        "assumed_shared_SL_R_ohms":.25,
        "calibration_from":"E30 ORIGINAL 9 CAL MASKS ONLY",
        "CAL_recalibrated_on_E31":False,
        "E31_new_DEV_masks":len(scenarios),
        "DEV_spatial_families":list(AREAS),
        "repeats_per_family_and_count":args.repeats,
        "new_DEV":scenarios,"results":{}}
    (work/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("E31_PRIVATE_ROOT",work,flush=True)
    print("E31_FROZEN_E30_SOURCE_SHA",source_sha,flush=True)
    print("E31_GF_256ROW_4COL_NEW_DEV",len(scenarios),"CIRCUIT_CASES",
          len(profiles),"ALL_CELLS_PER_SCENARIO",1024,flush=True)
    print("E31_NO_NEW_CAL, OOD_SPATIAL_FAMILY_GATE; ASSUMED_R_NOT_PEX",flush=True)
    outputs={arm:{} for arm in ARMS}
    for idx,part_sc in enumerate(e30.chunked(scenarios,args.chunk_scenarios)):
        ids={x["scenario_id"] for x in part_sc}
        group=[x for x in profiles if x["scenario_id"] in ids]
        group_by={x["id"]:x["scenario_id"] for x in group}
        folder=work/("part_%02d"%idx)
        folder.mkdir(mode=0o700)
        for arm,rseg,coupled in (
            ("ideal_independent",0.,False),
            ("assumed_BL_independent",.25,False),
            ("assumed_BL_shared_SL",.25,True)):
            deck,_=e30.make_deck(folder/("_gen_"+arm),256,24,group,rseg,e19,template,model,args)
            if coupled:
                deck,check=rewire(deck,group_by,.25,
                       expected_rows=256,expected_sources=len(group))
            else:check=None
            currents,receipt=e30.spectre_run(deck,folder/arm,group,e19,args.timeout_sec)
            for j,pf in enumerate(group):
                sid=str(pf["scenario_id"])
                if sid not in outputs[arm]:outputs[arm][sid]=[None]*4
                outputs[arm][sid][pf["col"]]=currents[j]
            info={"part":idx,"electrical":receipt}
            if check:info["return_topology"]=check
            manifest["results"].setdefault(arm,{"part_receipts":[]})["part_receipts"].append(info)
            manifest["results"][arm]["currents_by_scenario_A"]=outputs[arm]
            (work/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
            print("E31_GF_SPECTRE_DONE",arm,"PART",idx,"NEW_DEV_MASKS",len(part_sc),
                  "GF_CURRENT_MIN_MAX_uA",
                  [min(currents)*1e6,max(currents)*1e6],flush=True)
    for arm in ARMS:
        if len(outputs[arm])!=len(scenarios):
            die("Incomplete actual GF arm "+arm)
        r=eval_new(scenarios,outputs[arm],cal_models[arm],arm,e30p)
        manifest["results"][arm]["FROZEN_CAL_DEV_ANALYSIS"]=r
        for family,policy_result in r["summary"].items():
            print("E31_HELD_OUT_FAMILY",arm,family,
                  " ".join("{}:{}/{}".format(name,v["wrong"],v["total"])
                           for name,v in policy_result.items()),flush=True)
    manifest["status"]="FINISHED"
    result=work/"E31_RESULTS.json"
    result.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("E31_COMPLETE_ACTUAL_GF_NEW_DEV",result,flush=True)
    print("E31_NOT_PEX_NOT_INDEPENDENT_CHIP_NOT_FULL_DNN_OR_RECOVERY",flush=True)

if __name__=="__main__":main()
