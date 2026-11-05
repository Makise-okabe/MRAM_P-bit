#!/usr/bin/env python3
"""E30P: offline strong CAL-only decoders for actual NUS E30 GF currents.

Reads a private E30_RESULTS.json; no Spectre or new circuits. Positions and
read currents are from a GF-NFET + student static MTJ model with ASSUMED
wire resistances, NOT 1T1MTJ PEX. Split is CAL/DEV input masks on SAME nominal
device, NOT independent chip validation. No physical ADC or full network.
Python 3.6 standard library only.
"""
from __future__ import print_function
import argparse, hashlib, json, math, statistics
from pathlib import Path

ARMS=("ideal_independent","assumed_BL_independent","assumed_BL_shared_SL")
AREAS=("ROW_LO","ROW_HI","DISTRIBUTED")
COUNTS=(11,12,13)

def stop(message):
    raise SystemExit("E30P_BLOCKED: "+message)

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for buf in iter(lambda:f.read(1024*1024),b""):h.update(buf)
    return h.hexdigest()

def qscore(active,nrows,direction):
    s=set(active);v=0;total=0
    iterator=range(nrows-1,-1,-1) if direction=="suffix" else range(nrows)
    for row in iterator:
        v+=int(row in s)
        total+=v*v
    return total/100000.0

def decode(value,centres):
    return min(sorted(centres),key=lambda k:(abs(value-centres[k]),k))

def rows_for_arm(manifest,arm):
    sc=manifest["scenarios"]
    val=manifest["results"][arm]["currents_by_scenario_A"]
    rows=[]
    for s in sc:
        sid=str(s["scenario_id"])
        current=val[sid]
        if len(current)!=manifest["columns"] or not all(math.isfinite(x) for x in current):
            stop("Incomplete or nonfinite four-column GF current vector")
        active=s["selected_rows"]
        if len(active)!=24 or len(set(active))!=24:
            stop("Wrong active-mask size")
        if min(active)<0 or max(active)>=256:stop("Row outside 0..255")
        rows.append({"area":s["spatial_group"],"n":int(s["C0_true_n"]),
                     "split":s["split"],"scenario_id":sid,"current_uA":current[0]*1e6,
                     "q_suffix":qscore(active,256,"suffix"),
                     "q_prefix":qscore(active,256,"prefix")})
    strata={(x["area"],x["n"],x["split"]) for x in rows}
    required={(a,n,t) for a in AREAS for n in COUNTS for t in ("CAL","DEV")}
    if len(rows)!=18 or strata!=required:stop("Need complete 3 area x 3 counts x CAL/DEV design")
    return rows

def calibrated_models(cal):
    # Three global current levels: only CAL ideal n may label count classes.
    global_c={n:statistics.mean(x["current_uA"] for x in cal if x["n"]==n)
              for n in COUNTS}
    area_offset={a:statistics.mean(x["current_uA"]-global_c[x["n"]]
                     for x in cal if x["area"]==a) for a in AREAS}
    area_c={(a,n):next(x["current_uA"] for x in cal if x["area"]==a and x["n"]==n)
            for a in AREAS for n in COUNTS}
    qfit={}
    for direction in ("suffix","prefix"):
        key="q_"+direction
        qm={n:statistics.mean(x[key] for x in cal if x["n"]==n) for n in COUNTS}
        denom=sum((x[key]-qm[x["n"]])**2 for x in cal)
        if denom<=0:stop("Q has zero CAL variance")
        beta=sum((x[key]-qm[x["n"]])*(x["current_uA"]-global_c[x["n"]])
                 for x in cal)/denom
        b={n:global_c[n]-beta*qm[n] for n in COUNTS}
        cal_sse=sum((x["current_uA"]-(b[x["n"]]+beta*x[key]))**2 for x in cal)
        qfit[direction]={"beta":beta,"intercepts":b,"CAL_SSE":cal_sse}
    direction=min(qfit,key=lambda k:(qfit[k]["CAL_SSE"],k))
    return global_c,area_offset,area_c,qfit,direction

def evaluate(rows):
    cal=[x for x in rows if x["split"]=="CAL"]
    dev=[x for x in rows if x["split"]=="DEV"]
    if len(cal)!=9 or len(dev)!=9:stop("Expected 9 CAL / 9 DEV")
    g,offset,area_c,qfit,direction=calibrated_models(cal)
    residuals={name:[] for name in ("GLOBAL","CAL_AREA_OFFSET","CAL_AREA_COUNT_BANK","CAL_INPUT_Q")}
    details=[]
    qmodel=qfit[direction]
    for x in dev:
        a=x["area"];obs=x["current_uA"]
        options={
         "GLOBAL":g,
         "CAL_AREA_OFFSET":{n:g[n]+offset[a] for n in COUNTS},
         "CAL_AREA_COUNT_BANK":{n:area_c[(a,n)] for n in COUNTS},
         "CAL_INPUT_Q":{n:qmodel["intercepts"][n]+qmodel["beta"]*x["q_"+direction]
                        for n in COUNTS}}
        predicted={method:decode(obs,ref) for method,ref in options.items()}
        details.append({"area":a,"true_n":x["n"],"current_uA":obs,
                        "predicted":predicted})
        for method,n in predicted.items():residuals[method].append(n-x["n"])
    metrics={name:{"wrong":sum(e!=0 for e in err),"total":len(err),
                   "MAE_count":sum(abs(e) for e in err)/len(err),
                   "RMSE_count":math.sqrt(sum(e*e for e in err)/len(err))}
             for name,err in residuals.items()}
    return {"global_centres_CAL_uA":g,"area_offsets_CAL_uA":offset,
            "Q_direction_CAL_selected":direction,
            "Q_fit_CAL_SSE_uA2":{k:v["CAL_SSE"] for k,v in qfit.items()},
            "Q_beta_uA_per_scaledQ":qmodel["beta"],
            "metrics":metrics,"DEV_cases":details,
            "important_CAL_warning":"Exactly ONE CAL observation per area/count; do not infer independent-chip accuracy."}

def selftest():
    assert qscore([0,1],4,"prefix")==13/100000.0
    assert qscore([0,1],4,"suffix")==5/100000.0
    assert decode(103.9,{11:98.2,12:99.9,13:101.6})==13
    assert decode(103.9,{11:102.2,12:103.9,13:105.6})==12
    print("E30P_SELFTEST_PASS: Q position metric and CAL-only decoder logic")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--selftest",action="store_true")
    ap.add_argument("--source",type=Path)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    selftest()
    if args.selftest:return
    if not args.source or not args.source.is_file():stop("Pass --source /private/E30_RESULTS.json")
    if args.source.stat().st_size>50000000:stop("Unusually large source")
    m=json.loads(args.source.read_text())
    if m.get("state")!="FINISHED" or m.get("rows")!=256 or m.get("columns")!=4:
        stop("Requires complete E30 256x4 result")
    if any(x not in m.get("results",{}) for x in ARMS):stop("Missing electrical arm")
    reports={}
    data={}
    for arm in ARMS:
        data[arm]=rows_for_arm(m,arm)
        reports[arm]=evaluate(data[arm])
    ideal=data["ideal_independent"]
    lo12=next(x["current_uA"] for x in data["assumed_BL_shared_SL"]
              if (x["area"],x["n"],x["split"])==("ROW_LO",12,"CAL"))
    hi12=next(x["current_uA"] for x in data["assumed_BL_shared_SL"]
              if (x["area"],x["n"],x["split"])==("ROW_HI",12,"CAL"))
    centres=reports["ideal_independent"]["global_centres_CAL_uA"]
    step=(centres[13]-centres[11])/2.
    bl=data["assumed_BL_independent"]
    shared=data["assumed_BL_shared_SL"]
    shifts=[abs(x["current_uA"]-y["current_uA"]) for x,y in zip(bl,shared)]
    physical={
      "same_count_n12_LO_minus_HI_uA":lo12-hi12,
      "ideal_one_count_step_uA":step,
      "spatial_shift_in_ideal_count_steps":(lo12-hi12)/step,
      "C0_shared_return_max_abs_shift_nA":max(shifts)*1000,
      "C0_shared_return_mean_abs_shift_nA":statistics.mean(shifts)*1000,
      "warning":"BL 0.25Ω/segment and shared SL 0.25Ω ASSUMED, NOT extracted 1T1MTJ physical RC"}
    dest=args.out or args.source.parent/"E30P_OFFLINE_BASELINES.json"
    if dest.exists():stop("Refusing overwrite "+str(dest))
    report={"experiment":"E30P_NUS_GF_CURRENT_OFFLINE_CAL_ONLY",
            "source_SHA256":digest(args.source),"CAL_DEV_same_nominal_chip":True,
            "no_layout_PEX":True,"no_physical_ADC":True,
            "no_full_W4A8":True,"one_CAL_per_area_count":True,
            "physical_scale_summary":physical,"arms":reports}
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("E30P_SOURCE_SHA",report["source_SHA256"])
    print("E30P_SPATIAL_SHIFT_n12_LO_MINUS_HI_uA",physical["same_count_n12_LO_minus_HI_uA"])
    print("E30P_SPATIAL_SHIFT_IDEAL_COUNT_EQUIV",physical["spatial_shift_in_ideal_count_steps"])
    print("E30P_SHARED_SL_C0_MAX_ABS_SHIFT_nA",physical["C0_shared_return_max_abs_shift_nA"])
    for arm,results in reports.items():
        print("========== E30P",arm,"==========")
        print("E30P_CAL_AREA_OFFSET_uA",results["area_offsets_CAL_uA"])
        print("E30P_Q_DIRECTION_CAL_ONLY",results["Q_direction_CAL_selected"])
        for name,metrics in results["metrics"].items():
            print("E30P_DEV_WRONG",name,metrics["wrong"],"/",metrics["total"],
                  "MAE",metrics["MAE_count"])
        print("E30P_GLOBAL_WRONG_DETAILS",[(x["area"],x["true_n"],
             x["predicted"]["GLOBAL"]) for x in results["DEV_cases"]
             if x["predicted"]["GLOBAL"]!=x["true_n"]])
    print("E30P_PRIVATE_RESULT",dest)
    print("E30P_NO_NEW_SPECTRE_NO_PEX_NO_NEURAL_RECOVERY_CLAIM")

if __name__=="__main__":main()
