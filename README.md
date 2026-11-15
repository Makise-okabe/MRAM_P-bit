# STT-MRAM p-bit FYP — coupling-matrix representation

**This is the only active research and report repository.** The root
[main.tex](main.tex) is the current FYP manuscript, with the [completed-CAL results chapter](report/maxcut/10_coupling_matrix_cal_results.tex)
and the [M5 dense](report/maxcut/20_heldout_m5_results.tex) plus
[M6 sparse](report/maxcut/30_heldout_m6_results.tex) held-out chapters and
[cross-instance interpretation](report/maxcut/40_m5_m6_discussion.tex),
including native vector figures.
The separate earlier report repository is historical, not current.

## E0 FP64 solver pilot closed; minimum-width decision next (15 November 2026)

The [E0 protocol and read-only audit](https://github.com/Makise-okabe/MRAM_P-bit/blob/research/m4-gain-fusion-20261107/docs/E0_FP64_TWO_CAL_PILOT_FREEZE_20261112.md) have been completed on the two previously viewed CAL graphs: 80/80 FP64 runs and full host integrity audit PASS. The new geometric schedule's paired final 50k gap contrasts against linear were **−0.325 pp** on dense (95% CI [−1.183, +0.533]) and **+0.280 pp** on sparse (95% CI [−0.566, +1.084]). Neither CI excludes zero, and neither schedule achieved the exploratory 1% mean optimum-gap target. **Keep the established linear, 50,000-update operating point** for prospective width design; it is a finite-budget baseline, not a converged solver. [E0 original CSVs, manifests, and protocol are now archived on the research branch](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107/results/e0_fp64_two_cal_20261112); the seven required files were verified present remotely, with 80 run rows, 320 checkpoints, 800 trace bins, 16 summary rows, and eight paired contrast rows.

The [new E0 results chapter](report/maxcut/45_e0_fp64_solver_calibration.tex) and [minimum useful width design](report/maxcut/50_prospective_minimum_width_study.tex) are included in `main.tex`. Next decision, **subject to Prof Fong's approval**, is (1) linear **50,000 attempted updates**, and (2) upper 95% paired CI of extra Max-Cut gap **≤+0.5 percentage points relative to same-budget, same-device-response FP64**. The +0.5 pp proposal is distinct from E0's 1% absolute-optimum aspiration and must not overwrite M5/M6's frozen screens.

**Next bounded exploratory check is now specified:** [EX1 FP5/INT8 on previously viewed M5](https://github.com/Makise-okabe/MRAM_P-bit/blob/research/m4-gain-fusion-20261107/docs/EX1_M5_FP5_INT8_EXPLORATORY_PROTOCOL_20261115.md) and its [standalone runner](https://github.com/Makise-okabe/MRAM_P-bit/blob/research/m4-gain-fusion-20261107/experiments/ex1_m5_fp5_int8_exploratory.py). This authorizes **48 new runs maximum** on the already-viewed dense graph at zero device variation, recycling the original FP64/FP6/INT6 d=0 paired rows. Source and archived data hashes must pass before execution. **EX1 completed on host (FP5 24/24 and INT8 24/24), with original M5 source gate PASS.** The [EX1 results chapter](report/maxcut/47_ex1_m5_exploratory_width.tex) reports the exploratory d=0 mean optimum gaps: FP5 3.9827%, FP6 3.8169%, INT6 4.6029%, INT8 4.0412%; only FP6 has an unadjusted 95% extra-gap upper CI below the candidate +0.5 pp margin. The [new raw EX1 protocol, 48 runs, direct-format contrasts and manifest are now archived on the research branch](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107/results/ex1_m5_fp5_int8_20261115). The new direct paired INT8−FP6 estimate is +0.224 pp (95% CI [−0.253,+0.690]); FP5−FP6 is +0.166 pp (CI [−0.380,+0.720]). Neither contrast establishes equivalence. This is not independent held-out evidence for b* or k. This is preliminary width-boundary exploration, not an independent holdout or a claim that b* and k are established. A subsequent INT7 study, fresh-graph validation, seed top-ups, and device-population expansion remain on hold pending a separately frozen confirmatory design. A professor discussion is useful but is not required just to run read-only analysis or this tightly capped retrospective pilot. A format whose CI straddles the proposed cutoff at the predeclared sample cap will have its useful width reported as *unresolved*.

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
held-out `ising2.5-100_7777` and sparse held-out `t2g10_7777`
have each completed 216 FP64/FP6/INT6 solver trials. Existing digital
row-core and common-interface costs are component-level only.

## Completed M5 dense held-out validation (9 Nov 2026)

- 216/216 original-weight Max-Cut solver runs: FP64, FP6, INT6 × offset halfspans 0/0.8/1.6 × 24 matched seeds.
- FP6 has a paired original-cut quality advantage over INT6 at d=0 and d=0.8, but not a statistically confirmed one at d=1.6.
- FP6 has lower static switching-probability distortion on common FP64-returned states at all three offsets; neither offset interaction CI excludes zero.
- 144 post-hoc mechanism records recovered from the untouched original solver evidence after NUL corruption, with 6/6 source-summary checks passing. No solver reruns.
- [M5 report chapter](report/maxcut/20_heldout_m5_results.tex) includes native PGFPlots figures for Overleaf, with no external image dependency.
- **Dense M5 validation COMPLETE.** [Source-verified M5 interpretation](https://github.com/Makise-okabe/MRAM_P-bit/blob/755e4199f4542088b1dfc59f6bcb1e668d54f0a4/results/m2_heldout_dense_fp6_int6_20261109/M5_RESULTS_INTERPRETATION.md) and [archived run-level evidence, runner, manifests, summary CSVs and figures](https://github.com/Makise-okabe/MRAM_P-bit/commit/755e4199f4542088b1dfc59f6bcb1e668d54f0a4) now exist on the research branch. The prior note about missing raw files is obsolete. The script/data archive is not silently merged into `main`.
- FP6 cleared both predeclared quality screens at d=0 and 0.8; at d=1.6 the paired FP6–INT6 cut-gap contrast is inconclusive, and neither nonzero-offset interaction is established. These are results from one dense graph and one assumed device population.
- **Sparse M6 completed and locally audited (10 Nov 2026):** [frozen 216-run sparse protocol](https://github.com/Makise-okabe/MRAM_P-bit/blob/research/m4-gain-fusion-20261107/docs/M6_SPARSE_HELDOUT_PROTOCOL_20261110.md), [M6 result summary](https://github.com/Makise-okabe/MRAM_P-bit/blob/research/m4-gain-fusion-20261107/docs/M6_SPARSE_RESULTS_20261110.md), and [native M6 Overleaf chapter](report/maxcut/30_heldout_m6_results.tex). All 216 runs, 144 snapshot rows, and six figures passed the host audit and are now [archived on the research branch](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107/results/m2_heldout_sparse_fp6_int6_20261110), including the original manifest, CSVs, and figures. The later dense-width FP8/INT8 study remains deferred.

## Dense M5 versus sparse M6: workload-conditioned results

- **Dense M5:** FP6 has lower static probability distortion than INT6 at all three offsets (paired CIs support this); the direct solver-quality advantage is supported at d=0 and 0.8, not at 1.6.
- **Sparse M6:** INT6 has lower static probability distortion than FP6 at all three offsets (paired CIs support this); the predeclared FP6 sparse-fidelity prediction at d=0.8 and 1.6 was contradicted.
- Sparse M6 direct FP6–INT6 solver gap comparisons are statistically inconclusive at all offsets. Both formats pass both engineering quality screens at d=0.8; only FP6 passes at d=1.6.
- No causal effect of sparsity alone or universal format ranking is established by these two particular graph instances. The device population is synthetic, not experimentally measured.

## What the raw-data comparison suggests

The [full report discussion](report/maxcut/40_m5_m6_discussion.tex) shows that the relative RMS local-field error also reverses: FP6 is about 3.4–3.5% across both instances, while INT6 changes from roughly 4.8% in dense M5 to 1.9% in sparse M6. This points to the source weight distribution, global scaling and state-conditioned field errors as hypotheses, not a proved sparsity mechanism. The verified M6 offset-by-format difference-in-differences CIs include zero at d=0.8 and 1.6. No additional simulations were performed for this analysis.

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
