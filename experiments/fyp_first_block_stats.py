#!/usr/bin/env python3
"""Locked joint-registry and paired bootstrap-t analysis; first block is descriptive."""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape
import numpy as np

CORE_CANDIDATES=("fp5","fp6","int5","int6","int7","int8")
FAMILIES=("ring","torus")
CORE_REGISTRY=tuple((fam, f"{left}-{right}") for fam in FAMILIES for left,right in (
    ("fp6","int6"),("fp5","int6"),("fp6","int7"),
    *((name,"ref64") for name in CORE_CANDIDATES)))
DEVICE_REGISTRY=tuple((fam,kind) for fam in FAMILIES for kind in
    ("selected_fp-selected_int","selected_fp-ref64","selected_int-ref64"))
CORE_TAIL_Q=0.04/(2*18)
DEVICE_TAIL_Q=0.01/(2*6)
RESAMPLES=500_000


def paired_t_interval(values, *, q=0.025, resamples=RESAMPLES, seed=20261120, batch=4096):
    """Paired bootstrap-t bounds, NumPy linear sample quantile, NaNs unresolved."""
    a=np.asarray(values,dtype=np.float64)
    if a.ndim!=1 or a.size<2 or not np.all(np.isfinite(a)) or not (0<q<0.5):
        raise ValueError("invalid paired vector")
    n=a.size
    mu=float(a.mean())
    if np.max(a)==np.min(a):
        return mu,mu,mu
    se=float(np.std(a,ddof=1)/np.sqrt(n))
    if not math.isfinite(se) or se<=0:
        return mu,float("nan"),float("nan")
    rng=np.random.default_rng(seed)
    tvalues=np.empty(resamples,dtype=np.float64)
    for start in range(0,resamples,batch):
        count=min(batch,resamples-start)
        x=a[rng.integers(n,size=(count,n))]
        means=np.mean(x,axis=1)
        sds=np.std(x,axis=1,ddof=1)/np.sqrt(n)
        if np.any(sds<=0) or not np.all(np.isfinite(sds)):
            return mu,float("nan"),float("nan")
        tvalues[start:start+count]=(means-mu)/sds
    lo=mu-float(np.quantile(tvalues,1-q,method="linear"))*se
    hi=mu-float(np.quantile(tvalues,q,method="linear"))*se
    return mu,lo,hi


def claims(mu,lo,hi,tol=0.5):
    if not all(math.isfinite(v) for v in (mu,lo,hi)):
        return {"status":"UNRESOLVED_STUDENTIZATION"}
    # Multiple claims are not mutually exclusive: e.g. superiority and NI.
    return {"statistical_superiority":hi<0,
            "statistical_inferiority":lo>0,
            "estimated_benefit_gt_0p5pp":mu < -tol,
            "true_benefit_gt_0p5pp":hi < -tol,
            "non_inferior":hi < tol,
            "practically_equivalent":lo > -tol and hi < tol,
            "penalty_exceeds_tolerance":lo > tol,
            "unresolved":not (hi < tol or lo > tol),
            "noninferiority_unresolved":not (hi < tol or lo > tol)}


def write_csv(path,rows):
    if not rows:
        raise ValueError("empty CSV")
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)


def svg_quality(rows,out):
    # All six paired point estimates, whiskers are ordinary 95% bootstrap-t.
    W,H=1120,490
    y0,y1=80,405
    plotted=[r for r in rows if r["metric"]=="gap_contrast_pp"]
    ext=max([1.0]+[abs(float(r[key])) for r in plotted for key in ("ci95_low","ci95_high") if math.isfinite(float(r[key]))])
    limit=max(1.0,math.ceil(ext*2)/2)
    def xx(x):return 270+(float(x)+limit)/(2*limit)*790
    def yy(index):return 120+index*50
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           '<rect width="1120" height="490" fill="white"/>',
           '<text x="38" y="39" font-family="Arial" font-size="23" font-weight="bold">FP5 - INT6: original-optimum gap difference</text>',
           '<text x="38" y="63" font-family="Arial" font-size="13" fill="#444">Paired 95% bootstrap-t intervals; negative favours FP5. Two fixed viewed graphs.</text>']
    for value in (-limit,-limit/2,0,limit/2,limit):
        x=xx(value)
        parts.append(f'<line x1="{x:.1f}" y1="82" x2="{x:.1f}" y2="422" stroke="{("#222" if value==0 else "#ddd")}" stroke-width="{(2 if value==0 else 1)}"/>')
        parts.append(f'<text x="{x:.1f}" y="444" font-size="13" text-anchor="middle" font-family="Arial">{value:+.2f}</text>')
    for i,r in enumerate(plotted):
        g=r["graph"].rsplit("_",1)[-1]
        cond={"raw":"raw beta","calibrated":"beta / a","change":"paired change"}[r["condition"]]
        y=yy(i)
        parts.append(f'<text x="38" y="{y+4}" font-family="Arial" font-size="15">{escape(g)} / {cond}</text>')
        x=xx(r["mean"]); low=xx(r["ci95_low"]); high=xx(r["ci95_high"])
        color="#2670a8" if r["condition"]=="raw" else "#d16b32" if r["condition"]=="calibrated" else "#527d55"
        parts.append(f'<line x1="{low:.1f}" y1="{y}" x2="{high:.1f}" y2="{y}" stroke="{color}" stroke-width="3"/>')
        for z in (low,high):
            parts.append(f'<line x1="{z:.1f}" y1="{y-8}" x2="{z:.1f}" y2="{y+8}" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{y}" r="5.5" fill="{color}"/>')
        parts.append(f'<text x="{min(1060,max(270,x+9)):.1f}" y="{y-13}" font-size="12" font-family="Arial">{float(r["mean"]):+.3f}</text>')
    parts+=['<text x="650" y="477" font-size="14" text-anchor="middle" font-family="Arial">Gap contrast (percentage points)</text>','</svg>']
    out.write_text("\n".join(parts)+"\n",encoding="utf-8")


def svg_losses(summary,out):
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560">',
           '<rect width="1200" height="560" fill="white"/>',
           '<text x="40" y="42" font-family="Arial" font-size="23" font-weight="bold">Where the original-optimum gap is lost</text>',
           '<text x="40" y="67" font-family="Arial" font-size="13">Mean trajectory decomposition, 128 paired seeds per graph; each bar sums to returned gap.</text>']
    order=[(g,c,f) for g in ("5555","7777") for c in ("raw","calibrated") for f in ("fp5","int6")]
    lookup={(r["graph"].rsplit("_",1)[-1],r["condition"],r["representation"]):r for r in summary}
    maxv=max(0.1,max(sum(float(lookup[k][p]) for p in ("unreached_pp","selection_pp","tie_pp")) for k in order))*1.12
    colors=("#4573a3","#e0a13c","#a75b65")
    names=("not visited","represented-selection","earliest ties")
    for tick in range(6):
        y=460-350*tick/5
        v=maxv*tick/5
        parts.append(f'<line x1="100" y1="{y}" x2="1160" y2="{y}" stroke="#e0e0e0"/>')
        parts.append(f'<text x="87" y="{y+4}" font-family="Arial" font-size="12" text-anchor="end">{v:.2f}</text>')
    for index,key in enumerate(order):
        row=lookup[key];x=118+index*130
        bottom=460
        for value,color,tag in zip((float(row[k]) for k in ("unreached_pp","selection_pp","tie_pp")),colors,names):
            h=350*value/maxv
            if h < -1e-8:raise ValueError("negative trajectory component")
            parts.append(f'<rect x="{x}" y="{bottom-h:.2f}" width="88" height="{h:.2f}" fill="{color}"/>')
            bottom-=h
        parts.append(f'<text x="{x+44}" y="481" font-family="Arial" font-size="13" text-anchor="middle">{key[0]} {key[1][0].upper()}</text>')
        parts.append(f'<text x="{x+44}" y="500" font-family="Arial" font-size="13" text-anchor="middle">{key[2].upper()}</text>')
    for j,(label,color) in enumerate(zip(names,colors)):
        x=220+260*j
        parts.append(f'<rect x="{x}" y="523" width="17" height="17" fill="{color}"/>')
        parts.append(f'<text x="{x+23}" y="537" font-family="Arial" font-size="13">{label}</text>')
    parts.append('</svg>')
    out.write_text("\n".join(parts)+"\n",encoding="utf-8")


def analyse(out):
    from experiments.fyp_first_block_20261120 import (read_jsonl, GRAPH_INFO, ARMS,
                                                        SEEDS_PER_GRAPH, canonical)
    frozen=json.loads((out/"frozen_settings.json").read_text())
    rows=read_jsonl(out/"records.jsonl")
    fidelity=read_jsonl(out/"fidelity.jsonl")
    if len(rows)!=1280 or len(fidelity)!=2048:
        raise ValueError("incomplete block: no results may be claimed")
    observed={(r["graph"],int(r["seed"]),r["arm"]):r for r in rows}
    if len(observed)!=1280:
        raise ValueError("duplicate run keys")
    byfid={(r["graph"],int(r["seed"]),int(r["attempt"]),r["representation"]):r for r in fidelity}
    if len(byfid)!=2048:
        raise ValueError("duplicate fidelity keys")
    contrasts=[];components=[];qualities=[]; fidelity_summary=[]
    for graph,sha,optimum,base in GRAPH_INFO:
        seeds=list(range(base,base+SEEDS_PER_GRAPH))
        if any((graph,seed,arm) not in observed for seed in seeds for arm,_,_ in ARMS):
            raise ValueError("missing paired arm")
        trials={arm:[observed[(graph,s,arm)] for s in seeds] for arm,_,_ in ARMS}
        for arm,fmt,condition in ARMS:
            one=trials[arm]
            for r in one:
                if r["graph_sha256"]!=sha or r["official_optimum"]!=optimum or r["seed"] not in seeds:
                    raise ValueError("inconsistent immutable source")
                if abs((optimum-r["R"])-((optimum-r["V"])+(r["V"]-r["M"])+(r["M"]-r["R"])))>1e-6:
                    raise ValueError("trajectory identity failed")
                for pt in r["checkpoints"]:
                    if not pt["V"]>=pt["M"]>=pt["R"]:
                        raise ValueError("invalid checkpoint ordering")
            qualities.append({"graph":graph,"arm":arm,"representation":fmt,"condition":condition,
                              "seeds":128,"mean_returned_cut":float(np.mean([r["R"] for r in one])),
                              "mean_gap_pct":float(np.mean([r["gap_pct"] for r in one])),
                              "mean_flips":float(np.mean([r["actual_flips"] for r in one])),
                              "mean_improvements":float(np.mean([r["improvements"] for r in one])),
                              "a":one[0]["source_projection_a"]})
            entry={"graph":graph,"condition":condition,"representation":fmt,"seeds":128}
            for name,value in (("unreached_pp",[100*(optimum-r["V"])/optimum for r in one]),
                               ("selection_pp",[100*(r["V"]-r["M"])/optimum for r in one]),
                               ("tie_pp",[100*(r["M"]-r["R"])/optimum for r in one])):
                entry[name]=float(np.mean(value))
            components.append(entry)
        def gap(row):return float(row["gap_pct"])
        def contrasts_of(a,b):return np.asarray([gap(x)-gap(y) for x,y in zip(trials[a],trials[b])])
        raw=contrasts_of("fp5_raw","int6_raw")
        cal=contrasts_of("fp5_cal","int6_cal")
        for ix,(label,vector) in enumerate((("raw",raw),("calibrated",cal),("change",cal-raw))):
            mu,lo,hi=paired_t_interval(vector,seed=2026112000+100*int(graph[-4:])+ix)
            contrasts.append({"graph":graph,"metric":"gap_contrast_pp","condition":label,
                              "representation":"fp5_minus_int6","n":128,"mean":mu,
                              "ci95_low":lo,"ci95_high":hi,
                              "decision":json.dumps(claims(mu,lo,hi),sort_keys=True)})
        for condition in ("raw","cal"):
            for part,expr in (("unreached",lambda r:optimum-r["V"]),
                              ("selection",lambda r:r["V"]-r["M"]),
                              ("tie",lambda r:r["M"]-r["R"])):
                vector=[100*(expr(a)-expr(b))/optimum for a,b in zip(trials[f"fp5_{condition}"],trials[f"int6_{condition}"])]
                mu,lo,hi=paired_t_interval(vector,seed=2026113000+int(graph[-4:])*10+len(contrasts))
                contrasts.append({"graph":graph,"metric":part+"_difference_pp","condition":condition,
                                  "representation":"fp5_minus_int6","n":128,"mean":mu,
                                  "ci95_low":lo,"ci95_high":hi,
                                  "decision":json.dumps(claims(mu,lo,hi),sort_keys=True)})
        for point in (5000,15000,30000,50000):
            for fmt in ("fp5","int6"):
                chunk=[byfid[(graph,s,point,fmt)] for s in seeds]
                for metric in ("field_rms","logit_rms","probability_mae"):
                    vector=[x[metric] for x in chunk]
                    mu,lo,hi=paired_t_interval(vector,seed=2026120000+int(graph[-4:])*100+point//5000*10+(fmt=="int6")*3+("field_rms","logit_rms","probability_mae").index(metric))
                    fidelity_summary.append({"graph":graph,"attempt":point,"representation":fmt,
                                             "metric":metric,"n":128,"mean":mu,"ci95_low":lo,"ci95_high":hi})
        for point in (5000,15000,30000,50000):
            for metric in ("field_rms","logit_rms","probability_mae"):
                diff=[byfid[(graph,s,point,"fp5")][metric]-byfid[(graph,s,point,"int6")][metric] for s in seeds]
                mu,lo,hi=paired_t_interval(diff,seed=2026130000+int(graph[-4:])*100+point//5000*10+("field_rms","logit_rms","probability_mae").index(metric))
                fidelity_summary.append({"graph":graph,"attempt":point,"representation":"fp5_minus_int6",
                                         "metric":metric,"n":128,"mean":mu,"ci95_low":lo,"ci95_high":hi})
    write_csv(out/"quality_summary.csv",qualities)
    write_csv(out/"paired_contrasts.csv",contrasts)
    write_csv(out/"trajectory_components.csv",components)
    write_csv(out/"common_state_fidelity.csv",fidelity_summary)
    svg_quality(contrasts,out/"quality_calibration.svg")
    svg_losses(components,out/"trajectory_loss.svg")
    key=lambda suffix,condition:next(r for r in contrasts if r["graph"].endswith(suffix) and r["condition"]==condition and r["metric"]=="gap_contrast_pp")
    note=["# First viewed-dense block — results", "", "Scope: two *viewed* official Biq Mac dense instances, 128 paired fresh solver seeds each, ideal sigmoid at gain 1 and offset 0. No MTJ measurements or family-level inference.", "", "| Graph | Raw FP5–INT6 gap (pp), 95% CI | beta/a gap (pp), 95% CI | Paired calibration change (pp), 95% CI |", "| --- | ---: | ---: | ---: |"]
    for suffix in ("5555","7777"):
        values=[key(suffix,c) for c in ("raw","calibrated","change")]
        formatval=lambda r:f'{r["mean"]:+.3f} [{r["ci95_low"]:+.3f}, {r["ci95_high"]:+.3f}]'
        note.append(f'| {suffix} | '+" | ".join(formatval(x) for x in values)+" |")
    note.extend(["", "Negative FP5–INT6 indicates FP5 yielded a smaller original-optimum gap. The calibration interaction is tested *directly*, not inferred from different significance labels.",
                 "", "The trajectory-components and fidelity CSVs explain where mean loss occurs. Components partition each run's gap exactly; they do not independently prove energetic-barrier causality.",
                 "", "Statistical superiority: upper interval < 0; true >0.5pp benefit: upper interval < -0.5; non-inferiority: upper interval < +0.5; equivalence: full interval inside [-0.5,+0.5]. These are descriptive 95% within-graph statements, NOT the later 18-contrast familywise inference.",
                 "", "Next under locked plan: generated independent ring/torus ensemble and official six-anchor ideal study, then selected-candidate assumed offset-bank validation and memory-inclusive architectural comparison. The _6666 anchors remain untouched until the later freeze.",
                 "", "Sources: frozen_settings.json, records.jsonl, fidelity.jsonl. The fixed 1,280-run cap closes this block regardless of sign."])
    (out/"RESULTS.md").write_text("\n".join(note)+"\n",encoding="utf-8")
    complete={"status":"FIRST_VIEWED_DENSE_1280_COMPLETE","total_unique_solver_runs":1280,
              "common_reference_checkpoint_records":2048,"graph_count":2,"source_commit":frozen["source_commit"],
              "bootstrap_resamples":RESAMPLES,"bootstrap_quantile_method":"numpy linear",
              "core_registry_count":len(CORE_REGISTRY),"device_registry_count":len(DEVICE_REGISTRY),
              "core_one_tail_q":CORE_TAIL_Q,"device_one_tail_q":DEVICE_TAIL_Q}
    for filename in ("frozen_settings.json","records.jsonl","fidelity.jsonl","quality_summary.csv",
                     "paired_contrasts.csv","trajectory_components.csv","common_state_fidelity.csv",
                     "quality_calibration.svg","trajectory_loss.svg","RESULTS.md"):
        import hashlib
        complete[filename+"_sha256"]=hashlib.sha256((out/filename).read_bytes()).hexdigest()
    (out/"manifest.json").write_text(json.dumps(complete,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print((out/"RESULTS.md").read_text(),flush=True)
    print("ANALYSIS COMPLETE",out,flush=True)


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("results/fyp_first_block_20261120"))
    a=p.parse_args()
    analyse(a.out)
