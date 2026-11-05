> **CURRENT RESEARCH STATUS — 5 Nov 2026:** Original three directions: **F1 neural-inference failure prediction (primary)**, **F3 reliability-aware mapping (conditional mitigation)** and **F7 Ising (paused)**; [ADR-0010](research/decisions/ADR-0010-three-direction-hierarchy-after-E31.md). **NUS E31 COMPLETE:** actual GF access-NFET + student static MTJ current simulations for 256 rows ×4 simultaneous columns under ASSUMED 0.25Ω/BL-row-segment and 0.25Ω shared return; 36 fresh input masks, original nine CAL frozen, global C0 decode **15/36 wrong**, input-mask Q **0/36**. Not new 1T1 PEX/ADC/independent chips/full W4A8 inference. **NEXT offline tests (code committed, NUS run pending):** [E33 hypothetical ADC precision](research/experiments/2026-11-05-E33-frozen-GF-ADC-precision-PENDING.md) and [E34 all-four-column generalization](research/experiments/2026-11-05-E34-four-column-calibration-generalization-PENDING.md), one run `bash experiments/run_e33_e34_nus.sh`. **NEXT PHYSICAL gate:** [E32 real 1T1-specific BL/WL/SL extraction](research/experiments/2026-11-05-E32-1T1-physical-interconnect-extraction-NEXT.md). [Prof Fong meeting brief](research/communications/2026-11-05-prof-fong-evidence-E31-E34-brief.md). N2 selective recovery remains an unvalidated candidate. Old dated notes below retained for provenance; these top instructions supersede stale statuses.

---

> **Active update — 5 Nov 2026:** The user selected a **new 1T1MTJ analog CIM prototype** as the current physical research architecture. Its fresh 1T1 4×4 layout/PEX is **not built yet**; the earlier extracted 4×4 GF local-floating-SL **2T1MTJ** is historical, not interchangeable. [Architecture decision](research/decisions/ADR-0009-architecture-gate-1T1MTJ-vs-legacy-2T1MTJ-PEX.md) · [E27 physical protocol](research/experiments/2026-11-05-E27-1T1MTJ-physical-CIM-pilot-PENDING.md) · [E27A NUS preflight](experiments/e27a_1t1_cim_preflight.py). E24 1T1-like GF-access-NFET read-current tests were already executed with **assumed wire R** (not PEX); E26A FC1 E01 arithmetic checks passed, physical joint-error test still blocked. Algorithm-level signed multibit mitigation, not ADC margin, is the proposed novelty focus. Supervisor architecture approval remains unverified. Historical status text below may be stale.

# MRAM Path Finding

**NUS ECE FYP research workspace** — 256 × 256 STT-MRAM compute-in-memory architecture, sensing reliability, inference, and conditional Ising-machine research.

**Status (4 November 2026):** Research pathfinding, not a selected novel method. Target physical-array characterization has **not** passed E02. Archived exploratory eight-cell/small-column read measurements are **not** target-array calibration or evidence.

## Research structure

**First NUS experiment:** follow [START_HERE.md](START_HERE.md). The tested one-command
runner reuses your documented frozen MNIST checkpoint and W4A8 quantizer, exports every
FC1 row block and runs the real-workload mapping screen. The real NUS run remains
pending; local checks do not establish target-array or MNIST results.

- `main.tex`, `references.bib`, `report/sections/` — **new Overleaf-ready LaTeX working report**. Compile `main.tex` with pdfLaTeX + BibTeX or latexmk.
- `research/` — research scope, method cards F1–F7, novelty review, literature register, decisions, logbook and experiment gates.
- `experiments/` — software-only verification, synthetic covariance probe and conditional Ising-reference checks. No claims of a measured 256×256 macro.
- `docs/OVERLEAF_SETUP.md` — how to create an Overleaf project from this repository.
- `report/MRAM_Pathfinding_Report.pdf` — generated PDF when the report-build workflow succeeds.

## Current physical target

256 physical rows × 256 columns = 65,536 binary MTJ positions. The new E02 phase requires a **fresh** authorized physical read model: validated cell, BL/SL/WL interconnect, drivers, sensing, calibration, persistent mismatch and held-out circuit checks. No retired small-cell measurements are carried into the target model. A 256×256 numerical array is not physical extraction; physical sectors require real isolation.


## 4 November update: revised CA2 and first new pilot

The uploaded 17-page CA2 revision restores the original proposal title and establishes
one **primary bounded development candidate**, F3 covariance-aware mapping, with F7
Ising retained conditionally. This is not an accepted novelty claim.

- **E01 exploratory**: separate digit-data 256-wide activation screen; frozen original FYP workload still missing.
- **E03M**: constructed covariance counterexample, not hardware.
- **E03Q newly executed**: finite-ADC/threshold-placement sensitivity on the same constructed fixture, with separate calibration and held-out chips; see [protocol and results](research/experiments/2026-11-04-E03Q-finite-adc-screen.md), [script](experiments/e03q_finite_adc_pilot.py) and [summary](experiments/results/E03Q_20261104_finite_adc_summary.json).
- **E02 next physical gate**: independently rebuild/characterize the target 256×256 GF 22FDX readout in the authorized NUS environment. Retired eight-cell read measurements must never calibrate the new array.

The **Overleaf report source** includes the revised research hierarchy and an E03Q
result subsection. GitHub Actions regenerates
\`report/MRAM_Pathfinding_Report.pdf\` and \`report/MRAM_Overleaf_Project.zip\`.

## Evidence policy

Separate exact arithmetic, software workload structure, constructed statistical examples, new target-circuit simulations, extracted layout and measured silicon. Report only the evidence actually obtained. E03M is a mathematical construction; E09A is reference verification. F3 is a candidate, and the Ising F7 branch remains open.

## Public repository notice

This repository is **public**. Do not commit licensed GlobalFoundries PDK/model files, access credentials, netlists with restricted foundry content or unpublished confidential data without authorization. Source documents and public-safe research text only.

## Overleaf

Use **New Project → Upload Project** with a ZIP of this repository, or work from `main.tex` and `report/sections/*.tex`. The primary LaTeX file is `main.tex`. GitHub and Overleaf are separate services; creating this repository does not automatically create a remote Overleaf project.

Legacy FYP history remains in `MRAM_FYP_Overleaf`; this new workspace contains only the active pathfinding project.
