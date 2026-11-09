# STT-MRAM p-bit FYP — coupling-matrix representation

**This is the only active research and report repository.** The root
[main.tex](main.tex) is the current FYP manuscript, with five vector
figures embedded in the
[completed-CAL results chapter](report/maxcut/10_coupling_matrix_cal_results.tex).
The separate earlier report repository is historical, not current.

## Research question

How do low-order floating-point representations of the symmetric Ising
coupling matrix J affect local-field accuracy, stochastic p-bit response,
and weighted Max-Cut solution quality under specified STT-MRAM nonidealities?

The benchmark is original-weight Biq Mac weighted Max-Cut; the matrix
follows J_ij = J_ji = -w_ij and has zero diagonal and problem bias.
Matched FP/INT4,5,6,8 controls are compared with ideal FP64.
These are **assumed response stresses**, not measured physical device
variability. FP superiority is not assumed.

## Completed CAL evidence

- Ideal precision: 936 completed numerical trials.
- FP64 offset scout: 240 completed trials.
- Primary low-bit offset: 576 completed trials.
- Conditional FP8/INT8: 192 completed trials.
- Static response diagnosis: 3,888 derived records on 144 saved
  FP64 states; no new optimiser evaluations.

Every solver gap is scored on original source weights. The two
original held-out 7777 instances remain untouched. Existing digital
row-core and common-interface costs are component-level only.

## Main manuscript, actual images and reproducibility

- [main.tex](main.tex): source of truth for the current report.
- [references.bib](references.bib): references.
- [results and five native figures](report/maxcut/10_coupling_matrix_cal_results.tex).
- [report/data](report/maxcut/data): audited means, 15 traceable
  confidence intervals and static response snapshots.
- [report/figures](report/figures): physical PNG/PDF figures generated
  by the report workflow.
- [Python generator](scripts/plot_report_figures.py): data visualisation
  only; it never runs an optimiser or inspects held-out graphs.
- [sync instructions](docs/OVERLEAF_SETUP.md): connect the web editor
  to this repository's main branch and pull changes.

**Error bar policy:** Retain all 36 completed mean gap values, but
display error bars only for the 15 source-supported confidence intervals
available in the report mirror. Do not infer zero uncertainty where
an interval has not yet been imported. To complete 36/36 genuine intervals,
read the existing archived primary and eight-bit summary CSV files.

## Research code

The frozen experiment and RTL sources continue on the
[research/m4-gain-fusion-20261107 branch](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107).
The active main branch is currently the report/documentation entry point;
research branches are not silently merged.

The [focused literature and mechanism synthesis](https://github.com/Makise-okabe/MRAM_P-bit/blob/research/m4-gain-fusion-20261107/docs/COUPLING_MATRIX_RESEARCH_SYNTHESIS_20261108.md)
provides the detailed novelty analysis and proposed held-out hypotheses.
