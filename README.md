# STT-MRAM p-bit FYP — Coupling Precision × Device Nonidealities

**Research scope LOCKED, amended 12 November 2026:** [authoritative roadmap including the newer E0 allowance](docs/ROADMAP_LOCKED_2026-11-06.md) · [evidence rules](docs/RESEARCH_PROTOCOL.md).

### Active next work — FP64 solver calibration only

Following dense M5/sparse M6 completion, the next authorized new solver work is the [E0-A two-graph CAL-only FP64 pilot](docs/E0_FP64_TWO_CAL_PILOT_FREEZE_20261112.md) implemented in [e0_fp64_two_cal_pilot.py](experiments/e0_fp64_two_cal_pilot.py). **Status: runner and freeze protocol committed; no on-host E0 pilot runs yet.** Use synthetic solver-parity test and on-host frozen source/code hashes before execution. At equal 50,000-update budgets, compare legacy linear versus conditional-uphill-calibrated geometric beta on `ising2.5-100_5555` and `t2g10_5555` with 20 paired seeds per graph (80 total solver runs). Record ten flip/conditional-uphill acceptance bins and best-cut gap checkpoints. The wider FP8/INT8 or INT7 width selection is deferred until E0 is interpreted and separately preregistered.

**Prospective FYP endpoint (not yet demonstrated):** minimum useful bit width `b*` at agreed equal Max-Cut quality; `k=b*(INT)-b*(FP)` storage bits saved per coupling; then assess whether physically grounded, independently drawn STT-MRAM p-bit gain/offset populations change `k`. A +0.5 pp margin is still a supervisor discussion item, not the retrospective M5/M6 +1 pp screen.

**One question, two axes:** Which low-order coupling representation preserves useful weighted-Max-Cut solution quality under specified STT-MRAM p-bit switching nonidealities, and is its implementation cost worthwhile?

- **Design choice:** existing low-order FP coupling precision, with matched INT controls and retained/optional BFP support.
- **Physical condition:** gain and offset variation, studied separately.
- **Task:** original Biq Mac Mac weighted Max-Cut.
- **Outcome:** precision × device-quality regime maps, a conditional precision-selection rule, held-out validation and one supporting cost table.

## Frozen execution scope

Two 100-spin CAL instances (ising2.5-100_5555, t2g10_5555) and two designated held-outs: dense ising2.5-100_7777 (M5 complete) and sparse t2g10_7777 (M6 complete, host integrity audit passed). Initial primary formats: FP/INT 4/5/6 bits + FP64; existing 8-bit variants under the declared six-bit-failure/uncertainty rule. Retain BFP results; optional BFP6 adds no new representation search.

Keep 50,000 attempted updates, frozen linear beta, 24 paired trials per cell, symmetric J=-w, h=0, represented-energy retention and original-weight scoring. Study gain and offset in separate slices; no gain × offset × contrast grid.

**Previously planned:** the already authored gain-only dense-CAL pilot, then interpret its first regime plot. It reuses matching ideal data and requires 624 new runs; no result is claimed merely because code/tests exist. See the roadmap for the staged campaign and corrected run counts.

**Hardware expansion is frozen.** Existing RTL/Sky130 results provide bounded cost evidence. Genus/library repair, old Spectre searches, new processor/DAC/ADC work, other benchmarks and new solvers are not prerequisites.

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
- Current scientific gate: experiments/m2_precision_gain_regime.py.
- Earlier six-bit combined-response screen: historical supporting code, not the current regime-map campaign.
- Current report: https://github.com/Makise-okabe/MRAM_P-bit/blob/main/main.tex (Overleaf sync via `main`). Earlier report repository is archived.

All future chats should read the locked roadmap before proposing another step. FP superiority, a moved precision threshold, and priority over all literature remain hypotheses until supported.

## 9 November 2026 completed M5 checkpoint

The dense held-out FP64/FP6/INT6 study and its static-probability diagnostic are completed and documented in [M5 closeout](docs/M5_HELDOUT_DENSE_20261109.md). This is a separate verified checkpoint, not proof that the planned gain-only campaign has completed. Run-level evidence, original M5 script and the documented topology amendment are now included in [archive commit](https://github.com/Makise-okabe/MRAM_P-bit/commit/755e4199f4542088b1dfc59f6bcb1e668d54f0a4). Dense M5 is COMPLETE; it does not establish an FP6-versus-INT6 offset interaction or a statistically confirmed cut-gap advantage at d=1.6.

## Sparse M6 completed and locally audited (10 Nov 2026)

The [sparse M6 frozen protocol](docs/M6_SPARSE_HELDOUT_PROTOCOL_20261110.md) passed synthetic self-test, sparse CAL smoke test and on-host source-hash freeze before any access to `t2g10_7777`. All 216 FP64/FP6/INT6 solver trials completed with exit status 0. The local integrity audit verified 216 unique source-hashed runs, 9 quality rows, 6 contrasts, 144 static snapshots and 6 summary rows. All six figures were subsequently generated without solver reruns.

[Audited M6 results and dense/sparse contrast](docs/M6_SPARSE_RESULTS_20261110.md): the static probability-fidelity ranking reverses, with sparse INT6 beating FP6 on matched reference states at d=0/0.8/1.6 (95% paired CI support), whereas dense M5 favours FP6. The sparse direct paired FP6–INT6 Max-Cut gap contrasts remain inconclusive at all d. This contradicts the predeclared sparse direction and is not proof that sparsity alone causes the reversal.

**Archive COMPLETE:** [M6 raw CSVs, source/protocol manifest and all six figures](results/m2_heldout_sparse_fp6_int6_20261110) are now on this research branch. The new [cross-instance manuscript synthesis](https://github.com/Makise-okabe/MRAM_P-bit/blob/main/report/maxcut/40_m5_m6_discussion.tex) connects the raw-field error, screening margins, and bounded hardware area. M5 remains archived and separate; CAL 36/36 CI import and gain-data recovery are separate. A potential 48-run FP8/INT8 width experiment stays on hold until the new width protocol is explicitly frozen.
