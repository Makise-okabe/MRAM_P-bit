#!/usr/bin/env python3
"""Analysis of the 20 November locked ideal-response study; never runs a solver.

Generated inference uses nine registered contrasts in each of two families (18
total), jointly resampled whole-graph vectors.  Mechanism endpoints and anchors
are descriptive.  Existing first-block files are read-only inputs.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

CANDIDATES = ("fp5", "fp6", "int5", "int6", "int7", "int8", "ref64")
LOW_PRECISION = CANDIDATES[:-1]
FAMILIES = ("ring", "torus")
CORE_PAIRS = (("fp6", "int6"), ("fp5", "int6"), ("fp6", "int7")) + tuple(
    (name, "ref64") for name in LOW_PRECISION
)
CORE_REGISTRY = tuple((family, left, right) for family in FAMILIES for left, right in CORE_PAIRS)
MECHANISM_PAIRS = (("fp5", "int6"), ("fp6", "int7"), ("fp6", "int6"))
PREDICTIONS = {"fp5-int6": "positive", "fp6-int7": "positive", "fp6-int6": "none"}
ALPHA_CORE = 0.04
CORE_TAIL_Q = ALPHA_CORE / (2 * len(CORE_REGISTRY))
RESAMPLES = 500_000
QUANTILE_METHOD = "linear"
MARGINS = (0.25, 0.5, 1.0)
CHECKPOINTS = (5000, 15000, 30000, 50000)


def analysis_registry():
    """Machine-readable settings to include in the executable freeze."""
    return {
        "core": [{"family": f, "left": a, "right": b, "contrast": f"{a}-{b}"}
                 for f, a, b in CORE_REGISTRY],
        "core_count_total": 18, "core_count_per_family": 9,
        "alpha_core": ALPHA_CORE, "one_tail_q": CORE_TAIL_Q,
        "resamples": RESAMPLES, "quantile": "numpy linear", "rng": "PCG64DXSM",
        "core_seed_sequences": {f: [20261120, 940, i] for i, f in enumerate(FAMILIES)},
        "descriptive_seed_sequences": {f: [20261120, 940, i, 1] for i, f in enumerate(FAMILIES)},
        "anchor_seed_sequences": "[20261120,940,family,2,anchor_label_index]; labels 5555=0,6666=1,7777=2",
        "primary_margin_pp": 0.5, "sensitivity_margins_pp": [0.25, 1.0],
        "resampling_unit": "whole graph vector; no nested seed resampling",
        "reference": "B_g=max(0,V) over exactly 128 reference and 7*64 main trajectories",
        "deterministic_equality": "requires external algebraic/kernel proof; observed zero variance alone is unresolved",
        "descriptive": {
            "alpha_from_core": 0,
            "contrasts": [{"left": a, "right": b, "rz_prediction": PREDICTIONS[f"{a}-{b}"]}
                          for a, b in MECHANISM_PAIRS],
            "interval": "ordinary two-sided 95% bootstrap-t, whole-graph-vector resampling",
            "endpoints": ["Rz difference", "access A difference", "graph sign counts",
                          "SD of graph means", "median within-graph standard error",
                          "per-candidate Spearman(Rz/A,probability_mae/field_rms/zeroed_weight_mass_fraction)",
                          "signed R_last-R"],
            "no_direction": ["fp6-int6"],
            "Rz_sign_caveat": "Rz is nonnegative by definition; its sign is not mechanism evidence",
            "R_last_missing": "not reconstructed or zero-filled for reused first-block rows",
        },
    }


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _clean(obj):
    if isinstance(obj, dict):
        return {str(k): _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _clean(obj.tolist())
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return float(obj) if math.isfinite(float(obj)) else None
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def write_json(path, obj):
    Path(path).write_text(json.dumps(_clean(obj), sort_keys=True, indent=2, allow_nan=False) + "\n")


def write_csv(path, rows):
    rows = [_clean(r) for r in rows]
    if not rows:
        Path(path).write_text("")
        return
    fields = list(rows[0])
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})


def read_records(path):
    """Read JSONL/gzip and verify any per-record hash without altering inputs."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    rows = []
    with opener(path, "rt", encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            if not line.strip():
                raise ValueError(f"blank record {path}:{number}")
            row = json.loads(line)
            if "record_sha256" in row:
                payload = {k: v for k, v in row.items() if k != "record_sha256"}
                if hashlib.sha256(canonical(payload).encode()).hexdigest() != row["record_sha256"]:
                    raise ValueError(f"record digest mismatch {path}:{number}")
            rows.append(row)
    return rows


def decision_labels(mean, low, high, tolerance=0.5):
    """Claims overlap; the NI label is decided at +tolerance, never at zero."""
    finite = all(v is not None and math.isfinite(float(v)) for v in (mean, low, high))
    if not finite:
        return {"qualification": "UNRESOLVED", "interval_status": "UNDEFINED_OR_UNSTABLE",
                "statistical_superiority": False, "statistical_inferiority": False,
                "estimated_benefit_gt_margin": bool(mean is not None and math.isfinite(float(mean)) and mean < -tolerance),
                "true_benefit_gt_margin": False, "non_inferior": False,
                "practically_equivalent": False, "penalty_exceeds_tolerance": False,
                "noninferiority_unresolved": True, "benefit_at_least_margin_ruled_out": False}
    if low > high:
        raise ValueError("inverted confidence bounds")
    ni, fail = high < tolerance, low > tolerance
    return {"qualification": "PASS" if ni else "FAIL" if fail else "UNRESOLVED",
            "interval_status": "FINITE", "statistical_superiority": high < 0,
            "statistical_inferiority": low > 0, "estimated_benefit_gt_margin": mean < -tolerance,
            "true_benefit_gt_margin": high < -tolerance, "non_inferior": ni,
            "practically_equivalent": low > -tolerance and high < tolerance,
            "penalty_exceeds_tolerance": fail, "noninferiority_unresolved": not (ni or fail),
            "benefit_at_least_margin_ruled_out": low > -tolerance}


def bootstrap_t_vectors(values, *, q=CORE_TAIL_Q, resamples=RESAMPLES,
                        seed_sequence=(20261120, 940, 0), batch=2048,
                        deterministic_equal=None):
    """Joint graph-vector resampling; each column receives its own t pivot.

    Analytically proven zero contrasts may be marked deterministic_equal. An
    observed constant vector alone never supplies a degenerate certainty claim.
    Any zero/nonfinite resampled standard error makes that column unresolved;
    it is not silently discarded. Other columns continue with identical indices.
    """
    x = np.asarray(values, dtype=np.float64)
    if x.ndim == 1:
        x = x[:, None]
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 1 or not np.all(np.isfinite(x)):
        raise ValueError("finite n-by-p observations with n>=2 required")
    if not (0 < q < 0.5) or int(resamples) != resamples or resamples < 2 or batch < 1:
        raise ValueError("invalid bootstrap settings")
    n, p = x.shape
    proven = np.zeros(p, dtype=bool) if deterministic_equal is None else np.asarray(deterministic_equal, dtype=bool)
    if proven.shape != (p,) or np.any(proven & np.any(x != 0, axis=0)):
        raise ValueError("deterministic equality must prove an identically zero column")
    means = x.mean(axis=0)
    ses = x.std(axis=0, ddof=1) / math.sqrt(n)
    constant = np.ptp(x, axis=0) == 0
    active = (~constant) & np.isfinite(ses) & (ses > 0)
    active_indices = np.flatnonzero(active)
    bad_counts = np.zeros(p, dtype=np.int64)
    pivots = np.empty((resamples, len(active_indices)), dtype=np.float64)
    rng = np.random.Generator(np.random.PCG64DXSM(np.random.SeedSequence(seed_sequence)))
    xa = x[:, active_indices]
    for start in range(0, resamples if len(active_indices) else 0, batch):
        size = min(batch, resamples - start)
        indices = rng.integers(0, n, size=(size, n))
        if not len(active_indices):
            continue
        samples = xa[indices]
        bm = samples.mean(axis=1)
        bs = samples.std(axis=1, ddof=1) / math.sqrt(n)
        bad = (~np.isfinite(bs)) | (bs <= 0)
        bad_counts[active_indices] += bad.sum(axis=0)
        with np.errstate(divide="ignore", invalid="ignore"):
            pivots[start:start + size] = (bm - means[active_indices]) / bs
    results = []
    active_pos = {col: ix for ix, col in enumerate(active_indices)}
    for col in range(p):
        entry = {"n": n, "mean": float(means[col]), "se": float(ses[col]),
                 "low": None, "high": None, "status": "UNRESOLVED_STUDENTIZATION",
                 "q": q, "resamples": int(resamples), "bad_resamples": int(bad_counts[col])}
        if proven[col]:
            entry.update(low=0.0, high=0.0, status="DETERMINISTIC_EQUALITY_PROVEN")
        elif active[col] and not bad_counts[col]:
            t = pivots[:, active_pos[col]]
            if np.all(np.isfinite(t)):
                loq, hiq = np.quantile(t, [q, 1-q], method=QUANTILE_METHOD)
                entry.update(low=float(means[col] - hiq * ses[col]),
                             high=float(means[col] - loq * ses[col]), status="OK")
        results.append(entry)
    return results


def _fmt(row):
    value = str(row.get("representation", row.get("configuration", ""))).lower()
    return "ref64" if value in ("fp64", "ref64") else value


def _cut(row, key):
    if key not in row and key == "R":
        return float(row["returned_original_cut"])
    return float(row[key])


def fixed_reference_pool(main_rows, reference_rows, *, verify_cut=None,
                         seeds_per_candidate=64, reference_count=128):
    """Largest original cut V observed in exactly the locked trajectory pool."""
    main_rows, reference_rows = list(main_rows), list(reference_rows)
    if len(main_rows) != seeds_per_candidate * len(CANDIDATES) or len(reference_rows) != reference_count:
        raise ValueError("reference pool must have exactly the registered main/reference counts")
    main_keys = {(_fmt(r), int(r["seed"])) for r in main_rows}
    if len(main_keys) != len(main_rows):
        raise ValueError("duplicate main key in reference pool")
    seed_sets = [{int(r["seed"]) for r in main_rows if _fmt(r) == f} for f in CANDIDATES]
    if any(len(s) != seeds_per_candidate or s != seed_sets[0] for s in seed_sets):
        raise ValueError("unpaired/incomplete main reference pool")
    reference_seeds = [int(r["seed"]) for r in reference_rows]
    if len(set(reference_seeds)) != reference_count or any(_fmt(r) != "ref64" for r in reference_rows):
        raise ValueError("invalid independent reference pool")
    if set(reference_seeds) & seed_sets[0]:
        raise ValueError("reference/main random streams overlap")
    result = {"B_g": 0, "value_field": "V", "witness_state_hex": "0",
              "witness_representation": "empty_cut", "witness_seed": None,
              "witness_stage": "empty_cut", "pool_main_count": len(main_rows),
              "pool_reference_count": len(reference_rows), "rescore_verified": False,
              "reference_label": "largest feasible original cut observed in locked trajectory pool"}
    candidates = [("reference", r) for r in reference_rows] + [("main", r) for r in main_rows]
    for stage, row in sorted(candidates, key=lambda z: (z[0], _fmt(z[1]), int(z[1]["seed"]))):
        value = _cut(row, "V")
        if not math.isfinite(value) or value != int(value):
            raise ValueError("reference witness cut must be a finite integer")
        if value > result["B_g"]:
            result.update(B_g=int(value), witness_state_hex=row["V_state_hex"],
                          witness_representation=_fmt(row), witness_seed=int(row["seed"]), witness_stage=stage)
    if verify_cut is not None:
        scored = verify_cut(result["witness_state_hex"])
        if int(scored) != scored or int(scored) != result["B_g"]:
            raise ValueError("reference witness does not rescore exactly")
        result["rescore_verified"] = True
    result["normalized_qualification_defined"] = result["B_g"] > 0
    return result


def mechanism_values(candidate, matched_reference, denominator):
    """Per-run extra gap = A + Rz_candidate - Rz_FP64."""
    if not math.isfinite(denominator) or denominator <= 0:
        raise ValueError("positive normalizing reference required")
    v, m, r = (_cut(candidate, k) for k in ("V", "M", "R"))
    vr, mr, rr = (_cut(matched_reference, k) for k in ("V", "M", "R"))
    if not (v >= m >= r and vr >= mr >= rr):
        raise ValueError("invalid pathwise ordering")
    k = 100.0 / denominator
    a, rz, rzref = k*(vr-v), k*(v-r), k*(vr-rr)
    extra = k*(rr-r)
    if not math.isclose(extra, a + rz - rzref, rel_tol=1e-11, abs_tol=1e-11):
        raise ValueError("extra-gap decomposition failed")
    last = candidate.get("R_last")
    return {"A_pp": a, "Rz_pp": rz, "Rz_reference_pp": rzref,
            "represented_selection_pp": k*(v-m), "earliest_tie_pp": k*(m-r),
            "extra_pp": extra, "R_last_minus_R": None if last is None else float(last)-r,
            "R_last_minus_R_pp": None if last is None else k*(float(last)-r)}


def _se(values):
    a = np.asarray(values, dtype=float)
    return float(a.std(ddof=1) / math.sqrt(len(a))) if len(a) >= 2 else None


def _family(value):
    if value in (0, "0", "ring"):
        return "ring"
    if value in (1, "1", "torus"):
        return "torus"
    raise ValueError(f"unknown family {value!r}")


def summarize_graph(main_rows, fidelity_rows, representation_metrics, *, graph, family,
                    denominator, denominator_label, reference_B=None, kind="generated",
                    expected_seeds=64, candidates=CANDIDATES, index=None):
    """Create the complete graph vector, retaining paired seed arrays for diagnostics."""
    rows = list(main_rows)
    lookup = {(_fmt(r), int(r["seed"])): r for r in rows}
    if len(lookup) != len(rows) or len(rows) != expected_seeds*len(candidates):
        raise ValueError("incomplete or duplicate main rows")
    seeds = sorted(int(r["seed"]) for r in rows if _fmt(r) == "ref64")
    if len(seeds) != expected_seeds or len(set(seeds)) != expected_seeds:
        raise ValueError("invalid FP64 seed set")
    if set(lookup) != {(f, s) for f in candidates for s in seeds}:
        raise ValueError("unpaired candidate seed sets")
    fid = {}
    for r in fidelity_rows:
        key = (_fmt(r), int(r["seed"]), int(r["attempt"]))
        if key in fid:
            raise ValueError("duplicate common-state fidelity key")
        fid[key] = r
    output = {"graph": graph, "family": _family(family), "index": index, "kind": kind,
              "denominator": denominator, "denominator_label": denominator_label,
              "B_g": reference_B, "n_seeds": expected_seeds, "candidates": {},
              "paired": {}, "core": {}, "mechanism": {}}
    defined = denominator is not None and math.isfinite(float(denominator)) and denominator > 0
    for f in candidates:
        rr = [lookup[(f, s)] for s in seeds]
        returned = np.asarray([_cut(r, "R") for r in rr])
        mm = [mechanism_values(r, lookup[("ref64", s)], denominator) for r, s in zip(rr, seeds)] if defined else []
        one = {"mean_returned_cut": float(returned.mean()), "sd_returned_cut": float(returned.std(ddof=1)),
               "mean_shortfall_pp": float(100*(denominator-returned.mean())/denominator) if defined else None,
               "mean_reference_normalized_shortfall_pp": float(100*(reference_B-returned.mean())/reference_B)
                    if reference_B is not None and reference_B > 0 else None,
               "mean_extra_pp": float(np.mean([r["extra_pp"] for r in mm])) if defined else None,
               "mean_A_pp": float(np.mean([r["A_pp"] for r in mm])) if defined else None,
               "mean_Rz_pp": float(np.mean([r["Rz_pp"] for r in mm])) if defined else None,
               "mean_represented_selection_pp": float(np.mean([r["represented_selection_pp"] for r in mm])) if defined else None,
               "mean_earliest_tie_pp": float(np.mean([r["earliest_tie_pp"] for r in mm])) if defined else None,
               "within_se_A_pp": _se([r["A_pp"] for r in mm]) if defined else None,
               "within_se_Rz_pp": _se([r["Rz_pp"] for r in mm]) if defined else None}
        last_diffs = [float(r["R_last"])-_cut(r, "R") for r in rr if r.get("R_last") is not None]
        one.update(R_last_available=len(last_diffs), R_last_missing=expected_seeds-len(last_diffs),
                   mean_R_last_minus_R=float(np.mean(last_diffs)) if last_diffs else None,
                   mean_R_last_minus_R_pp=float(100*np.mean(last_diffs)/denominator) if last_diffs and defined else None,
                   R_last_positive=int(sum(v>0 for v in last_diffs)),
                   R_last_negative=int(sum(v<0 for v in last_diffs)), R_last_zero=int(sum(v==0 for v in last_diffs)))
        source = representation_metrics.get(f, {})
        one["zeroed_weight_mass_fraction"] = source.get("zeroed_weight_mass_fraction", source.get("zeroed_abs_weight_mass_fraction"))
        one["nonzero_count"] = source.get("nonzero_count")
        if f == "ref64":
            one.update(field_rms=0.0, logit_rms=0.0, probability_mae=0.0)
        else:
            chunk = [fid[(f, s, t)] for s in seeds for t in CHECKPOINTS if (f, s, t) in fid]
            if len(chunk) != expected_seeds*len(CHECKPOINTS):
                raise ValueError(f"incomplete common-state fidelity for {graph}:{f}")
            for metric in ("field_rms", "logit_rms", "probability_mae"):
                one[metric] = float(np.mean([r.get(metric, r.get("prob_mae")) if metric == "probability_mae" else r[metric] for r in chunk]))
        output["candidates"][f] = one
        output["paired"][f] = {"seeds": seeds, "R": returned.tolist(),
                               **{key: [r[key] for r in mm] for key in ("A_pp", "Rz_pp", "extra_pp")}}
    for left, right in CORE_PAIRS:
        if left not in candidates or right not in candidates:
            continue
        name = f"{left}-{right}"
        if defined:
            a, b = np.asarray(output["paired"][left]["R"]), np.asarray(output["paired"][right]["R"])
            diff = 100*(b-a)/denominator
            output["core"][name] = {"mean": float(diff.mean()), "within_se": _se(diff), "paired_values": diff.tolist()}
        else:
            output["core"][name] = {"mean": None, "within_se": None, "paired_values": []}
    for left, right in MECHANISM_PAIRS:
        if left not in candidates or right not in candidates:
            continue
        name = f"{left}-{right}"
        entry = {"prediction_Rz": PREDICTIONS[name]}
        for metric in ("A_pp", "Rz_pp"):
            diff = np.asarray(output["paired"][left][metric]) - np.asarray(output["paired"][right][metric])
            entry[metric] = {"mean": float(diff.mean()) if len(diff) else None,
                             "within_se": _se(diff) if len(diff) else None, "paired_values": diff.tolist()}
        output["mechanism"][name] = entry
    return output


def rank_average(values):
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or not np.all(np.isfinite(x)):
        raise ValueError("finite rank vector required")
    order = np.argsort(x, kind="stable")
    ranks = np.empty(len(x), dtype=float)
    lo = 0
    while lo < len(x):
        hi = lo+1
        while hi < len(x) and x[order[hi]] == x[order[lo]]:
            hi += 1
        ranks[order[lo:hi]] = (lo+hi-1)/2 + 1
        lo = hi
    return ranks


def spearman(x, y):
    """Descriptive rank correlation with average ranks; no p-value or alpha use."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError("paired correlation vectors required")
    if len(x) < 3 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        return {"rho": None, "n": len(x), "status": "UNDEFINED_NONFINITE_OR_TOO_FEW"}
    a, b = rank_average(x), rank_average(y)
    if np.ptp(a) == 0 or np.ptp(b) == 0:
        return {"rho": None, "n": len(x), "status": "UNDEFINED_CONSTANT_RANKS"}
    return {"rho": float(np.corrcoef(a, b)[0, 1]), "n": len(x), "status": "DESCRIPTIVE"}


def select_pair(core_rows):
    """Frozen lowest-certified selection; missing either class invokes fallback."""
    lookup = {row["contrast"]: row for row in core_rows}
    labels = {f: lookup[f"{f}-ref64"]["qualification"] for f in LOW_PRECISION}
    fp = [f for f in ("fp5", "fp6") if labels[f] == "PASS"]
    integer = [f for f in ("int5", "int6", "int7", "int8") if labels[f] == "PASS"]
    selected_fp = fp[0] if fp else None
    selected_int = integer[0] if integer else None
    fallback = selected_fp is None or selected_int is None
    result = {"lowest_tested_certified_FP": selected_fp, "lowest_tested_certified_INT": selected_int,
              "qualification": labels, "selected_FP": "fp6" if fallback else selected_fp,
              "selected_INT": "int6" if fallback else selected_int, "matched_reference": "ref64",
              "diagnostic_fallback": fallback, "offset_run_authorized": False,
              "true_minimum_claim": "not inferred from a lowest certified choice",
              "k_cert": None if fallback else int(selected_int[3:])-int(selected_fp[2:])}
    if not fallback:
        pair_name = f"{selected_fp}-{selected_int}"
        if pair_name in lookup:
            pair = lookup[pair_name]
            lo, hi = pair["low"], pair["high"]
            method = "registered_direct_contrast"
        else:
            f, i = lookup[f"{selected_fp}-ref64"], lookup[f"{selected_int}-ref64"]
            lo = None if f["low"] is None or i["high"] is None else f["low"]-i["high"]
            hi = None if f["high"] is None or i["low"] is None else f["high"]-i["low"]
            method = "conservative_difference_of_simultaneous_bounds"
        result["selected_pair_bounds"] = {"low": lo, "high": hi, "method": method,
                                          "pairwise_NI": hi is not None and hi < 0.5}
        result["smaller_unresolved_FP"] = [f for f in ("fp5", "fp6") if int(f[2:]) < int(selected_fp[2:]) and labels[f] == "UNRESOLVED"]
        result["smaller_unresolved_INT"] = [f for f in ("int5", "int6", "int7", "int8") if int(f[3:]) < int(selected_int[3:]) and labels[f] == "UNRESOLVED"]
    return result


def _interval_rows(matrix, names, family, *, q, resamples, seed_sequence, scope):
    if not np.all(np.isfinite(matrix)):
        means = [float(np.mean(v)) if np.all(np.isfinite(v)) else None for v in np.asarray(matrix).T]
        bounds = [{"mean": m, "low": None, "high": None, "se": None,
                   "status": "UNRESOLVED_UNDEFINED_REFERENCE", "bad_resamples": None} for m in means]
    else:
        bounds = bootstrap_t_vectors(matrix, q=q, resamples=resamples, seed_sequence=seed_sequence)
    rows = []
    for name, bound in zip(names, bounds):
        rows.append({"family": family, "contrast": name, "scope": scope, "graphs": len(matrix),
                     "mean": bound["mean"], "low": bound["low"], "high": bound["high"],
                     "se": bound["se"], "interval_status": bound["status"],
                     "bad_resamples": bound["bad_resamples"], "one_tail_q": q,
                     "resamples": resamples})
    return rows


def analyse_graph_summaries(groups, out, *, resamples=RESAMPLES, expected_graphs=72):
    """No solver work. Emit deterministic tables/figures for the frozen bundles."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    generated = [g for g in groups if g["kind"] == "generated"]
    anchors = [g for g in groups if g["kind"] == "anchor"]
    if len({g["graph"] for g in groups}) != len(groups):
        raise ValueError("duplicate graph summary")
    core_rows, mechanism_rows, correlations, candidate_rows, last_rows = [], [], [], [], []
    graph_contrasts = []
    chosen = {}
    names = [f"{a}-{b}" for a, b in CORE_PAIRS]
    for fi, family in enumerate(FAMILIES):
        gg = sorted([g for g in generated if g["family"] == family], key=lambda g: g["index"])
        if len(gg) != expected_graphs:
            raise ValueError(f"{family}: expected {expected_graphs} graphs, got {len(gg)}")
        matrix = np.asarray([[g["core"][name]["mean"] for name in names] for g in gg], dtype=float)
        rows = _interval_rows(matrix, names, family, q=CORE_TAIL_Q, resamples=resamples,
                              seed_sequence=[20261120, 940, fi], scope="CORE_SIMULTANEOUS_GENERATED_REFERENCE_SHORTFALL")
        for row in rows:
            labels = decision_labels(row["mean"], row["low"], row["high"])
            row["qualification"] = labels["qualification"]
            row["labels_0p5"] = labels
            row["labels_0p25"] = decision_labels(row["mean"], row["low"], row["high"], 0.25)
            row["labels_1p0"] = decision_labels(row["mean"], row["low"], row["high"], 1.0)
        chosen[family] = select_pair(rows)
        core_rows.extend(rows)
        mnames = [f"{a}-{b}/{metric}" for a, b in MECHANISM_PAIRS for metric in ("Rz_pp", "A_pp")]
        mm = np.asarray([[g["mechanism"][name.split('/')[0]][name.split('/')[1]]["mean"] for name in mnames] for g in gg], dtype=float)
        mrows = _interval_rows(mm, mnames, family, q=0.025, resamples=resamples,
                               seed_sequence=[20261120, 940, fi, 1], scope="DESCRIPTIVE_GRAPH_RESAMPLED_95_PERCENT")
        for j, row in enumerate(mrows):
            pair, metric = row["contrast"].split('/')
            vals = mm[:, j]
            finite = np.all(np.isfinite(vals))
            within = [g["mechanism"][pair][metric]["within_se"] for g in gg]
            row.update(metric=metric, contrast=pair, graph_positive=int(np.sum(vals>0)),
                       graph_negative=int(np.sum(vals<0)), graph_zero=int(np.sum(vals==0)),
                       sd_graph_means=float(np.std(vals, ddof=1)) if finite else None,
                       typical_within_graph_se=float(np.median(within)) if all(v is not None for v in within) else None,
                       typical_se_definition="median of per-graph paired-seed SE",
                       alpha_from_core=0,
                       prediction=PREDICTIONS[pair] if metric == "Rz_pp" else "none")
            if row["prediction"] == "positive":
                row["prediction_point_status"] = "CONSISTENT" if row["mean"] is not None and row["mean"]>0 else "FAILED_OR_UNDEFINED"
                row["prediction_interval_status"] = "DESCRIPTIVE_POSITIVE" if row["low"] is not None and row["low"]>0 else "DESCRIPTIVE_OPPOSITE" if row["high"] is not None and row["high"]<0 else "UNRESOLVED"
            else:
                row["prediction_point_status"] = "NO_DIRECTION_PREDICTED"
                row["prediction_interval_status"] = "NO_DIRECTION_PREDICTED"
            mechanism_rows.append(row)
        for f in LOW_PRECISION:
            for endpoint in ("mean_Rz_pp", "mean_A_pp"):
                for metric in ("probability_mae", "field_rms", "zeroed_weight_mass_fraction"):
                    values_x = [g["candidates"][f][endpoint] for g in gg]
                    values_y = [g["candidates"][f][metric] for g in gg]
                    corr = spearman(values_x, values_y)
                    correlations.append({"family": family, "representation": f, "endpoint": endpoint,
                                         "predictor": metric, "scope": "DESCRIPTIVE_NO_ALPHA_OR_P_VALUE", **corr})
        for g in gg:
            for name in names:
                c = g["core"][name]
                graph_contrasts.append({"family": family, "graph": g["graph"], "index": g["index"],
                                        "contrast": name, "mean": c["mean"], "within_seed_se": c["within_se"],
                                        "B_g": g["B_g"], "denominator_label": g["denominator_label"]})
    for g in groups:
        for fmt, c in g["candidates"].items():
            candidate_rows.append({"kind": g["kind"], "family": g["family"], "graph": g["graph"],
                                   "representation": fmt, "n_seeds": g["n_seeds"], "denominator": g["denominator"],
                                   "denominator_label": g["denominator_label"], "B_g": g["B_g"], **c})
            last_rows.append({"kind": g["kind"], "family": g["family"], "graph": g["graph"],
                              "representation": fmt, "scope": "DESCRIPTIVE_SIGNED_LATEST_MINUS_EARLIEST",
                              **{k:v for k,v in c.items() if "R_last" in k}})
    family_quality = []
    for family in FAMILIES:
        gg = [g for g in generated if g["family"] == family]
        for fmt in CANDIDATES:
            cc = [g["candidates"][fmt] for g in gg]
            row = {"family": family, "representation": fmt, "graphs": len(gg),
                   "scope": "DESCRIPTIVE_EQUAL_GRAPH_MEANS_B_g_NOT_OPTIMUM"}
            for metric in ("mean_returned_cut", "mean_shortfall_pp", "mean_extra_pp", "mean_A_pp", "mean_Rz_pp", "mean_R_last_minus_R", "mean_R_last_minus_R_pp"):
                values = [c[metric] for c in cc]
                row[metric] = float(np.mean(values)) if all(v is not None for v in values) else None
            for metric in ("R_last_available", "R_last_missing", "R_last_positive", "R_last_negative", "R_last_zero"):
                row[metric] = sum(c[metric] for c in cc)
            family_quality.append(row)
    anchor_rows, anchor_intervals, anchor_quality = [], [], []
    for g in anchors:
        gg = [x for x in generated if x["family"] == g["family"]]
        b = g["B_g"]
        fi = FAMILIES.index(g["family"])
        hi = ("5555", "6666", "7777").index(g["graph"].split('_')[-1])
        matrix = np.asarray([g["core"][name]["paired_values"] for name in names], dtype=float).T
        ordinary = _interval_rows(matrix, names, g["family"], q=.025, resamples=resamples,
                                  seed_sequence=[20261120,940,fi,2,hi], scope="DESCRIPTIVE_FIXED_ANCHOR_PAIRED_SEED_95_PERCENT")
        for row in ordinary:
            row["paired_seeds"] = row.pop("graphs")
            row["graph"] = g["graph"]
            row["denominator"] = g["denominator"]
            row["denominator_label"] = "published_original_optimum"
            row["labels_0p5"] = decision_labels(row["mean"], row["low"], row["high"])
            anchor_intervals.append(row)
        for name in names:
            left, right = name.split('-')
            raw_mean = g["candidates"][right]["mean_returned_cut"] - g["candidates"][left]["mean_returned_cut"]
            value = 100*raw_mean/b if b and b>0 else None
            spread = np.asarray([x["core"][name]["mean"] for x in gg], dtype=float)
            finite = value is not None and np.all(np.isfinite(spread))
            lo, hi = (float(np.min(spread)), float(np.max(spread))) if finite else (None, None)
            q025, q975 = np.quantile(spread, [0.025,0.975], method=QUANTILE_METHOD) if finite else (None,None)
            anchor_rows.append({"graph": g["graph"], "family": g["family"], "contrast": name,
                                "anchor_optimum_normalized_mean": g["core"][name]["mean"],
                                "anchor_reference_normalized_mean": value,
                                "anchor_published_optimum_C": g["denominator"], "B_anchor": b,
                                "anchor_pool_trajectories": 896, "generated_pool_trajectories": 576,
                                "generated_min": lo, "generated_max": hi,
                                "generated_q025": q025, "generated_q975": q975,
                                "within_generated_range": lo <= value <= hi if finite else None,
                                "within_generated_central_95pct": q025 <= value <= q975 if finite else None,
                                "scope": "DESCRIPTIVE_SPREAD_NOT_PREDICTION_INTERVAL; anchor reference pool uses 7*128 anchor trajectories"})
        for fmt in CANDIDATES:
            c = g["candidates"][fmt]
            value = c["mean_reference_normalized_shortfall_pp"]
            spread = np.asarray([x["candidates"][fmt]["mean_shortfall_pp"] for x in gg], dtype=float)
            finite = value is not None and np.all(np.isfinite(spread))
            lo, high = (float(np.min(spread)),float(np.max(spread))) if finite else (None,None)
            q025,q975 = np.quantile(spread,[.025,.975],method=QUANTILE_METHOD) if finite else (None,None)
            anchor_quality.append({"graph":g["graph"],"family":g["family"],"representation":fmt,
                                   "mean_returned_cut":c["mean_returned_cut"],
                                   "anchor_optimum_normalized_gap_pp":c["mean_shortfall_pp"],
                                   "anchor_reference_normalized_shortfall_pp":value,
                                   "anchor_published_optimum_C":g["denominator"],"B_anchor":b,
                                   "anchor_pool_trajectories":896,"generated_pool_trajectories":576,
                                   "generated_reference_shortfall_min":lo,"generated_reference_shortfall_max":high,
                                   "generated_reference_shortfall_q025":q025,"generated_reference_shortfall_q975":q975,
                                   "within_generated_range":lo<=value<=high if finite else None,
                                   "within_generated_central_95pct":q025<=value<=q975 if finite else None,
                                   "scope":"DESCRIPTIVE_SPREAD_NOT_PREDICTION_INTERVAL; different fixed anchor/generated reference pools"})
    write_csv(out/"core_contrasts.csv", core_rows)
    write_csv(out/"graph_contrasts.csv", graph_contrasts)
    write_csv(out/"graph_quality_mechanism.csv", candidate_rows)
    write_csv(out/"mechanism_contrasts.csv", mechanism_rows)
    write_csv(out/"mechanism_correlations.csv", correlations)
    write_csv(out/"R_last_differences.csv", last_rows)
    write_csv(out/"family_quality_mechanism.csv", family_quality)
    write_csv(out/"anchor_spread.csv", anchor_rows)
    write_csv(out/"anchor_contrasts_descriptive.csv", anchor_intervals)
    write_csv(out/"anchor_quality_spread.csv", anchor_quality)
    write_json(out/"selected_pairs.json", chosen)
    write_json(out/"analysis_registry.json", analysis_registry())
    _forest_svg(core_rows, out/"core_contrasts.svg", "Registered ideal-response contrasts", "Simultaneous bootstrap-t bounds; generated B_g shortfall differences (pp)")
    _forest_svg(mechanism_rows, out/"mechanism_contrasts.svg", "Descriptive access and selection differences", "Ordinary graph-resampled 95% intervals; no core alpha allocated")
    if anchor_intervals:
        _forest_svg([{**r,"family":r["graph"]} for r in anchor_intervals], out/"anchor_contrasts.svg", "Descriptive official-anchor contrasts", "Ordinary paired-seed 95% bootstrap-t; published-optimum-normalized gaps (pp)")
    text = ["# Locked ideal-response checkpoint", "", "This analysis stops before offset, gain or hardware work.",
            "Generated values are shortfalls relative to the frozen best-observed B_g, not optimum gaps. All nine contrasts per family (18 total) use the registered simultaneous bounds.",
            "", "| Family | Contrast | Mean pp | Bounds pp | +0.5 pp NI |", "| --- | --- | ---: | --- | --- |"]
    def num(x): return "undefined" if x is None else f"{x:+.6f}"
    for r in core_rows:
        text.append(f'| {r["family"]} | {r["contrast"]} | {num(r["mean"])} | [{num(r["low"])}, {num(r["high"])}] | {r["qualification"]} |')
    text += ["", "## Selected choices for the later offset stage (not run)", ""]
    for f, pair in chosen.items():
        text.append(f'- {f}: certified FP={pair["lowest_tested_certified_FP"]}; certified INT={pair["lowest_tested_certified_INT"]}; selected={pair["selected_FP"]}/{pair["selected_INT"]}/FP64; diagnostic fallback={pair["diagnostic_fallback"]}.')
    text += ["", "## Descriptive mechanism", "", "Rz is nonnegative by construction. Its sign alone is not evidence of a mechanism. The comparisons below concern differences between encodings. Access differences are A_FP-A_INT; negative favors FP access.",
             "", "| Family | Contrast | Endpoint | Mean pp | 95% bounds | Graph signs + / - / 0 | Prediction status |", "| --- | --- | --- | ---: | --- | --- | --- |"]
    for r in mechanism_rows:
        text.append(f'| {r["family"]} | {r["contrast"]} | {r["metric"]} | {num(r["mean"])} | [{num(r["low"])}, {num(r["high"])}] | {r["graph_positive"]}/{r["graph_negative"]}/{r["graph_zero"]} | {r["prediction_interval_status"]} |')
    text += ["", "Per-candidate Spearman correlations, graph-mean SDs, median within-graph SEs and signed R_last-R are in the accompanying CSVs. Missing R_last for reused first-block rows is retained as missing. Correlations and mechanism intervals are descriptive and consume none of the core alpha.",
             "", "## Official-anchor spread", "", "anchor_spread.csv compares all nine reference-normalized anchor contrasts against the full generated range and 2.5/97.5 percentiles. anchor_quality_spread.csv does the same for each candidate's reference shortfall. Both retain published-optimum-normalized anchor values and B_anchor. These are descriptive comparisons, not prediction intervals. B_anchor is the largest V from 7*128 anchor trajectories (896), while B_g uses 7*64 main plus 128 independent references (576); the pool-size difference limits direct calibration."]
    (out/"RESULTS.md").write_text("\n".join(text)+"\n")
    manifest = {"scope": "IDEAL_ONLY_CHECKPOINT", "core_contrasts": 18, "graphs_per_family": expected_graphs,
                "generated_graphs": len(generated), "anchors": len(anchors), "resamples": resamples,
                "numpy_version": np.__version__, "offset_executed": False,
                "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name != "analysis_manifest.json"}}
    write_json(out/"analysis_manifest.json", manifest)
    return {"core": core_rows, "mechanism": mechanism_rows, "selected_pairs": chosen, "anchors": anchor_rows}


def _forest_svg(rows, path, title, subtitle):
    width, step = 1150, 37
    height = 135 + step*len(rows)
    finite = [abs(r[k]) for r in rows for k in ("mean", "low", "high") if r[k] is not None and math.isfinite(r[k])]
    limit = max(1.0, max(finite, default=1)*1.1)
    def xx(v): return 350+(v+limit)/(2*limit)*640
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             f'<rect width="{width}" height="{height}" fill="white"/>',
             f'<text x="28" y="35" font-family="sans-serif" font-size="22" font-weight="bold">{escape(title)}</text>',
             f'<text x="28" y="59" font-family="sans-serif" font-size="13">{escape(subtitle)}</text>']
    for tick in (-limit, -0.5, 0, 0.5, limit):
        x = xx(tick)
        lines.append(f'<line x1="{x}" x2="{x}" y1="80" y2="{height-40}" stroke="{"#666" if tick==0 else "#ddd"}"/>')
        lines.append(f'<text x="{x}" y="{height-17}" text-anchor="middle" font-family="sans-serif" font-size="12">{tick:+.2f}</text>')
    for i, r in enumerate(rows):
        y=100+step*i
        label=f'{r["family"]} {r["contrast"]}'+(f' {r["metric"]}' if "metric" in r else "")
        lines.append(f'<text x="28" y="{y+4}" font-family="sans-serif" font-size="13">{escape(label)}</text>')
        if r["low"] is not None and r["high"] is not None:
            lines.append(f'<line x1="{xx(r["low"])}" x2="{xx(r["high"])}" y1="{y}" y2="{y}" stroke="#226e94" stroke-width="3"/>')
        if r["mean"] is not None:
            lines.append(f'<circle cx="{xx(r["mean"])}" cy="{y}" r="4" fill="#163b53"/>')
        label=r.get("qualification",r.get("prediction_interval_status",""))
        lines.append(f'<text x="1004" y="{y+4}" font-family="sans-serif" font-size="10">{escape(label)}</text>')
    lines.append('</svg>')
    Path(path).write_text("\n".join(lines)+"\n")


def analyse_bundle_dir(base, out=None, *, resamples=RESAMPLES):
    """Load root runner's frozen per-graph gzip bundles and analyse once complete."""
    base = Path(base)
    groups = []
    locations = [("generated", p) for f in FAMILIES for p in sorted((base/"generated"/f).glob("[0-9][0-9][0-9]"))]
    locations += [("anchor", p) for p in sorted((base/"anchors").glob("*")) if p.is_dir()]
    for kind, folder in locations:
        manifest = json.loads((folder/"manifest.json").read_text())
        rows = read_records(folder/"records.jsonl.gz")
        fidelity = read_records(folder/"fidelity.jsonl.gz")
        metrics = json.loads((folder/"representation_metrics.json").read_text())
        metrics = metrics.get("representations", metrics)
        graph = manifest.get("graph", rows[0]["graph"])
        family = manifest.get("family", rows[0].get("family", "ring" if graph.startswith("ising") else "torus"))
        if kind == "generated":
            if len(rows) != 576 or {r.get("stage") for r in rows} != {"main", "reference"}:
                raise ValueError(f"unexpected generated record count or stages: {graph}")
            main = [r for r in rows if r["stage"] == "main"]
            refs = [r for r in rows if r["stage"] == "reference"]
            pool = fixed_reference_pool(main, refs)
            b = manifest.get("B_g")
            if isinstance(b, dict): b = b.get("B_g", b.get("value"))
            if b is None: b = manifest.get("reference_pool", {}).get("B_g")
            if b != pool["B_g"]:
                raise ValueError(f"frozen B_g mismatch for {graph}")
            denominator, n = b, 64
            label = "frozen_best_observed_B_g_not_optimum"
            index = int(manifest.get("index", folder.name))
        else:
            if len(rows) != 896 or {r.get("stage") for r in rows} != {"anchor"}:
                raise ValueError(f"unexpected anchor record count or stages: {graph}")
            main = [r for r in rows if r.get("stage") == "anchor"]
            b = max([0]+[_cut(r, "V") for r in main])
            denominator = manifest.get("published_optimum", manifest.get("official_optimum", main[0].get("official_optimum")))
            if denominator is None:
                raise ValueError(f"anchor lacks published optimum: {graph}")
            n, label, index = 128, "published_original_optimum", None
        groups.append(summarize_graph(main, fidelity, metrics, graph=graph, family=family,
                                      denominator=denominator, denominator_label=label, reference_B=b,
                                      kind=kind, expected_seeds=n, index=index))
    if len([g for g in groups if g["kind"] == "anchor"]) != 6:
        raise ValueError("six complete official anchors required")
    return analyse_graph_summaries(groups, out or base/"analysis", resamples=resamples)


def smoke_first_block(source, out, *, resamples=RESAMPLES):
    """Read the closed first block; compute only descriptive fixed-graph checks."""
    source, out = Path(source), Path(out)
    before = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob("*") if p.is_file()}
    rows = read_records(source/"records.jsonl")
    if len(rows) != 1280:
        raise ValueError("closed first block must contain 1280 records")
    records = []
    for h, graph in ((0, "ising2.5-100_5555"), (2, "ising2.5-100_7777")):
        rr = [r for r in rows if r["graph"] == graph and r["condition"] == "raw"]
        by = {(_fmt(r), int(r["seed"])): r for r in rr}
        seeds = sorted(s for f, s in by if f == "ref64")
        if len(rr) != 384 or len(seeds) != 128:
            raise ValueError("unexpected first-block raw count")
        d = rr[0]["official_optimum"]
        f = [mechanism_values(by[("fp5",s)], by[("ref64",s)], d) for s in seeds]
        i = [mechanism_values(by[("int6",s)], by[("ref64",s)], d) for s in seeds]
        matrix = np.asarray([[a["extra_pp"]-b["extra_pp"], a["A_pp"]-b["A_pp"], a["Rz_pp"]-b["Rz_pp"]] for a,b in zip(f,i)])
        if not np.allclose(matrix[:,0], matrix[:,1]+matrix[:,2], rtol=0, atol=1e-11):
            raise ValueError("first-block contrast accounting failed")
        bounds = bootstrap_t_vectors(matrix, q=0.025, resamples=resamples, seed_sequence=[20261120,940,0,2,h])
        for metric, values in zip(("extra_gap", "access_A", "selection_Rz"), bounds):
            result = {"graph": graph, "contrast": "fp5-int6", "metric": metric,
                      "scope": "DESCRIPTIVE_FIXED_VIEWED_GRAPH_SEED_BOOTSTRAP_SMOKE_ONLY", **values}
            if metric == "extra_gap":
                result["labels"] = decision_labels(values["mean"],values["low"],values["high"])
            else:
                result["mechanism_inference"] = "DESCRIPTIVE_ONLY_NO_QUALIFICATION_LABEL_OR_CORE_ALPHA"
            records.append(result)
        records.append({"graph": graph, "contrast": "fp5-int6", "metric": "Rz_means",
                        "scope": "DESCRIPTIVE_FIXED_VIEWED_GRAPH_POINT_VALUES",
                        "fp5_Rz_pp": float(np.mean([r["Rz_pp"] for r in f])),
                        "int6_Rz_pp": float(np.mean([r["Rz_pp"] for r in i])),
                        "R_last_missing_raw_records": sum(r.get("R_last") is None for r in rr)})
    after = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob("*") if p.is_file()}
    if before != after:
        raise AssertionError("closed first-block archive changed")
    out.mkdir(parents=True, exist_ok=True)
    write_json(out/"first_block_analysis_smoke.json", {"status": "PASS", "solver_runs": 0,
                "archive_unchanged": True, "source_file_hashes": before, "registry": analysis_registry(), "results": records})
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--analyse", type=Path, help="complete ideal-response bundle directory")
    group.add_argument("--first-block-smoke", type=Path, help="read-only first-block analysis smoke test")
    group.add_argument("--registry", action="store_true", help="print the frozen registry without reading outcomes")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.registry:
        print(json.dumps(analysis_registry(), sort_keys=True, indent=2))
    elif args.first_block_smoke:
        if args.out is None: parser.error("--out required for smoke outputs")
        smoke_first_block(args.first_block_smoke, args.out)
        print("DESCRIPTIVE FIRST-BLOCK ANALYSIS SMOKE PASS; no solver runs")
    else:
        analyse_bundle_dir(args.analyse, args.out)
        print("IDEAL-RESPONSE ANALYSIS COMPLETE; checkpoint before offsets")
