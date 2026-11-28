#!/usr/bin/env python3
"""EX1: M5-viewed, d=0 exploratory FP5/INT8 extension (exactly 48 runs).

--selftest: synthetic 4-spin parity and 5/8-bit codebook checks; no M5 source.
--preflight: READ ONLY original M5 source and archived 216-run evidence.
--freeze: after preflight, create immutable new protocol JSON (no solver).
--execute: verify frozen hashes and M5 originals, then run FP5/INT8 x 24.

Designed to scope candidate widths, NOT to certify minimum b*, k or an
independent held-out finding. M5/M6/E0 original files are never modified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from types import SimpleNamespace

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph, prepare
from experiments.m1_biqmac_reference_quality_gate import solve_reference
from experiments.m1_biqmac_precision_sweep import bootstrap_paired_ci
from experiments.m1_precision_codebooks import build_global, describe_codebook
from experiments.m2_e2_response_gate import EVIDENCE, solve_with_response
from experiments.m2_heldout_dense_sixbit import (
    NAME, GRAPH_PATH, GRAPH_INDEX, OPTIMUM, UPDATES_FROZEN,
    device_models, paired_seed, sha_json,
)

ROOT = Path(__file__).resolve().parents[1]
OLD = Path("results/m2_heldout_dense_fp6_int6_20261109")
OUT = Path("results/ex1_m5_fp5_int8_20261115")
CANDIDATES = (("fp5", "fp", 5), ("int8", "int", 8))
BASELINE = ("ref64", "fp6", "int6")
SEEDS = tuple(paired_seed(GRAPH_INDEX))
N_NEW = 48
BOOTSTRAP = 4000
MARGINS = (0.5, 1.0)
HASH_FILES = (
    "experiments/ex1_m5_fp5_int8_exploratory.py",
    "experiments/biqmac_maxcut.py",
    "experiments/m0_ising_math.py",
    "experiments/m1_biqmac_ideal_pilot.py",
    "experiments/m1_biqmac_reference_quality_gate.py",
    "experiments/m1_biqmac_precision_sweep.py",
    "experiments/m1_precision_codebooks.py",
    "experiments/m1_coupling_formats.py",
    "experiments/m2_stt_pbit_transfer_preflight.py",
    "experiments/m2_e2_response_gate.py",
    "experiments/m2_offset_fp64_scout.py",
    "experiments/m2_heldout_dense_sixbit.py",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_read(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def csv_save_new(path, rows):
    if not rows:
        raise ValueError("No rows to write")
    with path.open("x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def json_save_new(path, obj):
    with path.open("x", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")


def selftest():
    g = SimpleNamespace(n=4, edges=((0, 1, 2), (1, 2, -3),
                                    (2, 3, 4), (0, 3, 1)))
    model = {
        "evidence_level": EVIDENCE, "n_devices": 4,
        "per_device_gain": [1.0] * 4,
        "per_device_offset_logit": [0.0] * 4,
    }
    for key, family, width in CANDIDATES:
        fmt = describe_codebook(family, width)
        assert fmt["width"] == width
        rep = build_global(g, family, width)
        assert len(rep["edges"]) == len(g.edges)
        assert rep["scale_metadata_bits"] == 32
        for seed in (731, 789):
            a = solve_reference(g, rep, 0.03, 200, seed, "linear")
            b = solve_with_response(g, rep, 0.03, 200, seed,
                                    model, offset_limit=0.0)
            for field in ("returned_state_hex", "returned_original_cut",
                          "returned_represented_energy", "actual_flips"):
                if a[field] != b[field]:
                    raise AssertionError(f"{key} ideal/E2 parity failed {field}")
    assert UPDATES_FROZEN == 50000 and len(SEEDS) == 24
    assert SEEDS == tuple(range(20661201, 20661225))
    print("EX1 SELFTEST PASS: FP5/INT8 codebooks and exact ideal/E2 parity")


def baseline_and_source(*, verbose=False):
    """Strictly read-only. No source download, no solver run, no output write."""
    manifest = json.loads((OLD / "manifest.json").read_text())
    prot = json.loads((OLD / "protocol.json").read_text())
    gate = json.loads((OLD / "source_gate.json").read_text())
    old_csv = OLD / "runs.csv"
    assert manifest["status"] == "DENSE_7777_216_RUNS_COMPLETE"
    assert manifest["n_solver_runs"] == 216
    assert sha(old_csv) == manifest["raw_runs_sha256"]
    assert sha(OLD / "protocol.json") == manifest["protocol_sha256"]
    assert prot["graph"] == NAME and prot["seeds"] == list(SEEDS)
    assert prot["updates"] == UPDATES_FROZEN
    assert prot["device_model_hashes"]["0.0"] == sha_json(device_models()[0.0])
    if not GRAPH_PATH.is_file():
        raise FileNotFoundError("Original viewed M5 graph missing: " + str(GRAPH_PATH))
    g = load_rudy(GRAPH_PATH)
    assert (g.source == str(GRAPH_PATH) and g.n == 100
            and g.raw_edge_count == 4950 and len(g.edges) == 4869)
    assert g.sha256 == manifest["graph_sha256"] == gate["graph_sha256"]
    assert manifest["official_optimum"] == OPTIMUM == 3363230
    beta = beta_from_original_graph(g)
    raw = csv_read(old_csv)
    assert len(raw) == 216
    keys = {(float(x["offset_logit_halfspan"]), x["configuration"], int(x["seed"]))
            for x in raw}
    assert len(keys) == 216
    subset = {}
    for x in raw:
        if float(x["offset_logit_halfspan"]) != 0.0:
            continue
        key = (x["configuration"], int(x["seed"]))
        assert x["configuration"] in BASELINE
        assert x["graph_sha256"] == g.sha256
        assert x["schedule"] == "linear"
        assert int(x["attempted_updates"]) == UPDATES_FROZEN
        assert math.isclose(float(x["beta"]), beta, rel_tol=1e-14)
        assert int(x["seed"]) in SEEDS
        assert key not in subset
        subset[key] = x
    assert len(subset) == 72
    assert set(subset) == {(key, seed) for key in BASELINE for seed in SEEDS}
    reps = {name: build_global(g, family, width)
            for name, family, width in CANDIDATES}
    reps["fp6"] = build_global(g, "fp", 6)
    reps["int6"] = build_global(g, "int", 6)
    for key in ("fp6", "int6"):
        old_scale = float(subset[(key, SEEDS[0])]["scale"])
        assert math.isclose(reps[key]["scale"], old_scale, rel_tol=1e-14)
    if verbose:
        print(f"EX1 READ-ONLY SOURCE GATE PASS: {NAME}, n={g.n},"
              f" raw={g.raw_edge_count}, nonzero={len(g.edges)}")
        print(f"M5 RAW ARCHIVE PASS: 216/216, d=0 baseline 72/72; beta={beta:.12g}")
        print("STATIC COEFFICIENT-ONLY AUDIT (no new solver runs):")
        for key in ("fp5", "fp6", "int6", "int8"):
            rep = reps[key]
            print(f"  {key:4} scale={rep['scale']:.8g}"
                  f" zeroed={rep['zeroed_edges']}/4869"
                  f" rel_L1={rep['relative_abs_coefficient_error']:.6g}"
                  f" MSE={rep['coefficient_mse']:.6g}"
                  f" nominal_dense_bits={rep['nominal_one_copy_dense_total_bits']}")
    return g, beta, manifest, prot, gate, subset, reps


def protocol():
    g, beta, oldman, oldprot, gate, _, reps = baseline_and_source()
    return {
        "status": "EX1_FROZEN_BEFORE_EXPLORATORY_RUNS",
        "scope": "VIEWED M5 instance; exploratory ONLY; no independent holdout; d=0",
        "graph": NAME, "graph_sha256": g.sha256,
        "official_optimum": OPTIMUM, "graph_index": GRAPH_INDEX,
        "baseline_archive_sha256": sha(OLD / "runs.csv"),
        "baseline_manifest_sha256": sha(OLD / "manifest.json"),
        "baseline_protocol_sha256": sha(OLD / "protocol.json"),
        "baseline_source_gate_sha256": sha(OLD / "source_gate.json"),
        "baseline_formats": list(BASELINE), "new_formats": [n for n, _, _ in CANDIDATES],
        "baseline_seed_rule": "20261201 + 100000*4 + k; k=0..23",
        "seeds": list(SEEDS), "new_runs": N_NEW,
        "updates": UPDATES_FROZEN,
        "schedule": "linear 0.5*beta_G to 2.0*beta_G; same seed and d=0 E2 model",
        "beta": beta,
        "device_model_hash_0": oldprot["device_model_hashes"]["0.0"],
        "scales": {k: reps[k]["scale"] for k in ("fp5", "int8")},
        "scale_policy": "source_mse_loggrid_v1",
        "return_policy": "best represented energy visited",
        "evaluation": "original signed weighted Max-Cut only",
        "exploratory_margins_pp": list(MARGINS),
        "bootstrap_resamples": BOOTSTRAP,
        "code_hashes": {p: sha(ROOT / p) for p in HASH_FILES},
        "limitations": (
            "Viewed graph; 24 paired seeds; single ideal d=0 population; "
            "intervals exploratory and not familywise adjusted; cannot establish b*/k."
        ),
    }


def boot(values, seed):
    lo, hi = bootstrap_paired_ci(values, seed, replicates=BOOTSTRAP)
    return statistics.mean(values), lo, hi


def status(lo, hi, margin):
    if hi <= margin:
        return "EXPLORATORY_NONINFERIOR"
    if lo > margin:
        return "EXPLORATORY_INFERIOR"
    return "EXPLORATORY_INCONCLUSIVE"


def execute():
    frozen_path = OUT / "protocol.json"
    if not frozen_path.is_file():
        raise ValueError("Run --freeze first and inspect immutable protocol")
    frozen = json.loads(frozen_path.read_text())
    if frozen != protocol():
        raise ValueError("EX1 PROTOCOL OR ORIGINAL M5 FILE CHANGED — REFUSE")
    if any((OUT / x).exists() for x in
           ("new_runs.csv", "exploratory_summary.csv", "manifest.json")):
        raise FileExistsError("EX1 outputs already exist; no silent reruns")
    selftest()
    g, beta, _, _, _, baseline, reps = baseline_and_source(verbose=True)
    device = device_models()[0.0]
    raw = []
    for name, family, width in CANDIDATES:
        rep = reps[name]
        for seed in SEEDS:
            result = solve_with_response(g, rep, beta, UPDATES_FROZEN, seed,
                                         device, offset_limit=0.0)
            cut = float(result["returned_original_cut"])
            if not math.isfinite(cut) or cut > OPTIMUM + 1e-7:
                raise AssertionError("Returned cut above published optimum")
            raw.append({
                "graph": NAME, "graph_sha256": g.sha256,
                "official_optimum": OPTIMUM, "offset_logit_halfspan": 0.0,
                "configuration": name, "seed": seed,
                "attempted_updates": UPDATES_FROZEN, "schedule": "linear",
                "beta": beta, "scale": rep["scale"],
                "returned_original_cut": cut,
                "gap_pct": 100*(OPTIMUM-cut)/OPTIMUM,
                "actual_flips": result["actual_flips"],
                "improvements": result["improvements"],
                "returned_represented_energy": result["returned_represented_energy"],
                "returned_state_hex": result["returned_state_hex"],
            })
        print(f"EX1 DONE {name}: 24/24 new runs", flush=True)
    assert len(raw) == N_NEW
    by = {(x["configuration"], int(x["seed"])): float(x["gap_pct"])
          for x in raw}
    assert len(by) == N_NEW
    for key, old in baseline.items():
        by[key] = float(old["gap_pct"])
    summary = []
    for i, name in enumerate(("fp5", "fp6", "int6", "int8")):
        gap = [by[(name, k)] for k in SEEDS]
        ref = [by[("ref64", k)] for k in SEEDS]
        fp6 = [by[("fp6", k)] for k in SEEDS]
        versus_ref = [a-b for a,b in zip(gap,ref)]
        versus_fp6 = [a-b for a,b in zip(gap,fp6)]
        mean, low, high = boot(versus_ref, 915010+i)
        dmean, dlo, dhi = boot(versus_fp6, 915110+i)
        summary.append({
            "configuration": name,
            "data_source": "new_24_runs" if name in ("fp5", "int8")
                           else "reused_M5_24_runs",
            "mean_gap_pct": statistics.mean(gap),
            "paired_ref64_extra_mean_pp": mean,
            "paired_ref64_extra_ci95_lo_pp": low,
            "paired_ref64_extra_ci95_hi_pp": high,
            "paired_fp6_gap_diff_mean_pp": dmean,
            "paired_fp6_gap_diff_ci95_lo_pp": dlo,
            "paired_fp6_gap_diff_ci95_hi_pp": dhi,
            "status_at_0p5_pp": status(low, high, 0.5),
            "status_at_1p0_pp": status(low, high, 1.0),
        })
    csv_save_new(OUT / "new_runs.csv", raw)
    csv_save_new(OUT / "exploratory_summary.csv", summary)
    json_save_new(OUT / "manifest.json", {
        "status": "EX1_VIEWED_M5_EXPLORATORY_48_RUNS_COMPLETE",
        "frozen_protocol_sha256": sha(frozen_path),
        "baseline_archive_sha256": frozen["baseline_archive_sha256"],
        "new_runs_sha256": sha(OUT / "new_runs.csv"),
        "exploratory_summary_sha256": sha(OUT / "exploratory_summary.csv"),
        "new_solver_runs": N_NEW, "baseline_solver_runs_reused": 72,
        "scope": "viewed M5 graph, d=0 only; not independent evidence for b*/k",
    })
    print("EX1 VIEWED-GRAPH EXPLORATORY COMPLETE: 48 runs; no originals modified")
    for item in summary:
        print(f"{item['configuration']:4} gap={item['mean_gap_pct']:.4f}% "
              f"extra_vs_ref64={item['paired_ref64_extra_mean_pp']:+.4f} pp "
              f"95CI=[{item['paired_ref64_extra_ci95_lo_pp']:+.4f},"
              f"{item['paired_ref64_extra_ci95_hi_pp']:+.4f}] "
              f"screen_0.5={item['status_at_0p5_pp']}")


def freeze():
    selftest()
    baseline_and_source(verbose=True)
    data = protocol()
    if OUT.exists():
        raise FileExistsError("Output already exists; refusing new freeze")
    OUT.mkdir(parents=True)
    json_save_new(OUT / "protocol.json", data)
    print(f"EX1 PROTOCOL FROZEN: {OUT / 'protocol.json'}")
    print("NO NEW SOLVER RUNS. Review before --execute.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--selftest", action="store_true")
    grp.add_argument("--preflight", action="store_true")
    grp.add_argument("--freeze", action="store_true")
    grp.add_argument("--execute", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    elif args.preflight:
        selftest()
        baseline_and_source(verbose=True)
        print("EX1 PREFLIGHT PASS — no new solver runs")
    elif args.freeze:
        freeze()
    elif args.execute:
        execute()


if __name__ == "__main__":
    main()
