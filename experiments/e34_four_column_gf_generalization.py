#!/usr/bin/env python3
"""E34: actual GF 256x4 cross-column CAL->DEV count generalization.

E30/E31 Spectre recorded four simultaneous currents per scenario, but E31
only scored C0. Recover all four resident P/AP weight maps from the E30
manifest, recompute exact offline n labels for all columns, and score C0-C3.
Do not treat these four columns as signed W4 bitplanes; mapping is NOT proven.

CAL: nine ORIGINAL E30 CAL masks, never original DEV or new E31 DEV.
DEV: 36 NEW E31 masks, each of four columns; SAME nominal weight map.
For each column and each of three original GF circuit arms, calibrate models:
   Global linear I(n) = a + b*n
   CAL-only continuous feature I(n,z)=a+b*n+c*z
      z = known input mask row-centroid, far-half occupancy, Q suffix/prefix.
   Choose Q direction only from CAL residual SSE, never from DEV results.
All baseline model coefficients learned per-column on identical CAL budgets.
The true n is NOT used during inference, only CAL labels and DEV scoring.
No new Spectre, no foundry PEX, no physical ADC, no mismatch or DNN inference.
Python3.6+ stdlib only.
"""
from __future__ import print_function
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

E30_SHA="f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52"
E30_PATH=Path.home()/"mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30_RESULTS.json"
E31_PATH=Path.home()/"mram_private/E31_1T1/E31_256x4_20261105T033721Z_2792/E31_RESULTS.json"
ARMS=("ideal_independent","assumed_BL_independent","assumed_BL_shared_SL")
POLICIES=("GLOBAL_LINEAR","MEAN_ROW_LINEAR","FAR_HALF_LINEAR","Q_CAL_SELECTED")
FEATURES=("MEAN_ROW","FAR_HALF","Q_PREFIX","Q_SUFFIX")

def die(msg):raise SystemExit("E34_BLOCKED: "+str(msg))

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def solve(A,b):
    """Small dense normal-equation solver with partial pivot; no numpy."""
    n=len(b)
    m=[list(map(float,A[j]))+[float(b[j])] for j in range(n)]
    for col in range(n):
        pivot=max(range(col,n),key=lambda row:abs(m[row][col]))
        scale=max(1.0,max(abs(m[r][c]) for r in range(n) for c in range(n)))
        if abs(m[pivot][col])<=1e-12*scale:
            raise ValueError("insufficient CAL variation / collinearity")
        m[pivot],m[col]=m[col],m[pivot]
        v=m[col][col]
        for j in range(col,n+1):m[col][j]/=v
        for row in range(n):
            if row==col:continue
            t=m[row][col]
            for j in range(col,n+1):
                m[row][j]-=t*m[col][j]
    return [m[i][-1] for i in range(n)]

def fit(rows,feature=None):
    x=[[1.0,float(r["n"])] + ([float(r["feature"][feature])] if feature else [])
       for r in rows]
    y=[float(r["current_uA"]) for r in rows]
    n=len(x[0])
    normal=[[sum(r[i]*r[j] for r in x) for j in range(n)] for i in range(n)]
    rhs=[sum(r[i]*v for r,v in zip(x,y)) for i in range(n)]
    params=solve(normal,rhs)
    sse=sum((sum(a*b for a,b in zip(params,xx))-yy)**2 for xx,yy in zip(x,y))
    return {"params":params,"feature":feature,"CAL_SSE_uA2":sse}

def expected_uA(model,n,feature):
    coef=model["params"]
    return coef[0]+coef[1]*n+(coef[2]*feature[model["feature"]]
                              if model["feature"] else 0.0)

def decode(model,current,feature,m=24):
    return min(range(m+1),key=lambda n:(abs(current-expected_uA(model,n,feature)),n))

def feature_values(mask):
    from e30p_offline_strong_baselines import qscore
    if len(mask)!=24 or len(set(mask))!=24 or min(mask)<0 or max(mask)>=256:
        die("E34 invalid input mask")
    return {"MEAN_ROW":sum(mask)/(24.0*255.0),
            "FAR_HALF":sum(1 for k in mask if k>=128)/24.0,
            "Q_PREFIX":qscore(mask,256,"prefix"),
            "Q_SUFFIX":qscore(mask,256,"suffix")}

def weights_by_col(e30):
    profiles=e30["source_profiles"]
    if len(profiles)!=len(e30["scenarios"])*4:die("E30 source profiles not complete")
    refs={}
    for p in profiles:
        c=int(p["col"])
        w=frozenset(int(j) for j in p["weight_P_rows_0based"])
        if c not in range(4) or len(w)!=128:die("Invalid 256-row resident P map")
        if c in refs and refs[c]!=w:die("E30 weights mutated between scenarios")
        refs[c]=w
        a=set(p["active_rows_0based"])
        if len(a)!=24 or len(a & w)!=int(p["true_n"]):
            die("E30 true n and bit states mismatch")
    if set(refs)!=set(range(4)):die("E30 missing columns")
    return refs

def get_sources(e30_path,e31_path):
    if not e30_path.is_file() or not e31_path.is_file():
        die("Need private E30 and E31 result JSON")
    if digest(e30_path)!=E30_SHA:die("E30 source SHA mismatch")
    e30=json.loads(e30_path.read_text())
    e31=json.loads(e31_path.read_text())
    if e30.get("state")!="FINISHED" or e31.get("status")!="FINISHED":
        die("E30 or E31 incomplete")
    if e30.get("rows")!=256 or e30.get("columns")!=4 or \
       e31.get("source_e30_sha256")!=E30_SHA or \
       e31.get("resident_weights_identical") is not True or \
       e31.get("CAL_recalibrated_on_E31") is not False:
        die("Unmatched E30/E31 physical/circuit contract")
    if len(e30["scenarios"])!=18 or len(e31["new_DEV"])!=36:
        die("E30 9 CAL+9 DEV and E31 36 fresh masks required")
    original_masks={tuple(s["selected_rows"]) for s in e30["scenarios"]}
    fresh_masks={tuple(s["selected_rows"]) for s in e31["new_DEV"]}
    if len(fresh_masks)!=36 or fresh_masks & original_masks:
        die("E31 DEV masks duplicate original masks")
    weights=weights_by_col(e30)
    return e30,e31,weights

def extract(e30,e31,weights,arm):
    cal=[]
    dev=[]
    for origin,source,target in (("CAL",e30,e30["scenarios"]),
                                 ("DEV",e31,e31["new_DEV"])):
        val=source["results"][arm]["currents_by_scenario_A"]
        for s in target:
            if origin=="CAL" and s["split"]!="CAL":continue
            sid=str(s["scenario_id"])
            currents=val.get(sid)
            if not currents or len(currents)!=4:die("Missing joint current vector "+sid)
            mask=s["selected_rows"]
            feat=feature_values(mask)
            for c in range(4):
                I=currents[c]*1e6
                if not math.isfinite(I):die("Nonfinite GF source current")
                item={"scenario":sid,"col":c,"n":len(set(mask)&weights[c]),
                      "current_uA":I,"feature":feat,
                      "area":s["spatial_group"],
                      "seen_area":s["spatial_group"] in ("ROW_LO","ROW_HI","DISTRIBUTED")}
                (cal if origin=="CAL" else dev).append(item)
    if len(cal)!=36 or len(dev)!=144:die("Expected CAL 9x4, DEV 36x4")
    return cal,dev

def metrics(items):
    err=[x["pred"]-x["n"] for x in items]
    return {"wrong":sum(e!=0 for e in err),"total":len(err),
            "MAE":sum(abs(e) for e in err)/len(err),
            "max_abs_count_error":max(abs(e) for e in err)}

def evaluate(cal,dev):
    bycol={}
    all_rows={p:[] for p in POLICIES}
    for c in range(4):
        fitcal=[x for x in cal if x["col"]==c]
        fitdev=[x for x in dev if x["col"]==c]
        if len(fitcal)!=9 or len(fitdev)!=36:die("Missing CAL/DEV per col")
        models={"GLOBAL_LINEAR":fit(fitcal),
                "MEAN_ROW_LINEAR":fit(fitcal,"MEAN_ROW"),
                "FAR_HALF_LINEAR":fit(fitcal,"FAR_HALF")}
        suffix=fit(fitcal,"Q_SUFFIX")
        prefix=fit(fitcal,"Q_PREFIX")
        chosen=min((suffix,prefix),key=lambda x:(x["CAL_SSE_uA2"],x["feature"]))
        models["Q_CAL_SELECTED"]=chosen
        records=[]
        for x in fitdev:
            pred={p:decode(model,x["current_uA"],x["feature"]) for p,model in models.items()}
            row={"area":x["area"],"seen_area":x["seen_area"],
                 "n":x["n"],"pred":pred}
            records.append(row)
            for p in POLICIES:
                all_rows[p].append({"pred":pred[p],"n":x["n"],"col":c,
                                    "seen_area":x["seen_area"]})
        counts_cal=[x["n"] for x in fitcal]
        counts_dev=[x["n"] for x in fitdev]
        bycol[str(c)]={
            "CAL_count_range":[min(counts_cal),max(counts_cal)],
            "DEV_count_range":[min(counts_dev),max(counts_dev)],
            "DEV_outside_CAL_count_range":sum(n<min(counts_cal) or n>max(counts_cal) for n in counts_dev),
            "Q_direction_chosen_CAL":chosen["feature"],
            "CAL_SSE_uA2":{p:m["CAL_SSE_uA2"] for p,m in models.items()},
            "CAL_count_slope_uA":{p:m["params"][1] for p,m in models.items()},
            "metric":{p:metrics([{"pred":row["pred"][p],"n":row["n"]} for row in records])
                     for p in POLICIES},
            "DEV_records":records}
    totals={}
    for scope in ("ALL_4_COLUMNS","C0_ONLY","C1_C2_C3","SEEN_MASK_FAMILIES","UNSEEN_MASK_FAMILIES"):
        totals[scope]={}
        for p in POLICIES:
            rows=all_rows[p]
            if scope=="C0_ONLY":rows=[r for r in rows if r["col"]==0]
            if scope=="C1_C2_C3":rows=[r for r in rows if r["col"]!=0]
            if scope=="SEEN_MASK_FAMILIES":rows=[r for r in rows if r["seen_area"]]
            if scope=="UNSEEN_MASK_FAMILIES":rows=[r for r in rows if not r["seen_area"]]
            totals[scope][p]=metrics(rows)
    return {"columns":bycol,"totals":totals,
            "note":"144 column-read outcomes from 36 joint masks, not 144 independent chips"}

def selftest():
    A=[[3.,0.,0.],[0.,2.,0.],[0.,0.,1.]]
    assert solve(A,[3.,6.,2.])==[1.,3.,2.]
    data=[]
    for n in (9,10,11):
        for j in (0,1,2):
            z=j/2.0
            data.append({"n":n,"current_uA":100+2*n+3*z,
                         "feature":{"MEAN_ROW":z}})
    model=fit(data,"MEAN_ROW")
    assert abs(model["params"][1]-2)<1e-6
    assert abs(model["params"][2]-3)<1e-6
    assert decode(model,100+2*12+3*0.5,{"MEAN_ROW":0.5})==12
    print("E34_SELFTEST_PASS: CAL-only 256-row linear count/position regression, four-column decoder")
    print("E34_SELFTEST_NO_NEW_SPECTRE_NO_PEX_NO_SIGNED_PLANE_CLAIM")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode",choices=("selftest","run"))
    ap.add_argument("--e30",type=Path,default=E30_PATH)
    ap.add_argument("--e31",type=Path,default=E31_PATH)
    ap.add_argument("--outdir",type=Path,default=Path.home()/"mram_private/E34_1T1")
    args=ap.parse_args()
    selftest()
    if args.mode=="selftest":return
    e30,e31,weights=get_sources(args.e30,args.e31)
    report={"experiment":"E34_FOUR_COLUMN_POSITION_CAL_GENERALIZATION",
        "source_e30_sha256":digest(args.e30),"source_e31_sha256":digest(args.e31),
        "evidence":"actual_GF_transistor_multi_column_NUS_Spectre_plus_assumed_interconnect",
        "electrical_arms":{},"no_PEX":True,"no_physical_ADC":True,
        "no_independent_chips":True,"no_full_W4A8":True,
        "four_columns_NOT_four_signed_bitplanes":True,
        "calibration":"E30 9 CAL masks per column only, no DEV tuning",
        "evaluation":"E31 36 new activation masks x4 columns"}
    for arm in ARMS:
        cal,dev=extract(e30,e31,weights,arm)
        result=evaluate(cal,dev)
        report["electrical_arms"][arm]=result
        print("========== E34",arm,"==========")
        for c,r in result["columns"].items():
            print("E34_COLUMN",c,"CAL_n",r["CAL_count_range"],"DEV_n",r["DEV_count_range"],
                  "DEV_EXTRAPOLATED_n",r["DEV_outside_CAL_count_range"],
                  "Q_CAL",r["Q_direction_chosen_CAL"]," ".join(
                  "{}:{}/36".format(p,r["metric"][p]["wrong"]) for p in POLICIES))
        for region,met in result["totals"].items():
            print("E34_TOTAL",region," ".join("{}:{}/{}".format(
                p,met[p]["wrong"],met[p]["total"]) for p in POLICIES))
    out=args.outdir.expanduser().resolve()
    out.mkdir(parents=True,exist_ok=True)
    dest=out/"E34_RESULTS.json"
    summary=out/"E34_FOR_PROF_FONG.md"
    if dest.exists() or summary.exists():die("Refuse overwrite existing result")
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n", encoding="utf-8")
    lines=["# E34 — Real GF currents: does C0 calibration generalize across all 4 columns?",
           "",
           "**Status:** POSTPROCESSING of NUS actual GF Spectre currents (E30/E31)."
           " BL/SL R assumed, MTJ student static model. No PEX, physical ADC, independent"
           " chip mismatch or neural inference. 36 fresh input masks ×4 columns,"
           " but column readouts are electrically related; no independent-chip BER claim.",
           "",
           "| GF read arm | Global wrong/144 | Mean row wrong/144 | Half-line wrong/144 | CAL-Q wrong/144 |",
           "|---|---:|---:|---:|---:|"]
    for arm,result in report["electrical_arms"].items():
        totals=result["totals"]["ALL_4_COLUMNS"]
        lines.append("| {} | {} | {} | {} | {} |".format(arm,
          totals["GLOBAL_LINEAR"]["wrong"],totals["MEAN_ROW_LINEAR"]["wrong"],
          totals["FAR_HALF_LINEAR"]["wrong"],totals["Q_CAL_SELECTED"]["wrong"]))
    lines+=["",
        "## Interpretation",
        "Four simultaneously read physical/conceptual columns do NOT automatically equal"
        " signed W4 planes. All 4 columns have different resident weights, so this is a"
        " **cross-column calibration generalization** test, not W4 cancellation or DNN"
        " accuracy. If C1-C3 reveal post-Q count failures, first inspect per-column"
        " training count coverage and compare equally simple spatial regressors."
        " Do not claim a failure predictor/recovery novelty until actual 1T1 geometry"
        " and signed bitplane mapping are verified.",
        ""]
    summary.write_text("\n".join(lines), encoding="utf-8")
    print("E34_RESULT_JSON",dest)
    print("E34_PROF_SUMMARY",summary)
    print("E34_FOUR_COLUMNS_NOT_SIGNED_PLANES_NO_PEX")
if __name__=="__main__":main()
