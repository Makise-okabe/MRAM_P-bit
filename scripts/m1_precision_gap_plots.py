#!/usr/bin/env python3
"""Render one dependency-free SVG gap-vs-width graph PER original source graph.

Y = original-weight published-optimum gap (%), lower is better.
95% whiskers are the paired additional-gap bootstrap CI translated
to the paired FP64 mean (NOT independent absolute-gap CI).
"""
import argparse
import csv
import math
from pathlib import Path
from xml.sax.saxutils import escape

BITS=(4,5,6,8)
FAMILIES=("fp","int","bfp")
COLORS={"fp":"#236BB7","int":"#D17C21","bfp":"#16866C"}
MARGIN=75
W,H=940,580


def text(x,y,t,size=16,anchor="start",color="#263441",weight="normal"):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'font-family="Arial,Helvetica,sans-serif" text-anchor="{anchor}" '
            f'font-weight="{weight}">{escape(str(t))}</text>')


def plot_graph(rows, directory):
    graph=rows[0]["graph"]
    configs={r["configuration"]:r for r in rows}
    expected={"ref64"}|{f"{f}{b}" for f in FAMILIES for b in BITS}
    if set(configs)!=expected:
        raise ValueError(f"incomplete format/bit-width panel: {graph}")
    rref=configs["ref64"]
    ref=float(rref["mean_reference_gap_pct"])
    all_values=[ref,ref+1]
    for family in FAMILIES:
        for b in BITS:
            p=configs[f"{family}{b}"]
            all_values.extend([float(p["mean_optimality_gap_pct"]),
                 ref+float(p["bootstrap_95_lo_additional_gap_pp"]),
                 ref+float(p["bootstrap_95_hi_additional_gap_pp"])])
    vmin=min(all_values)
    vmax=max(all_values)
    padding=max(0.15,(vmax-vmin)*0.12)
    low=max(0,vmin-padding)
    high=vmax+padding
    left,right=100,700
    top,bottom=95,480
    def x(bit):return left+(bit-4)/4*(right-left)
    def y(value):return bottom-(value-low)/(high-low)*(bottom-top)
    parts=[
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<rect width="100%" height="100%" fill="white"/>',
        text(38,37,f"Weighted Max-Cut — {graph}",24,weight="bold"),
        text(38,64,"50,000 linear Gibbs updates · 24 fresh paired seeds · global source-MSE scale",14,color="#5d6876")
    ]
    for tick in range(6):
        v=low+(high-low)*tick/5
        yy=y(v)
        parts.append(f'<line x1="{left}" y1="{yy:.2f}" x2="{right}" y2="{yy:.2f}" stroke="#e5eaf0"/>')
        parts.append(text(left-12,f"{yy+5:.2f}",f"{v:.2f}",13,anchor="end"))
    for bit in BITS:
        xx=x(bit)
        parts.append(text(xx,bottom+27,str(bit),15,anchor="middle"))
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#4b5a68"/>')
    parts.append(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#4b5a68"/>')
    parts.append(text((left+right)/2,bottom+60,"Coupling precision (bits)",17,anchor="middle"))
    parts.append(text(42,90,"Published-optimum gap (%) — lower is better",14))
    for v,color,caption,dash in ((ref,"#5a6370","paired FP64","6,4"),
                                 (ref+1,"#A1A9B1","FP64 + 1pp threshold","3,5")):
        yy=y(v)
        parts.append(f'<line x1="{left}" y1="{yy:.2f}" x2="{right}" y2="{yy:.2f}" stroke="{color}" stroke-dasharray="{dash}" stroke-width="2"/>')
        parts.append(text(725,yy+4,f"{caption}: {v:.2f}%",12,color=color))
    # Whiskers slightly horizontally offset for readability at same width.
    dx={"fp":-10,"int":0,"bfp":10}
    for family in FAMILIES:
        color=COLORS[family]
        coords=[]
        for bit in BITS:
            p=configs[f"{family}{bit}"]
            yy=y(float(p["mean_optimality_gap_pct"]))
            xx=x(bit)+dx[family]
            coords.append((xx,yy))
            lower=ref+float(p["bootstrap_95_lo_additional_gap_pp"])
            upper=ref+float(p["bootstrap_95_hi_additional_gap_pp"])
            a,b=sorted((y(lower),y(upper)))
            parts.append(f'<line x1="{xx:.2f}" y1="{a:.2f}" x2="{xx:.2f}" y2="{b:.2f}" stroke="{color}" stroke-width="1.4"/>')
            for cap in (a,b):
                parts.append(f'<line x1="{xx-4:.2f}" y1="{cap:.2f}" x2="{xx+4:.2f}" y2="{cap:.2f}" stroke="{color}" stroke-width="1.4"/>')
        points=" ".join(f"{xx:.1f},{yy:.1f}" for xx,yy in coords)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for xx,yy in coords:
            parts.append(f'<circle cx="{xx:.2f}" cy="{yy:.2f}" r="4" fill="{color}"/>')
    for i,family in enumerate(FAMILIES):
        parts.append(f'<line x1="745" y1="{160+i*29}" x2="772" y2="{160+i*29}" stroke="{COLORS[family]}" stroke-width="3"/>')
        parts.append(text(785,165+i*29,{"fp":"Finite FP E2M1/E2M2/E3M2/E4M3",
                                        "int":"Symmetric INT","bfp":"BFP global PoT"}[family],12))
    parts.append(text(38,545,"Whiskers: paired-seed bootstrap CI translated to FP64 mean; NOT a graph-population CI.",12,color="#5d6876"))
    parts.append('</svg>')
    directory.mkdir(parents=True,exist_ok=True)
    name="gap_vs_bits_"+graph.replace(".","_")+".svg"
    path=directory/name
    with path.open("x",encoding="utf-8") as fd:
        fd.write("\n".join(parts)+"\n")
    print("PRECISION GAP FIGURE:",path)
    return path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv",type=Path,required=True)
    ap.add_argument("--out-dir",type=Path,required=True)
    a=ap.parse_args()
    with a.csv.open(newline="",encoding="utf-8") as fp:
        rows=list(csv.DictReader(fp))
    by_graph={}
    for r in rows:
        by_graph.setdefault(r["graph"],[]).append(r)
    if len(by_graph)!=3:
        raise ValueError("expected exactly three frozen graph panels")
    for graph,values in by_graph.items():
        plot_graph(values,a.out_dir)


if __name__=="__main__":
    main()
