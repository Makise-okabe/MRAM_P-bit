import csv
import json
import hashlib
import re
import os
import subprocess
from pathlib import Path

OUT = Path(os.environ.get("HW02_OUT", "results/hw02a_20261129"))
HW = Path("results/hw01_20261129_archive")
IDEAL = Path("results/fyp_ideal_20261120/analysis")
POLICY = Path("results/fyp_policy_device_20261121/analysis")

FORMATS = ("fp5", "int5", "int6")
FAMILIES = ("ring", "torus")
MARGINS = (0.25, 0.5, 1.0)
RATIOS = (0, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1, 2)

N = 100
UPDATES = 50000
DENSE_EDGES = N * (N - 1) // 2
TORUS_EDGES = 200

LAYOUTS = {
    "dense_triangular": "dense_triangular_bits",
    "dense_duplicated": "dense_row_duplicated_bits",
    "torus_csr": "torus_csr_bits",
    "torus_bitmap": "torus_bitmap_bits",
}

sources = set()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_text(path):
    sources.add(path)
    return path.read_text()


def read_json(path):
    return json.loads(read_text(path))


def read_csv(path):
    return list(csv.DictReader(read_text(path).splitlines()))


def write_csv(name, rows):
    require(bool(rows), f"Empty output: {name}")
    with (OUT / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# =================================================
# 1. VERIFY ARCHIVED HARDWARE EVIDENCE
# =================================================

print("===== INPUT VERIFICATION =====")

subprocess.run(
    ["sha256sum", "-c", "--quiet", "SHA256SUMS"],
    cwd=HW,
    check=True,
)

manifest = read_json(HW / "manifest.json")

require(manifest["N"] == N, "Unexpected N")
require(manifest["terms_per_row"] == 99, "Unexpected row length")
require(manifest["clock_ns"] == 10, "Unexpected clock constraint")
require(
    sha(HW / "hw01_matched.v")
    == manifest["generated_rtl_sha256"],
    "RTL hash mismatch",
)

verification = HW / "rtl_verification/verification.csv"

checks = {
    row[0]: (int(row[1]), row[2])
    for row in csv.reader(read_text(verification).splitlines())
    if row
}

expected = {
    "fp5": (166, "PASS"),
    "int5": (164, "PASS"),
    "int6": (228, "PASS"),
}

require(checks == expected, "RTL verification mismatch")

memory = {
    r["format"]: {
        k: int(v) for k, v in r.items()
        if k != "format"
    }
    for r in read_csv(HW / "memory_cost.csv")
}

area = {}
hardware_rows = []

for fmt in FORMATS:
    rpt = read_text(HW / fmt / "area.rpt")

    match = re.search(
        rf"^\s*hw01_{fmt}\s+(\d+)\s+([\d.]+)"
        r"\s+([\d.]+)\s+([\d.]+)",
        rpt,
        re.M,
    )

    require(match is not None, f"Area parse failed: {fmt}")
    require("NangateOpenCellLibrary" in rpt, "Library mismatch")

    cells = int(match.group(1))
    area[fmt] = float(match.group(2))

    timing = read_text(HW / fmt / "timing.rpt")

    slack = re.search(
        r"Path 1:\s+MET\s+\(([\d.]+)\s+ps\)",
        timing,
    )

    delay = re.search(
        r"Data Path:-\s+([\d.]+)",
        timing,
    )

    require(slack is not None, f"Setup check failed: {fmt}")
    require(delay is not None, f"Delay unavailable: {fmt}")

    status = read_text(HW / fmt / "synthesis_status.txt")

    require(
        f"HW01_SYNTH_PASS=hw01_{fmt}" in status,
        f"Synthesis status mismatch: {fmt}",
    )

    hardware_rows.append({
        "format": fmt,
        "logic_area_um2": area[fmt],
        "cells": cells,
        "data_path_ns": float(delay.group(1)) / 1000,
        "setup_slack_ns": float(slack.group(1)) / 1000,
        "rtl_cases_passed": checks[fmt][0],
        **memory[fmt],
    })

write_csv("hardware_summary.csv", hardware_rows)

print("HW01 ARCHIVE PASS")
print("558/558 RTL cases recorded")
print("3/3 reported setup checks MET")


# =================================================
# 2. MEMORY-LOGIC COST SENSITIVITY
# =================================================

print("===== MEMORY-LOGIC COST MODEL =====")

cost_rows = []

for layout, key in LAYOUTS.items():
    for bit_area in RATIOS:
        for fmt in FORMATS:
            bits = memory[fmt][key]

            cost_rows.append({
                "layout": layout,
                "format": fmt,
                "assumed_area_per_bit_um2": bit_area,
                "logic_area_um2": area[fmt],
                "storage_bits": bits,
                "memory_area_proxy_um2": bits * bit_area,
                "logic_plus_memory_proxy_um2":
                    area[fmt] + bits * bit_area,
                "physical_macro": "NOT_IMPLEMENTED",
            })

write_csv("area_sensitivity.csv", cost_rows)

break_even = []

for layout, key in LAYOUTS.items():
    saved = memory["int6"][key] - memory["fp5"][key]
    overhead = area["fp5"] - area["int6"]

    require(saved > 0, "Invalid storage comparison")

    break_even.append({
        "layout": layout,
        "fp5_logic_overhead_um2": overhead,
        "fp5_bits_saved_vs_int6": saved,
        "fp5_storage_saving_pct":
            100 * saved / memory["int6"][key],
        "break_even_area_per_bit_um2": overhead / saved,
    })

write_csv("break_even.csv", break_even)


# =================================================
# 3. LOGICAL MEMORY ACCESS ACCOUNTING
# =================================================

access_rows = []

for fmt in FORMATS:
    b = memory[fmt]["coefficient_bits"]

    # Dense streaming of all 99 coefficients per update.
    access_rows.append({
        "format": fmt,
        "access_model": "dense_serial",
        "updates": UPDATES,
        "terms_per_update": 99,
        "coefficient_payload_bits": UPDATES * 99 * b,
        "neighbor_index_payload_bits": 0,
        "row_pointer_payload_bits": 0,
        "spin_operand_bits": UPDATES * 99,
        "assumption": "Logical payload; address/control excluded",
    })

    # Structural degree-four torus sensitivity.
    # Same datapath, hypothetical skipped-zero scheduling.
    access_rows.append({
        "format": fmt,
        "access_model": "torus_csr_4_neighbors",
        "updates": UPDATES,
        "terms_per_update": 4,
        "coefficient_payload_bits": UPDATES * 4 * b,
        "neighbor_index_payload_bits": UPDATES * 4 * 7,
        "row_pointer_payload_bits": UPDATES * 2 * 9,
        "spin_operand_bits": UPDATES * 4,
        "assumption": "Two row-pointer reads; sparse scheduler unsynthesized",
    })

write_csv("memory_access.csv", access_rows)


# =================================================
# 4. OUTPUT POLICY COST
# =================================================

policy_cost = []

for topology, edges in (
    ("dense_capacity", DENSE_EDGES),
    ("torus_degree4", TORUS_EDGES),
):
    for weight_bits in (32, 64):
        for k in (1, 16):
            policy_cost.append({
                "topology": topology,
                "original_weight_bits_assumed": weight_bits,
                "candidate_capacity": k,
                "candidate_state_payload_bits": k * N,
                "host_original_weight_payload_bits":
                    edges * weight_bits,
                "candidate_transfer_payload_upper_bits":
                    k * N,
                "host_edge_evaluations_upper_bound":
                    k * edges,
                "additional_buffer_payload_vs_k1_bits":
                    (k - 1) * N,
                "scope":
                    "One output event; metadata, scores and control excluded",
            })

write_csv("output_policy_cost.csv", policy_cost)


# =================================================
# 5. IMPORT REGISTERED QUALITY EVIDENCE
# =================================================

print("===== IMPORTING EXISTING QUALITY RESULTS =====")

quality = {}


def record(policy, family, fmt, mean, low, high, decisions):
    key = (policy, family, fmt)

    require(key not in quality, f"Duplicate contrast: {key}")

    quality[key] = {
        "mean": float(mean),
        "low": float(low),
        "high": float(high),
        "decisions": decisions,
    }


# Original output policy, ideal response.
for r in read_csv(IDEAL / "core_contrasts.csv"):
    for fmt in FORMATS:
        if r["contrast"] == fmt + "-ref64":
            require(r["graphs"] == "72", "Graph count mismatch")

            record(
                "ideal_original",
                r["family"],
                fmt,
                r["mean"],
                r["low"],
                r["high"],
                {
                    "0.25": json.loads(
                        r["labels_0p25"]
                    )["qualification"],
                    "0.5": r["qualification"],
                    "1.0": json.loads(
                        r["labels_1p0"]
                    )["qualification"],
                },
            )


# Ideal top-16 and assumed persistent offset.
for filename, policy in (
    ("stage_a_certification.json", "ideal_top16"),
    ("stage_b_device_contrasts.json", "offset_original"),
):
    report = read_json(POLICY / filename)

    for r in report["contrasts"]:
        for fmt in FORMATS:
            if r["contrast"] == fmt + "-ref64":
                require(r["n"] == 72, "Graph count mismatch")

                record(
                    policy,
                    r["family"],
                    fmt,
                    r["mean"],
                    r["low"],
                    r["high"],
                    {
                        str(m): r["decisions"][str(m)]
                        ["qualification"]
                        for m in MARGINS
                    },
                )

require(len(quality) == 16, "Unexpected contrast count")

quality_rows = []

for policy in (
    "ideal_original",
    "ideal_top16",
    "offset_original",
):
    for family in FAMILIES:
        for fmt in FORMATS:
            q = quality.get((policy, family, fmt))

            for margin in MARGINS:
                quality_rows.append({
                    "policy": policy,
                    "family": family,
                    "format": fmt,
                    "margin_pp": margin,
                    "mean_extra_shortfall_pp":
                        q["mean"] if q else "",
                    "lower_bound_pp":
                        q["low"] if q else "",
                    "upper_bound_pp":
                        q["high"] if q else "",
                    "qualification":
                        q["decisions"][str(margin)]
                        if q else "NOT_REGISTERED",
                    "device_model":
                        "assumed_offset_not_measured"
                        if policy == "offset_original"
                        else "ideal",
                })

write_csv("quality_evidence.csv", quality_rows)


# =================================================
# 6. CONDITIONAL MINIMUM-COST CHOICE
# =================================================

print("===== QUALITY-CONSTRAINED COST SELECTION =====")

selection = []

for policy in (
    "ideal_original",
    "ideal_top16",
    "offset_original",
):
    for family in FAMILIES:

        layouts = ["dense_triangular", "dense_duplicated"]

        if family == "torus":
            layouts += ["torus_csr", "torus_bitmap"]

        for margin in MARGINS:
            certified = [
                fmt for fmt in FORMATS
                if (policy, family, fmt) in quality
                and quality[(policy, family, fmt)]
                ["decisions"][str(margin)] == "PASS"
            ]

            for layout in layouts:
                key = LAYOUTS[layout]

                for bit_area in RATIOS:
                    costs = {
                        fmt: area[fmt] +
                        bit_area * memory[fmt][key]
                        for fmt in certified
                    }

                    winner = (
                        min(costs, key=costs.get)
                        if costs else None
                    )

                    ties = [
                        f for f in costs
                        if abs(costs[f] - costs[winner]) < 1e-9
                    ] if winner else []

                    selection.append({
                        "policy": policy,
                        "family": family,
                        "margin_pp": margin,
                        "layout": layout,
                        "assumed_area_per_bit_um2": bit_area,
                        "certified_candidates":
                            ";".join(certified),
                        "minimum_proxy_cost_candidate":
                            ";".join(ties)
                            if ties else "UNRESOLVED",
                        "minimum_proxy_area_um2":
                            costs[winner] if winner else "",
                        "absolute_quality_gate":
                            "NOT_YET_APPLIED",
                        "cross_policy_comparison":
                            "NOT_AUTHORIZED_BY_THIS_PROXY",
                        "scope":
                            "Conditional within HW01 candidates only",
                    })

write_csv("conditional_selection.csv", selection)


# =================================================
# 7. FIGURES (OPTIONAL MATPLOTLIB)
# =================================================

figure_status = "NOT_GENERATED"

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for family in FAMILIES:
        fig, ax = plt.subplots(figsize=(7, 4.5))

        for fmt in FORMATS:
            y = [
                area[fmt]
                + x * memory[fmt]["dense_triangular_bits"]
                for x in RATIOS
            ]

            ax.plot(RATIOS, y, marker="o", label=fmt.upper())

        ax.set_xlabel("Assumed memory area per bit (um2)")
        ax.set_ylabel("Logic + memory area proxy (um2)")
        ax.set_title("Dense coupling storage sensitivity")
        ax.legend()
        ax.grid(alpha=0.2)

        fig.tight_layout()
        fig.savefig(OUT / f"{family}_cost_sensitivity.png", dpi=180)
        plt.close(fig)

        fig, axes = plt.subplots(
            1, 3, figsize=(12, 4), sharey=True
        )

        for ax, policy in zip(
            axes,
            ("ideal_original", "ideal_top16", "offset_original"),
        ):
            for fmt in FORMATS:
                q = quality.get((policy, family, fmt))

                if q is None:
                    continue

                # Explicit illustrative memory-area assumption.
                cost = area[fmt] + (
                    0.5 * memory[fmt]["dense_triangular_bits"]
                )

                ax.errorbar(
                    cost,
                    q["mean"],
                    yerr=[
                        [q["mean"] - q["low"]],
                        [q["high"] - q["mean"]],
                    ],
                    fmt="o",
                    capsize=3,
                )

                ax.annotate(
                    fmt.upper(), (cost, q["mean"]),
                    xytext=(4, 4), textcoords="offset points",
                )

            ax.axhline(0.5, linestyle="--", color="gray")
            ax.set_title(policy.replace("_", " "))
            ax.set_xlabel("Area proxy (um2)")
            ax.grid(alpha=0.2)

        axes[0].set_ylabel("Extra shortfall vs FP64 (pp)")

        fig.suptitle(
            f"{family}: conditional quality-cost comparison"
            "\nAssumed memory area = 0.5 um2/bit;"
            " host costs excluded"
        )

        fig.tight_layout()
        fig.savefig(OUT / f"{family}_quality_cost.png", dpi=180)
        plt.close(fig)

    figure_status = "PASS"

except ImportError:
    print("Matplotlib unavailable; CSV analysis retained")


# =================================================
# 8. RESEARCH SUMMARY AND PROVENANCE
# =================================================

summary = [
    "# HW02-A: Conditional architectural cost integration",
    "",
    "## Status",
    "",
    "Offline integration of archived HW01 logic results and",
    "existing registered software quality contrasts.",
    "No new solver trajectories or EDA simulations.",
    "",
    "## Hardware",
    "",
    "| Format | Logic area (um2) | Dense bits | RTL cases |",
    "|---|---:|---:|---:|",
]

for r in hardware_rows:
    summary.append(
        f"| {r['format']} | {r['logic_area_um2']} | "
        f"{r['dense_triangular_bits']} | "
        f"{r['rtl_cases_passed']} |"
    )

summary += [
    "",
    "## Conditional choices",
    "",
    "Illustrative assumption: 0.5 um2 per stored bit,",
    "dense triangular storage, +0.5 pp relative tolerance.",
    "",
    "| Policy | Family | Certified candidates | Lowest proxy cost |",
    "|---|---|---|---|",
]

for r in selection:
    if (
        r["layout"] == "dense_triangular"
        and r["margin_pp"] == 0.5
        and r["assumed_area_per_bit_um2"] == 0.5
    ):
        summary.append(
            f"| {r['policy']} | {r['family']} | "
            f"{r['certified_candidates']} | "
            f"{r['minimum_proxy_cost_candidate']} |"
        )

summary += [
    "",
    "## Interpretation and limits",
    "",
    "- Quality is relative to the matched FP64 policy and device regime.",
    "- Generated graph references are best-observed feasible cuts,",
    "  not proven global optima.",
    "- Relative tolerance does not establish absolute solution quality.",
    "- The assumed offset distribution is not physically measured.",
    "- Unregistered contrasts are not treated as failures or passes.",
    "- Area per bit is a sensitivity parameter, not macro characterization.",
    "- No memory peripheral, addressing, routing, gain generation,",
    "  device offset circuit, or complete controller area is included.",
    "- Sparse access scheduling is hypothetical and not synthesized.",
    "- Top-16 payload, host storage and edge-evaluation costs are",
    "  reported separately, not converted into unsupported area numbers.",
    "- Cross-policy total-cost optimality is not established.",
    "- Absolute quality gate remains open.",
    "- Results apply only to the three HW01 hardware candidates.",
    "- No final device-aware representation is certified.",
    "",
    f"Figure generation: {figure_status}",
]

(OUT / "RESULTS.md").write_text("\n".join(summary) + "\n")

provenance = {
    "experiment": "HW02-A",
    "status": "OFFLINE_PROXY_INTEGRATION_COMPLETE",
    "source_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip(),
    "source_hashes": {
        str(p): sha(p) for p in sorted(sources)
    },
    "analysis_script_sha256": sha(Path(__file__)),
    "N": N,
    "updates": UPDATES,
    "margins_pp": MARGINS,
    "area_per_bit_assumptions": RATIOS,
    "quality_contrasts": len(quality),
    "selection_rows": len(selection),
    "rtl_simulations": 0,
    "spectre_simulations": 0,
    "genus_runs": 0,
    "maxcut_solver_runs": 0,
    "physical_memory_macro": False,
    "absolute_quality_gate_applied": False,
    "figure_status": figure_status,
}

(OUT / "manifest.json").write_text(
    json.dumps(provenance, indent=2) + "\n"
)

with (OUT / "SHA256SUMS").open("w") as f:
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name != "SHA256SUMS":
            f.write(f"{sha(p)}  {p.name}\n")

print()
print((OUT / "RESULTS.md").read_text())
print(f"QUALITY CONTRASTS: {len(quality)}")
print(f"SELECTION ROWS: {len(selection)}")
print("HW02-A ANALYSIS PASS")

