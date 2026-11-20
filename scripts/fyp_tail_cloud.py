#!/usr/bin/env python3
"""Operational cloud recovery and reporting; scientific code remains frozen."""
from pathlib import Path
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np

FREEZE_SHA = "54c06ff593c8acded95f7e4ce6f04a347c6164f7"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PREFLIGHT = ROOT/"results/fyp_tail_preflight_20261121"
RESULT = ROOT/"results/fyp_tail_probe_20261121"

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write_json(p, obj):
    Path(p).write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+"\n")

def preflight():
    from experiments.biqmac_maxcut import load_rudy
    from experiments.fyp_ideal_solver import representation, solve_logged
    from experiments.fyp_tail_probe import solve_buffered, legacy_fields, UPDATES
    from experiments.m1_biqmac_ideal_pilot import beta_from_original_graph
    if RESULT.exists():
        raise RuntimeError("Existing scientific result directory; refuse automatic rerun.")
    if np.__version__ != "2.3.5":
        raise RuntimeError("Frozen NumPy required.")
    path = Path("docs/FYP_TAIL_FREEZE_20261121.json")
    committed = subprocess.check_output(["git", "show", f"{FREEZE_SHA}:{path.as_posix()}"])
    subprocess.run(["git", "merge-base", "--is-ancestor", FREEZE_SHA, "HEAD"], check=True)
    if committed != path.read_bytes():
        raise RuntimeError("Published freeze differs from checkout.")
    frozen = json.loads(committed)
    for name, expected in frozen["file_sha256"].items():
        if sha(ROOT/name) != expected:
            raise RuntimeError("Frozen file mismatch: "+name)
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests",
                    "-p", "test_fyp_tail_probe.py", "-v"], check=True)
    plan = json.loads(Path("results/fyp_ideal_preflight_20261120/archived_parity_plan.json").read_text())
    controls = [c for c in plan["controls"] if c["representation"] in ("ref64", "fp6", "int6")]
    cache = {}
    checks = []
    for c in controls:
        if sha(c["archive"]) != c["archive_sha256"]:
            raise RuntimeError("Historical source archive hash mismatch.")
        key = (c["graph"], c["representation"])
        if key not in cache:
            source = Path("data/biqmac/raw/ising")/c["graph"]
            if sha(source) != c["graph_sha256"]:
                raise RuntimeError("Historical graph hash mismatch.")
            g = load_rudy(source)
            cache[key] = (g, representation(g, c["representation"]), beta_from_original_graph(g))
        g, rep, beta = cache[key]
        new = solve_buffered(g, rep, beta, UPDATES, c["seed"])
        old = solve_logged(g, rep, beta, UPDATES, c["seed"])
        if legacy_fields(new) != old:
            raise RuntimeError("Cross-environment legacy parity failed.")
        for field, expected in c["expected"].items():
            match = new[field] == str(expected) if field == "returned_state_hex" else new[field] == float(expected)
            if not match:
                raise RuntimeError("Historical archived parity failed: "+str(key)+"/"+field)
        checks.append({"graph": c["graph"], "representation": c["representation"],
                       "seed": c["seed"], "result": "EXACT"})
    if len(checks) != 21:
        raise RuntimeError("Unexpected control count.")
    evidence = {"status": "PASS", "controls": checks, "control_count": len(checks),
                "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                            "platform": platform.platform()},
                "freeze_commit": FREEZE_SHA, "freeze_sha256": sha(path),
                "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
                "fresh_solver_outcomes_inspected": False}
    write_json(PREFLIGHT/"cloud_preflight.json", evidence)
    write_json(PREFLIGHT/"freeze_receipt.json",
               {"freeze_commit": FREEZE_SHA, "freeze_sha256": sha(path),
                "remote_bytes_verified": True,
                "verification_method": "Native git-show at exact previously published freeze; all file SHA256 values checked before fresh execution"})
    print(json.dumps({"status": "PASS", "archived_controls": 21, "frozen_files": len(frozen["file_sha256"]),
                      "python": platform.python_version(), "numpy": np.__version__}), flush=True)

def fmt(x):
    return "unresolved" if x is None else f"{x:+.5f}"

def finalize():
    verification = json.loads((RESULT/"verification.json").read_text())
    if verification["status"] != "PASS" or verification["raw_records"] != 18432:
        raise RuntimeError("Complete integrity gate required.")
    analysis = json.loads((RESULT/"analysis/analysis_summary.json").read_text())
    family = {(r["family"], r["representation"], r["metric"]): r for r in analysis["family"]}
    def cell(f, a, m):
        r = family[f, a, m]
        return f'{fmt(r["mean"])} [{fmt(r["low"])}, {fmt(r["high"])}]'
    lines = [
        "# Weak-tail mechanism checkpoint — 21 November 2026",
        "",
        "Scientific freeze: "+FREEZE_SHA+". All 18,432 prescribed unique trajectories completed on GitHub Actions.",
        "",
        "## Execution recovery",
        "",
        "The original Codex workspace execution became inaccessible after at least 19 graph bundles (7,296 trajectories) had been observed complete. The environment then reported an executor startup protocol failure. Its final completion count and remaining outputs could not be recovered. No fresh quality outcomes had been inspected before that failure.",
        "",
        "This cloud execution re-executed exactly the same 48 committed graph files, six arms, 64 paired seeds and frozen analysis. The inaccessible local outputs were not pooled or treated as extra observations. There are 18,432 unique scientific keys in the analysed dataset. Actual total computational work includes an unknown amount of duplicated local computation; no claim of only 18,432 total physical solver invocations is made.",
        "",
        "The cloud run first passed all nine synthetic test methods and 21 full archived replay controls, with the frozen NumPy version. Native git-show and every frozen file SHA256 were checked before execution. The operational recovery changed no scientific code, graph, seed, threshold or endpoint.",
        "",
        "## Registered ring contrasts",
        "",
        "Each contrast uses one-sided alpha 0.0125, 500,000 studentized graph-vector bootstrap resamples and 24 independent graphs. The lower bound below is the confirmatory 98.75% one-sided lower bound. The upper bound is displayed for context; together the displayed bounds form a nominal 97.5% two-sided interval.",
        "",
        "| Contrast | Meaning | Mean, pp | Lower bound | Upper for context | Decision |",
        "|---|---|---:|---:|---:|---|",
    ]
    for r in analysis["confirmatory"]:
        meaning = "Remove the accurate FP6 weak tail" if r["contrast"] == "C1" else "Restore the accurate tail to INT6"
        lines.append(f'| {r["contrast"]} | {meaning} | {fmt(r["mean"])} | {fmt(r["low"])} | {fmt(r["high"])} | {r["decision"]} |')
    lines += [
        "",
        "SUPPORTED requires the lower bound to exceed zero. NOT_ESTABLISHED does not establish zero effect, prove a probability-error explanation, or justify independent device and precision budgets. The intervention concerns these specific weak-tail values, not edge count in isolation.",
        "",
        "## Live-trajectory search and selection",
        "",
        "All following intervals are ordinary descriptive 95% graph-resampled intervals. Each graph mean averages its 64 paired seeds. The reference denominator is the frozen best observed original cut from FP64/FP6/INT6 x64 on that graph, not a known optimum. Probe arms may outperform this fixed reference.",
        "",
        "Extra loss = access A + total selection Rz. Rz = represented-objective loss (V-M) + earliest-tie loss (M-R). FP64 selection is zero by construction. Constant or undefined studentization is shown as unresolved; its point value is still reported.",
    ]
    arms = ("ref64", "fp6", "fp6_mask", "int6", "int6_tail", "int6_keep")
    for f in ("ring", "torus"):
        lines += ["", "### "+f.capitalize(), "",
                  "| Arm | Extra, pp [95%] | Access A, pp [95%] | Selection Rz, pp [95%] | V-M, pp [95%] | M-R, pp [95%] |",
                  "|---|---|---|---|---|---|"]
        for a in arms:
            lines.append("| "+a+" | "+" | ".join(cell(f, a, m) for m in
                         ("extra_pp", "A_pp", "Rz_pp", "selection_pp", "tie_pp"))+" |")
    lines += ["", "## Descriptive factorial interaction", "",
              "Interaction is (FP6_mask-FP6)-(INT6-INT6_tail): the difference between tail-removal effects with FP6 and INT6 strong-coupling values.",
              "", "| Family | Metric | Mean, pp | Descriptive 95% interval |", "|---|---|---:|---|"]
    for r in analysis["interaction"]:
        lines.append(f'| {r["family"]} | {r["metric"]} | {fmt(r["mean"])} | [{fmt(r["low"])}, {fmt(r["high"])}] |')
    lines += ["", "## Shared-bank ranking and passive top-16 recovery", "",
              "Each graph bank pools the top-16 states from all six arms and all 64 seeds, deduplicating raw spin vectors. Every encoding ranks this same bank. Smallest state integer resolves bank ties independently of original cut. These are conditional bank comparisons, not proof about every possible state.",
              "",
              "The live buffer retains states by represented energy and earliest first visit only. Original quality never selects a buffer member. Best-of-16 rescoring requires original J accessible on the host and additional state transfer and scoring. The oracle M need not fit in the buffer. Global inversions remain distinct raw spin vectors.",
              ""]
    for f in ("ring", "torus"):
        lines += ["", "### "+f.capitalize()+" output measurements", "",
                  "| Arm | Bank selection loss, pp [95%] | Bank V-M, pp [95%] | Bank M-R, pp [95%] | Top16 gain over actual return, pp [95%] | Residual extra loss after rescoring, pp [95%] | Mean tied minimum states [95%] |",
                  "|---|---|---|---|---|---|---|"]
        for a in arms:
            lines.append("| "+a+" | "+" | ".join(cell(f, a, m) for m in
                         ("bank_Rz_pp", "bank_selection_pp", "bank_tie_pp", "buffer_gain_pp",
                          "buffer_extra_pp", "minimum_distinct_states"))+" |")
    lines += [
        "",
        "## Interpretation limits and checkpoint",
        "",
        "FP6_mask and INT6_tail are mechanism probes; no implementable low-bit format or hardware saving is claimed for them. INT6_keep is diagnostic only because it inflates weak weights. Torus near-null behavior is a descriptive expectation without a registered equivalence margin.",
        "",
        "Both p-bit transition probabilities and objective rankings can change under these interventions. The common bank controls candidate identity for ranking comparisons, while the live contrasts include the trajectories each arm actually visits. A positive live contrast alone does not uniquely identify a ranking-only cause.",
        "",
        "This experiment uses six-bit controls. It does not directly re-certify FP5 versus INT6 under a modified output policy. The earlier 18-contrast ideal study and its selected offset triples remain unchanged.",
        "",
        "All responses here are ideal (gain 1, offset 0). No measured STT-MTJ, offset, gain-variation or hardware result is added. The study is stopped at the mechanism checkpoint.",
        "",
        "Raw per-graph records, top-16 payloads, common-bank states and bundle manifests are committed in the ring/ and torus/ directories. Source graphs are under data/fyp_tail_probe_20261121. Detailed tables are in analysis/.",
        "",
        "## Reproduction",
        "",
        "Use NumPy 2.3.5. The GitHub workflow verifies the published freeze and cross-environment parity before execution. A full replay should use a fresh clone and first move the already archived results/fyp_tail_probe_20261121 directory to a separate location; the solver refuses existing scientific output directories. Keep the committed freeze_receipt.json in the preflight directory. Run the frozen fyp_tail_probe module with --run --freeze-commit "+FREEZE_SHA+" --workers 6, then the fyp_tail_analysis module with the same freeze SHA. All repeated computation must be identified as reproduction, not additional independent observations.",
        "",
    ]
    (RESULT/"RESULTS.md").write_text("\n".join(lines))
    write_json(RESULT/"recovery.json", {
        "local_environment_status": "failed", "local_completed_bundles_observed": 19,
        "local_trajectories_observed_complete": 7296, "local_final_count": None,
        "local_outputs_in_analysis": False, "cloud_unique_trajectories": 18432,
        "same_prescribed_keys_reexecuted": True, "additional_independent_observations": 0,
        "scientific_freeze_unchanged": FREEZE_SHA,
        "reason": "exec-server protocol error: failed to query executor configuration capabilities",
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_url": "https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/"+os.environ.get("GITHUB_RUN_ID", ""),
    })
    manifest = {"status": "COMPLETE_AT_MECHANISM_CHECKPOINT", "freeze_commit": FREEZE_SHA,
                "unique_scientific_records": 18432, "graph_bundles": 48,
                "offset_executed": False, "gain_variation_executed": False,
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "files": {p.relative_to(RESULT).as_posix(): {"sha256": sha(p), "bytes": p.stat().st_size}
                          for p in sorted(RESULT.rglob("*")) if p.is_file() and p.name != "deliverable_manifest.json"}}
    write_json(RESULT/"deliverable_manifest.json", manifest)
    readme = ROOT/"README.md"
    marker = "## Weak-tail mechanism checkpoint — 21 November 2026"
    content = readme.read_text()
    if marker not in content:
        note = "\n\n"+marker+"\n\nThe frozen six-arm mechanism experiment is complete: 48 new graphs, 64 paired seeds and 18,432 unique trajectories. See [the complete checkpoint report](results/fyp_tail_probe_20261121/RESULTS.md), [registered contrasts](results/fyp_tail_probe_20261121/analysis/confirmatory.csv), and [execution recovery disclosure](results/fyp_tail_probe_20261121/recovery.json). The inaccessible local execution was replaced by a disclosed re-execution of the same fixed scientific keys on GitHub Actions; its outputs were not pooled. Offset, gain and hardware work remain stopped pending review.\n"
        content += note
        readme.write_text(content)
    print(json.dumps({"status": "CHECKPOINT_ARCHIVED", "unique_records": 18432,
                      "scientific_files": len(manifest["files"]), "offset_executed": False}), flush=True)

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("preflight", "finalize"):
        raise SystemExit("choose preflight or finalize")
    preflight() if sys.argv[1] == "preflight" else finalize()
