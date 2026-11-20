#!/usr/bin/env python3
"""Rebuild thesis diagrams from pinned scientific research-branch archives.

No hardcoded observed results. Requires Python 3.12+, matplotlib and numpy.
Example: python scripts/make_thesis_figures.py
The completed checkpoint is read from immutable committed research-branch JSON.

Reads version-pinned CSV/JSON and one source tar archive from the research
branch, never regenerates scientific trajectories or alters a frozen study.
Generates PDFs and PNG previews. Missing new device data is never fabricated.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
from pathlib import Path
import tarfile
import urllib.request
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

PIN = "bf710c5ece7b7a6435ede73905127abda9be0660"
RAW = "https://raw.githubusercontent.com/Makise-okabe/MRAM_P-bit/" + PIN + "/"
CHECKPOINT_PIN = "6c20537a24711c1fca53092808e38eca8c2bdf61"
CHECKPOINT_RAW = ("https://raw.githubusercontent.com/Makise-okabe/MRAM_P-bit/"
                  + CHECKPOINT_PIN + "/results/fyp_policy_device_20261121/analysis/")
IDEAL = "results/fyp_ideal_20261120/analysis/"
TAIL = "results/fyp_tail_probe_20261121/analysis/"
COLOUR = {"fp": "#2166ac", "int": "#d95f02", "ref": "#6d6e71", "other": "#7c6aa6"}
MARGIN = 0.5


def fetch(path):
    url = RAW + path
    with urllib.request.urlopen(url, timeout=90) as handle:
        return handle.read()


def read_csv(path):
    return list(csv.DictReader(io.StringIO(fetch(path).decode("utf-8"))))


def read_json(path):
    return json.loads(fetch(path))


def checkpoint_json(name):
    with urllib.request.urlopen(CHECKPOINT_RAW + name, timeout=90) as handle:
        return json.loads(handle.read())


def f(row, key):
    return float(row[key])


def colour(name):
    return COLOUR["fp" if name.startswith("fp") else "int" if name.startswith("int") else "ref" if name == "ref64" else "other"]


def save(fig, out, name):
    fig.savefig(out / (name + ".pdf"), bbox_inches="tight")
    fig.savefig(out / (name + ".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def tidy(ax, xgrid=False):
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="x" if xgrid else "y", alpha=.18)


def draw_pipeline(out):
    fig, ax = plt.subplots(figsize=(12.4, 3.4))
    ax.set(xlim=(0, 14), ylim=(0, 4))
    ax.axis("off")
    nodes = [
        ("Original graph", "weighted cut, source J"),
        ("Encode coupling", "FP / INT + scale"),
        ("Local field", "H = J-hat x s"),
        ("Stochastic p-bit", "sigmoid(2 beta g H + delta)"),
        ("Output policy", "earliest min energy / top 16"),
        ("Original score", "weighted Max-Cut C_w(s)"),
    ]
    for i, (title, desc) in enumerate(nodes):
        x = .12 + i * 2.31
        color = COLOUR["int" if i == 3 else "fp" if i in (1, 2) else "ref"]
        ax.add_patch(FancyBboxPatch((x, 1.38), 2.05, 1.28,
                                    boxstyle="round,pad=0.08", facecolor="white",
                                    edgecolor=color, lw=1.5))
        ax.text(x+1.025, 2.23, title, ha="center", va="center", weight="bold", fontsize=9)
        ax.text(x+1.025, 1.78, desc, ha="center", va="center", fontsize=7.5)
        if i < len(nodes)-1:
            ax.add_patch(FancyArrowPatch((x+2.13, 2.01), (x+2.25, 2.01),
                                         arrowstyle="-|>", mutation_scale=11, color="#6d6e71"))
    ax.text(6.9, .82, "SEARCH: trajectories can reach different original-weight cuts", ha="center", fontsize=9)
    ax.text(6.9, .43, "SELECTION: the represented-energy output rule can reject the best visited cut",
            ha="center", fontsize=9, color=COLOUR["int"])
    save(fig, out, "F01_pipeline")


def source_graphs():
    data = fetch("data/fyp_locked_20261120/sources.tar.gz")
    result = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for fam in ("ring", "torus"):
            blob = archive.extractfile(f"{fam}/000.rudy").read().decode("ascii")
            lines = blob.splitlines()
            n, m = (int(x) for x in lines[0].split())
            if n != 100 or len(lines) != m + 1:
                raise ValueError("Pinned Rudy source graph dimensions changed")
            result[fam] = [(int(i)-1, int(j)-1, int(w))
                           for i, j, w in (line.split() for line in lines[1:])]
    return result


def weights_distribution(out, graphs, quality):
    fig, axes = plt.subplots(1, 2, figsize=(11.3, 4.5), sharey=False)
    for ax, fam in zip(axes, ("ring", "torus")):
        weights = np.array([abs(w) for _, _, w in graphs[fam] if w], dtype=float)
        ax.hist(np.log10(weights), bins=32, color=COLOUR["ref"], alpha=.75)
        ax.set(xlabel="log10(|source weight|)", ylabel="Number of original edges",
               title=f"{fam.capitalize()} (source graph 000)")
        tidy(ax)
        means = [r for r in quality if r["kind"] == "generated" and r["family"] == fam and
                 r["graph"] == f"{fam}_000" and r["representation"] in ("fp5","fp6","int6","int7")]
        notes = "; ".join(f'{r["representation"].upper()}: {int(r["nonzero_count"])} kept' for r in means)
        ax.text(.02, .97, notes, transform=ax.transAxes, va="top", fontsize=7.5,
                bbox={"facecolor":"white","alpha":.8, "edgecolor":"none"})
    fig.suptitle("The ring contains a far broader weak-weight tail; format support depends on the codebook",
                 fontsize=11)
    save(fig, out, "F02_weight_histograms")


def ring_distance(out, graphs):
    edges = graphs["ring"]
    n = 100
    distance = np.array([(n/np.pi)*np.sin(np.pi*abs(i-j)/n) for i,j,_ in edges])
    weights = np.array([abs(w) for _,_,w in edges])
    fig, ax = plt.subplots(figsize=(10, 4.8))
    keep = weights > 0
    ax.scatter(distance[keep], weights[keep], s=6, alpha=.4, color=COLOUR["fp"])
    ax.set_yscale("log")
    ax.set(xlabel="Periodic ring distance r_ij (vertices)",
           ylabel="Original |w_ij| (arbitrary integer units)",
           title="Long-range couplings form the weak tail in the ring family")
    tidy(ax)
    save(fig, out, "F03_ring_distance")


def forest(out, core):
    selected = [r for r in core if r["contrast"].endswith("-ref64")]
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5), sharex=True)
    for ax, fam in zip(axes, ("ring", "torus")):
        rows = sorted([r for r in selected if r["family"] == fam],
                      key=lambda x: (int(x["contrast"][2]) if x["contrast"].startswith("fp") else int(x["contrast"][3]),x["contrast"]))
        for i, row in enumerate(rows):
            if row["interval_status"] != "OK":
                continue
            center, lo, hi = (f(row, k) for k in ("mean","low","high"))
            ax.plot([lo, hi], [i, i], lw=2, color=colour(row["contrast"]))
            ax.plot(center, i, marker="o", color=colour(row["contrast"]))
            ax.text(hi + .03, i, row["qualification"], va="center", fontsize=8)
        ax.axvspan(-MARGIN, MARGIN, color="#c2c2c2", alpha=.18)
        ax.axvline(MARGIN, color="#777", ls="--", lw=1)
        ax.axvline(0, color="#555", lw=.8)
        ax.set_yticks(range(len(rows)), [x["contrast"].split("-")[0].upper() for x in rows])
        ax.invert_yaxis()
        ax.set(xlabel="Additional loss versus FP64 (percentage points)",
               title=fam.capitalize())
        tidy(ax, xgrid=True)
    fig.suptitle("Ideal family-mean certification: simultaneous whole-graph intervals", fontsize=11)
    save(fig, out, "F04_ideal_forest")


def width_ladder(out, selected, stage_a):
    original = {fam: selected[fam]["qualification"] for fam in ("ring","torus")}
    buffer = stage_a["certification"]
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4), squeeze=False)
    formats = ["fp5","fp6","int5","int6","int7","int8"]
    for ax, stage in zip(axes[0], ("Original earliest-energy output", "Host top-16 rescoring")):
        for i, fam in enumerate(("ring", "torus")):
            labels = (original[fam] if stage.startswith("Original")
                      else buffer[fam]["0.5"]["formats"])
            for j, fmt in enumerate(formats):
                label = labels.get(fmt, "UNRESOLVED")
                color = "#d9ece5" if label == "PASS" else "#f9d7d0" if label == "FAIL" else "#f2ebcc"
                ax.add_patch(plt.Rectangle((j-.48, 1-i-.42), .96, .84, facecolor=color, edgecolor="white"))
                ax.text(j, 1-i, label, va="center", ha="center", fontsize=7.2)
        ax.set_xticks(range(6), [x.upper() for x in formats])
        ax.set_yticks([1,0],["Ring","Torus"])
        ax.set(xlim=(-.5, 5.5), ylim=(-.5,1.5), title=stage)
        ax.tick_params(length=0)
        for spine in ax.spines.values(): spine.set_visible(False)
    fig.suptitle("A passive output buffer changes the certified ring width ladder (+0.5 pp)", fontsize=11)
    save(fig, out, "F05_width_ladder")


def mechanisms(out, family_mechanisms):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), sharey=True)
    formats = ["int5","fp5","int6","fp6","int7","int8"]
    for ax, fam in zip(axes, ("ring","torus")):
        rows = {x["representation"]:x for x in family_mechanisms if x["family"]==fam}
        for j, fmt in enumerate(formats):
            if fmt not in rows: continue
            a, z = f(rows[fmt],"mean_A_pp"), f(rows[fmt],"mean_Rz_pp")
            ax.bar(j, a, color=colour(fmt), alpha=.85)
            ax.bar(j, z, bottom=a, color=colour(fmt), alpha=.33, hatch="//", edgecolor="white")
        ax.set_xticks(range(len(formats)),[x.upper() for x in formats],rotation=30)
        ax.set(title=fam.capitalize(), ylabel="Extra loss vs matched FP64 (pp)")
        tidy(ax)
    fig.suptitle("Decomposed penalty: solid search/access + hatched output-selection", fontsize=11)
    save(fig, out, "F06_search_selection")


def retained_vs_loss(out, quality):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    markers = {"fp5": "o", "fp6": "^", "int5": "s",
               "int6": "D", "int7": "v", "int8": "P"}
    for ax, fam in zip(axes, ("ring", "torus")):
        for fmt in ("fp5", "fp6", "int5", "int6", "int7", "int8"):
            rows = [r for r in quality if r["kind"] == "generated"
                    and r["family"] == fam and r["representation"] == fmt]
            if not rows:
                continue
            x = np.mean([f(r, "nonzero_count") for r in rows])
            y = np.mean([f(r, "mean_Rz_pp") for r in rows])
            ax.scatter(x, y, s=75, marker=markers[fmt], color=colour(fmt),
                       label=fmt.upper(), edgecolors="white", zorder=3)
        ax.set(title=fam.capitalize(), xlabel="Mean retained coefficients / graph",
               ylabel="Mean selection loss Rz (pp)")
        ax.legend(ncol=2, frameon=False, loc="upper right", fontsize=8)
        tidy(ax)
    fig.suptitle("Retained coefficient count alone does not determine selection loss",
                 fontsize=11)
    fig.text(.5, -.025, "Descriptive format means; not a registered causal contrast.",
             ha="center", fontsize=9)
    save(fig, out, "F07_retained_vs_selection")


def tail_intervention(out, graph_summary):
    arms = ["fp6","fp6_mask","int6_tail","int6"]
    ring = [r for r in graph_summary if r["family"]=="ring" and r["representation"] in arms]
    fig, axes = plt.subplots(1,3,figsize=(13.7,4.8))
    for ax, metric, label in zip(axes,
                                ("Rz_pp","extra_pp","minimum_distinct_states"),
                                ("Selection Rz (pp)","Total extra loss (pp)","Distinct minimum-energy states")):
        for i, arm in enumerate(arms):
            vals = np.asarray([f(r,metric) for r in ring if r["representation"]==arm])
            if len(vals) != 24:
                raise ValueError("Weak-tail graph data incomplete")
            mean = vals.mean()
            lower = 1.96 * vals.std(ddof=1)/np.sqrt(len(vals))
            ax.bar(i,mean,color=colour(arm),alpha=.76)
            ax.errorbar([i],[mean],yerr=[[lower],[lower]],fmt="none",color="#222",capsize=3)
        ax.set_xticks(range(len(arms)),[a.upper().replace("_","\n") for a in arms],fontsize=8)
        ax.set(ylabel=label)
        tidy(ax)
    fig.suptitle("Registered tail intervention changes selection; other panels descriptive (95% normal-SE bars)",
                 fontsize=11)
    save(fig, out, "F08_weak_tail")


def output_policy(out, graph_summary):
    ring = [r for r in graph_summary if r["family"]=="ring"]
    fig, ax = plt.subplots(figsize=(8.5,4.7))
    for i,arm in enumerate(("fp6","int6")):
        rows = [r for r in ring if r["representation"]==arm]
        live = np.mean([f(r,"extra_pp") for r in rows])
        buffered = np.mean([f(r,"buffer_extra_pp") for r in rows])
        ax.bar(i-.19,live,width=.36,color=colour(arm),label="Earliest represented minimum" if i==0 else None)
        ax.bar(i+.19,buffered,width=.36,color=colour(arm),alpha=.42,
               label="Original-J top-16 host rescore" if i==0 else None)
    ax.set_xticks([0,1],["FP6","INT6"])
    ax.set(ylabel="Extra original-weight loss vs FP64 (pp)",
           title="Top-16 rescoring reduces selection loss, not search deficiency")
    ax.legend(frameon=False)
    tidy(ax)
    save(fig,out,"F09_output_policy")


def heterogeneity(out, graph_contrasts, anchor_contrasts):
    fig, axes = plt.subplots(1,2,figsize=(12,4.8),sharey=True)
    for ax, key in zip(axes,("fp6-int6","fp5-int6")):
        values = sorted([f(r,"mean") for r in graph_contrasts
                         if r["family"]=="ring" and r["contrast"]==key])
        if len(values)!=72: raise ValueError("Need 72 ring contrasts")
        ax.scatter(range(len(values)),values,s=14,color=colour(key),alpha=.75)
        ax.axhline(0,lw=.8,color="#555")
        ax.axhspan(-MARGIN,MARGIN,color="#aaa",alpha=.13)
        anchors = [r for r in anchor_contrasts if r["family"]=="ring" and r["contrast"]==key]
        for j,r in enumerate(anchors):
            ax.axhline(f(r,"mean"),ls="--",lw=1.1,color="#b34444" if "6666" in r["graph"] else "#888")
            if "6666" in r["graph"]:
                ax.text(3,f(r,"mean"),"_6666",color="#b34444",va="bottom")
        ax.set(xlabel="Generated ring graph (ordered by mean contrast)",ylabel="FP - INT added loss (pp)",
               title=key.upper())
        tidy(ax)
    fig.suptitle("Family means conceal large instance-to-instance differences",fontsize=11)
    save(fig,out,"F10_instance_heterogeneity")


def evidence_map(out):
    boxes=[("Historical pilots","descriptive"),
           ("Ideal 144-graph study","registered widths"),
           ("Weak-tail 2x2","registered mechanism"),
           ("Output buffer","Stage A registered"),
           ("Persistent offsets","Stage B registered"),
           ("Memory + hardware","pending approval")]
    fig,ax=plt.subplots(figsize=(13,2.9))
    ax.set(xlim=(0,15),ylim=(0,3))
    ax.axis("off")
    for i,(title,scope) in enumerate(boxes):
        x=.15+i*2.49
        ax.add_patch(FancyBboxPatch((x,.95),2.16,1.25,boxstyle="round,pad=0.06",
                 facecolor="white",edgecolor=COLOUR["ref" if i==5 else "fp"],lw=1.2))
        ax.text(x+1.08,1.75,title,ha="center",fontsize=8.4,weight="bold")
        ax.text(x+1.08,1.3,scope,ha="center",fontsize=7.8)
        if i<5:
            ax.add_patch(FancyArrowPatch((x+2.22,1.58),(x+2.43,1.58),
                                 arrowstyle="-|>",mutation_scale=12,color="#999"))
    save(fig,out,"F12_evidence_map")


def device_plot(out, records):
    fig, axes = plt.subplots(2, 2, figsize=(11.1, 8.0))
    for col, fam in enumerate(("ring", "torus")):
        group = [r for r in records if r["family"] == fam]
        formats = ("fp5","int6","fp6") if fam=="ring" else ("fp5","int5","fp6","int6")
        upper, lower = axes[0,col], axes[1,col]
        for fmt in formats:
            rows = [r for r in group if r["format"] == fmt]
            if len(rows) != 72:
                raise ValueError("Missing frozen graph-bank mechanism summaries for " + fam + fmt)
            ideal = np.mean([float(r["ideal_extra_loss_pp"]) for r in rows])
            now = np.mean([float(r["offset_extra_loss_pp"]) for r in rows])
            upper.plot([0,1],[ideal,now],marker="o",color=colour(fmt),
                       label=fmt.upper(),linewidth=1.8)
        upper.set_xticks([0,1],["Ideal","Assumed offsets"])
        upper.set(xlim=(-.2,1.2),title=f"{fam.capitalize()}: original-policy extra loss")
        upper.set_ylabel("Extra loss vs matched FP64 (pp)")
        upper.legend(frameon=False,fontsize=8)
        tidy(upper)
        for j, fmt in enumerate(formats):
            rows = [r for r in group if r["format"] == fmt]
            da = np.mean([float(r["shift_access_A_pp"]) for r in rows])
            dz = np.mean([float(r["shift_selection_Rz_pp"]) for r in rows])
            lower.bar(j-.18,da,width=.34,color=colour(fmt),alpha=.86)
            lower.bar(j+.18,dz,width=.34,color=colour(fmt),alpha=.35,hatch="//")
        lower.set_xticks(range(len(formats)), [x.upper() for x in formats])
        lower.axhline(0,color="#555",linewidth=.8)
        lower.set(ylabel="Offset - ideal loss component (pp)",
                  title="Search/access (solid) vs selection (hatched) shifts")
        tidy(lower)
    fig.suptitle("Persistent synthetic logit offsets: mean response shifts, descriptive (72 graphs/family)",
                 fontsize=11)
    fig.tight_layout(rect=[0,.02,1,.95])
    fig.text(.5,0,"Not measured STT-MRAM offsets; no registered interaction test.",
             ha="center",fontsize=9)
    save(fig,out,"F11_offset_sensitivity")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("report/figures"))
    # Stage A/B source pin is fixed above; results are fetched, not re-simulated.
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    core=read_csv(IDEAL+"core_contrasts.csv")
    quality=read_csv(IDEAL+"graph_quality_mechanism.csv")
    family=read_csv(IDEAL+"family_quality_mechanism.csv")
    graph_contrasts=read_csv(IDEAL+"graph_contrasts.csv")
    anchors=read_csv(IDEAL+"anchor_contrasts_descriptive.csv")
    weak=read_csv(TAIL+"graph_summary.csv")
    selected=read_json(IDEAL+"selected_pairs.json")
    graphs=source_graphs()
    stage_a=checkpoint_json("stage_a_certification.json")
    stage_b=checkpoint_json("stage_b_graph_mechanisms.json")
    draw_pipeline(args.out)
    weights_distribution(args.out,graphs,quality)
    ring_distance(args.out,graphs)
    forest(args.out,core)
    width_ladder(args.out,selected,stage_a)
    mechanisms(args.out,family)
    retained_vs_loss(args.out,quality)
    tail_intervention(args.out,weak)
    output_policy(args.out,weak)
    heterogeneity(args.out,graph_contrasts,anchors)
    evidence_map(args.out)
    device_plot(args.out,stage_b)
    print("Created F01-F12 figures from pinned scientific CSV/JSON/source archives.")


if __name__=="__main__":
    main()
