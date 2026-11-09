# STT-MRAM p-bit FYP — coupling-matrix representation

**This is the only active research and report repository.** The root
[main.tex](main.tex) is the current FYP manuscript, with the [completed-CAL results chapter](report/maxcut/10_coupling_matrix_cal_results.tex)
and the [independent M5 held-out chapter](report/maxcut/20_heldout_m5_results.tex),
including native vector figures.
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

Every solver gap is scored on original source weights. The dense
held-out `ising2.5-100_7777` has now been evaluated with 216 completed
FP64/FP6/INT6 trials. The sparse `t2g10_7777` remains untouched. Existing digital
row-core and common-interface costs are component-level only.

## Completed M5 dense held-out validation (9 Nov 2026)

- 216/216 original-weight Max-Cut solver runs: FP64, FP6, INT6 × offset halfspans 0/0.8/1.6 × 24 matched seeds.
- FP6 has a paired original-cut quality advantage over INT6 at d=0 and d=0.8, but not a statistically confirmed one at d=1.6.
- FP6 has lower static switching-probability distortion on common FP64-returned states at all three offsets; neither offset interaction CI excludes zero.
- 144 post-hoc mechanism records recovered from the untouched original solver evidence after NUL corruption, with 6/6 source-summary checks passing. No solver reruns.
- [M5 report chapter](report/maxcut/20_heldout_m5_results.tex) includes native PGFPlots figures for Overleaf, with no external image dependency.
- [Verified M5 evidence and provenance](docs/M5_HELDOUT_DENSE_20261109.md) documents the source data boundaries; raw host CSVs/PNGs are not yet uploaded in this repo.

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

**Error bar policy:** The current CAL figure displays 15/36 source-backed
95% CI whiskers; a later host-side source recovery verified all 36
intervals, but the remaining 21 numerical CI bounds have not yet been
imported into the report mirror. Missing whiskers are not zero uncertainty.
M5's paired CIs are reported separately in its completed chapter.

## Research code

The frozen experiment and RTL sources continue on the
[research/m4-gain-fusion-20261107 branch](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107).
The active main branch is currently the report/documentation entry point;
research branches are not silently merged.

The [focused literature and mechanism synthesis](https://github.com/Makise-okabe/MRAM_P-bit/blob/research/m4-gain-fusion-20261107/docs/COUPLING_MATRIX_RESEARCH_SYNTHESIS_20261108.md)
provides the detailed novelty analysis and proposed held-out hypotheses.
