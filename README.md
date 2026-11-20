# Low-order FP coupling matrices for STT-MRAM p-bits

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

**Ideal-response checkpoint COMPLETE.** The [checkpoint report](results/fyp_ideal_20261120/RESULTS.md) records all 18 registered contrasts, absolute quality, descriptive mechanisms and official-anchor exceptions. The executable freeze is [d217ab5](https://github.com/Makise-okabe/MRAM_P-bit/commit/d217ab54fc41a3a84d6a500f3ab0f3aa433059dd), committed before official `_6666` access and main-campaign execution. All 88,320 ideal records passed integrity checks: 87,552 new trajectories and exactly 768 reused first-block records. No first-block results were changed.

At the registered +0.5 pp family-mean tolerance, the lowest tested certified choices are **FP5/INT6 on the ring (one coupling bit saved)** and **FP5/INT5 on the torus (no bit saving)**. The unseen ring `_6666` case is a substantial counterexample to an individual-instance guarantee. The descriptive prediction that FP6 has greater total selection loss than INT7 also fails on the ring. Read the report before using the family-average choices.

**STOPPED at the requested checkpoint.** The selected future offset-stage triples are ring FP5/INT6/FP64 and torus FP5/INT5/FP64. No offset, gain or hardware work is authorized beyond this checkpoint without the student's confirmation. The previous 116,480-run full plan remains the workload including the unexecuted device phase.

Method choices are owned by the student and justified in methods. The protocol records the uncertainty, comparison set and stopping conditions. A positive bits-saved result is one possible contribution alongside an equal-width quality benefit or supported integer sufficiency.

## First viewed-dense block (20 Nov lock)

**COMPLETE: 1,280 unique ideal-response trajectories**, source and archived deterministic parity checked. Two fixed viewed Biq Mac dense instances, raw FP5/INT6 versus beta/a with paired calibration-change test. See [results, figures and frozen provenance](results/fyp_first_block_20261120/RESULTS.md). These are software results, not physical STT-MRAM measurements or family-level width selection.

## Completed E0 and EX1 evidence

E0 is closed. Its geometric schedule did not establish a final-quality improvement, so the 50,000-update linear reference is retained as a finite-budget operating point. [E0 archive](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107/results/e0_fp64_two_cal_20261112)

EX1 is also closed and archived. Its viewed-dense d=0 means were FP5 3.9827%, FP6 3.8169%, INT6 4.6029% and INT8 4.0412%. These exploratory observations do not establish minimum required width. Historical M5/M6 screening rules keep their original meaning. [EX1 archive](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107/results/ex1_m5_fp5_int8_20261115)

## Evidence already established

| Evidence | Status and limit |
|---|---|
| Original-source checks | 10 official Biq Mac source audits passed |
| FP64 calibration | 144 ideal runs; 50k linear operating point selected |
| Ideal precision study | 936 actual CAL runs across three original graphs, 13 configurations, 24 paired seeds |
| Arithmetic implementation | Official graph-to-RTL row checks passed |
| Row-core mapping | Sky130 HD FP6 1438.88 vs INT6/BFP6 929.6416 square micrometres |
| Common digital interface | 27 RTL cases and Sky130 mapping recorded; FP6 23481.2704 vs INT6/BFP6 18061.0720 square micrometres |
| Joint response-regime study | Gain-only runner authored; scientific completion must be established from actual outputs |
| Held-out validation | Dense `ising2.5-100_7777`: 216/216 completed, 144 post-hoc records recovered, six summary consistency checks PASS; sparse `t2g10_7777`: 216/216 and host archive audit PASS. See [M5 closeout](docs/M5_HELDOUT_DENSE_20261109.md). |

Mapped standard-cell area is not full-chip area, measured energy, physical MTJ validation or GF22FDX evidence. The current variation magnitudes are explicitly assumed E2 sensitivity levels, not measured post-calibration residuals.

## Active implementation and report

The working implementation is on [research/m4-gain-fusion-20261107](https://github.com/Makise-okabe/MRAM_P-bit/tree/research/m4-gain-fusion-20261107), [Draft PR #20](https://github.com/Makise-okabe/MRAM_P-bit/pull/20), building on [PR #19](https://github.com/Makise-okabe/MRAM_P-bit/pull/19). The default branch may contain only the scope/documentation baseline; this update does not merge research code.

- Ideal precision: experiments/m1_biqmac_precision_sweep.py.
- Existing codebooks: experiments/m1_precision_codebooks.py.
- Completed locked ideal study: experiments/fyp_ideal_campaign.py and experiments/fyp_ideal_analysis.py; source/code/seed registries are in docs/FYP_IDEAL_FREEZE_20261120.json.
- Historical gain-only implementation: experiments/m2_precision_gain_regime.py; it is not authorization to run a new gain campaign.
- Earlier six-bit combined-response screen: historical supporting code, not the current regime-map campaign.
- Current report: https://github.com/Makise-okabe/MRAM_P-bit/blob/main/main.tex (Overleaf sync via `main`). Earlier report repository is archived.

All future chats should read the locked roadmap before proposing another step. FP superiority, a moved precision threshold, and priority over all literature remain hypotheses until supported.

## 9 November 2026 completed M5 checkpoint

The dense held-out FP64/FP6/INT6 study and its static-probability diagnostic are completed and documented in [M5 closeout](docs/M5_HELDOUT_DENSE_20261109.md). This is a separate verified checkpoint, not proof that the planned gain-only campaign has completed. Run-level evidence, original M5 script and the documented topology amendment are now included in [archive commit](https://github.com/Makise-okabe/MRAM_P-bit/commit/755e4199f4542088b1dfc59f6bcb1e668d54f0a4). Dense M5 is COMPLETE; it does not establish an FP6-versus-INT6 offset interaction or a statistically confirmed cut-gap advantage at d=1.6.

## Sparse M6 completed and locally audited (10 Nov 2026)

The [sparse M6 frozen protocol](docs/M6_SPARSE_HELDOUT_PROTOCOL_20261110.md) passed synthetic self-test, sparse CAL smoke test and on-host source-hash freeze before any access to `t2g10_7777`. All 216 FP64/FP6/INT6 solver trials completed with exit status 0. The local integrity audit verified 216 unique source-hashed runs, 9 quality rows, 6 contrasts, 144 static snapshots and 6 summary rows. All six figures were subsequently generated without solver reruns.

[Audited M6 results and dense/sparse contrast](docs/M6_SPARSE_RESULTS_20261110.md): the static probability-fidelity ranking reverses, with sparse INT6 beating FP6 on matched reference states at d=0/0.8/1.6 (95% paired CI support), whereas dense M5 favours FP6. The sparse direct paired FP6–INT6 Max-Cut gap contrasts remain inconclusive at all d. This contradicts the predeclared sparse direction and is not proof that sparsity alone causes the reversal.

**Archive COMPLETE:** [M6 raw CSVs, source/protocol manifest and all six figures](results/m2_heldout_sparse_fp6_int6_20261110) are now on this research branch. The new [cross-instance manuscript synthesis](https://github.com/Makise-okabe/MRAM_P-bit/blob/main/report/maxcut/40_m5_m6_discussion.tex) connects the raw-field error, screening margins, and bounded hardware area. M5 remains archived and separate; CAL 36/36 CI import and gain-data recovery are separate. A potential 48-run FP8/INT8 width experiment stays on hold until the new width protocol is explicitly frozen.


## Weak-tail mechanism checkpoint — 21 November 2026

The frozen 2x2 mechanism experiment completed 18,432 unique trajectories on 48 fresh graphs. Both registered ring contrasts were supported: removing the accurate FP6 tail raised selection loss by 0.07562 pp (98.75% one-sided lower bound 0.04719), and restoring the tail to INT6 reduced it by 0.09132 pp (lower bound 0.06210). See [the full checkpoint report](results/fyp_tail_probe_20261121/RESULTS.md) and [registered contrasts](results/fyp_tail_probe_20261121/analysis/confirmatory.csv).

The workspace failure required a disclosed replay of the same fixed keys on GitHub Actions; inaccessible local outputs were not pooled. The subsequent ignored-directory archive error was repaired from the existing artifact with zero additional solver calls. All raw bundles and source hashes are archived. Offset, gain and hardware work remain stopped at the requested checkpoint.

Read [the interpretation, limits and output-buffer findings](docs/FYP_WEAK_TAIL_CHECKPOINT_20261121.md) alongside the frozen tables. The main experiment is stopped at the requested mechanism checkpoint.
