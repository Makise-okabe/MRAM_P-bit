# FYP manuscript source snapshot — 20 November 2026

This **archive branch** is a copy of `main` at commit `41d586844bfd4f04167276127d4366851d71c279` (last main commit 15 November 2026). It preserves the manuscript **source**, bibliography, report chapters, numerical tables, generated figure assets, and documentation without changing the active `main` or the research branch.

## Authoritative document at snapshot

- `main.tex`: manuscript entry point (current GitHub source).
- `references.bib`: references.
- `report/maxcut/10_coupling_matrix_cal_results.tex`: completed CAL.
- `report/maxcut/20_heldout_m5_results.tex`: dense M5.
- `report/maxcut/30_heldout_m6_results.tex`: sparse M6.
- `report/maxcut/40_m5_m6_discussion.tex`: cross-graph interpretation.
- `report/maxcut/45_e0_fp64_solver_calibration.tex`: completed E0.
- `report/maxcut/47_ex1_m5_exploratory_width.tex`: EX1.
- `report/maxcut/50_prospective_minimum_width_study.tex`: proposed, **not** completed, minimum-width endpoint.
- `report/figures/` and `report/maxcut/data/`: figures/data mirrors.

## Important provenance warning

**This is a GitHub source snapshot, not a verified download from the Overleaf web editor.** Overleaf may not have pulled the last GitHub changes. See `docs/OVERLEAF_SETUP.md` for sync instructions.

The latest GitHub Actions report workflow run at snapshot, [run 43716822060](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/43716822060), **failed** during LaTeX compilation, before PDF upload: `report/maxcut/30_heldout_m6_results.tex` line 167 has the unescaped literal `paired_contrasts.csv` (underscore). Later source lines have not been verified by a completed compile.

The **last successfully compiled PDF** predates the 15-Nov E0/EX1 chapters: [run 42848304785](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42848304785), artifact `FYP-coupling-matrix-report` (GitHub artifact ID `13778618247`, created 10 November 2026). Treat its `main.pdf` as **historical**, not a current 20-Nov Overleaf PDF.

## Frozen evidence locations

Research code, RTL, and run-level archived E0/EX1/M5/M6 evidence remain on [research/m4-gain-fusion-20261107](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107); they are not silently merged into main.

The prospective equal-quality, minimum-useful-width/bit-saving endpoint is **not established** as of this source snapshot. E2 gain/offset variability is assumed, not experimentally verified STT-MRAM residual spread. Do not infer E3 physical device validation, energy-to-solution, a universal FP-vs-INT win or bit savings from this archive.
