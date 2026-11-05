#!/usr/bin/env python3
"""E33: ADC-precision/failure-boundary test on actual NUS E30/E31 GF DC currents.

No new Spectre; reads private GF-NFET+student-static-MTJ 256x4 current vectors.
All BL/SL parasitics remain ASSUMED. A mathematical uniform ADC is applied
to pre-existing true current values, NOT a simulated actual GF ADC circuit.

The converter span is fixed ONCE using ONLY E30 ideal-wire CAL n=11/12/13:
extrapolate a constant ideal P/AP count step to n=0 and n=24, with 10% headroom
on EACH side. This is an explicit DESIGN ASSUMPTION, not measured fullscale.
Use the SAME fixed current span for all read arms and all ADC resolutions.

For EACH bit depth, re-fit simple decoders using ONLY the NINE E30 CAL currents
after the SAME ADC quantization; evaluate untouched 36 E31 DEV input masks.
Strong continuous known-input baselines: position mean, half-line occupancy,
and suffix/prefix Q (orientation chosen on CAL by fit residual only).
No actual ADC noise, jitter, timing, area/energy or MTJ variation. A wrong
count here is a constructed read+ideal-ADC failure, NOT a physical MRAM BER.
Python 3.6 stdlib only. Does not export foundry decks or private raw data.
"""
from __future__ import print_function
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

SOURCE_E30_SHA="f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52"
DEFAULT_E30=Path.home()/"mram_private/E30_1T1/E30_256x4_20261105T031022Z_866/E30_RESULTS.json"
DEFAULT_E31=Path.home()/"mram_private/E31_1T1/E31_256x4_20261105T033721Z_2792/E31_RESULTS.json"
ARMS=("ideal_independent","assumed_BL_independent","assumed_BL_shared_SL")
BITS=(4,5,6,7,8,9,10,12)
COUNTS=(11,12,13)
FEATURES=("Q_SUFFIX","Q_PREFIX","MEAN_ROW","FAR_HALF_FRACTION")
POLICIES=("GLOBAL","AREA_OFFSET","CONTINUOUS_MEAN_ROW","CONTINUOUS_HALF_FRACTION","CONTINUOUS_Q_CAL")
AREAS_SEEN=("ROW_LO","ROW_HI","DISTRIBUTED")

def fail(s):
    raise SystemExit("E33_BLOCKED: "+str(s))

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1048576),b""):h.update(c)
    return h.hexdigest()

def numeric(x):
    if not isinstance(x,(int,float)) or not math.isfinite(x):
        fail("Nonfinite/invalid GF current")
    return float(x)

def adc(i_uA,bits,low,high):
    if not isinstance(bits,int) or bits<2 or bits>16 or not high>low:
        raise ValueError("Bad ideal ADC configuration")
    levels=1<<bits
    x=numeric(i_uA)
    clipped=(x<low or x>=high)
    index=max(0,min(levels-1,int(math.floor((x-low)*levels/(high-low)))))
    reconstructed=low+(index+0.5)*(high-low)/levels
    return reconstructed,index,clipped

def features(selected):
    from e30p_offline_strong_baselines import qscore
    if len(selected)!=24 or len(set(selected))!=24 or min(selected)<0 or max(selected)>=256:
        fail("Invalid 24-row mask")
    return {
        "Q_SUFFIX":qscore(selected,256,"suffix"),
        "Q_PREFIX":qscore(selected,256,"prefix"),
        "MEAN_ROW":sum(selected)/(24.0*255.0),
        "FAR_HALF_FRACTION":sum(int(v>=128) for v in selected)/24.0,
    }

def get_e30(path):
    if not path.is_file():fail("E30 source missing")
    if digest(path)!=SOURCE_E30_SHA:fail("E30 original frozen source SHA changed")
    data=json.loads(path.read_text())
    if data.get("state")!="FINISHED" or data.get("rows")!=256 or data.get("columns")!=4:
        fail("Source is not finished 256x4 E30")
    if len(data.get("scenarios",[]))!=18:fail("Original E30 9 CAL +9 DEV missing")
    if set(ARMS)-set(data["results"]):fail("Missing E30 arm")
    return data

def get_e31(path,e30):
    if not path.is_file():fail("E31 source missing")
    data=json.loads(path.read_text())
    if data.get("status")!="FINISHED" or data.get("source_e30_sha256")!=SOURCE_E30_SHA:
        fail("E31 not completed with exactly frozen E30")
    if not data.get("resident_weights_identical") or data.get("CAL_recalibrated_on_E31") is not False:
        fail("Resident weights or CAL freeze not confirmed")
    if (len(data.get("new_DEV",[]))!=36 or
        len({tuple(x["selected_rows"]) for x in data["new_DEV"]})!=36):
        fail("E31 must have 36 distinct new DEV masks")
    seen={(tuple(x["selected_rows"])) for x in e30["scenarios"]}
    if any(tuple(x["selected_rows"]) in seen for x in data["new_DEV"]):
        fail("E31 mask leaked E30 CAL or DEV")
    if set(ARMS)-set(data["results"]):fail("Missing E31 read arm")
    return data

def span_from_ideal_cal(e30):
    """Freeze ADC fullscale from ideal CAL current centers only, no DEV labels."""
    from e30p_offline_strong_baselines import rows_for_arm
    orig=rows_for_arm(e30,"ideal_independent")
    cal=[r for r in orig if r["split"]=="CAL"]
    means={n:statistics.mean(r["current_uA"] for r in cal if r["n"]==n)
           for n in COUNTS}
    slope=(means[13]-means[11])/2.0
    if slope<=0 or not all(math.isfinite(x) for x in means.values()):
        fail("Invalid nominal count current levels for ADC range")
    lo=means[12]-12*slope
    hi=means[12]+12*slope
    guard=0.1*(hi-lo)
    return lo-guard,hi+guard,{"count_step_uA":slope,"ideal_cal_centres_uA":means,
                              "rule":"extrapolate n0/n24 from n11..13 ideal CAL; 10% guard at each end"}

def observations_e30(e30,arm):
    from e30p_offline_strong_baselines import rows_for_arm
    xs=rows_for_arm(e30,arm)
    out=[]
    for x in xs:
        if x["split"]!="CAL":continue
        mask=next(s["selected_rows"] for s in e30["scenarios"] if str(s["scenario_id"])==x["scenario_id"])
        out.append({"area":x["area"],"n":x["n"],"current_uA":x["current_uA"],
                    "features":features(mask),"split":"CAL"})
    if len(out)!=9:fail("Expected exactly 9 E30 CAL currents")
    return out

def observations_e31(e31,arm):
    vectors=e31["results"][arm]["currents_by_scenario_A"]
    data=[]
    for s in e31["new_DEV"]:
        sid=str(s["scenario_id"])
        if sid not in vectors or len(vectors[sid])!=4:
            fail("Missing 4 simultaneously solved column currents for E31 scenario "+sid)
        current=numeric(vectors[sid][0])*1e6
        data.append({"scenario_id":sid,"area":s["spatial_group"],"n":int(s["C0_true_n"]),
                     "current_uA":current,"features":features(s["selected_rows"]),
                     "split":"DEV","seen":s["spatial_group"] in AREAS_SEEN})
    if len(data)!=36 or sum(x["seen"] for x in data)!=18:
        fail("E31 needs 18 familiar +18 unfamiliar spatial families")
    if set(x["n"] for x in data)!=set(COUNTS):
        fail("E31 count classes unexpected")
    return data

def fit(cal):
    # All data are quantized CAL measurements, never DEV true counts.
    mean={n:statistics.mean(x["adc_uA"] for x in cal if x["n"]==n)
          for n in COUNTS}
    offsets={a:statistics.mean(x["adc_uA"]-mean[x["n"]] for x in cal if x["area"]==a)
             for a in AREAS_SEEN}
    per_feature={}
    for feature in FEATURES:
        f_mean={n:statistics.mean(x["features"][feature] for x in cal if x["n"]==n)
                for n in COUNTS}
        numerator=sum((x["features"][feature]-f_mean[x["n"]])*
                      (x["adc_uA"]-mean[x["n"]]) for x in cal)
        denominator=sum((x["features"][feature]-f_mean[x["n"]])**2 for x in cal)
        slope=numerator/denominator if denominator>1e-22 else 0.0
        intercept={n:mean[n]-slope*f_mean[n] for n in COUNTS}
        sse=sum((x["adc_uA"]-intercept[x["n"]]-slope*x["features"][feature])**2
                for x in cal)
        per_feature[feature]={"slope":slope,"intercept":intercept,"CAL_SSE":sse}
    # Compare two Q orientations ONLY using original E30 CAL.
    q_name=min(("Q_SUFFIX","Q_PREFIX"),
               key=lambda k:(per_feature[k]["CAL_SSE"],k))
    return mean,offsets,per_feature,q_name

def decode(current,centres):
    return min(COUNTS,key=lambda n:(abs(current-centres[n]),n))

def evaluate(cal_raw,dev_raw,bits,low,high):
    cal=[]
    dev=[]
    for src,dest in ((cal_raw,cal),(dev_raw,dev)):
        for row in src:
            converted,idx,clipped=adc(row["current_uA"],bits,low,high)
            entry=dict(row)
            entry["adc_uA"]=converted
            entry["adc_code"]=idx
            entry["clipped"]=clipped
            dest.append(entry)
    mean,offsets,features_fit,q_name=fit(cal)
    details=[]
    for row in dev:
        a=row["area"]; y=row["adc_uA"]
        predictions={}
        refs={
            "GLOBAL":mean,
            "AREA_OFFSET":{n:mean[n]+offsets[a] if a in offsets else mean[n] for n in COUNTS}
        }
        for feat,pol in (("MEAN_ROW","CONTINUOUS_MEAN_ROW"),
                         ("FAR_HALF_FRACTION","CONTINUOUS_HALF_FRACTION"),
                         (q_name,"CONTINUOUS_Q_CAL")):
            rule=features_fit[feat]
            refs[pol]={n:rule["intercept"][n]+rule["slope"]*row["features"][feat]
                       for n in COUNTS}
        for pol in POLICIES:predictions[pol]=decode(y,refs[pol])
        margin=abs(row["current_uA"]-y)  # posthoc ADC quantization error, never runtime feature
        details.append({"area":a,"n_true":row["n"],"seen":row["seen"],"adc_code":row["adc_code"],
                        "clipped":row["clipped"],"quantization_abs_error_uA":margin,
                        "prediction":predictions})
    metric={}
    for group in ("SEEN","UNSEEN","ALL"):
        subset=[d for d in details if group=="ALL" or d["seen"]==(group=="SEEN")]
        metric[group]={}
        for pol in POLICIES:
            errors=[d["prediction"][pol]-d["n_true"] for d in subset]
            metric[group][pol]={"wrong":sum(x!=0 for x in errors),
                                "total":len(errors),
                                "MAE":sum(abs(x) for x in errors)/len(errors)}
    cal_codes={str(n):sorted({x["adc_code"] for x in cal if x["n"]==n}) for n in COUNTS}
    return {"bit_depth":bits,"LSB_uA":(high-low)/(1<<bits),
            "CAL_Q_orientation":q_name,
            "CAL_Q_SSE_uA2":features_fit[q_name]["CAL_SSE"],
            "CAL_feature_SSE_uA2":{f:v["CAL_SSE"] for f,v in features_fit.items()},
            "CAL_ADC_codes_by_count":cal_codes,
            "CAL_clipped_count":sum(x["clipped"] for x in cal),
            "DEV_clipped_count":sum(x["clipped"] for x in dev),
            "DEV_max_quantization_abs_error_uA":max(x["quantization_abs_error_uA"] for x in details),
            "metric":metric,"DEV_detail":details}

def selftest():
    lo,hi=0.,16.
    assert adc(0.,4,lo,hi)==(.5,0,False)
    assert adc(1.,4,lo,hi)==(1.5,1,False)
    assert adc(-3.,4,lo,hi)==(.5,0,True)
    assert adc(16.,4,lo,hi)==(15.5,15,True)
    f=features(list(range(24)))
    assert all(math.isfinite(v) for v in f.values())
    z=[{"n":n,"area":a,"adc_uA":float(100+n+(ord(a[0])%4)),"features":{
        "Q_SUFFIX":float(i),"Q_PREFIX":float(8-i),
        "MEAN_ROW":float(i)/10,"FAR_HALF_FRACTION":float(i%3)/3}}
        for i,(n,a) in enumerate((n,a) for n in COUNTS for a in AREAS_SEEN)]
    x=fit(z)
    assert len(x[0])==3 and x[3] in ("Q_SUFFIX","Q_PREFIX")
    print("E33_SELFTEST_PASS: fixed ideal ADC, CAL-only feature regressions and decoder")
    print("E33_SELFTEST_NO_GF_PEX_NO_ADC_CIRCUIT")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("selftest","run"))
    p.add_argument("--e30",type=Path,default=DEFAULT_E30)
    p.add_argument("--e31",type=Path,default=DEFAULT_E31)
    p.add_argument("--outdir",type=Path,default=Path.home()/"mram_private/E33_1T1")
    args=p.parse_args()
    selftest()
    if args.mode=="selftest":return
    e30=get_e30(args.e30);e31=get_e31(args.e31,e30)
    low,high,rationale=span_from_ideal_cal(e30)
    report={"experiment":"E33_ADC_FAILURE_BOUNDARY_REAL_GF_CURRENTS",
        "evidence_level":"GF_compact_NFET_static_MTJ_real_Spectre_currents_plus_ASSUMED_ideal_ADC",
        "source_e30_sha256":digest(args.e30),"source_e31_sha256":digest(args.e31),
        "layout_PEX":False,"physical_ADC":False,"independent_chip":False,
        "full_W4A8_inference":False,"calibration_data":"E30 original 9 CAL masks only",
        "evaluation_data":"E31 36 fresh DEV masks only",
        "assumed_parasitics":"0.25ohm per BL segment, 0.25ohm shared SL; not extracted",
        "uniform_adc_range_uA":{"low":low,"high":high,"rationale":rationale},
        "ADC_bits":list(BITS),"results":{}}
    for arm in ARMS:
        cal=observations_e30(e30,arm)
        dev=observations_e31(e31,arm)
        report["results"][arm]={}
        for bits in BITS:
            summary=evaluate(cal,dev,bits,low,high)
            report["results"][arm][str(bits)]=summary
            errors=summary["metric"]["ALL"]
            print("E33_ADC",arm,"BITS",bits,"LSB_uA",round(summary["LSB_uA"],6),
                 "CAL_Q",summary["CAL_Q_orientation"],
                 "DEV_CLIPPED",summary["DEV_clipped_count"],
                 "GLOBAL",errors["GLOBAL"]["wrong"],"/36",
                 "Q",errors["CONTINUOUS_Q_CAL"]["wrong"],"/36",
                 "MEAN_ROW",errors["CONTINUOUS_MEAN_ROW"]["wrong"],"/36",
                 "FAR_HALF",errors["CONTINUOUS_HALF_FRACTION"]["wrong"],"/36",flush=True)
    out=args.outdir.expanduser().resolve()
    out.mkdir(parents=True,exist_ok=True)
    path=out/"E33_ADC_SWEEP.json"
    if path.exists():fail("Refusing overwrite "+str(path))
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    md=out/"E33_FOR_PROF_FONG.md"
    table=["# E33 — ADC precision vs calibrated 256-row read errors",
           "",
           "**Evidence:** Actual NUS GF access-transistor current vectors from E30/E31;"
           " static student MTJ; ASSUMED BL/SL R; POSTPROCESSED mathematical ideal ADC."
           " No actual ADC circuit, PEX, mismatch, neural inference, or new Spectre.",
           "",
           "**ADC design:** one fixed fullscale derived from E30 ideal-wire CAL n11/12/13 only,",
           "linear extrapolation to n0/24 with 10% current-span guard band each end.",
           " This is a declared hypothetical converter, not a validated physical ADC.",
           "",
           "ADC fixed current fullscale: [{:.6f}, {:.6f}] µA.".format(low,high),
           "",
           "## Main coupled read arm: assumed_BL_shared_SL",
           "",
           "| ADC bits | LSB (µA) | Global wrong /36 | Mean-row wrong /36 | Half-row wrong /36 | Q wrong /36 | ADC clips /36 |",
           "|---:|---:|---:|---:|---:|---:|---:|"]
    for b in BITS:
        r=report["results"]["assumed_BL_shared_SL"][str(b)]
        m=r["metric"]["ALL"]
        table.append("| {} | {:.4f} | {} | {} | {} | {} | {} |".format(
            b,r["LSB_uA"],m["GLOBAL"]["wrong"],m["CONTINUOUS_MEAN_ROW"]["wrong"],
            m["CONTINUOUS_HALF_FRACTION"]["wrong"],m["CONTINUOUS_Q_CAL"]["wrong"],
            r["DEV_clipped_count"]))
    table+=["","## Interpretation gate",
       "If Q remains good at sufficiently fine ADC precision, the ideal-wire"
       " and assumed-parasitic nominal model still does not justify costly N2"
       " digital replacement. If low-precision quantization produces residual"
       " failures, compare continuously calibrated mean-row/near-far baselines"
       " before claiming novelty. Quantization-induced failure is a *mathematical"
       " ADC-model* outcome until actual converter span/noise/timing and physical"
       " 1T1 wire PEX are established.",
       "",
       "Sources are private on NUS, and this summary contains NO licensed model"
       " or netlist content.",
       ""]
    md.write_text("\n".join(table))
    print("E33_FIXED_ADC_FULLSCALE_uA",low,high)
    print("E33_OUTPUT_JSON",path)
    print("E33_PROF_BRIEF",md)
    print("E33_NO_NEW_SPECTRE_NO_PEX_NO_PHYSICAL_ADC_NO_INFERENCE")
if __name__=="__main__":main()
