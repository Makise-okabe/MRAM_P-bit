#!/usr/bin/env python3
"""Registered two-contrast weak-tail analysis; whole generated graphs replicate.

The two directional ring hypotheses each use one-sided alpha .0125. All other
bounds are descriptive ordinary 95% intervals. Non-support never identifies a
different cause, and common-bank results are conditional on the shared bank.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
from pathlib import Path

import numpy as np

from experiments.fyp_ideal_analysis import bootstrap_t_vectors, write_csv, write_json
from experiments.fyp_tail_probe import (
    ARMS, CONTROLS, GRAPHS, SEEDS, UPDATES, K, RESULT_DIR, ROOT, SOURCE_DIR,
    digest, solver_seed, verify_freeze,
)

RESAMPLES = 500_000
ALPHA_ONE_SIDED = 0.0125
PAIRS = (("C1", "fp6_mask", "fp6"), ("C2", "int6", "int6_tail"))
METRICS = ("Rz_pp", "A_pp", "extra_pp", "selection_pp", "tie_pp", "buffer_gain_pp",
           "buffer_extra_pp", "minimum_distinct_states", "visited_distinct_states",
           "bank_Rz_pp", "bank_selection_pp", "bank_tie_pp", "bank_minimum_distinct_states")


def registry():
    return {"date": "2026-11-21", "confirmatory_family": "ring", "confirmatory": [
        {"name": name, "left": a, "right": b, "endpoint": "Rz_pp", "prediction": ">0",
         "one_sided_alpha": ALPHA_ONE_SIDED} for name, a, b in PAIRS],
        "confirmatory_familywise_alpha": 0.025, "resamples": RESAMPLES,
        "resampling_unit": "whole 24-graph vectors after paired-seed averaging",
        "bootstrap": "studentized bootstrap-t; PCG64DXSM; NumPy linear quantiles",
        "confirmatory_seed_sequence": [20261121, 940, 0],
        "descriptive_seed_sequence": "[20261121,940,family,1]",
        "common_bank": "pooled top16 states from all six arms and all64 seeds per graph; smallest state-integer breaks represented-energy ties",
        "buffer": "K16 distinct raw spin vectors; earliest first visit breaks represented-energy ties; original quality never retains a candidate",
        "reference": "B_control=max(0,V) over only FP64/FP6/INT6 x64, fixed once per graph; not an optimum",
        "counterfactual_cost": "original J accessible on host plus state transfer and host rescoring; no measured implementation saving",
        "diagnostic": "INT6_keep cannot refute the accurate-weak-tail hypothesis",
        "outcomes": "lower bound>0 supports directional hypothesis; otherwise NOT_ESTABLISHED; failure is not proof of a probability-error mechanism",
        "no_material_torus_effect": "descriptive prediction only; no equivalence margin registered",
        "descriptive_metrics": list(METRICS),
        "interaction": "(FP6_mask-FP6)-(INT6-INT6_tail), reported for Rz/A/extra",
        "coefficient_factorization": "S={INT6 nonzero}; T=FP6 values outside S; four cells F_S+T, F_S, I_S+T, I_S",
        "stop": "after mechanism checkpoint; no offset/gain/hardware work"}


def read_gzip(path):
    with gzip.open(path, "rt") as handle:
        return json.load(handle)


def verify_records(rows, family, index):
    expected = {(a, solver_seed(family, index, r)) for a in ARMS for r in range(SEEDS)}
    keys = [(r["representation"], r["seed"]) for r in rows]
    if len(keys) != len(expected) or set(keys) != expected:
        raise ValueError("unexpected or duplicate run keys")
    for row in rows:
        payload = {k: v for k, v in row.items() if k != "record_sha256"}
        from experiments.fyp_first_block_20261120 import canonical
        import hashlib
        if hashlib.sha256(canonical(payload).encode()).hexdigest() != row["record_sha256"]:
            raise ValueError("record hash mismatch")
        if row["attempted_updates"] != UPDATES or row["gain"] != 1 or row["offset_logit"] != 0:
            raise ValueError("unregistered response or update budget")
        if row["V"] < row["M"] or row["M"] < row["R"] or row["M"] < row["R_last"]:
            raise ValueError("trajectory ordering violated")
        if not 1 <= len(row["buffer"]) <= K:
            raise ValueError("buffer cap violated")
        if len({p["state_hex"] for p in row["buffer"]}) != len(row["buffer"]):
            raise ValueError("duplicate buffered state")
        if row["representation"] == "ref64" and row["R"] != row["V"]:
            raise ValueError("FP64 return is not original visited best")


def summarize_graph(rows, bank, metrics, manifest):
    by = {(r["representation"], r["seed"]): r for r in rows}
    graph = f'{manifest["family"]}_{manifest["index"]:03d}'
    b = manifest["B_control"]
    if b != max(0, max(r["V"] for r in rows if r["representation"] in CONTROLS)):
        raise ValueError("reference pool mismatch")
    banks = {r["representation"]: r for r in bank["results"]}
    results = []
    for arm in ARMS:
        arm_rows = [r for r in rows if r["representation"] == arm]
        data = {key: [] for key in METRICS[:9]}
        for r in arm_rows:
            ref = by[("ref64", r["seed"])]
            data["Rz_pp"].append(100*(r["V"]-r["R"])/b)
            data["A_pp"].append(100*(ref["V"]-r["V"])/b)
            data["extra_pp"].append(100*(ref["R"]-r["R"])/b)
            data["selection_pp"].append(100*(r["V"]-r["M"])/b)
            data["tie_pp"].append(100*(r["M"]-r["R"])/b)
            data["buffer_gain_pp"].append(100*(r["buffer_best_original_cut"]-r["R"])/b)
            data["buffer_extra_pp"].append(100*(ref["R"]-r["buffer_best_original_cut"])/b)
            data["minimum_distinct_states"].append(r["minimum_distinct_states"])
            data["visited_distinct_states"].append(r["visited_distinct_states"])
        summary = {"family": manifest["family"], "index": manifest["index"], "graph": graph,
                   "representation": arm, "seeds": SEEDS, "B_control": b,
                   "nonzero_count": metrics[arm]["nonzero_count"],
                   "coefficient_mse": metrics[arm]["coefficient_mse"],
                   "bank_size": len(bank["states"]),
                   **{key: float(np.mean(values)) for key, values in data.items()}}
        z = banks[arm]
        summary.update(bank_Rz_pp=100*z["total_loss_cut"]/b,
                       bank_selection_pp=100*z["selection_loss_cut"]/b,
                       bank_tie_pp=100*z["tie_loss_cut"]/b,
                       bank_minimum_distinct_states=z["minimum_distinct_states"])
        if not math.isclose(summary["extra_pp"], summary["A_pp"]+summary["Rz_pp"], abs_tol=1e-11):
            raise AssertionError("extra = access + selection failed")
        results.append(summary)
    return results


def describe_bounds(values, family, resamples=RESAMPLES):
    return bootstrap_t_vectors(values, q=0.025, resamples=resamples,
                               seed_sequence=[20261121, 940, family, 1])


def scientific_analysis(graph_rows, out, resamples=RESAMPLES):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    by = {(r["family"], r["index"], r["representation"]): r for r in graph_rows}
    if len(by) != 48*6 or len(graph_rows) != len(by):
        raise ValueError("exactly 48 complete six-arm graph summaries required")
    confirm = np.asarray([[by[("ring", g, a)]["Rz_pp"]-by[("ring", g, b)]["Rz_pp"]
                           for _, a, b in PAIRS] for g in range(GRAPHS)])
    bounds = bootstrap_t_vectors(confirm, q=ALPHA_ONE_SIDED, resamples=resamples,
                                 seed_sequence=[20261121, 940, 0])
    contrasts = []
    for (name, a, b), result in zip(PAIRS, bounds):
        supported = result["low"] is not None and result["low"] > 0
        contrasts.append({"contrast": name, "left": a, "right": b, "metric": "Rz_pp",
                          "family": "ring", "graphs": GRAPHS, **result,
                          "decision": "SUPPORTED" if supported else "NOT_ESTABLISHED",
                          "one_sided_alpha": ALPHA_ONE_SIDED,
                          "bound_reading": "low is the confirmatory 98.75% one-sided lower bound; high shown for context"})
    family_rows, interactions = [], []
    for f, family in enumerate(("ring", "torus")):
        keys = [(a, key) for a in ARMS for key in METRICS]
        values = np.asarray([[by[(family, g, a)][key] for a, key in keys] for g in range(GRAPHS)])
        db = describe_bounds(values, f, resamples)
        for (arm, key), result in zip(keys, db):
            family_rows.append({"family": family, "representation": arm, "metric": key,
                                "scope": "DESCRIPTIVE_95_PERCENT_GRAPH_BOOTSTRAP", **result})
        iv = np.asarray([[by[(family, g, "fp6_mask")][key]-by[(family, g, "fp6")][key]
                          -by[(family, g, "int6")][key]+by[(family, g, "int6_tail")][key]
                          for key in ("Rz_pp", "A_pp", "extra_pp")] for g in range(GRAPHS)])
        ib = describe_bounds(iv, f, resamples)
        for key, result in zip(("Rz_pp", "A_pp", "extra_pp"), ib):
            interactions.append({"family": family, "metric": key,
                                 "scope": "DESCRIPTIVE_95_PERCENT_GRAPH_BOOTSTRAP", **result})
    write_csv(out/"confirmatory.csv", contrasts)
    write_csv(out/"graph_summary.csv", graph_rows)
    write_csv(out/"family_descriptive.csv", family_rows)
    write_csv(out/"factorial_interaction.csv", interactions)
    write_json(out/"registry.json", registry())
    write_json(out/"analysis_summary.json", {"confirmatory": contrasts, "family": family_rows,
                                            "interaction": interactions, "offset_executed": False,
                                            "generated_graphs": 48, "solver_runs": 18432})
    return {"confirmatory": contrasts, "family": family_rows, "interaction": interactions}


def analyse(freeze_commit, base=RESULT_DIR):
    verify_freeze(freeze_commit)
    rows, checks = [], []
    for family, name in enumerate(("ring", "torus")):
        for index in range(GRAPHS):
            folder = Path(base)/name/f"{index:03d}"
            if (folder/"IN_PROGRESS").exists() or (folder/"FAILED").exists():
                raise ValueError("partial/failed bundle: "+str(folder))
            manifest = json.loads((folder/"manifest.json").read_text())
            if manifest["freeze_commit"] != freeze_commit:
                raise ValueError("mixed execution freezes")
            for p, sha in manifest["files"].items():
                if digest(folder/p) != sha:
                    raise ValueError("bundle hash mismatch")
            raw = read_gzip(folder/"records.json.gz")
            verify_records(raw, family, index)
            bank = read_gzip(folder/"common_bank.json.gz")
            metrics = json.loads((folder/"representations.json").read_text())
            rows.extend(summarize_graph(raw, bank, metrics, manifest))
            checks.append({"family": name, "index": index, "records": len(raw),
                           "manifest_sha256": digest(folder/"manifest.json")})
    save = Path(base)/"analysis"
    result = scientific_analysis(rows, save)
    write_json(Path(base)/"verification.json", {"status": "PASS", "freeze_commit": freeze_commit,
                 "graphs": 48, "arms": list(ARMS), "seeds_per_arm": SEEDS,
                 "raw_records": sum(x["records"] for x in checks), "bundles": checks,
                 "offset_executed": False, "gain": 1.0, "offset": 0.0})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    result = analyse(args.freeze_commit)
    print(json.dumps(result["confirmatory"], indent=2, allow_nan=False))
