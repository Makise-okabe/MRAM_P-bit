#!/usr/bin/env python3
"""M5: 216-run dense held-out FP6 versus INT6 validation.

--selftest: no held-out graph access
--freeze: freeze the protocol before graph access
--execute: use the frozen protocol and run/resume the experiment

Reuses the existing quantizer, solver, beta schedule, and E2
synthetic offset population. No new CAL runs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import urllib.request
from pathlib import Path
from types import SimpleNamespace

from experiments.biqmac_maxcut import load_rudy
from experiments.m1_biqmac_ideal_pilot import (
    beta_from_original_graph, prepare,
)
from experiments.m1_biqmac_reference_quality_gate import solve_reference
from experiments.m1_biqmac_precision_sweep import (
    BASE_SEED_FROZEN, SEEDS_FROZEN, UPDATES_FROZEN,
    bootstrap_paired_ci,
)
from experiments.m1_precision_codebooks import build_global, SCALE_POLICY
from experiments.m2_e2_response_gate import (
    EVIDENCE, solve_with_response, validate_device_model,
)
from experiments.m2_offset_fp64_scout import models, paired_seed
from experiments.m2_coupling_matrix_snapshot_diagnostic import (
    decode_spins, local_fields, snapshot_metrics,
)

NAME = "ising2.5-100_7777"
GRAPH_INDEX = 4
GRAPH_URL = f"https://biqmac.aau.at/library/mac/ising/{NAME}"
GRAPH_PATH = Path("data/biqmac/raw/ising") / NAME
OPTIMUM = 3363230
OPTIMUM_SOURCE = "https://biqmac.aau.at/biqmaclib.pdf"

LEVELS = (0.0, 0.8, 1.6)
FORMATS = ("ref64", "fp6", "int6")
PHASE = 2.0
REPS = 4000
OUT = Path("results/m2_heldout_dense_fp6_int6_20261109")
EXPECTED_RUNS = 216
QUALITY_CEILING = 5.0
EXTRA_GAP_CEILING_PP = 1.0

RUN_COLS = (
    "graph", "graph_sha256", "official_optimum",
    "offset_logit_halfspan", "configuration", "seed",
    "attempted_updates", "schedule", "beta", "scale",
    "returned_original_cut", "gap_pct", "actual_flips",
    "improvements", "returned_represented_energy",
    "returned_state_hex",
)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_json(obj):
    raw = json.dumps(
        obj, sort_keys=True, separators=(",", ":"),
        allow_nan=False
    ).encode()
    return sha_bytes(raw)


def save_json(path, obj):
    with path.open("x", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_csv(path, rows):
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def device_models():
    # Same single persistent offset population as completed CAL.
    base = models(100)

    zero = dict(base[0.8])
    zero.update(
        per_device_offset_logit=[0.0] * 100,
        offset_logit_halfspan_assumed=0.0,
        gain_halfspan_assumed=0.0,
    )

    result = {
        0.0: zero,
        0.8: base[0.8],
        1.6: base[1.6],
    }

    for d, model in result.items():
        validate_device_model(model, 100, offset_limit=d)
        assert all(x == 1.0 for x in model["per_device_gain"])

    return result


def code_hashes():
    root = Path(__file__).resolve().parents[1]
    names = [
        "experiments/m2_heldout_dense_sixbit.py",
        "experiments/m1_biqmac_precision_sweep.py",
        "experiments/m1_precision_codebooks.py",
        "experiments/m1_biqmac_ideal_pilot.py",
        "experiments/m1_biqmac_reference_quality_gate.py",
        "experiments/m2_e2_response_gate.py",
        "experiments/m2_offset_fp64_scout.py",
        "experiments/m2_coupling_matrix_snapshot_diagnostic.py",
        "experiments/biqmac_maxcut.py",
    ]
    return {
        name: sha_bytes((root / name).read_bytes())
        for name in names
    }


def selftest():
    # Tiny synthetic graph: no held-out data accessed.
    graph = SimpleNamespace(
        n=3,
        edges=((0, 1, 2), (1, 2, -3)),
    )
    model = {
        "evidence_level": EVIDENCE,
        "n_devices": 3,
        "per_device_gain": [1.0] * 3,
        "per_device_offset_logit": [0.0] * 3,
    }

    for fmt in FORMATS:
        if fmt == "ref64":
            rep = prepare(graph, "ref64", "source")
        else:
            rep = build_global(graph, fmt[:-1], 6)

        ideal = solve_reference(
            graph, rep, 0.15, 300, 12345, "linear"
        )
        e2 = solve_with_response(
            graph, rep, 0.15, 300, 12345,
            model, offset_limit=0.0
        )

        assert ideal["returned_state_hex"] == e2["returned_state_hex"]
        assert ideal["returned_original_cut"] == e2["returned_original_cut"]

    assert SEEDS_FROZEN == 24
    assert UPDATES_FROZEN == 50000
    assert len(paired_seed(GRAPH_INDEX)) == 24

    print("SELFTEST PASS: solver parity; held-out graph untouched")


def protocol():
    return {
        "status": "FROZEN_BEFORE_HELDOUT_ACCESS",
        "graph": NAME,
        "graph_index": GRAPH_INDEX,
        "graph_url": GRAPH_URL,
        "published_cut_optimum": OPTIMUM,
        "reference": OPTIMUM_SOURCE,
        "graph_sha256": "TO_BE_RECORDED_AFTER_FREEZE",
        "formats": list(FORMATS),
        "offset_levels_logit": list(LEVELS),
        "global_scale_policy": SCALE_POLICY,
        "device_evidence": EVIDENCE,
        "device_populations": 1,
        "device_model_hashes": {
            str(d): sha_json(m)
            for d, m in device_models().items()
        },
        "gain": 1.0,
        "seed_rule": "20261201 + 100000*4 + k",
        "seeds": list(paired_seed(GRAPH_INDEX)),
        "updates": UPDATES_FROZEN,
        "schedule": "linear beta 0.5 to 2.0",
        "return_policy": "lowest represented energy visited",
        "evaluation": "original signed weighted Max-Cut",
        "coupling": "J_ij=-w_ij, h_i=0",
        "snapshot_source": "FP64 returned state, same offset and seed",
        "snapshot_beta_multiplier": PHASE,
        "quality_screen_abs_gap_pct_upper": QUALITY_CEILING,
        "quality_screen_quant_loss_pp_upper": EXTRA_GAP_CEILING_PP,
        "bootstrap_resamples": REPS,
        "hypotheses": {
            "H1": "FP6 minus INT6 static mean |dP| < 0 at d=0.8 and d=1.6",
            "H2": "Measure FP6 minus INT6 solver gap; no assumed sign",
            "H3": "Measure offset interaction versus d=0",
        },
        "expected_new_runs": EXPECTED_RUNS,
        "code_hashes": code_hashes(),
        "limitations": (
            "One graph and one assumed device population; "
            "no measured physical-device variation."
        ),
    }


def freeze(out):
    selftest()
    if out.exists():
        raise FileExistsError(
            f"{out} already exists. Refusing to overwrite frozen work."
        )

    out.mkdir(parents=True)
    save_json(out / "protocol.json", protocol())

    print("\nPROTOCOL FROZEN")
    print("Path:", out / "protocol.json")
    print("No held-out graph accessed.")
    print("Run --execute only after reviewing protocol.")


def acquire_graph():
    if GRAPH_PATH.is_file():
        return GRAPH_PATH

    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = GRAPH_PATH.with_name(NAME + ".download_tmp")

    if tmp.exists():
        raise FileExistsError(f"Partial download exists: {tmp}")

    try:
        with urllib.request.urlopen(GRAPH_URL, timeout=60) as response:
            data = response.read()

        if len(data) < 100:
            raise ValueError("Downloaded graph looks invalid")

        with tmp.open("xb") as f:
            f.write(data)

        tmp.replace(GRAPH_PATH)
    finally:
        if tmp.exists():
            tmp.unlink()

    return GRAPH_PATH


def read_existing(path, graph_hash, seeds):
    if not path.exists():
        return {}

    allowed = {
        (d, fmt, seed)
        for d in LEVELS
        for fmt in FORMATS
        for seed in seeds
    }
    result = {}

    for row in read_csv(path):
        key = (
            float(row["offset_logit_halfspan"]),
            row["configuration"],
            int(row["seed"]),
        )

        if key not in allowed or key in result:
            raise ValueError("Unexpected or duplicate saved run")

        if (
            row["graph"] != NAME
            or row["graph_sha256"] != graph_hash
            or float(row["official_optimum"]) != OPTIMUM
            or int(row["attempted_updates"]) != UPDATES_FROZEN
            or row["schedule"] != "linear"
        ):
            raise ValueError("Saved run does not match frozen protocol")

        result[key] = row

    return result


def append_run(path, row):
    existing = path.exists()

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RUN_COLS)
        if not existing:
            writer.writeheader()
        writer.writerow(row)
        f.flush()


def mean_ci(values, bootstrap_seed):
    assert len(values) == SEEDS_FROZEN

    low, high = bootstrap_paired_ci(
        values, bootstrap_seed, replicates=REPS
    )

    return statistics.mean(values), low, high


def make_figures(out, quality, contrasts, snapshots):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib missing; CSV results still available.")
        return

    folder = out / "figures"
    folder.mkdir(exist_ok=True)

    colors = {
        "ref64": "#586174",
        "fp6": "#2864af",
        "int6": "#d27728",
    }

    # Figure 1: original Max-Cut gap and confidence intervals.
    fig, ax = plt.subplots(figsize=(8.5, 4.5))

    for j, fmt in enumerate(FORMATS):
        rows = sorted(
            [r for r in quality if r["configuration"] == fmt],
            key=lambda r: r["offset_logit_halfspan"],
        )
        x = [
            r["offset_logit_halfspan"] + (j-1)*0.12
            for r in rows
        ]
        y = [r["mean_gap_pct"] for r in rows]
        err = [
            [v-r["ci95_gap_lo_pct"] for v, r in zip(y, rows)],
            [r["ci95_gap_hi_pct"]-v for v, r in zip(y, rows)],
        ]

        ax.errorbar(
            x, y, yerr=err, fmt="o-",
            capsize=3, color=colors[fmt], label=fmt.upper()
        )

    ax.axhline(
        QUALITY_CEILING, linestyle="--",
        color="#9c2929", label="5% threshold"
    )
    ax.set_xticks(LEVELS)
    ax.set_xlabel("Assumed offset halfspan (logit)")
    ax.set_ylabel("Original-weight optimum gap (%)")
    ax.set_title("Held-out dense Max-Cut: 24 paired seeds")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(folder / "quality_gap_95ci.png", dpi=220)
    fig.savefig(folder / "quality_gap_95ci.pdf")
    plt.close(fig)

    # Figure 2: static switching-probability distortion.
    fig, ax = plt.subplots(figsize=(8.5, 4.5))

    for fmt in ("fp6", "int6"):
        rows = sorted(
            [r for r in snapshots if r["configuration"] == fmt],
            key=lambda r: r["offset_logit_halfspan"],
        )
        x = [r["offset_logit_halfspan"] for r in rows]
        y = [r["mean_abs_dP"] for r in rows]
        err = [
            [v-r["ci95_dP_lo"] for v, r in zip(y, rows)],
            [r["ci95_dP_hi"]-v for v, r in zip(y, rows)],
        ]

        ax.errorbar(
            x, y, yerr=err, fmt="o-",
            capsize=3, color=colors[fmt], label=fmt.upper()
        )

    ax.set_xticks(LEVELS)
    ax.set_xlabel("Assumed offset halfspan (logit)")
    ax.set_ylabel("Mean absolute switching-probability distortion")
    ax.set_title("Common FP64 states, beta multiplier = 2")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(folder / "probability_distortion_95ci.png", dpi=220)
    fig.savefig(folder / "probability_distortion_95ci.pdf")
    plt.close(fig)

    # Figure 3: offset-dependent FP6 vs INT6 interaction.
    rows = [
        r for r in contrasts
        if r["contrast"] == "FP6_gap_minus_INT6_gap"
        and r["offset_logit_halfspan"] > 0
    ]

    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    x = list(range(len(rows)))
    y = [r["did_mean_pp"] for r in rows]
    err = [
        [v-r["did_ci95_lo_pp"] for v, r in zip(y, rows)],
        [r["did_ci95_hi_pp"]-v for v, r in zip(y, rows)],
    ]

    ax.errorbar(x, y, yerr=err, fmt="o", capsize=4)
    ax.axhline(0, linestyle="--", color="gray")
    ax.set_xticks(x)
    ax.set_xticklabels([
        f"d={r['offset_logit_halfspan']}" for r in rows
    ])
    ax.set_ylabel("Difference-in-differences (pp)")
    ax.set_title("FP6–INT6 offset interaction")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(folder / "offset_interaction_95ci.png", dpi=220)
    fig.savefig(folder / "offset_interaction_95ci.pdf")
    plt.close(fig)


def analyze(out, runs, graph, reps, beta, devices):
    seeds = paired_seed(GRAPH_INDEX)

    gaps = {
        (d, fmt, seed): float(runs[(d, fmt, seed)]["gap_pct"])
        for d in LEVELS
        for fmt in FORMATS
        for seed in seeds
    }

    quality = []
    contrasts = []
    raw_snapshots = []
    snapshot_summary = []

    for di, d in enumerate(LEVELS):
        # Quality versus same-condition FP64.
        for fi, fmt in enumerate(FORMATS):
            values = [gaps[(d, fmt, s)] for s in seeds]
            references = [gaps[(d, "ref64", s)] for s in seeds]
            extra = [x-y for x, y in zip(values, references)]

            mean, lo, hi = mean_ci(
                values, 91000 + di*1000 + fi*41
            )
            emean, elo, ehi = mean_ci(
                extra, 92000 + di*1000 + fi*41
            )

            quality.append(dict(
                graph=NAME,
                offset_logit_halfspan=d,
                configuration=fmt,
                n_paired_seeds=SEEDS_FROZEN,
                device_populations=1,
                mean_gap_pct=mean,
                ci95_gap_lo_pct=lo,
                ci95_gap_hi_pct=hi,
                mean_extra_gap_pp=emean,
                ci95_extra_lo_pp=elo,
                ci95_extra_hi_pp=ehi,
                eligible=(
                    hi <= QUALITY_CEILING
                    and ehi <= EXTRA_GAP_CEILING_PP
                ),
            ))

        # Direct paired quality difference.
        direct = [
            gaps[(d, "fp6", s)] - gaps[(d, "int6", s)]
            for s in seeds
        ]

        ideal_direct = [
            gaps[(0.0, "fp6", s)] - gaps[(0.0, "int6", s)]
            for s in seeds
        ]

        interaction = [
            a-b for a, b in zip(direct, ideal_direct)
        ]

        mean, lo, hi = mean_ci(direct, 93000 + di*100)
        imean, ilo, ihi = mean_ci(interaction, 94000 + di*100)

        contrasts.append(dict(
            offset_logit_halfspan=d,
            contrast="FP6_gap_minus_INT6_gap",
            units="percentage_points",
            mean_difference=mean,
            ci95_difference_lo=lo,
            ci95_difference_hi=hi,
            did_mean_pp=imean,
            did_ci95_lo_pp=ilo,
            did_ci95_hi_pp=ihi,
        ))

        # Static diagnostic: same FP64 state for BOTH formats.
        for seed in seeds:
            state_hex = runs[(d, "ref64", seed)]["returned_state_hex"]
            spins = decode_spins(state_hex, graph.n)

            h_ref = local_fields(reps["ref64"], spins)

            for fmt in ("fp6", "int6"):
                h_quant = local_fields(reps[fmt], spins)
                metric = snapshot_metrics(
                    h_ref,
                    h_quant,
                    devices[d]["per_device_offset_logit"],
                    beta,
                    PHASE,
                )

                raw_snapshots.append(dict(
                    graph=NAME,
                    offset_logit_halfspan=d,
                    configuration=fmt,
                    seed=seed,
                    anneal_beta_multiplier=PHASE,
                    **metric,
                ))

        for fi, fmt in enumerate(("fp6", "int6")):
            matching = [
                r for r in raw_snapshots
                if r["offset_logit_halfspan"] == d
                and r["configuration"] == fmt
            ]

            values = [
                float(r["mean_abs_switch_prob_distortion"])
                for r in matching
            ]
            mean, lo, hi = mean_ci(
                values, 95000 + di*100 + fi
            )

            snapshot_summary.append(dict(
                offset_logit_halfspan=d,
                configuration=fmt,
                mean_abs_dP=mean,
                ci95_dP_lo=lo,
                ci95_dP_hi=hi,
                mean_abs_dH=statistics.mean(
                    float(r["mean_abs_dH"]) for r in matching
                ),
                mean_relative_rms_dH=statistics.mean(
                    float(r["relative_rms_field_error"])
                    for r in matching
                ),
            ))

        # Direct paired static probability-distortion difference.
        by_fmt = {
            fmt: {
                int(r["seed"]): float(
                    r["mean_abs_switch_prob_distortion"]
                )
                for r in raw_snapshots
                if r["offset_logit_halfspan"] == d
                and r["configuration"] == fmt
            }
            for fmt in ("fp6", "int6")
        }

        differences = [
            by_fmt["fp6"][s] - by_fmt["int6"][s]
            for s in seeds
        ]

        mean, lo, hi = mean_ci(
            differences, 96000 + di*100
        )

        contrasts.append(dict(
            offset_logit_halfspan=d,
            contrast="FP6_mean_abs_dP_minus_INT6_mean_abs_dP",
            units="absolute_probability",
            mean_difference=mean,
            ci95_difference_lo=lo,
            ci95_difference_hi=hi,
            did_mean_pp="",
            did_ci95_lo_pp="",
            did_ci95_hi_pp="",
        ))

    save_csv(out / "quality_summary.csv", quality)
    save_csv(out / "paired_contrasts.csv", contrasts)
    save_csv(out / "snapshot_rows.csv", raw_snapshots)
    save_csv(out / "snapshot_summary.csv", snapshot_summary)

    make_figures(out, quality, contrasts, snapshot_summary)

    save_json(out / "manifest.json", dict(
        status="DENSE_7777_216_RUNS_COMPLETE",
        graph=NAME,
        graph_sha256=graph.sha256,
        official_optimum=OPTIMUM,
        n_solver_runs=len(runs),
        n_static_snapshot_rows=len(raw_snapshots),
        device_populations=1,
        evidence_level=EVIDENCE,
        raw_runs_sha256=sha_bytes((out / "runs.csv").read_bytes()),
        protocol_sha256=sha_bytes(
            (out / "protocol.json").read_bytes()
        ),
        limitations=(
            "One held-out graph and one assumed E2 device "
            "population; not hardware validation."
        ),
    ))

    print("\n===== HELD-OUT VALIDATION COMPLETE =====")
    for r in quality:
        print(
            f"d={r['offset_logit_halfspan']:.1f} "
            f"{r['configuration']:5s} "
            f"gap={r['mean_gap_pct']:.3f}% "
            f"CI=[{r['ci95_gap_lo_pct']:.3f},"
            f"{r['ci95_gap_hi_pct']:.3f}] "
            f"eligible={r['eligible']}"
        )

    print("\n===== PAIRED CONTRASTS =====")
    for r in contrasts:
        print(
            f"d={r['offset_logit_halfspan']:.1f} "
            f"{r['contrast']} "
            f"mean={r['mean_difference']:+.6f} "
            f"CI=[{r['ci95_difference_lo']:+.6f},"
            f"{r['ci95_difference_hi']:+.6f}]"
        )

    print("\nSaved to:", out.resolve())


def execute(out):
    path = out / "protocol.json"

    if not path.is_file():
        raise FileNotFoundError(
            "Freeze the protocol FIRST using --freeze."
        )

    frozen = json.loads(path.read_text(encoding="utf-8"))

    if frozen != protocol():
        raise ValueError(
            "Protocol or code changed after freeze. "
            "Refusing held-out access."
        )

    selftest()

    source = acquire_graph()
    graph = load_rudy(source)

    if (
        graph.n != 100
        or graph.raw_edge_count != 4950
        or len(graph.edges) != 4950
    ):
        raise ValueError("Unexpected graph topology")

    graph_hash = sha_bytes(source.read_bytes())
    gate_path = out / "source_gate.json"

    if gate_path.exists():
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        if gate["graph_sha256"] != graph_hash:
            raise ValueError("Held-out graph changed")
    else:
        save_json(gate_path, dict(
            graph=NAME,
            graph_sha256=graph_hash,
            official_optimum=OPTIMUM,
            source_url=GRAPH_URL,
            n=graph.n,
            edge_count=len(graph.edges),
        ))

    beta = beta_from_original_graph(graph)
    devices = device_models()

    reps = {
        "ref64": prepare(graph, "ref64", "source"),
        "fp6": build_global(graph, "fp", 6),
        "int6": build_global(graph, "int", 6),
    }

    seeds = paired_seed(GRAPH_INDEX)
    raw_path = out / "runs.csv"
    runs = read_existing(raw_path, graph_hash, seeds)

    if (out / "manifest.json").exists():
        raise FileExistsError("This experiment is already complete.")

    for d in LEVELS:
        for fmt in FORMATS:
            rep = reps[fmt]

            for seed in seeds:
                key = (d, fmt, seed)

                if key in runs:
                    continue

                result = solve_with_response(
                    graph, rep, beta,
                    UPDATES_FROZEN, seed,
                    devices[d], offset_limit=d,
                )

                score = float(result["returned_original_cut"])

                if score > OPTIMUM + 1e-7:
                    raise AssertionError(
                        "Reported cut exceeds published optimum."
                    )

                row = dict(
                    graph=NAME,
                    graph_sha256=graph_hash,
                    official_optimum=OPTIMUM,
                    offset_logit_halfspan=d,
                    configuration=fmt,
                    seed=seed,
                    attempted_updates=UPDATES_FROZEN,
                    schedule="linear",
                    beta=beta,
                    scale=(
                        1.0 if fmt == "ref64"
                        else rep["scale"]
                    ),
                    returned_original_cut=score,
                    gap_pct=100 * (OPTIMUM-score) / OPTIMUM,
                    actual_flips=result["actual_flips"],
                    improvements=result["improvements"],
                    returned_represented_energy=(
                        result["returned_represented_energy"]
                    ),
                    returned_state_hex=result["returned_state_hex"],
                )

                append_run(raw_path, row)
                runs[key] = row

            print(
                f"DONE d={d:g}, format={fmt}, "
                f"24 seeds, total={len(runs)}/216",
                flush=True,
            )

    if len(runs) != EXPECTED_RUNS:
        raise AssertionError(
            f"Incomplete experiment: {len(runs)}/216"
        )

    analyze(out, runs, graph, reps, beta, devices)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--selftest", action="store_true")
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--execute", action="store_true")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    if args.selftest:
        selftest()
    elif args.freeze:
        freeze(args.out)
    elif args.execute:
        execute(args.out)


if __name__ == "__main__":
    main()
