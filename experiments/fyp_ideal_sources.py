#!/usr/bin/env python3
"""Source-only generator and seed namespaces for the locked 2026-11-20 study.

This module never runs a solver or reads official 6666 files.  Generated Rudy
files retain raw zero entries so source integerization is independently auditable.
The complete source manifest must be committed in the executable freeze before
the first ensemble trajectory is run.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal
import hashlib
import json
import platform
from pathlib import Path
from typing import Iterable

import numpy as np


NUMPY_VERSION = "2.3.5"
N = 100
GRAPHS_PER_FAMILY = 72
MAIN_SEEDS = 64
REFERENCE_SEEDS = 128
ANCHOR_SEEDS = 128
UPDATES = 50_000
SOURCE_MULTIPLIER = 100_000
FAMILIES = {0: "ring", 1: "torus"}
CANDIDATES = ("ref64", "fp5", "fp6", "int5", "int6", "int7", "int8")
ANCHORS = (
    {"index": 0, "family": 0, "name": "ising2.5-100_5555", "published_optimum": 2460049},
    {"index": 1, "family": 0, "name": "ising2.5-100_6666", "published_optimum": 2031217},
    {"index": 2, "family": 0, "name": "ising2.5-100_7777", "published_optimum": 3363230},
    {"index": 3, "family": 1, "name": "t2g10_5555", "published_optimum": 6049461},
    {"index": 4, "family": 1, "name": "t2g10_6666", "published_optimum": 5757868},
    {"index": 5, "family": 1, "name": "t2g10_7777", "published_optimum": 6509837},
)
VIEWED_SOURCE_HASHES = {
    "ising2.5-100_5555": "c8fa3ce4df1997b89aad6199525a66e55699c259680483b62cc5fd3cfc1e316e",
    "ising2.5-100_7777": "109e1ed2edc71d5f43d623367410d9257a72662d665c7a0c71af4cdd8babaf99",
    "t2g10_5555": "c742b78ebdebb47ad7146bffd657d42fab814a7fa82c4a17942b37f2f7fa96cb",
    "t2g10_7777": "8f7dc4e791eb4893f7b7114b6ac51d29f37f652645ba58a22e3cd29b709fd4ef",
}
DEFAULT_OUT = Path("data/fyp_locked_20261120")


def require_numpy_version() -> None:
    if np.__version__ != NUMPY_VERSION:
        raise RuntimeError(f"NumPy {NUMPY_VERSION} required; found {np.__version__}")


def _integer_in(value: int, lower: int, upper: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or not lower <= value < upper:
        raise ValueError(f"{label} must be an integer in [{lower},{upper})")


def _check_graph(family: int, index: int) -> None:
    _integer_in(family, 0, 2, "family")
    _integer_in(index, 0, GRAPHS_PER_FAMILY, "graph index")


def graph_name(family: int, index: int) -> str:
    _check_graph(family, index)
    return f"{FAMILIES[family]}_{index:03d}"


def graph_relative_path(family: int, index: int) -> str:
    _check_graph(family, index)
    return f"{FAMILIES[family]}/{index:03d}.rudy"


def graph_seed_sequence(family: int, index: int) -> list[int]:
    _check_graph(family, index)
    return [20261120, 910, int(family), int(index)]


def solver_seed(stage: str, family: int, index: int, replicate: int) -> int:
    """Locked reference/main streams, independent by graph and paired by code."""
    _check_graph(family, index)
    if stage == "reference":
        domain, count = 10**12, REFERENCE_SEEDS
    elif stage == "main":
        domain, count = 2 * 10**12, MAIN_SEEDS
    else:
        raise ValueError("stage must be 'reference' or 'main'")
    _integer_in(replicate, 0, count, "replicate")
    return int(domain + 100_000 * family + 1_000 * index + replicate)


def anchor_seed(anchor_index: int, replicate: int) -> int:
    _integer_in(anchor_index, 0, 6, "anchor index")
    _integer_in(replicate, 0, ANCHOR_SEEDS, "replicate")
    return int(3 * 10**12 + 10_000 * anchor_index + replicate)


def bootstrap_seed_sequence(family: int, *, descriptive: bool = False) -> list[int]:
    _integer_in(family, 0, 2, "family")
    entropy = [20261120, 940, int(family)]
    return entropy + [1] if descriptive else entropy


def ring_normalization(n: int = N) -> float:
    """c_N from the full periodic ring, summing all j != i (not half-ring)."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 3:
        raise ValueError("ring size must be an integer >= 3")
    distance = (n / np.pi) * np.sin(np.pi * np.arange(1, n, dtype=np.float64) / n)
    return float(np.sum(distance ** -5, dtype=np.float64) ** -0.5)


def torus_edges(side: int = 10) -> tuple[tuple[int, int], ...]:
    if isinstance(side, bool) or not isinstance(side, int) or side < 3:
        raise ValueError("torus side must be an integer >= 3")
    pairs: set[tuple[int, int]] = set()
    for x in range(side):
        for y in range(side):
            u = side * x + y
            for v in (side * ((x + 1) % side) + y, side * x + (y + 1) % side):
                pairs.add(tuple(sorted((u, v))))
    return tuple(sorted(pairs))


def _round_weights(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    if not np.all(np.isfinite(values)) or np.any(np.abs(values) >= 2**63):
        raise ValueError("nonfinite/out-of-int64 source value")
    return np.rint(values).astype(np.int64)


def generate_graph(family: int, index: int) -> tuple[tuple[tuple[int, int, int], ...], dict]:
    """Generate one declared source draw; no difficulty or quality filtering."""
    require_numpy_version()
    _check_graph(family, index)
    entropy = graph_seed_sequence(family, index)
    rng = np.random.Generator(np.random.PCG64DXSM(np.random.SeedSequence(entropy)))
    if family == 0:
        pairs = tuple((i, j) for i in range(N) for j in range(i + 1, N))
        distance = np.array([(N / np.pi) * np.sin(np.pi * abs(i-j) / N)
                             for i, j in pairs], dtype=np.float64)
        c_n = ring_normalization()
        z = rng.standard_normal(len(pairs))
        weights = _round_weights(SOURCE_MULTIPLIER * c_n * z / distance**2.5)
    else:
        pairs = torus_edges()
        c_n = None
        z = rng.standard_normal(len(pairs))
        weights = _round_weights(SOURCE_MULTIPLIER * z)
    raw_edges = tuple((i, j, int(w)) for (i, j), w in zip(pairs, weights))
    metadata = {
        "graph": graph_name(family, index), "family": int(family),
        "family_name": FAMILIES[family], "index": int(index), "n": N,
        "graph_seed_sequence": entropy, "generator": "PCG64DXSM",
        "numpy_version": NUMPY_VERSION, "rounding": "numpy.rint ties-to-even",
        "source_multiplier": SOURCE_MULTIPLIER, "c_N": c_n,
        **_edge_statistics(raw_edges),
    }
    return raw_edges, metadata


def _edge_statistics(edges: Iterable[tuple[int, int, int]]) -> dict:
    weights = np.asarray([w for _, _, w in edges], dtype=np.int64)
    zero_count = int(np.count_nonzero(weights == 0))
    return {
        "raw_edge_count": int(len(weights)), "zero_count": zero_count,
        "effective_nonzero_edges": int(len(weights)) - zero_count,
        "max_abs_weight": int(np.max(np.abs(weights))) if len(weights) else 0,
        "sum_weights": int(sum(int(w) for w in weights)),
        "sum_abs_weights": int(sum(abs(int(w)) for w in weights)),
    }


def rudy_bytes(edges: Iterable[tuple[int, int, int]], n: int = N) -> bytes:
    edges = tuple(edges)
    pairs = [(i, j) for i, j, _ in edges]
    if pairs != sorted(set(pairs)):
        raise ValueError("Rudy source pairs must be unique and lexicographically sorted")
    if any(not (0 <= i < j < n) or isinstance(w, bool) or not isinstance(w, (int, np.integer))
           for i, j, w in edges):
        raise ValueError("invalid canonical integer source edge")
    lines = [f"{n} {len(edges)}"]
    lines.extend(f"{i+1} {j+1} {int(w)}" for i, j, w in edges)
    return ("\n".join(lines) + "\n").encode("ascii")


def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n"


def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_statistics(path: str | Path, *, family: int | None = None,
                      label: str | None = None) -> dict:
    """Source metadata only, with raw zeros distinguished from loader support."""
    from experiments.biqmac_maxcut import load_rudy
    path = Path(path)
    graph = load_rudy(path)
    lines = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    raw_decimals = [Decimal(line.split()[2]) for line in lines[1:]]
    if graph.loops_ignored or graph.parallel_entries:
        raise ValueError("source-scale comparison requires unique loop-free input")
    if any(w != w.to_integral_value() for w in raw_decimals):
        raise ValueError("source-scale comparison requires integer weights")
    raw_weights = [int(w) for w in raw_decimals]
    if graph.zero_sum_edges != sum(w == 0 for w in raw_weights):
        raise ValueError("raw/effective zero count disagreement")
    result = {
        "graph": label or path.name, "n": graph.n, "sha256": graph.sha256,
        "raw_edge_count": graph.raw_edge_count,
        "zero_count": sum(w == 0 for w in raw_weights),
        "effective_nonzero_edges": len(graph.edges),
        "max_abs_weight": max((abs(w) for w in raw_weights), default=0),
        "sum_weights": sum(raw_weights), "sum_abs_weights": sum(abs(w) for w in raw_weights),
    }
    if family is not None:
        _integer_in(family, 0, 2, "family")
        result.update(family=int(family), family_name=FAMILIES[family])
    return result


def distribution_statistics(values: Iterable[float]) -> dict:
    values = np.asarray(tuple(values), dtype=np.float64)
    if values.ndim != 1 or not len(values) or not np.all(np.isfinite(values)):
        raise ValueError("expected nonempty finite scalar observations")
    q = np.quantile(values, [0, .25, .5, .75, 1], method="linear")
    return {"n": int(len(values)), "minimum": float(q[0]), "q25": float(q[1]),
            "median": float(q[2]), "q75": float(q[3]), "maximum": float(q[4]),
            "mean": float(values.mean()),
            "sd": float(values.std(ddof=1)) if len(values) > 1 else 0.0}


def protocol_parameters() -> dict:
    """Declared values only; no unobserved official source hashes are invented."""
    return {
        "schema": "fyp-ideal-sources-v1", "n": N, "families": ["ring", "torus"],
        "graphs_per_family": GRAPHS_PER_FAMILY, "candidates": list(CANDIDATES),
        "main_seeds_per_graph": MAIN_SEEDS, "reference_seeds_per_graph": REFERENCE_SEEDS,
        "anchor_seeds_per_graph": ANCHOR_SEEDS, "updates": UPDATES,
        "numpy_version": NUMPY_VERSION, "generator": "PCG64DXSM",
        "graph_seed_sequence": "[20261120,910,family,index]",
        "main_seed": "2000000000000+100000*family+1000*index+replicate",
        "reference_seed": "1000000000000+100000*family+1000*index+replicate",
        "anchor_seed": "3000000000000+10000*anchor_index+replicate",
        "core_bootstrap_seed_sequence": "[20261120,940,family]",
        "descriptive_bootstrap_seed_sequence": "[20261120,940,family,1]",
        "bootstrap_resamples": 500_000,
        "bootstrap_quantile_convention": "numpy.quantile method='linear'",
        "core_contrasts_total": 18, "alpha_core": 0.04,
        "core_one_sided_tail": 0.04 / (2 * 18),
        "offset_seed_sequence_reserved_not_executed": "[20261120,930,family,index]",
        "source_root": str(DEFAULT_OUT),
        "source_layout": "{ring|torus}/{index:03d}.rudy",
        "source_manifest": "source_manifest.json",
        "results_root": "results/fyp_ideal_20261120",
        "generated_results_layout": "generated/{ring|torus}/{index:03d}/",
        "source_multiplier": SOURCE_MULTIPLIER, "rounding": "numpy.rint ties-to-even",
        "ring_distance": "(N/pi)*sin(pi*abs(i-j)/N)",
        "ring_c_N": "sum_{j!=i}(r_ij^-5)^(-1/2)",
        "ring_c_N_at_100": ring_normalization(),
        "ring_weights": "rint(100000*c_N*z_ij/r_ij^2.5)",
        "torus_weights": "rint(100000*z_e)",
        "torus_vertex_index": "10*x+y",
        "torus_neighbors": "right/down periodic; canonical unique i<j sorted order",
        "normal_draws": "independent numpy standard_normal in canonical edge order",
        "zero_entries": "retained in raw Rudy sources, omitted by existing loader",
        "ising_mapping": "J_ij=J_ji=-w_ij; zero diagonal; h=0",
        "anchors": list(ANCHORS),
        "source_quality_filter": "NONE; retain every fixed draw",
    }


def generate_all(out: str | Path = DEFAULT_OUT) -> dict:
    """Write all 144 source draws and hashes, or verify an existing complete set."""
    require_numpy_version()
    out = Path(out)
    if (out / "source_manifest.json").exists():
        return verify_sources(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError("nonempty source directory without a complete manifest")
    out.mkdir(parents=True, exist_ok=True)
    graphs = []
    for family in FAMILIES:
        (out / FAMILIES[family]).mkdir()
        for index in range(GRAPHS_PER_FAMILY):
            edges, meta = generate_graph(family, index)
            payload = rudy_bytes(edges)
            name = graph_relative_path(family, index)
            with (out / name).open("xb") as f:
                f.write(payload)
            meta.update(file=name, sha256=hashlib.sha256(payload).hexdigest(), bytes=len(payload))
            graphs.append(meta)
    summary = {FAMILIES[f]: {metric: distribution_statistics(
        g[metric] for g in graphs if g["family"] == f)
        for metric in ("max_abs_weight", "zero_count")} for f in FAMILIES}
    columns = ("graph", "family", "family_name", "index", "n", "raw_edge_count",
               "zero_count", "effective_nonzero_edges", "max_abs_weight",
               "sum_weights", "sum_abs_weights", "sha256", "file", "bytes")
    with (out / "source_statistics.csv").open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(graphs)
    manifest = {
        "status": "ALL_144_SOURCE_GRAPHS_SAVED_BEFORE_SOLVER_EXECUTION",
        "parameters": protocol_parameters(), "python_version": platform.python_version(),
        "graphs": graphs, "source_scale_distributions": summary,
        "source_statistics_csv_sha256": file_sha256(out / "source_statistics.csv"),
        "source_quality_observations": 0,
    }
    with (out / "source_manifest.json").open("x", encoding="utf-8") as f:
        f.write(canonical_json(manifest))
    return verify_sources(out)


def verify_sources(out: str | Path = DEFAULT_OUT) -> dict:
    require_numpy_version()
    out = Path(out)
    manifest = json.loads((out / "source_manifest.json").read_text())
    if manifest["parameters"] != protocol_parameters():
        raise ValueError("source parameters differ from the locked implementation")
    rows = manifest["graphs"]
    expected = {(family, index) for family in FAMILIES for index in range(GRAPHS_PER_FAMILY)}
    observed = {(g["family"], g["index"]) for g in rows}
    if len(rows) != 144 or observed != expected:
        raise ValueError("source manifest does not contain the fixed 144 unique graphs")
    if {p.relative_to(out).as_posix() for p in out.rglob("*.rudy")} != {g["file"] for g in rows}:
        raise ValueError("unexpected or missing generated source file")
    for g in rows:
        if g["file"] != graph_relative_path(g["family"], g["index"]):
            raise ValueError("source filename does not match family/index")
        path = out / g["file"]
        if file_sha256(path) != g["sha256"] or path.stat().st_size != g["bytes"]:
            raise ValueError(f"source content/hash changed: {path.name}")
        actual = source_statistics(path, family=g["family"], label=g["graph"])
        for key in ("n", "raw_edge_count", "zero_count", "effective_nonzero_edges",
                    "max_abs_weight", "sum_weights", "sum_abs_weights", "sha256"):
            if actual[key] != g[key]:
                raise ValueError(f"source metadata mismatch {path.name}: {key}")
    if file_sha256(out / "source_statistics.csv") != manifest["source_statistics_csv_sha256"]:
        raise ValueError("source statistics CSV hash changed")
    return manifest


def compare_viewed_sources(manifest: dict, official_dir: str | Path) -> dict:
    """Compare generated source spread to 5555/7777 only; never accesses 6666."""
    official_dir = Path(official_dir)
    rows = []
    for anchor in ANCHORS:
        name = anchor["name"]
        if name not in VIEWED_SOURCE_HASHES:
            continue
        record = source_statistics(official_dir / name, family=anchor["family"], label=name)
        if record["sha256"] != VIEWED_SOURCE_HASHES[name]:
            raise ValueError(f"viewed official source hash mismatch: {name}")
        rows.append(record)
    return {"scope": "source-only; no solver outcomes or instance selection",
            "generated_distributions": manifest["source_scale_distributions"],
            "viewed_official_sources": rows,
            "official_6666_files_opened": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--generate", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument("--viewed-official-dir", type=Path)
    args = parser.parse_args()
    result = generate_all(args.out) if args.generate else verify_sources(args.out)
    if args.viewed_official_dir:
        result = compare_viewed_sources(result, args.viewed_official_dir)
    else:
        result = {"status": result["status"], "graphs": len(result["graphs"]),
                  "source_scale_distributions": result["source_scale_distributions"]}
    print(canonical_json(result), end="")


if __name__ == "__main__":
    main()
