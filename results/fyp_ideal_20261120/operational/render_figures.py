"""Presentation only: render the frozen analysis CSVs without new inference."""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "figures"
OUT.mkdir(exist_ok=True)


def rows(name):
    with (BASE / "analysis" / name).open() as f:
        return list(csv.DictReader(f))


def name(value):
    return value.replace("ref64", "FP64").upper().replace("-", " − ")


plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
core = rows("core_contrasts.csv")
fig, axes = plt.subplots(1, 2, figsize=(13, 7.2), sharex=True)
for ax, family in zip(axes, ("ring", "torus")):
    rr = [r for r in core if r["family"] == family]
    ax.axvspan(-0.5, 0.5, color="#eef3f6", zorder=0)
    ax.axvline(0, color="#68717b", linewidth=1)
    ax.axvline(0.5, color="#a65b22", linestyle="--", linewidth=1.3)
    for i, r in enumerate(rr):
        m, lo, hi = (float(r[k]) for k in ("mean", "low", "high"))
        color = "#ad352f" if r["qualification"] == "FAIL" else "#17677d"
        ax.errorbar(m, i, xerr=[[m-lo], [hi-m]], fmt="o", capsize=4,
                    markersize=6, color=color, linewidth=1.8)
    ax.set_yticks(np.arange(len(rr)), [name(r["contrast"]) for r in rr])
    ax.invert_yaxis()
    ax.set_xlim(-0.4, 1.0)
    ax.set_xlabel("Extra reference shortfall (percentage points)")
    ax.set_title("Distance-decaying Gaussian ring" if family == "ring" else "Gaussian torus",
                 fontsize=13, fontweight="bold", pad=15)
    ax.grid(axis="x", color="#dce1e5", linewidth=.5)
fig.suptitle("Registered ideal-response precision contrasts", fontsize=19, fontweight="bold", y=.98)
fig.legend(handles=[Line2D([0], [0], color="#17677d", marker="o", label="PASS at +0.5 pp"),
                    Line2D([0], [0], color="#ad352f", marker="o", label="FAIL at +0.5 pp"),
                    Line2D([0], [0], color="#a65b22", linestyle="--", label="Noninferiority threshold")],
           loc="lower center", bbox_to_anchor=(.5, .075), ncol=3, frameon=False)
fig.text(.5, .025, "Nominal 96% simultaneous bootstrap-t bounds across 18 contrasts; 72 graphs per family.\n"
         "Negative favors the first encoding. Generated B_g is a best-observed feasible cut, not the optimum.",
         ha="center", va="center", fontsize=10)
fig.subplots_adjust(left=.11, right=.98, bottom=.23, top=.85, wspace=.42)
fig.savefig(OUT / "core_contrasts.png", dpi=180, facecolor="white")
plt.close(fig)

mechanism = rows("mechanism_contrasts.csv")
order = [(f, c) for f in ("ring", "torus") for c in ("fp5-int6", "fp6-int7", "fp6-int6")]
fig, ax = plt.subplots(figsize=(11.5, 6.7))
ax.axvline(0, color="#68717b", linewidth=1)
ax.axhline(2.5, color="#b7c1c7", linewidth=.8)
for i, (family, contrast) in enumerate(order):
    for metric, offset, color, marker in (("Rz_pp", -.12, "#17677d", "o"), ("A_pp", .12, "#b35c2e", "s")):
        r = next(r for r in mechanism if (r["family"], r["contrast"], r["metric"]) == (family, contrast, metric))
        m, lo, hi = (float(r[k]) for k in ("mean", "low", "high"))
        ax.errorbar(m, i+offset, xerr=[[m-lo], [hi-m]], fmt=marker, color=color,
                    capsize=4, markersize=6, linewidth=1.7)
ax.set_yticks(np.arange(6), [f"{f.title()}  {name(c)}" for f, c in order])
ax.invert_yaxis()
ax.set_xlim(-.19, .17)
ax.set_xlabel("FP minus INT component difference (percentage points)")
ax.grid(axis="x", color="#dce1e5", linewidth=.5)
fig.legend(handles=[Line2D([0], [0], color="#17677d", marker="o", label="Total selection loss Rz"),
                    Line2D([0], [0], color="#b35c2e", marker="s", label="Access A")],
           loc="lower center", bbox_to_anchor=(.60, .86), ncol=2, frameon=False)
fig.suptitle("Descriptive access and selection accounting", fontsize=18, fontweight="bold", y=.97)
fig.text(.5, .035, "Ordinary 95% graph-resampled intervals; no core alpha allocated. Rz = (V − R)/B_g × 100.\n"
         "The predicted positive ring FP6−INT7 Rz difference is contradicted; FP6−INT6 had no predicted direction.",
         ha="center", fontsize=10)
fig.subplots_adjust(left=.25, right=.97, top=.82, bottom=.18)
fig.savefig(OUT / "mechanism_contrasts.png", dpi=180, facecolor="white")
plt.close(fig)

manifest = {"scope": "presentation derived from frozen registered tables; no new inference",
            "matplotlib": matplotlib.__version__,
            "inputs": {s: hashlib.sha256((BASE/"analysis"/s).read_bytes()).hexdigest()
                       for s in ("core_contrasts.csv", "mechanism_contrasts.csv")},
            "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob("*.png"))}}
(OUT/"figure_manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2)+"\n")
print(json.dumps({"status": "RENDERED", "files": list(manifest["files"])}))
