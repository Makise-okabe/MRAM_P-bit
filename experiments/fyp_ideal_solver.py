#!/usr/bin/env python3
"""Passive latest-tie logging and fail-closed preflight for the locked ideal study.

The completed first-block runner and its archive remain unchanged. The update
arithmetic below deliberately mirrors its solve_logged function. R_last is the
only new trajectory output and never participates in transition or retention.
Preflight controls are viewed official cases, not new scientific observations.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from pathlib import Path
import platform
import random
import time

from experiments.biqmac_maxcut import load_rudy
from experiments.fyp_first_block_20261120 import (
    CHECKPOINTS, UPDATES, canonical, digest, hex_state, read_jsonl,
    solve_logged as first_block_solve_logged, state_from_hex,
)
from experiments.m0_ising_math import sigmoid
from experiments.m1_biqmac_ideal_pilot import (
    beta_from_original_graph, original_cut, prepare, represented_energy,
)
from experiments.m1_biqmac_reference_quality_gate import schedule_beta
from experiments.m1_precision_codebooks import build_global

CANDIDATES = ("ref64", "fp5", "fp6", "int5", "int6", "int7", "int8")
PARITY_KEYS = (
    "returned_state_hex", "returned_original_cut", "returned_represented_energy",
    "actual_flips", "improvements",
)
VIEWED_GRAPHS = (
    "ising2.5-100_5555", "ising2.5-100_7777", "t2g10_5555", "t2g10_7777",
)
VERIFICATION_SOURCES = (
    "experiments/fyp_ideal_solver.py", "tests/test_fyp_ideal_solver.py",
    "experiments/fyp_first_block_20261120.py",
    "experiments/m1_biqmac_reference_quality_gate.py",
    "experiments/m1_biqmac_ideal_pilot.py",
    "experiments/m1_precision_codebooks.py", "experiments/biqmac_maxcut.py",
    "experiments/m0_ising_math.py",
)


def verification_sources():
    return {path: digest(path) for path in VERIFICATION_SOURCES}


def exact_original_cut(graph, spins):
    """Integer source scoring, independent of the solver's floating cache."""
    if len(spins) != graph.n or any(s not in (-1, 1) for s in spins):
        raise ValueError("invalid spin vector")
    total = 0
    for i, j, w in graph.edges:
        iw = int(w)
        if w != iw:
            raise ValueError("locked study requires integer original weights")
        if spins[i] != spins[j]:
            total += iw
    return total


def solve_logged(graph, rep, beta, updates, seed, *, source_rep=None,
                 checkpoints=CHECKPOINTS):
    """Unchanged first-block kernel with a passive latest-minimum-energy cut.

    R_last updates on every attainment of the current represented-energy
    minimum, including equality. The real returned state remains the earliest
    strict minimum. Extra state bookkeeping consumes no random numbers.
    """
    if not (updates >= 1 and beta > 0 and math.isfinite(beta)):
        raise ValueError("invalid beta/updates")
    if any(t < 1 or t > updates for t in checkpoints):
        raise ValueError("checkpoint outside attempts")
    source_bound = 0
    for _, _, w in graph.edges:
        iw = int(w)
        if w != iw:
            raise ValueError("locked study requires integer original weights")
        source_bound += abs(iw)
    if 2 * source_bound >= 2**53:
        raise ValueError("original integer cache exceeds exact binary64 range")
    rng = random.Random(seed)
    spins = [1 if rng.randrange(2) else -1 for _ in range(graph.n)]
    adj = rep["adjacency"]
    fields = [sum(q*spins[j] for j, q in adj[i]) for i in range(graph.n)]
    energy = represented_energy(rep["edges"], spins)
    best_e = energy
    best_state = tuple(spins)
    source_rep = source_rep or prepare(graph, "ref64", "source")
    src_adj = source_rep["adjacency"]
    src_field = [sum(q*spins[j] for j, q in src_adj[i]) for i in range(graph.n)]
    current_cut = original_cut(graph, spins)
    V = M = R = current_cut
    V_state = M_state = best_state
    R_last = current_cut
    last_state = best_state
    flips = 0
    improvements = 0
    snaps = []
    checkpoint_set = set(checkpoints)
    for step in range(updates):
        i = rng.randrange(graph.n)
        u = rng.random()
        b = schedule_beta(beta, "linear", step, updates)
        old = spins[i]
        nxt = 1 if u < sigmoid(2*b*fields[i]) else -1
        if nxt != old:
            delta = nxt-old
            current_cut -= old*src_field[i]
            energy += 2*old*fields[i]
            spins[i] = nxt
            flips += 1
            for j, q in adj[i]:
                fields[j] += q*delta
            for j, q in src_adj[i]:
                src_field[j] += q*delta
        if current_cut > V:
            V, V_state = current_cut, tuple(spins)
        if energy < best_e:
            best_e = energy
            best_state = tuple(spins)
            improvements += 1
            R = M = current_cut
            M_state = best_state
            R_last, last_state = current_cut, best_state
        elif energy == best_e:
            R_last = current_cut
            if nxt != old:
                last_state = tuple(spins)
            if current_cut > M:
                M, M_state = current_cut, tuple(spins)
        if step+1 in checkpoint_set:
            if current_cut != exact_original_cut(graph, spins):
                raise AssertionError("original-score incremental cache drift")
            snaps.append({"attempt": step+1, "beta": b,
                          "current_state_hex": hex_state(spins),
                          "V": V, "M": M, "R": R, "R_last": R_last,
                          "unreached": None, "selection": V-M, "tie": M-R})
    final_e = represented_energy(rep["edges"], spins)
    saved = represented_energy(rep["edges"], best_state)
    if not math.isclose(final_e, energy, rel_tol=1e-7, abs_tol=1e-7):
        raise AssertionError("final represented energy parity failed")
    if not math.isclose(saved, best_e, rel_tol=1e-7, abs_tol=1e-7):
        raise AssertionError("retained represented energy parity failed")
    for score, st in ((V, V_state), (M, M_state), (R, best_state),
                      (R_last, last_state)):
        if score != exact_original_cut(graph, st):
            raise AssertionError("trajectory scored state mismatch")
    if not V >= M >= R or not M >= R_last:
        raise AssertionError("trajectory loss ordering failed")
    return {"seed": seed, "attempted_updates": updates, "actual_flips": flips,
            "improvements": improvements, "returned_original_cut": R,
            "final_original_cut": original_cut(graph, spins),
            "returned_represented_energy": saved,
            "final_represented_energy": final_e,
            "returned_state_hex": hex_state(best_state),
            "V": V, "M": M, "R": R, "R_last": R_last,
            "V_state_hex": hex_state(V_state),
            "M_state_hex": hex_state(M_state), "checkpoints": snaps}


def without_latest(record):
    """Remove only new passive outputs for exact legacy-output comparison."""
    stripped = dict(record)
    stripped.pop("R_last", None)
    stripped["checkpoints"] = [
        {k: v for k, v in point.items() if k != "R_last"}
        for point in record["checkpoints"]
    ]
    return stripped


def representation(graph, fmt):
    if fmt not in CANDIDATES:
        raise ValueError(f"unregistered representation: {fmt}")
    if fmt == "ref64":
        return prepare(graph, "ref64", "source")
    return build_global(graph, "fp" if fmt.startswith("fp") else "int",
                        int(fmt[2:] if fmt.startswith("fp") else fmt[3:]))


def representation_metrics(graph, rep):
    mass, zeroed_mass, zeros = 0, 0, 0
    if len(graph.edges) != len(rep["edges"]):
        raise ValueError("representation/source edge count mismatch")
    for (i, j, w), (u, v, q) in zip(graph.edges, rep["edges"]):
        if (i, j) != (u, v):
            raise ValueError("representation/source edge order mismatch")
        iw = int(w)
        if iw != w:
            raise ValueError("noninteger source coefficient")
        mass += abs(iw)
        if q == 0:
            zeros += 1
            zeroed_mass += abs(iw)
    return {
        "source_edges": len(graph.edges), "quantized_zero_edges": zeros,
        "retained_nonzero_edges": len(graph.edges)-zeros,
        "source_abs_weight_mass": mass, "zeroed_abs_weight_mass": zeroed_mass,
        "zeroed_abs_weight_mass_fraction": zeroed_mass/mass if mass else None,
    }


def field_fidelity(graph, ref_state_hex, rep, beta, *, source_rep=None):
    """Identical common-state field/probability metrics, without extra RNG."""
    spins = state_from_hex(ref_state_hex, graph.n)
    source_rep = source_rep or prepare(graph, "ref64", "source")
    field_ref = [sum(q*spins[j] for j, q in row)
                 for row in source_rep["adjacency"]]
    field_q = [sum(q*spins[j] for j, q in row) for row in rep["adjacency"]]
    rms = math.sqrt(sum((a-b)**2 for a, b in zip(field_q, field_ref))/graph.n)
    return {
        "field_rms": rms, "logit_rms": 2*beta*rms,
        "probability_mae": sum(abs(sigmoid(2*beta*a)-sigmoid(2*beta*b))
                               for a, b in zip(field_q, field_ref))/graph.n,
    }


def _write_new(path, obj):
    payload = json.dumps(obj, sort_keys=True, indent=2, allow_nan=False)+"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != payload:
            raise FileExistsError(f"refusing to replace existing preflight evidence: {path}")
        return
    path.write_text(payload)


def plan_parity(out):
    """Freeze the exact 25 archived rows before replaying any of them."""
    controls = []
    m5 = Path("results/m2_heldout_dense_fp6_int6_20261109/runs.csv")
    e0 = Path("results/e0_fp64_two_cal_20261112/run_rows.csv")
    first = Path("results/fyp_first_block_20261120/records.jsonl")
    m5_rows = list(csv.DictReader(m5.open()))
    e0_rows = list(csv.DictReader(e0.open()))
    first_rows = read_jsonl(first)

    def add(archive, row, fmt, source):
        controls.append({"archive": str(archive), "archive_sha256": digest(archive),
                         "source": source, "graph": row["graph"],
                         "graph_sha256": row["graph_sha256"],
                         "seed": int(row["seed"]), "representation": fmt,
                         "expected": {k: row[k] for k in PARITY_KEYS}})

    for fmt in ("ref64", "fp6", "int6"):
        rows = sorted((r for r in m5_rows if r["configuration"] == fmt
                       and float(r["offset_logit_halfspan"]) == 0
                       and int(r["attempted_updates"]) == UPDATES),
                      key=lambda r: int(r["seed"]))[:3]
        if len(rows) != 3:
            raise ValueError("missing M5 parity sample")
        for row in rows:
            add(m5, row, fmt, "M5")
    for name in ("ising2.5-100_5555", "t2g10_5555"):
        rows = sorted((r for r in e0_rows if r["graph"] == name
                       and r["schedule"] == "linear_legacy"
                       and int(r["attempted_updates"]) == UPDATES),
                      key=lambda r: int(r["seed"]))[:2]
        if len(rows) != 2:
            raise ValueError("missing E0 parity sample")
        for row in rows:
            add(e0, row, "ref64", "E0")
    for name in ("ising2.5-100_5555", "ising2.5-100_7777"):
        for fmt in ("ref64", "fp5", "int6"):
            rows = sorted((r for r in first_rows if r["graph"] == name
                           and r["condition"] == "raw"
                           and r["representation"] == fmt), key=lambda r: r["seed"])[:2]
            if len(rows) != 2:
                raise ValueError("missing first-block parity sample")
            for row in rows:
                add(first, row, fmt, "first_block")
    assert len(controls) == 25
    result = {"scope": "Fixed archived verification controls, not a first-block rerun",
              "source_sha256": verification_sources(),
              "sample_count": 25, "keys": list(PARITY_KEYS), "controls": controls}
    _write_new(out/"archived_parity_plan.json", result)
    return result


def archived_parity(graph_dir, out):
    plan_path = out/"archived_parity_plan.json"
    if not plan_path.exists():
        raise FileNotFoundError("write the fixed parity plan before running controls")
    if (out/"PARITY_FAILURE.json").exists():
        raise RuntimeError("parity failure exists: stop and report, do not retry")
    if (out/"archived_parity.json").exists():
        raise FileExistsError("archived parity already executed; no automatic rerun")
    plan = json.loads(plan_path.read_text())
    records = []
    graphs = {}
    reps = {}
    try:
        if verification_sources() != plan["source_sha256"]:
            raise ValueError("verification source changed after sample-plan freeze")
        for control in plan["controls"]:
            name, fmt, seed = control["graph"], control["representation"], control["seed"]
            if name not in VIEWED_GRAPHS or "6666" in name:
                raise ValueError("non-viewed graph in preflight plan")
            if digest(control["archive"]) != control["archive_sha256"]:
                raise ValueError("archived evidence changed after sample-plan freeze")
            if name not in graphs:
                path = graph_dir/name
                if digest(path) != control["graph_sha256"]:
                    raise ValueError("source SHA256 mismatch")
                graphs[name] = load_rudy(path)
            graph = graphs[name]
            key = (name, fmt)
            if key not in reps:
                reps[key] = representation(graph, fmt)
            rep, beta = reps[key], beta_from_original_graph(graph)
            new = solve_logged(graph, rep, beta, UPDATES, seed)
            for field, expected in control["expected"].items():
                value = new[field]
                equal = str(expected) == value if field == "returned_state_hex" else float(expected) == value
                if not equal:
                    raise AssertionError(f"archive mismatch {name}/{fmt}/{seed}/{field}: {expected!r} != {value!r}")
            # Only first-block controls need a complete old/new output audit.
            # Other archived schemas do not include checkpoints and V/M/R.
            if control["source"] == "first_block":
                old = first_block_solve_logged(graph, rep, beta, UPDATES, seed)
                if without_latest(new) != old:
                    raise AssertionError(f"passive-field output mismatch {name}/{fmt}/{seed}")
            records.append({k: control[k] for k in
                            ("source", "archive", "archive_sha256", "graph", "graph_sha256", "seed", "representation")}
                           | {"result": "PASS", "original_integer_rescore": "PASS"})
    except Exception as exc:
        _write_new(out/"PARITY_FAILURE.json", {
            "status": "STOP_REQUIRED", "error": str(exc),
            "exception_type": type(exc).__name__, "completed_controls": records,
            "plan_sha256": digest(plan_path),
        })
        raise
    result = {"status": "PASS", "sample_count": len(records),
              "python": platform.python_version(), "plan_sha256": digest(plan_path),
              "source_sha256": verification_sources(),
              "controls": records,
              "first_block_archive_modified": False,
              "missing_R_last_policy": "No backfill of reused records; parity results stay separate"}
    _write_new(out/"archived_parity.json", result)
    return result


def time_pipeline(graph_dir, out):
    """One seven-code pipeline on each viewed source; do not expose quality."""
    import numpy as np
    if np.__version__ != "2.3.5":
        raise ValueError("NumPy 2.3.5 required")
    if (out/"PARITY_FAILURE.json").exists():
        raise RuntimeError("parity failed; stop before timing")
    if not (out/"archived_parity.json").exists():
        raise RuntimeError("archived parity must pass before timing")
    result_path = out/"pipeline_timing.json"
    if result_path.exists():
        raise FileExistsError("timing already executed; no automatic rerun")
    results = []
    for name, seed in (("ising2.5-100_7777", 20661201), ("t2g10_5555", 20261112)):
        t0 = time.perf_counter()
        graph = load_rudy(graph_dir/name)
        load_seconds = time.perf_counter()-t0
        reps, fit_times, run_times, samples = {}, {}, {}, {}
        for fmt in CANDIDATES:
            start = time.perf_counter()
            reps[fmt] = representation(graph, fmt)
            fit_times[fmt] = time.perf_counter()-start
        beta = beta_from_original_graph(graph)
        for fmt in CANDIDATES:
            start = time.perf_counter()
            samples[fmt] = solve_logged(graph, reps[fmt], beta, UPDATES, seed,
                                        source_rep=reps["ref64"])
            run_times[fmt] = time.perf_counter()-start
        start = time.perf_counter()
        metrics = []
        for point in samples["ref64"]["checkpoints"]:
            for fmt in CANDIDATES[1:]:
                metrics.append(field_fidelity(graph, point["current_state_hex"], reps[fmt],
                                               point["beta"], source_rep=reps["ref64"]))
        metric_seconds = time.perf_counter()-start
        start = time.perf_counter()
        encoded = ("\n".join(canonical(samples[fmt]) for fmt in CANDIDATES)+"\n").encode()
        compressed = gzip.compress(encoded, compresslevel=9, mtime=0)
        serialize_compress_seconds = time.perf_counter()-start
        temp = out/"pipeline_timing_transient.tmp"
        start = time.perf_counter()
        temp.write_bytes(compressed)
        write_seconds = time.perf_counter()-start
        temp.unlink()
        results.append({"graph": name, "graph_sha256": graph.sha256, "seed": seed,
                        "load_seconds": load_seconds, "prepare_seconds": fit_times,
                        "logged_solver_seconds": run_times,
                        "four_checkpoint_six_candidate_fidelity_seconds": metric_seconds,
                        "serialize_compress_seconds": serialize_compress_seconds,
                        "write_seconds": write_seconds,
                        "seven_records_bytes": len(encoded),
                        "seven_records_gzip_bytes": len(compressed),
                        "quality_inspected_or_retained": False})
    result = {"scope": "Viewed-source engineering timing only; no main-campaign outcomes",
              "python": platform.python_version(), "numpy": np.__version__,
              "source_sha256": verification_sources(),
              "platform": platform.platform(), "updates": UPDATES,
              "samples_per_graph_candidate": 1, "graphs": results}
    _write_new(result_path, result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan-parity", action="store_true")
    p.add_argument("--parity", action="store_true")
    p.add_argument("--time", action="store_true")
    p.add_argument("--graph-dir", type=Path, default=Path("data/biqmac/raw/ising"))
    p.add_argument("--out", type=Path, default=Path("results/fyp_ideal_preflight_20261120"))
    args = p.parse_args()
    if not (args.plan_parity or args.parity or args.time):
        p.error("choose --plan-parity, --parity, or --time")
    if args.plan_parity:
        result = plan_parity(args.out)
        print(f"Frozen {result['sample_count']} archived parity controls", flush=True)
    if args.parity:
        result = archived_parity(args.graph_dir, args.out)
        print(f"Archived parity: {result['sample_count']} PASS", flush=True)
    if args.time:
        result = time_pipeline(args.graph_dir, args.out)
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
