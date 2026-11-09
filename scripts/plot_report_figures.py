#!/usr/bin/env python3
"""Reproduce FYP figures from the frozen, console-transcribed experiment CAL summaries.

Usage:
    python3 -m pip install matplotlib
    python3 research/plot_cal_figures.py
    python3 research/plot_cal_figures.py --out /tmp/cal_figures

DOES NOT run an annealer, read held-out graphs, or re-bootstrap uncertainty.
The 95% CI values were already calculated by the frozen experiment experiment
and transcribed to report/maxcut/data/cal_quality_{ref,fp,int}.csv.
The 144-state numerical diagnostic is STATIC on common FP64 states:
the x/y error metrics must not be called observed in-trajectory errors.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "report/maxcut/data"
FAMILIES = ("ref","fp","int")
COLOURS = {"ref":"#59687a", "fp":"#1765b1", "int":"#d8762c"}
GRAPH = (("Sparse", "s"),("Dense","d"))
STRESSES = ((0.8,"08"),(1.6,"16"))


def records(name):
    with (DATA/name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(fig, out, title):
    fig.savefig(out/(title+".pdf"), bbox_inches="tight")
    fig.savefig(out/(title+".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def tidy(ax):
    ax.grid(axis="y",color="#e2e5eb",linewidth=.7)
    ax.spines[["top","right"]].set_visible(False)
    ax.set_axisbelow(True)


def quality_plot(out):
    """All existing means; uncertainty bars only for documented CI sources."""
    panels={fam:records("cal_quality_"+fam+".csv") for fam in FAMILIES}
    fig,axes=plt.subplots(2,2,figsize=(13.4,7.5),sharey=True)
    for gi,(graph,prefix) in enumerate(GRAPH):
        for oi,(offset,suffix) in enumerate(STRESSES):
            ax=axes[gi,oi]; key=prefix+suffix
            ci={int(r["idx"]):r for r in records("cal_ci_"+key+".csv")}
            for fam in FAMILIES:
                for row in panels[fam]:
                    x=int(row["idx"]);mean=float(row[key+"mean"])
                    if x in ci:
                        item=ci[x];lo=float(item["lo"]);hi=float(item["hi"])
                        if not lo<=mean<=hi:
                            raise ValueError("CI/mean mismatch")
                        ax.errorbar(
                            x,mean,yerr=[[mean-lo],[hi-mean]],
                            fmt="D" if fam=="ref" else "s" if fam=="int" else "o",
                            color=COLOURS[fam],capsize=3,ms=6.4,lw=1.3)
                    else:
                        ax.plot(
                            x,mean,
                            marker="D" if fam=="ref" else "s" if fam=="int" else "o",
                            linestyle="None",markerfacecolor="white",
                            markeredgecolor=COLOURS[fam],
                            markeredgewidth=1.4,ms=6.5)
            ax.axhline(5,color="#bd463a",ls="--",lw=1.1)
            ax.set_title(f"{graph} | offset ±{offset:g} logit",
                         loc="left",weight="bold")
            ax.set_xticks(range(9),["FP64","FP4","FP5","FP6","FP8",
                                   "INT4","INT5","INT6","INT8"],
                         rotation=43,ha="right",fontsize=8.5)
            ax.set_ylim(2.5,9.0)
            if oi==0:ax.set_ylabel("Original-optimum gap (%)")
            tidy(ax)
    fig.suptitle("Coupling precision under assumed p-bit offset",
                 size=15,weight="bold")
    fig.subplots_adjust(hspace=.52,wspace=.16,top=.88,bottom=.15)
    fig.text(.5,.03,
       "24 seeds/cell. Whiskers: documented 95% CIs on 15/36 points ONLY; "
       "open markers: CI unavailable in this report.",
       ha="center",fontsize=9)
    save(fig,out,"fig_offset_quality")

def field_plot(out):
    fig, axes=plt.subplots(1,2,figsize=(11.7,5.2))
    for ax,(graph,_) in zip(axes,GRAPH):
        for fam in ("fp","int"):
            for r in records(f"cal_snap_{graph.lower()}_{fam}.csv"):
                x=float(r["rel_rms_pct"]); y=float(r["abs_dP"])
                ax.scatter(x,y,color=COLOURS[fam],marker="o" if fam=="fp" else "s",
                           s=65,edgecolors="white",linewidths=.7,zorder=3)
                ax.annotate(r["fmt"].upper(),(x,y),xytext=(5,5),
                            textcoords="offset points",fontsize=8.2)
        ax.set_title(f"{graph} J, ±1.6 logit",weight="bold",loc="left")
        ax.set_xlabel("Relative RMS field distortion (%)")
        tidy(ax)
    axes[0].set_ylabel("Mean absolute switching-probability distortion")
    fig.suptitle("Local-field error versus one-step probability distortion",
                 size=14,weight="bold",y=1.02)
    fig.subplots_adjust(bottom=.2,wspace=.25,top=.87)
    fig.text(.5,.04,"Same FP64-returned states; static β multiplier 2.0; "
                  "not an annealing trajectory measurement.",ha="center",fontsize=9)
    save(fig,out,"fig_field_probability")


def contrast_plot(out):
    fig,ax=plt.subplots(figsize=(9.4,5.5))
    for fam in ("fp","int"):
        for r in records(f"cal_snap_dense_{fam}.csv"):
            x,y=float(r["abs_dP"]),float(r["solver_gap"])
            ax.scatter(x,y,color=COLOURS[fam],marker="o" if fam=="fp" else "s",
                       s=85,edgecolors="white",zorder=3)
            ax.annotate(r["fmt"].upper(),(x,y),xytext=(6,5),
                        textcoords="offset points",fontsize=9)
    ax.axhline(5,color="#bd463a",ls="--",lw=1)
    ax.set_xlabel("Static mean |ΔP| on common FP64 states")
    ax.set_ylabel("Separate solver's original-optimum gap (%)")
    ax.set_title("Dense ±1.6: static decision fidelity vs separate solver quality",
                 weight="bold")
    tidy(ax)
    fig.subplots_adjust(bottom=.2)
    fig.text(.5,.04,"Descriptive juxtaposition only: these are not the "
                  "same sampled trajectories.",ha="center",fontsize=9)
    save(fig,out,"fig_static_vs_quality")


def pipeline_plot(out):
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    fig,ax=plt.subplots(figsize=(12.8,3.15))
    ax.set_xlim(0,13);ax.set_ylim(0,3.2);ax.axis("off")
    nodes=[
        ("Original J","J_ij = -w_ij"),
        ("Quantized J","FP / INT + global scale"),
        ("Local field","H = J s"),
        ("Nonideal p-bit","sigmoid(2βH + δ)"),
        ("Evaluation","Original-weight Max-Cut"),
    ]
    xs=[.1,2.8,5.5,8.2,10.9]
    for i,((name,desc),x) in enumerate(zip(nodes,xs)):
        c=COLOURS["ref" if i in (0,4) else "int" if i==3 else "fp"]
        ax.add_patch(FancyBboxPatch((x,1.05),2.0,1.35,boxstyle="round,pad=0.12",
                     edgecolor=c,facecolor="white",lw=1.6))
        ax.text(x+1,1.95,name,ha="center",weight="bold",fontsize=10,color=c)
        ax.text(x+1,1.45,desc,ha="center",fontsize=8.6)
        if i!=4:
            ax.add_patch(FancyArrowPatch((x+2.16,1.72),(xs[i+1]-.16,1.72),
                     arrowstyle="-|>",mutation_scale=14,color=COLOURS["ref"]))
    ax.text(6.5,.48,"Design variable: coupling coefficient encoding. "
            "The accumulator and device interface remain idealised.",
            ha="center",fontsize=9)
    save(fig,out,"fig_coupling_pipeline")



def eligibility_plot(out):
    """Frozen two-screen CAL eligibility; uncertified is not proven failure."""
    fig, ax=plt.subplots(figsize=(11.4,5.9))
    cond=[("Sparse",0.8),("Sparse",1.6),("Dense",0.8),("Dense",1.6)]
    formats=["FP4","FP5","FP6","FP8","INT4","INT5","INT6","INT8"]
    yes={("Sparse",0.8,"FP4"),("Sparse",0.8,"INT5"),
         ("Sparse",0.8,"INT6"),("Sparse",0.8,"INT8")}
    for r,fmt in enumerate(formats):
        for c,(g,d) in enumerate(cond):
            good=(g,d,fmt) in yes
            ax.add_patch(plt.Rectangle((c-.48,7-r-.46),.96,.91,
              facecolor="#dceee3" if good else "#eef0f4",
              edgecolor="white",linewidth=2))
            ax.text(c,7-r,"Eligible" if good else "Not certified",
              ha="center",va="center",fontsize=9,
              color="#226b46" if good else "#5f6d7a",
              fontweight="bold" if good else "normal")
    ax.set_xlim(-.6,3.6);ax.set_ylim(-.7,7.7)
    ax.set_xticks(range(4),[f"{g} | ±{d:g}" for g,d in cond])
    ax.set_yticks(range(8),list(reversed(formats)))
    ax.xaxis.tick_top();ax.tick_params(length=0)
    for spine in ax.spines.values():spine.set_visible(False)
    ax.set_title("Frozen two-screen precision eligibility",
                 fontweight="bold",fontsize=15,pad=46)
    fig.text(.5,.025,
      "Both 95% CI screens must pass. A missing certification does not prove failure.",
      ha="center",fontsize=9)
    fig.subplots_adjust(left=.15,right=.98,top=.79,bottom=.12)
    save(fig,out,"fig_precision_eligibility")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,
                   default=ROOT/"report/figures")
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    quality_plot(args.out)
    field_plot(args.out)
    contrast_plot(args.out)
    pipeline_plot(args.out)
    eligibility_plot(args.out)
    print("Generated 5 vector PDFs and 5 PNG previews in",args.out)
    print("No optimizer runs; no held-out graphs touched.")


if __name__=="__main__":
    main()
