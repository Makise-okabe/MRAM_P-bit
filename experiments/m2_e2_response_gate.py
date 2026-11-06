#!/usr/bin/env python3
"""One bounded E2 ASSUMPTION-only response × six-bit coupling screening gate.

No post-calibration STT-MTJ population data were available when frozen.
A 5%-gain/0.10-logit bounded synthetic heterogeneity is a USER-INDEPENDENT
SOFTWARE SENSITIVITY ASSUMPTION, NOT a measured residual or device claim.
Never call this E3, device characterized, or hardware performance.

Does NOT change the M1 50k linear solver, codebooks, scales, schedule,
original-cut evaluation, or best represented-energy retention.
E1 original raw CSV SHA256 is required to verify paired ideal baselines.
No reruns of 936 ideal solver jobs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph, original_cut, represented_energy, prepare
from experiments.m1_biqmac_precision_sweep import (
    GRAPH_NAMES, UPDATES_FROZEN, SEEDS_FROZEN, BASE_SEED_FROZEN,
    bootstrap_paired_ci,
)
from experiments.m1_biqmac_reference_quality_gate import schedule_beta, official_reference
from experiments.m1_precision_codebooks import build_global
from experiments.m2_stt_pbit_transfer_preflight import logistic

EVIDENCE = "E2_ASSUMED_NOT_MEASURED"
MODEL_SEED = 20261107
GAIN_HALFSPAN = 0.05
OFFSET_LOGIT_HALFSPAN = 0.10
FORMATS = ("ref64", "fp6", "int6", "bfp6")
IDEAL_RUNS_SHA256 = "27556b10bc9d2a778af28b2d007f28e34dedd47b14c0701fc444b5285e466b97"
IDEAL_REFERENCE_TYPE = "PUBLISHED_OPTIMUM"


def build_e2_assumption(n: int) -> dict:
    """One seeded persistent device identity for all formats/graphs/seeds.

    Two independent bounded uniform deviates. These magnitudes are CHOSEN
    ILLUSTRATIVE STRESSES; we do not claim their origin is the 2026 paper.
    """
    if n < 2:
        raise ValueError("at least two devices required")
    rng = random.Random(MODEL_SEED)
    gain = [1.0 + GAIN_HALFSPAN * rng.uniform(-1, 1) for _ in range(n)]
    offset = [OFFSET_LOGIT_HALFSPAN * rng.uniform(-1, 1) for _ in range(n)]
    model = dict(
        evidence_level=EVIDENCE,
        source="investigator-selected E2 stress, not extracted from any MTJ population",
        paper_interface_doi="10.1038/s41467-026-72020-8",
        n_devices=n, device_model_seed=MODEL_SEED,
        gain_halfspan_assumed=GAIN_HALFSPAN,
        offset_logit_halfspan_assumed=OFFSET_LOGIT_HALFSPAN,
        per_device_gain=gain, per_device_offset_logit=offset,
        persistence="each spin/device parameter fixed over complete solver run",
        pairing="same indexed device identity used by every coupling format",
        uncertainty="conditional on ONE illustrative device realization; no device-population CI",
        voltage="logit surrogate after nominal transfer; no calibrated physical voltage window"
    )
    validate_device_model(model, n)
    return model


def validate_device_model(model: dict, n: int) -> None:
    if model.get("evidence_level") != EVIDENCE or model.get("n_devices") != n:
        raise ValueError("not the frozen E2 population")
    gain = model.get("per_device_gain")
    offset = model.get("per_device_offset_logit")
    if not isinstance(gain, list) or not isinstance(offset, list) or len(gain) != n or len(offset) != n:
        raise ValueError("dimension mismatch")
    if any(not math.isfinite(x) or x <= 0 for x in gain) or any(not math.isfinite(x) for x in offset):
        raise ValueError("invalid device gain/offset")
    if any(abs(g-1) > GAIN_HALFSPAN+1e-12 for g in gain) or any(abs(z) > OFFSET_LOGIT_HALFSPAN+1e-12 for z in offset):
        raise ValueError("assumed bounded envelope violated")


def e2_probability(beta: float, field: float, gain: float, offset_logit: float) -> float:
    """sigmoid(gain_i * 2*beta*H_i + offset_logit_i).

    With gain=1 and offset=0 this equals the *exact frozen* M1 ideal Gibbs
    transfer, including the sign of the local field.
    """
    if not all(map(math.isfinite, (beta, field, gain, offset_logit))) or beta < 0 or gain <= 0:
        raise ValueError("invalid conditional response")
    return logistic(gain * (2 * beta * field) + offset_logit)


def solve_with_response(graph, rep, beta: float, updates: int, seed: int, model: dict) -> dict:
    """Mirror M1 linear solver except for its single probability expression.

    Same RNG sequence per format/seed. No device draws in solver loop.
    The returned state is selected ONLY by its represented energy.
    """
    if updates < 1 or beta <= 0:
        raise ValueError("positive budget and beta required")
    validate_device_model(model, graph.n)
    gain = model["per_device_gain"]
    offset = model["per_device_offset_logit"]
    rng = random.Random(seed)
    spins = [1 if rng.randrange(2) else -1 for _ in range(graph.n)]
    adj = rep["adjacency"]
    fields = [sum(q * spins[j] for j, q in adj[i]) for i in range(graph.n)]
    energy = represented_energy(rep["edges"], spins)
    best_e, best_state = energy, tuple(spins)
    flips = improvements = 0
    for step in range(updates):
        i = rng.randrange(graph.n)
        u = rng.random()
        b = schedule_beta(beta, "linear", step, updates)
        old = spins[i]
        nxt = 1 if u < e2_probability(b, fields[i], gain[i], offset[i]) else -1
        if nxt != old:
            delta = nxt - old
            energy += 2 * old * fields[i]
            spins[i] = nxt
            flips += 1
            for j, q in adj[i]:
                fields[j] += q * delta
        if energy < best_e:
            best_e, best_state = energy, tuple(spins)
            improvements += 1
    actual = represented_energy(rep["edges"], spins)
    saved = represented_energy(rep["edges"], best_state)
    if not math.isclose(actual, energy, rel_tol=1e-7, abs_tol=1e-7):
        raise AssertionError("final energy update mismatch")
    if not math.isclose(saved, best_e, rel_tol=1e-7, abs_tol=1e-7):
        raise AssertionError("retained represented energy mismatch")
    return dict(seed=seed, attempted_updates=updates, actual_flips=flips,
                improvements=improvements, returned_original_cut=original_cut(graph, best_state),
                returned_represented_energy=saved,
                returned_state_hex=format(sum(1 << i for i, s in enumerate(best_state) if s > 0), "x"))


def load_frozen_e1(path: Path) -> dict:
    if hashlib.sha256(path.read_bytes()).hexdigest() != IDEAL_RUNS_SHA256:
        raise ValueError("raw E1 936-run CSV SHA256 mismatch; refuse paired comparisons")
    with path.open(newline="", encoding="utf-8") as f:
        values = list(csv.DictReader(f))
    expected = len(GRAPH_NAMES) * 13 * SEEDS_FROZEN
    if len(values) != expected:
        raise ValueError("E1 raw CSV must contain exactly 936 rows")
    index = {}
    for item in values:
        key = (item["graph"], item["configuration"], int(item["seed"]))
        if key in index or int(item["attempted_updates"]) != UPDATES_FROZEN:
            raise ValueError("duplicate or unfrozen E1 record")
        index[key] = float(item["optimality_gap_pct"])
    for gix, graph in enumerate(GRAPH_NAMES):
        for fmt in FORMATS:
            for k in range(SEEDS_FROZEN):
                seed = BASE_SEED_FROZEN + 100000*gix + k
                if (graph, fmt, seed) not in index:
                    raise ValueError("missing paired E1 original-gap record")
    return index


def summarize_screen(rows: list[dict], ideal: dict) -> list[dict]:
    by_key = {(r["graph"], r["configuration"], r["seed"]): r for r in rows}
    summary = []
    for gix, graph in enumerate(GRAPH_NAMES):
        seeds = [BASE_SEED_FROZEN + 100000*gix + k for k in range(SEEDS_FROZEN)]
        for fmt in FORMATS:
            xs = [by_key[(graph, fmt, seed)]["gap_pct"] for seed in seeds]
            e1 = [ideal[(graph, fmt, seed)] for seed in seeds]
            e2_ref = [by_key[(graph, "ref64", seed)]["gap_pct"] for seed in seeds]
            additional = [x-y for x, y in zip(xs, e2_ref)]
            lo, hi = bootstrap_paired_ci(additional, 12000+gix*100+FORMATS.index(fmt))
            # Difference in differences against INT6, *paired on each seed*.
            # For other formats, it answers how that format changes vs INT6.
            d = [
                (by_key[(graph, fmt, seed)]["gap_pct"] -
                 by_key[(graph, "int6", seed)]["gap_pct"])
                - (ideal[(graph, fmt, seed)] - ideal[(graph, "int6", seed)])
                for seed in seeds
            ]
            dlo, dhi = bootstrap_paired_ci(d, 17000+gix*100+FORMATS.index(fmt))
            summary.append(dict(
                graph=graph, configuration=fmt, evidence=EVIDENCE,
                seeds=SEEDS_FROZEN, device_realizations=1,
                mean_absolute_original_gap_pct=sum(xs)/len(xs),
                mean_gap_change_vs_ideal_pp=sum(x-y for x,y in zip(xs,e1))/len(xs),
                mean_additional_gap_vs_e2_ref64_pp=sum(additional)/len(additional),
                paired_95_lo_vs_e2_ref64_pp=lo, paired_95_hi_vs_e2_ref64_pp=hi,
                mean_format_x_response_D_vs_int6_pp=sum(d)/len(d),
                paired_95_D_lo_pp=dlo, paired_95_D_hi_pp=dhi,
                preliminary_quality_gate_vs_e2_ref64=(
                    "YES_WITHIN_CAL_GRAPH" if hi <= 1.0 else "NO_OR_UNCERTAIN"
                ),
                interpretation="CAL graph/ONE E2 assumed device vector only; no cross-graph/device inference"
            ))
    return summary


def run(output: Path, ideal_csv: Path) -> None:
    if output.exists():
        raise ValueError("output already exists")
    ideal = load_frozen_e1(ideal_csv)  # fail early before launching runs
    refs = json.loads(Path("docs/BIQMAC_OFFICIAL_OPTIMA_2007.json").read_text())
    if refs.get("reference_type") != IDEAL_REFERENCE_TYPE:
        raise ValueError("unverified published optimum references")
    model = build_e2_assumption(100)
    # Freeze exact device values, provenance and their hash before solving.
    model_json = json.dumps(model, indent=2, sort_keys=True) + "\n"
    model_sha = hashlib.sha256(model_json.encode()).hexdigest()
    output.mkdir(parents=True, exist_ok=False)
    (output/"E2_ASSUMED_MODEL.json").write_text(model_json)
    configs = ("ref64", "fp6", "int6", "bfp6")
    rows = []
    for gix, graph_name in enumerate(GRAPH_NAMES):
        path = (Path("data/biqmac/raw/rudy") if gix == 0 else Path("data/biqmac/raw/ising"))/graph_name
        graph = load_rudy(path)
        if graph.n != 100:
            raise ValueError("frozen screening requires original 100-node graph")
        optimum = official_reference(graph, refs["graphs"][graph_name], refs)
        beta = beta_from_original_graph(graph)
        for fmt in configs:
            rep = prepare(graph, "ref64", "source") if fmt == "ref64" else build_global(graph, fmt[:-1], 6)
            for k in range(SEEDS_FROZEN):
                seed = BASE_SEED_FROZEN + gix*100000+k
                x = solve_with_response(graph, rep, beta, UPDATES_FROZEN, seed, model)
                score = x["returned_original_cut"]
                if score > optimum + 1e-7:
                    raise AssertionError("published original optimum exceeded")
                rows.append(dict(graph=graph_name, graph_sha256=graph.sha256,
                                 configuration=fmt, seed=seed, official_optimum=optimum,
                                 gap_pct=100*(optimum-score)/optimum,
                                 e1_paired_gap_pct=ideal[(graph_name,fmt,seed)],
                                 **x))
            print("E2 assumed", graph_name, fmt, "completed", flush=True)
    summary = summarize_screen(rows, ideal)
    for filename, table in (("E2_paired_runs.csv", rows), ("E2_summary.csv", summary)):
        with (output/filename).open("x", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(table[0]))
            w.writeheader()
            w.writerows(table)
    manifest = dict(
        status="E2_ASSUMED_SOFTWARE_ONLY", source_e1_sha256=IDEAL_RUNS_SHA256,
        model_file_sha256=model_sha, model_seed=MODEL_SEED, model_evidence=EVIDENCE,
        graphs=list(GRAPH_NAMES), configurations=list(FORMATS), device_realizations=1,
        seeds_per_graph=SEEDS_FROZEN, original_beta_and_source_scale_frozen=True,
        updates=UPDATES_FROZEN, schedule="linear 0.5 to 2 beta_G",
        selection="earliest best represented-energy state; original cut evaluation AFTER return",
        no_new_beta_or_scale_tuning=True, n_new_runs=len(rows),
        no_physical_claim="E2 is arbitrary bounded logit stress; no measured device residual or voltage limits",
        no_hardware_claim="no RTL, timing, coefficient-memory access energy, MTJ energy or time-to-target",
        statistical_scope="seed-conditional only on three previously seen CAL graphs/ONE device realization",
        application="original Biq Mac Mac weighted Max-Cut only"
    )
    (output/"manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    print("E2 ASSUMED RESPONSE SCREEN COMPLETE", len(rows), "new runs; model SHA256", model_sha)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--e1-raw-csv", type=Path, required=True,
                    help="the original 936-run precision_paired_runs.csv; must match archived SHA256")
    ap.add_argument("--out", type=Path, required=True, help="non-existing directory")
    args = ap.parse_args()
    run(args.out, args.e1_raw_csv)


if __name__ == "__main__":
    main()
