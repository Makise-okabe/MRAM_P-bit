#!/usr/bin/env python3
"""Assemble the prospective executable freeze; no solver or held-out access.

The generated sources are committed as a deterministic archive plus individual
SHA256 values. Extraction does not regenerate or resample any graph.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import platform
from pathlib import Path
import subprocess
import tarfile

import numpy as np

from experiments.fyp_ideal_analysis import analysis_registry
from experiments.fyp_ideal_sources import (
    ANCHORS, CANDIDATES, FAMILIES, anchor_seed, graph_name,
    graph_relative_path, graph_seed_sequence, protocol_parameters,
    solver_seed, verify_sources,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("data/fyp_locked_20261120")
PREFLIGHT = Path("results/fyp_ideal_preflight_20261120")
FREEZE = Path("docs/FYP_IDEAL_FREEZE_20261120.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def save_new(path, content):
    path = Path(path)
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError(f"refuse to change prospective artifact: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def deterministic_gzip(content):
    stream = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0, compresslevel=9) as f:
        f.write(content)
    return stream.getvalue()


def assemble():
    if Path.cwd() != ROOT:
        raise ValueError("run from repository root")
    if FREEZE.exists():
        raise ValueError("freeze already exists; never revise it after execution")
    for anchor in ANCHORS:
        if "6666" in anchor["name"] and (Path("data/biqmac/raw/ising") / anchor["name"]).exists():
            raise ValueError("held-out source present before freeze")
    if Path("results/fyp_ideal_20261120").exists():
        raise ValueError("prospective result directory exists before freeze")
    source_manifest = verify_sources(SOURCE)
    required = ("archived_parity.json", "archived_parity_plan.json",
                "synthetic_solver_verification.json", "pipeline_timing.json",
                "execution_plan.json", "analysis_synthetic_verification.json",
                "first_block_analysis_smoke.json", "campaign_synthetic_verification.json")
    for name in required:
        if not (PREFLIGHT / name).is_file():
            raise ValueError(f"missing preflight evidence: {name}")
    for path in PREFLIGHT.rglob("*"):
        if path.is_file() and "FAIL" in path.name.upper():
            raise ValueError(f"preflight failure marker: {path}")

    # The archive contains all original saved bytes, in fixed family/index order.
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT) as tf:
        for graph in source_manifest["graphs"]:
            content = (SOURCE / graph["file"]).read_bytes()
            info = tarfile.TarInfo(graph["file"])
            info.size = len(content)
            info.mode = 0o644
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tf.addfile(info, io.BytesIO(content))
    archive = SOURCE / "sources.tar.gz"
    save_new(archive, deterministic_gzip(buffer.getvalue()))

    seeds = {
        "scope": "fixed namespaces and complete seed lists; paired main seeds across seven codes",
        "generated": [
            {"family": f, "index": g, "graph": graph_name(f, g),
             "graph_seed_sequence": graph_seed_sequence(f, g),
             "main": [solver_seed("main", f, g, r) for r in range(64)],
             "reference": [solver_seed("reference", f, g, r) for r in range(128)]}
            for f in FAMILIES for g in range(72)
        ],
        "anchors": [{**a, "seeds": [anchor_seed(a["index"], r) for r in range(128)]}
                    for a in ANCHORS],
        "offset": "RESERVED, NOT EXECUTED: SeedSequence([20261120,930,family,index])",
    }
    seed_file = SOURCE / "seed_manifest.json.gz"
    save_new(seed_file, deterministic_gzip(json_bytes(seeds)))
    registry = analysis_registry()
    core_path = Path("docs/FYP_IDEAL_CORE_REGISTRY_20261120.json")
    descriptive_path = Path("docs/FYP_IDEAL_DESCRIPTIVE_REGISTRY_20261120.json")
    save_new(core_path, json_bytes({k: v for k, v in registry.items() if k != "descriptive"}))
    save_new(descriptive_path, json_bytes({
        **registry["descriptive"],
        "resamples": registry["resamples"], "quantile": registry["quantile"],
        "rng": registry["rng"],
        "family_seed_sequences": registry["descriptive_seed_sequences"],
        "anchor_seed_sequences": registry["anchor_seed_sequences"],
        "anchor_intervals": "ordinary paired-seed 95% bootstrap-t, no core alpha",
        "anchor_spread": "all nine contrast means and seven candidate mean shortfalls; empirical min/max and linear 2.5/97.5 percentiles; not prediction intervals",
        "anchor_reference": "max(0,V) over 7*128 anchor trajectories; published optimum remains primary; pool differs from generated 576",
        "source_spread": "max absolute raw weight and raw zero count; no exclusions",
    }))
    files = set(Path("experiments").glob("*.py"))
    files.update(Path("tests").glob("test_fyp_ideal*.py"))
    files.update(p for p in PREFLIGHT.rglob("*") if p.is_file())
    files.update(p for p in Path("results/fyp_first_block_20261120").iterdir() if p.is_file())
    files.update((Path("docs/FYP_STUDY_LOCK_20261120.md"),
                  Path("docs/FYP_MECHANISM_AMENDMENT_20261120.md"),
                  Path("docs/FYP_IDEAL_EXECUTION_20261120.md"),
                  Path(".github/workflows/fyp-ideal-locked.yml"), core_path, descriptive_path,
                  archive, seed_file, SOURCE / "source_manifest.json",
                  SOURCE / "source_statistics.csv", SOURCE / "source_scale_comparison.json"))
    files.update(SOURCE / graph_relative_path(f, g) for f in FAMILIES for g in range(72))
    files.update(Path("data/biqmac/raw/ising") / a["name"] for a in ANCHORS if "6666" not in a["name"])
    hashes = {p.as_posix(): sha(p) for p in sorted(files)}
    first_block = "results/fyp_first_block_20261120/records.jsonl"
    if hashes[first_block] != "5146df3096376a74aa5e9538cdec6319f1044185c153af88234898852f16e0a0":
        raise ValueError("first-block archive changed")
    manifest = {
        "schema": "fyp-ideal-executable-freeze-v1", "study_date": "2026-11-20",
        "status": "FROZEN_BEFORE_OFFICIAL_6666_ACCESS_AND_MAIN_ENSEMBLE_EXECUTION",
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                    "platform": platform.platform()},
        "parameters": protocol_parameters(), "analysis_registry": registry,
        "source_manifest_path": (SOURCE / "source_manifest.json").as_posix(),
        "source_manifest_sha256": sha(SOURCE / "source_manifest.json"),
        "source_archive_path": archive.as_posix(), "source_archive_sha256": sha(archive),
        "seed_manifest_path": seed_file.as_posix(), "seed_manifest_sha256": sha(seed_file),
        "source_sha256": hashes,
        "expected_counts": {"generated_graphs": 144, "generated_main": 64512,
            "generated_reference": 18432, "anchor_records": 5376,
            "first_block_reused": 768, "new_solver_runs": 87552,
            "raw_ideal_records_including_reuse": 88320, "historical_beta_controls_not_rerun": 512,
            "generated_fidelity_records": 221184, "anchor_fidelity_records": 18432},
        "reference_pool": {"value_field": "V", "main": "7*64", "independent_FP64": 128,
            "empty_cut_fallback": 0, "witness": "exact integer original-weight rescore and saved V_state_hex",
            "frozen_after_pool": True, "unknown_optimum_claim": False},
        "held_out_source_access": {"accessed_before_freeze": False,
            "sources": [{**a, "url": "https://biqmac.aau.at/library/mac/ising/" + a["name"],
                         "sha256": None, "hash_policy": "record exact downloaded bytes after freeze; never pretend pre-known"}
                        for a in ANCHORS if "6666" in a["name"]]},
        "first_block": {"policy": "reuse exactly 768 raw rows; no campaign rerun or R_last reconstruction",
                        "R_last_available": False, "archive_records_sha256": hashes[first_block]},
        "checkpoint": "STOP after ideal results; offset, gain and hardware not authorized",
    }
    save_new(FREEZE, json_bytes(manifest))
    print(json.dumps({"freeze": FREEZE.as_posix(), "sha256": sha(FREEZE),
                      "source_files_hashed": len(hashes), "generated_graphs": 144,
                      "source_archive_bytes": archive.stat().st_size,
                      "seed_archive_bytes": seed_file.stat().st_size}, sort_keys=True))


if __name__ == "__main__":
    assemble()
