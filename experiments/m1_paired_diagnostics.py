#!/usr/bin/env python3
"""Analyze user-run M1 screened MIMO frames without rerunning the solver.

Purpose: paired FORMAT and RESPONSE differences, not causal/device evidence.
No model refitting; read-only on original CSV; output to fresh directory.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

REQUIRED = {
    "frame_index", "channel_seed", "solver_seed", "snr_db",
    "response", "format", "selected_state", "bit_errors",
    "ml_hit", "original_residual_gap", "selected_at_update",
}
BITS = ("4", "6", "8")


def read_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError("missing required M1 paired_runs.csv fields")
        rows = list(reader)
    if not rows:
        raise ValueError("empty CSV")
    seen = set()
    for row in rows:
        key = (row["frame_index"],row["channel_seed"],row["solver_seed"],
               row["snr_db"],row["format"],row["response"])
        if key in seen:
            raise ValueError("duplicate frame/format/response records")
        seen.add(key)
        for col in ("bit_errors","ml_hit","selected_at_update"):
            int(row[col])
        float(row["original_residual_gap"])
    return rows


def analyze(rows):
    def basekey(row):
        return (row["frame_index"],row["channel_seed"],
                row["solver_seed"],row["snr_db"])
    snrs = sorted(set(float(r["snr_db"]) for r in rows))
    formats = sorted(set(r["format"] for r in rows))
    responses = sorted(set(r["response"] for r in rows))
    if "ideal" not in responses:
        raise ValueError("need ideal response control")
    lookup = {}
    for r in rows:
        lookup[(basekey(r),r["response"],r["format"])] = r
    response_deltas = []
    for resp in responses:
        if resp == "ideal":
            continue
        for snr in snrs:
            for fmt in formats:
                pairs = []
                for r in rows:
                    if r["response"]!=resp or float(r["snr_db"])!=snr or r["format"]!=fmt:
                        continue
                    control=lookup.get((basekey(r),"ideal",fmt))
                    if control is None:
                        raise ValueError("unmatched ideal response for frame")
                    pairs.append((control,r))
                if not pairs:
                    continue
                def df(a,b,col,conv):
                    return conv(b[col])-conv(a[col])
                response_deltas.append({
                    "response":resp, "snr_db":snr,"format":fmt,
                    "paired_frames":len(pairs),
                    "different_final_states":sum(a["selected_state"]!=b["selected_state"] for a,b in pairs),
                    "changed_ml_hit":sum(a["ml_hit"]!=b["ml_hit"] for a,b in pairs),
                    "changed_bit_error_count":sum(a["bit_errors"]!=b["bit_errors"] for a,b in pairs),
                    "changed_best_found_at_update":sum(a["selected_at_update"]!=b["selected_at_update"] for a,b in pairs),
                    "net_bit_error_difference":sum(df(a,b,"bit_errors",int) for a,b in pairs),
                    "mean_original_gap_difference":sum(df(a,b,"original_residual_gap",float) for a,b in pairs)/len(pairs),
                })
    fp_vs_int = []
    for resp in responses:
        for snr in snrs:
            for bit in BITS:
                f="fp"+bit; i="int"+bit
                if f not in formats or i not in formats:
                    continue
                pairs = []
                for r in rows:
                    if r["response"]!=resp or float(r["snr_db"])!=snr or r["format"]!=f:
                        continue
                    integer=lookup.get((basekey(r),resp,i))
                    if integer is None:
                        raise ValueError("unmatched INT comparison for FP frame")
                    pairs.append((r,integer))
                if not pairs:
                    continue
                fp_vs_int.append({
                    "response":resp,"snr_db":snr,"bits":int(bit),
                    "paired_frames":len(pairs),
                    "different_selected_states":sum(a["selected_state"]!=b["selected_state"] for a,b in pairs),
                    "fp_only_ml_hit":sum(int(a["ml_hit"])==1 and int(b["ml_hit"])==0 for a,b in pairs),
                    "int_only_ml_hit":sum(int(a["ml_hit"])==0 and int(b["ml_hit"])==1 for a,b in pairs),
                    "both_ml_hit":sum(int(a["ml_hit"])==1 and int(b["ml_hit"])==1 for a,b in pairs),
                    "neither_ml_hit":sum(int(a["ml_hit"])==0 and int(b["ml_hit"])==0 for a,b in pairs),
                    "fp_bit_errors":sum(int(a["bit_errors"]) for a,b in pairs),
                    "int_bit_errors":sum(int(b["bit_errors"]) for a,b in pairs),
                    "mean_gap_fp_minus_int":sum(float(a["original_residual_gap"])-float(b["original_residual_gap"]) for a,b in pairs)/len(pairs)
                })
    return {
        "evidence":"E1/E2 diagnostics of existing NUS software M1 pilot; not physical MRAM",
        "not_derived_from":"old TSP/CIM/device records",
        "response_vs_ideal":response_deltas,
        "fp_vs_equal_bit_int":fp_vs_int,
        "caution":"Final-best-state sensitivity != full trajectory sensitivity. "
                  "Best-of-recorded-samples can mask response effects. "
                  "No BER statistical significance with 12 frames, no hardware cost, "
                  "no physically validated p-bit response, per-frame MSE oracle scales."
    }


def write_report(output,source,diagnostics):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    digest=hashlib.sha256(Path(source).read_bytes()).hexdigest()
    payload=dict(diagnostics,input_file=Path(source).name,input_sha256=digest,
                 analyzer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    file=output/"m1_paired_diagnostics.json"
    file.write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    (output/"SHA256SUMS.json").write_text(json.dumps({file.name:hashlib.sha256(file.read_bytes()).hexdigest()},indent=2)+"\n",encoding="utf-8")
    return payload


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():
        p.error("output already exists; choose a new evidence directory")
    try:
        result=write_report(args.output,args.input,analyze(read_rows(args.input)))
    except (ValueError,FileExistsError) as exc:
        p.error(str(exc))
    print("=== RESPONSE vs IDEAL: distinct final states / paired frames ===")
    for r in result["response_vs_ideal"]:
        print(f'{r["response"]:12s} {r["snr_db"]:4g} dB {r["format"]:6s}: '
              f'{r["different_final_states"]}/{r["paired_frames"]} different states, '
              f'{r["changed_ml_hit"]} ML-hit flips, '
              f'{r["changed_best_found_at_update"]} different best-update checkpoints')
    print("=== SAME-BIT FP vs INT: discordant ML hits ===")
    for r in result["fp_vs_equal_bit_int"]:
        print(f'{r["response"]:12s} {r["snr_db"]:4g} dB '
              f'{r["bits"]}bit: FP-only={r["fp_only_ml_hit"]} '
              f'INT-only={r["int_only_ml_hit"]} '
              f'FP/INT bit errors={r["fp_bit_errors"]}/{r["int_bit_errors"]}')
    print(f'Full saved diagnostic: {args.output}/m1_paired_diagnostics.json')


if __name__=="__main__":
    main()
