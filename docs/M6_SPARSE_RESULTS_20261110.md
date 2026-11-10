# M6 sparse held-out validation — completed solver and integrity audit (10 Nov 2026)

**Status:** 216/216 FP64/FP6/INT6 solver runs completed successfully; process exit status **0**. The local post-run archive audit reported **PASS** for 216 unique solver keys, raw `runs.csv` SHA256 versus manifest, frozen protocol SHA256 versus manifest, 9 quality summary rows, 6 paired contrast rows, 144 saved snapshot rows and 6 snapshot summary rows. All six plotting outputs passed existence and >1000-byte size checks. No additional solver run was launched during the audit.

**Important provenance boundary:** The original M6 CSV/JSON data and all six PNG/PDF figures still reside on the experiment host `$HOME/MRAM_Pbit_M0`. This documentation commit transcribes the user's validated terminal output; it does not upload or independently reread the host's 216-row raw CSV archive. Do not claim this text file alone is an archival reproducibility check.

## Frozen protocol and source

- Original Biq Mac `t2g10_7777` sparse toroidal 100-spin weighted Max-Cut instance; graph gate: `n=100, raw=200, nonzero=200, zero=0`.
- Published optimum: **6,509,837**. Exact source graph SHA256 is stored in the local `source_gate.json`, `manifest.json`, and run records after acquisition; do not invent it here.
- `ref64`, FP6 E3M2, INT6 signed; same frozen source-only global MSE scale.
- One fixed E2 **assumed, unmeasured** synthetic persistent logit-offset population at `d=0, 0.8, 1.6`, gain exactly 1.
- 24 paired seeds, `20561201` to `20561224`, per condition. Fixed 50,000 attempted updates, linear beta schedule, retained represented-energy incumbent and original signed-weight scoring.
- Total: **3 formats × 3 offsets × 24 seeds = 216 runs**. `--selftest`, `--smoke-cal`, on-host `--freeze` and exact protocol equality check passed **before graph access**.
- Scientific claims are conditional on this graph and one device population; 24 bootstrap seeds do not constitute 24 graph or device-population samples.

## Solver optimum-gap means (percentage, lower is better)

| d | FP64 | FP6 | INT6 | FP64 eligible | FP6 eligible | INT6 eligible |
|---|---:|---:|---:|---|---|---|
| 0 | 2.797 | 3.413 | 3.061 | Yes | No | No |
| 0.8 | 3.513 | 2.609 | 3.424 | Yes | Yes | Yes |
| 1.6 | 3.621 | 3.591 | 4.084 | Yes | Yes | No |

The frozen eligibility conjunction is **both** (a) upper 95% seed-bootstrap mean original-optimum gap **≤5%** and (b) upper paired 95% bootstrap additional gap against **same-offset FP64 ≤+1 percentage point**. Both low-bit formats can have absolute-gap CI upper bounds <5% and still fail the second screen; that happens at d=0. `INT6` at d=1.6 fails the second screen despite a mean gap below 5% and absolute-gap upper CI of 4.831%. "Not eligible" here means **not certified against both bounds**; it is not evidence of a proven unacceptable cut gap.

### Per-format original-optimum gap CIs (95%)

| d | Format | Mean gap % | Lower bound % | Upper bound % | Eligible |
|---|---|---:|---:|---:|---|
| 0 | FP64 | 2.797 | 2.061 | 3.590 | Yes |
| 0 | FP6 | 3.413 | 2.665 | 4.122 | No |
| 0 | INT6 | 3.061 | 2.234 | 3.919 | No |
| 0.8 | FP64 | 3.513 | 2.680 | 4.383 | Yes |
| 0.8 | FP6 | 2.609 | 1.717 | 3.556 | Yes |
| 0.8 | INT6 | 3.424 | 2.769 | 4.056 | Yes |
| 1.6 | FP64 | 3.621 | 2.800 | 4.426 | Yes |
| 1.6 | FP6 | 3.591 | 2.779 | 4.411 | Yes |
| 1.6 | INT6 | 4.084 | 3.292 | 4.831 | No |

### Direct paired FP6-minus-INT6 gap differences (percentage points)

| d | Mean difference (pp) | 95% paired CI (pp) | Interpretation |
|---|---:|---|---|
| 0 | +0.352572 | [-0.680845, +1.395432] | inconclusive |
| 0.8 | -0.814155 | [-1.650418, +0.034324] | inconclusive |
| 1.6 | -0.492488 | [-1.378053, +0.385740] | inconclusive |

All three paired cut-gap CIs cross zero. Although FP6 and/or INT6 can meet the frozen engineering screens at particular offsets, **direct solver-quality superiority of either six-bit format is not statistically established on M6**. M6 offset difference-in-differences estimates were saved to `paired_contrasts.csv`, but exact CI bounds were not included in the supplied terminal excerpt; do not invent them. No cross-graph interaction has been statistically estimated.

## Common-state static switching-probability fidelity

Let `Δ = mean_abs_dP(FP6) - mean_abs_dP(INT6)` on matched FP64-returned reference states, with static beta multiplier 2. Negative means FP6 better probability fidelity, positive means INT6 better. These are **not** observed diverged trajectory error rates.

| d | Sparse M6 paired Δ | 95% paired CI | Dense M5 paired Δ |
|---|---:|---|---:|
| 0 | +0.000446 | [+0.000216, +0.000676] | -0.002335 |
| 0.8 | +0.000414 | [+0.000151, +0.000658] | -0.002236 |
| 1.6 | +0.000239 | [+0.000027, +0.000466] | -0.002099 |

**The directional sparse-fidelity prediction preregistered for d=0.8 and d=1.6 was contradicted.** Dense M5 favoured FP6 at all three d; sparse M6 favours INT6 at all three d, including nonzero offsets with paired CIs above zero. This is a between-two-specific-instance **ranking reversal**, not a causal demonstration that graph sparsity alone changed the representation ranking. The graph families also differ in weight distribution and other structure.

Furthermore, a better static fidelity score is **not sufficient** for a better finite-budget Max-Cut solution. Sparse INT6 has lower static distortion at d=1.6, while FP6 is certified by both predefined optimization-quality screens and INT6 is not. This does not establish a statistically significant direct FP6-over-INT6 gap benefit because its 95% CI contains zero.

## Scope, source audit, and follow-up gates

- Dense M5 remains immutable: https://github.com/Makise-okabe/MRAM_P-bit/commit/755e4199f4542088b1dfc59f6bcb1e668d54f0a4
- Sparse M6 is scientifically **solver-complete and locally audit-verified**. Original host files are to be archived on research branch before marking the GitHub data archive as complete.
- The six local verified figures are `quality_gap_95ci.{png,pdf}`, `probability_distortion_95ci.{png,pdf}`, `offset_interaction_95ci.{png,pdf}`. The earlier first run printed "Matplotlib missing"; post-run, read-only figure generation succeeded.
- Report and Overleaf summary can be committed independently as clearly marked source-transcribed material while raw host files are being archived.
- CAL 36/36 CI import and gain-data recovery are separate workstreams; do not conflate their state with M6 closure.
- No wider-format simulation yet. Next decision: separately freeze proposed **FP8/INT8 × 24 = 48** runs on already-viewed dense M5 at `d=0.8`, with a predeclared comparison against reused M5 `FP64/FP6/INT6` matched seeds. Any format-level logic-area comparison requires matched INT8 synthesis; payload saving alone is not area/energy saving.

**M6 summary is from the host's printed completed execution and independently reported local audit; this report document did not execute any solver.**
