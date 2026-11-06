#!/usr/bin/env python3
"""M1C: J-versus-h ablation and mixed-precision audit on FROZEN M1B heldout MIMO.

E0/E1 representation-only exact enumeration; NO p-bit sampling, device data,
physical hardware results, or invisible original-objective candidate selection.
'J_only' / 'h_only' leave the opposite block unquantized: diagnostic ORACLES.
"""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import m1_calibrated_scale_gate as gate

REQUIRED = ("fp4", "fp4_fn", "fp6_fn", "int4", "int6")
MIXED = (("fp4_fn","fp6_fn"),("int4","int6"))


def analyze(frames, frozen, formats, granularities, tile):
    """No calibration here. All per-group scales are already fixed on CAL."""
    for fmt in REQUIRED:
        if fmt not in formats:
            raise ValueError("M1B source missing required format: "+fmt)
    rows=[]
    for record in frames:
        frame=record["instance"]
        n=frame["tx"]
        frame_id=int(record["frame_index"])
        snr=float(record["snr_db"])
        for gran in granularities:
            q={}
            for fmt in formats:
                scales=frozen.get(f"{fmt}|{gran}")
                if scales is None:
                    raise ValueError("missing frozen scales "+fmt+"|"+gran)
                q[fmt]=gate.quantize_with_frozen(frame,fmt,gran,tile,scales)
            for fmt in formats:
                if fmt not in ("fp4","fp4_fn","fp6","fp6_fn","int4","int6","bfp4"):
                    continue
                for mode in ("both","J_only","h_only"):
                    represented={
                        "J":q[fmt]["J"] if mode!="h_only" else frame["J"],
                        "h":q[fmt]["h"] if mode!="J_only" else frame["h"],
                    }
                    stats=gate.exact_ground_compare(frame,represented)
                    rows.append(dict(frame_index=frame_id,snr_db=snr,
                        format=fmt,granularity=gran,mode=mode,
                        **stats,
                        nominal_stored_bits=q[fmt]["total_nominal_bits"] if mode=="both" else None,
                        cost_model="nominal-coefficient+scale-only" if mode=="both"
                                   else "oracle-diagnostic-unquantized-opposite",
                    ))
            for jfmt,hfmt in MIXED:
                if jfmt not in q or hfmt not in q:
                    raise ValueError("missing mixed-format pair")
                represented={"J":q[jfmt]["J"],"h":q[hfmt]["h"]}
                stats=gate.exact_ground_compare(frame,represented)
                edges=n*(n-1)//2
                j_groups=len(gate.groups_for(n,gran,tile))
                # Both are FP or both INT: 32 nominal bits per fitted J group
                # plus 32 for one h scale (even though ideal scale is float64
                # during the software calculation).
                bits=4*edges+6*n+32*(j_groups+1)
                rows.append(dict(frame_index=frame_id,snr_db=snr,
                    format=f"{jfmt}_J__{hfmt}_h",granularity=gran,
                    mode="mixed_both",**stats,nominal_stored_bits=bits,
                    cost_model="nominal-coefficient+scale-only",
                ))
    keyfn=lambda r:(r["format"],r["granularity"],r["mode"],r["snr_db"])
    grouped=defaultdict(list)
    for r in rows:
        grouped[keyfn(r)].append(r)
    summary=[]
    for key,sub in sorted(grouped.items()):
        fmt,gran,mode,snr=key
        n=len(sub)
        summary.append(dict(
            format=fmt,granularity=gran,mode=mode,snr_db=snr,
            heldout_frames=n,
            original_ml_preserved=sum(r["original_ml_preserved"] for r in sub),
            degenerate_ground_frames=sum(r["ground_degenerate"] for r in sub),
            mean_best_original_gap=sum(r["best_possible_original_gap"] for r in sub)/n,
            mean_worst_original_gap=sum(r["worst_possible_original_gap"] for r in sub)/n,
            nominal_stored_bits=sub[0]["nominal_stored_bits"],
        ))
    return rows,summary


def read_m1b(path):
    src=Path(path)
    manifest=json.loads((src/"m1b_manifest.json").read_text(encoding="utf-8"))
    conf=manifest["config"]
    frozen=manifest["frozen_scales"]
    with (src/"heldout_frames.jsonl").open(encoding="utf-8") as f:
        frames=[json.loads(line) for line in f if line.strip()]
    if not frames:
        raise ValueError("missing heldout MIMO frames")
    if set(range(conf["cal_seed"],conf["cal_seed"]+conf["cal_frames"])) & \
       set(range(conf["heldout_seed"],conf["heldout_seed"]+conf["heldout_frames"])):
        raise ValueError("CAL/HELD seed overlap")
    return frames,frozen,conf


def save(out,input_dir,rows,summary):
    p=Path(out)
    p.mkdir(parents=True,exist_ok=False)
    with (p/"jh_ablation_per_frame.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    src=Path(input_dir)
    metadata=dict(
        evidence_tier="E0/E1 independent HELDOUT exact-quantization analysis; not stochastic MRAM evidence",
        input_dir_name=src.name,
        input_hashes={fn:hashlib.sha256((src/fn).read_bytes()).hexdigest()
                      for fn in ("m1b_manifest.json","heldout_frames.jsonl")},
        source_hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest()
                       for f in (Path(__file__),Path(gate.__file__),Path(gate.quant.__file__))},
        caveats="J_only/h_only are mathematical diagnostics retaining unquantized other coefficients, not deployable low-bit hardware. "
                "Mixed FP4_J/FP6_h and INT4_J/INT6_h use separate CAL-only frozen group scales. "
                "No p-bit sampling, nonideality, actual bit-true scale, accumulation or hardware costs. "
                "Equal original ML solution preserved if any quantized ground state has original residual gap <=1e-8. "
                "Nominal storage counts unique symmetric J/h and assumed FP/INT scale words only. "
                "No scale programming/calibration, exponent alignment, routing, energy, time-to-target or CI inference.",
        summary=summary
    )
    (p/"m1c_manifest.json").write_text(json.dumps(metadata,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    checks={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in p.iterdir() if x.is_file()}
    (p/"SHA256SUMS.json").write_text(json.dumps(checks,indent=2,sort_keys=True)+"\n")
    return metadata


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--m1b-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    if a.output.exists():
        parser.error("output already exists; choose a fresh directory")
    try:
        frames,frozen,conf=read_m1b(a.m1b_dir)
        rows,summary=analyze(frames,frozen,conf["formats"],
                             conf["granularities"],conf["tile"])
        save(a.output,a.m1b_dir,rows,summary)
    except (ValueError,KeyError,FileNotFoundError,FileExistsError) as exc:
        parser.error(str(exc))
    print("== M1C held-out coefficient ablation: original ML kept in quantized minima ==")
    print("Format             Group    Mode      SNR | ML retained Degeneracies  Bits")
    for s in summary:
        print(f'{s["format"]:19s} {s["granularity"]:7s} {s["mode"]:10s} '
              f'{s["snr_db"]:4g} | {s["original_ml_preserved"]:2d}/{s["heldout_frames"]} '
              f'{s["degenerate_ground_frames"]:2d}/{s["heldout_frames"]} '
              f'{s["nominal_stored_bits"] if s["nominal_stored_bits"] is not None else "oracle"}')
    print("Saved: "+str(a.output))


if __name__=="__main__":
    main()
