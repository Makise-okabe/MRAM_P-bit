#!/usr/bin/env python3
"""Frozen archived-replay/top-16 certification and assumed-offset sensitivity.

No previous result is overwritten. Stage A enforces full per-run legacy parity.
Stage B reuses graph/solver keys with exactly one offset bank per graph.
All numbers arise from executing solver trajectories, never fabricated output.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time

import numpy as np

from experiments.biqmac_maxcut import load_rudy
from experiments.fyp_first_block_20261120 import canonical
from experiments.fyp_ideal_analysis import bootstrap_t_vectors, decision_labels
from experiments.fyp_ideal_campaign import validate_record_keys
from experiments.fyp_ideal_solver import representation
from experiments.fyp_ideal_sources import (
    CANDIDATES, FAMILIES, GRAPHS_PER_FAMILY, MAIN_SEEDS, UPDATES,
    graph_name, graph_relative_path, require_numpy_version, solver_seed,
)
from experiments.fyp_tail_probe import solve_buffered
from experiments.fyp_output_device_solver import solve_offset_buffered
from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/fyp_policy_device_20261121"
IDEAL = ROOT / "results/fyp_ideal_20261120"
SOURCES = ROOT / "data/fyp_locked_20261120"
REGISTRY = ROOT / "docs/FYP_POLICY_DEVICE_REGISTRY_20261121.json"
FULL_FREEZE = "d217ab54fc41a3a84d6a500f3ab0f3aa433059dd"
LEGACY = ("seed", "attempted_updates", "actual_flips", "improvements",
          "returned_original_cut", "final_original_cut", "returned_represented_energy",
          "final_represented_energy", "returned_state_hex", "V", "M", "R",
          "R_last", "V_state_hex", "M_state_hex", "checkpoints")
SELECTED = {0: ("ref64", "fp5", "int6"), 1: ("ref64", "fp5", "int5")}
ARMS_B = {0: ("ref64", "fp5", "int6", "fp6"),
          1: ("ref64", "fp5", "int5", "fp6", "int6")}
K = 16
BOOT = 500_000
Q_BUFFER = 0.01 / (2 * 12)
Q_DEVICE = 0.01 / (2 * 6)
TOLS = (0.25, 0.5, 1.0)
CODE_PATHS = ("experiments/fyp_output_device_solver.py",
              "experiments/fyp_policy_device_20261121.py",
              "experiments/fyp_tail_probe.py",
              "experiments/fyp_ideal_solver.py",
              "experiments/fyp_ideal_analysis.py",
              "experiments/fyp_ideal_sources.py",
              "experiments/m1_precision_codebooks.py",
              "docs/FYP_POLICY_DEVICE_REGISTRY_20261121.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj, compress=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    if compress:
        data = gzip.compress(data, compresslevel=6, mtime=0)
    with path.open("xb") as stream:
        stream.write(data)


def load(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def gate():
    require_numpy_version()
    spec = load(REGISTRY)
    if spec["schema"] != "fyp-policy-device-20261121-v1":
        raise ValueError("Unknown protocol")
    if tuple(spec["stage_a"]["formats"]) != CANDIDATES or spec["buffer_k"] != K:
        raise ValueError("Changed stage A registry")
    if spec["bootstrap_resamples"] != BOOT or spec["alpha_buffer"] != 0.01 or spec["alpha_device"] != 0.01:
        raise ValueError("Changed inferential registry")
    if spec["stage_b"]["gain"] != 1.0 or spec["stage_b"]["offset_halfspan"] != 0.8:
        raise ValueError("Changed device condition")
    for family, names in ARMS_B.items():
        if tuple(spec["stage_b"]["arms"][FAMILIES[family]]) != names:
            raise ValueError("Changed Stage B arms")
    current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    expected = os.environ.get("FYP_POLICY_FREEZE_SHA")
    if expected and expected != current:
        raise ValueError("Checkout not pinned to workflow-trigger freeze SHA")
    return current


def extract():
    expected = {f"{family}/{i:03d}.rudy" for family in ("ring", "torus") for i in range(72)}
    with tarfile.open(SOURCES/"sources.tar.gz", "r:gz") as archive:
        members = archive.getmembers()
        if len(members) != 144 or {m.name for m in members} != expected or any(not m.isfile() for m in members):
            raise ValueError("Frozen source tar members mismatch")
        for member in members:
            path = SOURCES/member.name
            data = archive.extractfile(member).read()
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and path.read_bytes() != data:
                raise ValueError("Source overwrite refused")
            if not path.exists():
                with path.open("xb") as output:
                    output.write(data)
    print("EXTRACT PASS: exactly 144 frozen graphs", flush=True)


def original_bundle(family, index):
    low = (index // 12) * 12
    family_name = FAMILIES[family]
    name = IDEAL/"raw_archives"/f"generated-{family_name}-{low:03d}-{low+11:03d}.tar.gz"
    prefix = f"generated/{family_name}/{index:03d}/"
    with tarfile.open(name, "r:gz") as archive:
        manifest = json.loads(archive.extractfile(prefix+"manifest.json").read())
        raw = archive.extractfile(prefix+"records.jsonl.gz").read()
    if sha_bytes(raw) != manifest["file_sha256"]["records.jsonl.gz"]:
        raise ValueError("Original bundle byte digest mismatch")
    rows = [json.loads(line) for line in gzip.decompress(raw).decode("utf-8").splitlines()]
    validate_record_keys(rows, "generated", family, index)
    for row in rows:
        digest = row["record_sha256"]
        if sha_bytes(canonical({k: v for k, v in row.items() if k != "record_sha256"}).encode()) != digest:
            raise ValueError("Archived record payload digest mismatch")
    if manifest["B_g"] <= 0 or manifest["graph"] != graph_name(family, index):
        raise ValueError("Reference denominator or original graph invalid")
    return manifest, [r for r in rows if r["stage"] == "main"]


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def verify_parity(new, old, context):
    for key in LEGACY:
        if key not in old or new[key] != old[key]:
            raise AssertionError(f"STOP: archived replay parity failed: {context} / {key}")
    if not new["R"] <= new["buffer_best_original_cut"] <= new["V"]:
        raise AssertionError("Buffer quality ordering invalid")


def preflight():
    frozen_commit = gate()
    extract()
    subprocess.run([sys.executable, "results/fyp_ideal_20261120/operational/archive.py",
                    "--freeze-commit", FULL_FREEZE, "--verify-only"], cwd=ROOT, check=True)
    verified = []
    for family in (0, 1):
        graph = load_rudy(SOURCES / graph_relative_path(family, 0))
        manifest, rows = original_bundle(family, 0)
        if graph.sha256 != manifest["graph_sha256"]:
            raise AssertionError("Frozen graph hash mismatch")
        beta = beta_from_original_graph(graph)
        reps = {fmt: representation(graph, fmt) for fmt in ("ref64", "fp5", "fp6", "int6")}
        for fmt in reps:
            old = next(r for r in rows if r["representation"] == fmt and r["replicate"] == 0)
            a = solve_buffered(graph, reps[fmt], beta, UPDATES, old["seed"],
                               source_rep=reps["ref64"], capacity=K)
            b = solve_offset_buffered(graph, reps[fmt], beta, UPDATES, old["seed"],
                                      source_rep=reps["ref64"], capacity=K, offsets=(0.0,) * 100)
            verify_parity(a, old, (family, fmt))
            if a != b:
                raise AssertionError("Entire zero-offset solver output parity failed")
            verified.append({"family": FAMILIES[family], "format": fmt, "status": "PASS"})
    save(OUT/"preflight.json", {
        "status": "PASS", "freeze_commit": frozen_commit,
        "code_sha256": {p: sha(ROOT/p) for p in CODE_PATHS},
        "ideal_archive_registry_sha256": sha(IDEAL/"raw_archives/archive_registry.json"),
        "parity_checks": verified, "buffer_k": K, "main_runs_not_yet_executed": True})
    print("PREFLIGHT PASS: archival verification and 8 double-solver checks", flush=True)


def run_a(family, start, stop):
    frozen_commit = gate()
    if not 0 <= start < stop <= 72:
        raise ValueError("Invalid shard")
    for index in range(start, stop):
        graph = load_rudy(SOURCES/graph_relative_path(family, index))
        manifest, archived = original_bundle(family, index)
        if graph.sha256 != manifest["graph_sha256"]:
            raise AssertionError("Source SHA mismatch")
        by_key = {(r["representation"], r["seed"]): r for r in archived}
        if len(by_key) != 448:
            raise ValueError("Archived main records incomplete")
        beta = beta_from_original_graph(graph)
        reps = {fmt: representation(graph, fmt) for fmt in CANDIDATES}
        rows = []
        for fmt in CANDIDATES:
            for replicate in range(MAIN_SEEDS):
                seed = solver_seed("main", family, index, replicate)
                old = by_key[(fmt, seed)]
                new = solve_buffered(graph, reps[fmt], beta, UPDATES, seed,
                                     source_rep=reps["ref64"], capacity=K)
                verify_parity(new, old, (family, index, fmt, replicate))
                rows.append({"representation": fmt, "replicate": replicate,
                             "source_record_sha256": old["record_sha256"], **new})
        save(OUT/"stage_a"/FAMILIES[family]/f"{index:03d}.json.gz", {
            "status": "FULL_PARITY_PASS", "family": FAMILIES[family], "index": index,
            "graph_sha256": graph.sha256, "freeze_commit": frozen_commit,
            "B_g": manifest["B_g"], "records": len(rows), "rows": rows}, True)
        print(f"Stage A parity PASS {FAMILIES[family]}/{index:03d} 448/448", flush=True)


def run_b(family, start, stop):
    frozen_commit = gate()
    if not 0 <= start < stop <= 72:
        raise ValueError("Invalid shard")
    for index in range(start, stop):
        prior = load(OUT/"stage_a"/FAMILIES[family]/f"{index:03d}.json.gz")
        if prior["status"] != "FULL_PARITY_PASS" or len(prior["rows"]) != 448:
            raise ValueError("Missing certified Stage A replay")
        graph = load_rudy(SOURCES/graph_relative_path(family, index))
        if graph.sha256 != prior["graph_sha256"]:
            raise ValueError("Stage B source mismatch")
        offsets = np.random.Generator(np.random.PCG64DXSM(
            np.random.SeedSequence([20261120, 930, family, index]))).uniform(-0.8, 0.8, size=graph.n)
        if graph.n != 100 or np.any(np.abs(offsets) > 0.8):
            raise AssertionError("Offset bank invalid")
        reps = {fmt: representation(graph, fmt) for fmt in ARMS_B[family]}
        beta = beta_from_original_graph(graph)
        rows = []
        for fmt in ARMS_B[family]:
            for replicate in range(MAIN_SEEDS):
                seed = solver_seed("main", family, index, replicate)
                sample = solve_offset_buffered(graph, reps[fmt], beta, UPDATES, seed,
                                               source_rep=reps["ref64"], capacity=K, offsets=offsets)
                rows.append({"representation": fmt, "replicate": replicate, **sample})
        save(OUT/"stage_b"/FAMILIES[family]/f"{index:03d}.json.gz", {
            "status": "COMPLETE", "family": FAMILIES[family], "index": index,
            "graph_sha256": graph.sha256, "freeze_commit": frozen_commit,
            "B_g": prior["B_g"], "gain": 1.0, "offset_halfspan": 0.8,
            "offset_bank_seed": [20261120, 930, family, index],
            "offset_bank_sha256": sha_bytes(offsets.tobytes()), "offsets": offsets.tolist(),
            "records": len(rows), "rows": rows}, True)
        print(f"Stage B COMPLETE {FAMILIES[family]}/{index:03d} {len(rows)} calls", flush=True)


def all_rows(stage):
    output = {}
    for family in (0, 1):
        for i in range(72):
            obj = load(OUT/stage/FAMILIES[family]/f"{i:03d}.json.gz")
            count = 448 if stage == "stage_a" else len(ARMS_B[family])*MAIN_SEEDS
            if obj["family"] != FAMILIES[family] or obj["index"] != i:
                raise ValueError("Missing/wrong graph")
            if obj["records"] != count or len(obj["rows"]) != count:
                raise ValueError("Wrong run count")
            keys = {(r["representation"], r["seed"]) for r in obj["rows"]}
            if len(keys) != count:
                raise ValueError("Duplicate/unregistered record keys")
            output[(family, i)] = obj
    return output


def row_map(rows):
    return {(r["representation"], r["seed"]): r for r in rows}


def avg(values):
    return float(np.mean(values))


def metrics(row, ref, bg):
    factor = 100.0/bg
    access = (ref["V"] - row["V"])*factor
    selection = (row["V"] - row["R"])*factor
    return {
        "access_A_pp": access,
        "selection_Rz_pp": selection,
        "represented_selection_pp": (row["V"]-row["M"])*factor,
        "earliest_tie_pp": (row["M"]-row["R"])*factor,
        "extra_loss_pp": (ref["R"]-row["R"])*factor,
        "buffer_extra_loss_pp": (ref["buffer_best_original_cut"] -
                                 row["buffer_best_original_cut"])*factor,
        "buffer_recovery_pp": (row["buffer_best_original_cut"]-row["R"])*factor,
        "tied_minimum_states": row["minimum_distinct_states"],
    }


def infer(matrix, contrast_names, family, stage):
    q = Q_BUFFER if stage == "A" else Q_DEVICE
    out = bootstrap_t_vectors(matrix, q=q, resamples=BOOT,
                              seed_sequence=[20261121, 955 if stage == "A" else 956, family])
    return [{"stage": stage, "family": FAMILIES[family], "contrast": name, **r,
             "decisions": {str(t): decision_labels(r["mean"], r["low"], r["high"], t)
                           for t in TOLS}}
            for name, r in zip(contrast_names, out)]


def analyse_a():
    dataset = all_rows("stage_a")
    contrasts, mech, graph_effects = [], [], []
    for family in (0, 1):
        candidate_names = list(CANDIDATES[1:])
        matrix = []
        for index in range(72):
            graph = dataset[(family, index)]
            rows, bg = row_map(graph["rows"]), graph["B_g"]
            vector = []
            for fmt in candidate_names:
                d = [100.0*(rows[("ref64", solver_seed("main", family, index, rep))]
                            ["buffer_best_original_cut"] -
                            rows[(fmt, solver_seed("main", family, index, rep))]
                            ["buffer_best_original_cut"])/bg for rep in range(MAIN_SEEDS)]
                vector.append(avg(d))
                graph_effects.append({"family": FAMILIES[family], "index": index,
                                      "format": fmt, "buffer_extra_loss_pp": vector[-1]})
            matrix.append(vector)
            for fmt in CANDIDATES:
                values = [metrics(rows[(fmt, solver_seed("main", family, index, r))],
                                  rows[("ref64", solver_seed("main", family, index, r))], bg)
                          for r in range(MAIN_SEEDS)]
                mech.append({"family": FAMILIES[family], "index": index, "format": fmt,
                             **{key: avg([x[key] for x in values]) for key in values[0]}})
        contrasts.extend(infer(np.asarray(matrix), [f"{f}-ref64" for f in candidate_names],
                               family, "A"))
    width = {}
    for family in (0, 1):
        family_name = FAMILIES[family]
        rows = [r for r in contrasts if r["family"] == family_name]
        width[family_name] = {}
        for t in TOLS:
            labels = {r["contrast"].split("-")[0]: r["decisions"][str(t)]["qualification"]
                      for r in rows}
            fp = next((f for f in ("fp5", "fp6") if labels[f] == "PASS"), None)
            inte = next((f for f in ("int5", "int6", "int7", "int8") if labels[f] == "PASS"), None)
            width[family_name][str(t)] = {
                "formats": labels, "lowest_certified_FP": fp, "lowest_certified_INT": inte,
                "k_cert": int(inte[3:])-int(fp[2:]) if fp and inte else None}
    save(OUT/"analysis"/"stage_a_certification.json", {
        "status": "COMPLETE", "full_archived_record_parity": "64512/64512",
        "registered_contrasts": 12, "alpha_buffer": 0.01,
        "bootstrap": "whole-graph studentized bootstrap-t, Bonferroni",
        "contrasts": contrasts, "certification": width,
        "first_block_buffer_data": "missing: immutable first-block not replayed",
        "anchor_buffer_data": "missing: anchors excluded from generated replay"})
    save(OUT/"analysis"/"stage_a_graph_mechanisms.json", mech)
    save(OUT/"analysis"/"stage_a_graph_contrasts.json", graph_effects)
    print("A ANALYSIS COMPLETE 64512/64512 parity and 12 registered contrasts", flush=True)


def analyse_b():
    ideal, device = all_rows("stage_a"), all_rows("stage_b")
    contrasts, graph_mechanisms = [], []
    for family in (0, 1):
        fmt = SELECTED[family][1]
        inte = SELECTED[family][2]
        matrix = []
        for index in range(72):
            a, b = ideal[(family, index)], device[(family, index)]
            if a["graph_sha256"] != b["graph_sha256"] or a["B_g"] != b["B_g"]:
                raise ValueError("Stage A/B graph mismatch")
            base, actual, bg = row_map(a["rows"]), row_map(b["rows"]), a["B_g"]
            columns = [[], [], []]
            per_arm = {arm: [] for arm in ARMS_B[family]}
            for rep in range(MAIN_SEEDS):
                seed = solver_seed("main", family, index, rep)
                fp, ip, ref = (actual[(x, seed)] for x in (fmt, inte, "ref64"))
                columns[0].append((ip["R"]-fp["R"])*100.0/bg)
                columns[1].append((ref["R"]-fp["R"])*100.0/bg)
                columns[2].append((ref["R"]-ip["R"])*100.0/bg)
                for arm in ARMS_B[family]:
                    now = metrics(actual[(arm, seed)], ref, bg)
                    old = metrics(base[(arm, seed)], base[("ref64", seed)], bg)
                    per_arm[arm].append({
                        **{"offset_"+k: v for k, v in now.items()},
                        **{"ideal_"+k: v for k, v in old.items()},
                        **{"shift_"+k: v-old[k] for k, v in now.items()}})
            matrix.append([avg(column) for column in columns])
            for arm, values in per_arm.items():
                graph_mechanisms.append({
                    "family": FAMILIES[family], "index": index, "format": arm,
                    "bank_sha256": b["offset_bank_sha256"],
                    **{key: avg([x[key] for x in values]) for key in values[0]}})
        contrasts.extend(infer(np.asarray(matrix),
            [f"{fmt}-{inte}", f"{fmt}-ref64", f"{inte}-ref64"], family, "B"))
    save(OUT/"analysis"/"stage_b_device_contrasts.json", {
        "status": "COMPLETE", "registered_contrasts": 6, "alpha_device": 0.01,
        "independent_units": "72 graph-bank pairs per family",
        "offsets": "persistent U[-0.8,+0.8] logit; assumed not measured",
        "gain": 1.0, "selected": {FAMILIES[f]: SELECTED[f] for f in (0, 1)},
        "contrasts": contrasts, "registered_trajectories": 27648,
        "descriptive_trajectories": 13824})
    save(OUT/"analysis"/"stage_b_graph_mechanisms.json", graph_mechanisms)
    print("B ANALYSIS COMPLETE 41472 solver calls / six registered contrasts", flush=True)


def summarize():
    a = load(OUT/"analysis"/"stage_a_certification.json")
    b = load(OUT/"analysis"/"stage_b_device_contrasts.json")
    lines = [
        "# Policy buffer and persistent-offset Checkpoint 1",
        "", "This report is produced from verified solver outputs, not estimates.",
        "Only ideal/assumed-logit software p-bit simulations; no MTJ physical model.",
        "", "## Stage A: full archived replay and top-16 certification",
        "", "64,512 main records, exact parity of legacy output and 12 registered contrasts.",
        "", "| Family | Candidate - FP64 | Mean pp | Lower pp | Upper pp | +0.5 status |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in a["contrasts"]:
        lines.append(f'| {row["family"]} | {row["contrast"]} | {row["mean"]:.6f} | {row["low"]} | {row["high"]} | {row["decisions"]["0.5"]["qualification"]} |')
    lines += ["", "Original no-buffer certified choices: ring FP5/INT6, k=1; torus FP5/INT5, k=0.",
              "Buffer-policy ladder at tolerances +0.25, +0.5 and +1.0 pp:",
              json.dumps(a["certification"], indent=2), "",
              "## Stage B: persistent offset validation", "",
              "27,648 selected-triple and 13,824 specifically registered descriptive-arm runs.",
              "", "| Family | Registered contrast | Mean pp | Lower pp | Upper pp | +0.5 status |",
              "|---|---|---:|---:|---:|---|"]
    for row in b["contrasts"]:
        lines.append(f'| {row["family"]} | {row["contrast"]} | {row["mean"]:.6f} | {row["low"]} | {row["high"]} | {row["decisions"]["0.5"]["qualification"]} |')
    lines += ["", "See analysis/stage_a_graph_mechanisms.json and stage_b_graph_mechanisms.json",
              "for access, represented selection, earliest-tie, top-16, and ideal-to-offset shifts.",
              "FP6-INT6 under offsets remains descriptive; this does not rerun the weak-tail intervention.",
              "The reused first-block and official-anchor buffer observations are missing.",
              "No gain variation, EDA, hardware or power analyses were performed.", ""]
    path = OUT/"RESULTS.md"
    with path.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=("extract","preflight","a","analyse-a",
                                      "b","analyse-b","summarize"))
    p.add_argument("--family", choices=("ring","torus"))
    p.add_argument("--start", type=int)
    p.add_argument("--stop", type=int)
    args = p.parse_args()
    if args.command == "extract":
        gate()
        extract()
    elif args.command == "preflight":
        preflight()
    elif args.command in ("a","b"):
        if args.family is None or args.start is None or args.stop is None:
            p.error("A/B requires --family --start --stop")
        family = 0 if args.family == "ring" else 1
        (run_a if args.command == "a" else run_b)(family, args.start, args.stop)
    elif args.command == "analyse-a":
        analyse_a()
    elif args.command == "analyse-b":
        analyse_b()
    else:
        summarize()


if __name__ == "__main__":
    main()
