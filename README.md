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
