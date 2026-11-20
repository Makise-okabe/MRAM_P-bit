# Low-order FP coupling matrices for STT-MRAM p-bits

**This is the only active research and report repository.** The root
[main.tex](main.tex) is the current FYP manuscript, with the [completed-CAL results chapter](report/maxcut/10_coupling_matrix_cal_results.tex)
and the [M5 dense](report/maxcut/20_heldout_m5_results.tex) plus
[M6 sparse](report/maxcut/30_heldout_m6_results.tex) held-out chapters and
[cross-instance interpretation](report/maxcut/40_m5_m6_discussion.tex),
including native vector figures.
The separate earlier report repository is historical, not current.

## Study locked on 20 November 2026

The [current study plan](docs/FYP_STUDY_LOCK_20261120.md) is authoritative. It incorporates the Round 2 review and six amendments, including INT7, generated-instance response validation and the dense-array cost baseline. Older next-step restrictions in historical notes are superseded by this plan.

**Research question.** How do low-order FP representations of J change local fields, p-bit switching responses and weighted Max-Cut quality under specified STT-MRAM nonidealities, and when is the implementation cost worthwhile?

**In plain English.** Store the same problem using several small-number encodings. Run the same p-bit solver with each encoding, check the answer on the original problem, explain where quality is lost, then test the useful choices with imperfect p-bit responses and count their memory and logic costs.

| Part | Locked choice |
| --- | --- |
| Candidates | FP5, FP6, INT5, INT6, INT7, INT8 and FP64 |
| Main instances | 72 generated ring + 72 generated torus graphs, 100 spins, 64 paired seeds |
| Official anchors | Six Biq Mac cases, 128 paired seeds per candidate |
| Controller | Existing 50,000-update linear random-site solver |
| Graph scale | 100000, with the documented ring normalization factor |
| Quality tolerance | +0.5 pp primary, +0.25/+1.0 sensitivity |
| Device validation | One persistent offset bank per generated graph, delta uniform in [-0.8,0.8], selected FP/INT plus FP64 |
| Hardware | Dense fixed all-to-all array primary, sparse layouts as sensitivity |

Generated-instance contrasts use a fixed-pool best-observed feasible cut reference and are labelled accordingly. Official anchors retain published-optimum gaps. The reference is not assumed within 1% of the unknown optimum. Adding INT7 and its direct FP6 comparison gives **18 core confirmatory contrasts**, plus six device contrasts.

**Next implementation work.** Integrate trajectory logging and verify unchanged solver outputs. Test the analysis script, then run the bounded **1,280-run viewed-dense block**. Freeze executable sources before the independent main campaign and official _6666 access. The INT7 extension has four passing targeted tests and 600 legacy scalar/scale parity checks. New ensemble/device outcomes are still prospective. The complete planned workload is 116,480 unique runs, including the first block.

Method choices are owned by the student and justified in methods. The protocol records the uncertainty, comparison set and stopping conditions. A positive bits-saved result is one possible contribution alongside an equal-width quality benefit or supported integer sufficiency.

## Completed E0 and EX1 evidence

E0 is closed. Its geometric schedule did not establish a final-quality improvement, so the 50,000-update linear reference is retained as a finite-budget operating point. [E0 archive](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107/results/e0_fp64_two_cal_20261112)

EX1 is also closed and archived. Its viewed-dense d=0 means were FP5 3.9827%, FP6 3.8169%, INT6 4.6029% and INT8 4.0412%. These exploratory observations do not establish minimum required width. Historical M5/M6 screening rules keep their original meaning. [EX1 archive](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107/results/ex1_m5_fp5_int8_20261115)

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
