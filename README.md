# MRAM Path Finding

**NUS ECE FYP research workspace** — 256 × 256 STT-MRAM compute-in-memory architecture, sensing reliability, inference, and conditional Ising-machine research.

**Status (4 November 2026):** Research pathfinding, not a selected novel method. Target physical-array characterization has **not** passed E02. Archived exploratory eight-cell/small-column read measurements are **not** target-array calibration or evidence.

## Research structure

- `main.tex`, `references.bib`, `report/sections/` — **new Overleaf-ready LaTeX working report**. Compile `main.tex` with pdfLaTeX + BibTeX or latexmk.
- `research/` — research scope, method cards F1–F7, novelty review, literature register, decisions, logbook and experiment gates.
- `experiments/` — software-only verification, synthetic covariance probe and conditional Ising-reference checks. No claims of a measured 256×256 macro.
- `docs/OVERLEAF_SETUP.md` — how to create an Overleaf project from this repository.
- `report/MRAM_Pathfinding_Report.pdf` — generated PDF when the report-build workflow succeeds.

## Current physical target

256 physical rows × 256 columns = 65,536 binary MTJ positions. The new E02 phase requires a **fresh** authorized physical read model: validated cell, BL/SL/WL interconnect, drivers, sensing, calibration, persistent mismatch and held-out circuit checks. No retired small-cell measurements are carried into the target model. A 256×256 numerical array is not physical extraction; physical sectors require real isolation.

## Evidence policy

Separate exact arithmetic, software workload structure, constructed statistical examples, new target-circuit simulations, extracted layout and measured silicon. Report only the evidence actually obtained. E03M is a mathematical construction; E09A is reference verification. F3 is a candidate, and the Ising F7 branch remains open.

## Public repository notice

This repository is **public**. Do not commit licensed GlobalFoundries PDK/model files, access credentials, netlists with restricted foundry content or unpublished confidential data without authorization. Source documents and public-safe research text only.

## Overleaf

Use **New Project → Upload Project** with a ZIP of this repository, or work from `main.tex` and `report/sections/*.tex`. The primary LaTeX file is `main.tex`. GitHub and Overleaf are separate services; creating this repository does not automatically create a remote Overleaf project.

Legacy FYP history remains in `MRAM_FYP_Overleaf`; this new workspace contains only the active pathfinding project.
