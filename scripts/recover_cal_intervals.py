#!/usr/bin/env python3
"""Recover existing CAL 95% confidence intervals from archived CSVs.

Read-only input. No simulations. No fabricated uncertainty.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

DEFAULT_PRIMARY = Path(
    "results/m2_offset_precision_primary_20261108/"
    "E2_offset_primary_summary.csv"
)
DEFAULT_EXT = Path(
    "results/m2_offset_8bit_extension_20261108/"
    "E2_offset_8bit_summary.csv"
)
DEFAULT_OUT = Path(
    "results/cal_95ci_source_recovery_20261109"
)

GRAPHS = ("t2g10_5555", "ising2.5-100_5555")
LEVELS = (0.8, 1.6)
CORE = ("ref64", "fp4", "fp5", "fp6", "int4", "int5", "int6")
EXTRA = ("fp8", "int8")


def records(path):
    if not path.is_file():
        raise FileNotFoundError(f"Missing archived file: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", type=Path, default=DEFAULT_PRIMARY)
    parser.add_argument("--extension", type=Path, default=DEFAULT_EXT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if args.out.exists():
        raise FileExistsError(
            f"Output exists; refusing overwrite: {args.out}"
        )

    specs = (
        (args.primary, CORE, 42),
        (args.extension, EXTRA, 8),
    )

    cells = {}
    sources = {}
    seen_ideal = set()

    for path, formats, expected_count in specs:
        rows = records(path)

        if len(rows) != expected_count:
            raise ValueError(
                f"{path}: expected {expected_count} rows, "
                f"got {len(rows)}"
            )

        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        sources[str(path)] = digest

        for row in rows:
            graph = row["graph"]
            d = float(row["offset_logit_halfspan"])
            fmt = row["configuration"]

            if path == args.primary and d == 0.0:
                key = (graph, fmt)
                if (
                    graph not in GRAPHS
                    or fmt not in CORE
                    or key in seen_ideal
                ):
                    raise ValueError(f"Invalid ideal row: {key}")
                seen_ideal.add(key)
                continue

            key = (graph, d, fmt)

            if (
                graph not in GRAPHS
                or d not in LEVELS
                or fmt not in formats
                or key in cells
            ):
                raise ValueError(f"Invalid/duplicate cell: {key}")

            mean = float(row["mean_absolute_gap_pct"])
            low = float(row["ci95_abs_gap_lo_pct"])
            high = float(row["ci95_abs_gap_hi_pct"])

            if not (0 <= low <= mean <= high):
                raise ValueError(f"Invalid CI: {key}")

            cells[key] = dict(
                graph=graph,
                offset_logit_halfspan=d,
                configuration=fmt,
                mean_gap_pct=mean,
                ci95_gap_lo_pct=low,
                ci95_gap_hi_pct=high,
                source_file=str(path),
                source_sha256=digest,
            )

    expected = {
        (g, d, fmt)
        for g in GRAPHS
        for d in LEVELS
        for fmt in CORE + EXTRA
    }

    if len(seen_ideal) != 14:
        raise ValueError("Missing ideal rows in primary source")

    if set(cells) != expected or len(cells) != 36:
        raise ValueError(
            f"Incomplete CAL intervals: {expected-set(cells)}"
        )

    args.out.mkdir(parents=True)

    output = args.out / "cal_all_36_source_verified_intervals.csv"

    with output.open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(next(iter(cells.values())))
        )
        writer.writeheader()

        for key in sorted(cells):
            writer.writerow(cells[key])

    manifest = dict(
        status="36_CAL_INTERVALS_RECOVERED",
        verified_intervals=len(cells),
        source_sha256=sources,
        new_solver_runs=0,
        output_sha256=hashlib.sha256(
            output.read_bytes()
        ).hexdigest(),
        uncertainty_scope=(
            "24 solver seeds per fixed graph and "
            "synthetic device population"
        ),
    )

    (args.out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("PASS: 36/36 CAL confidence intervals recovered")
    print("CSV:", output)
    print("Manifest:", args.out / "manifest.json")


if __name__ == "__main__":
    main()
