# Migration register — 4 November 2026

This repository is a **new, separate, public pathfinding workspace**. The original repository `Makise-okabe/MRAM_FYP_Overleaf` is not modified or deleted by the migration.

The editable CA2 report source was copied from the original report's `main.tex`, `references.bib`, and seven report sections, with a new section 08 stating the fresh 256×256 E02 physical-array requirements. Research methodology, literature notes, decisions, scripts, tests and constructed evidence were also copied with their existing evidence labels.

## Original PDF attachment

User-supplied `CA2_working_draft.pdf`, 15 pages, SHA256:
`5a7f2e81018fdd047b4bd02d2d823a65f9e831891c5744279a2e762ca695e726`.

This exact binary PDF is retained as the user's original chat attachment. It has not been byte-for-byte uploaded to the new repository by this GitHub migration. The version-controlled **source document** is present, and the GitHub Action builds an updated PDF from it at `report/MRAM_Pathfinding_Report.pdf` when the workflow succeeds.

## Evidence and access constraints

- The new target is a physical 256×256 array; 65,536 MTJ positions.
- Prior eight-cell/small-column electrical readings cannot enter the new target calibration or validations.
- No foundry PDK content, restricted netlists, private model packages, or secrets have been copied.
- The E03M covariance figure is constructed and E09A is Ising reference verification, not new target MRAM measurements.
- The E01 exploratory digits256 workload note is not an MRAM circuit result.

## Overleaf

See `docs/OVERLEAF_SETUP.md`. Import the GitHub repository ZIP into a **new Overleaf project** and use `main.tex` as the root file. The GitHub connector cannot create a cloud Overleaf project directly.
