# NUS M1 global-scale precision–quality results — 936/936 runs

**Observed user-run NUS data, 7 Nov 2026.** Repository checkout `0e33fd4`; source/optimizer/codebooks already preregistered in `docs/M1_GLOBAL_PRECISION_FREEZE_20261107.md`. Source run folder:
`results/m1_precision_global_20261106T195502Z_3314224`.

**True experiment:** 3 original Biq Mac Mac weighted Max-Cut CALIBRATION graphs × (fresh FP64 + twelve FP/INT/BFP formats at b=4,5,6,8) × 24 paired solver seeds = **936** actually completed ideal mathematical Gibbs solver runs, each with **50,000 attempted updates** and frozen linear 0.5→2.0 beta schedule. Original unsigned/signed source weights scored original Max-Cut, paired published optimum gap (%), runtime output retained best represented Ising energy; one global source-MSE scale per graph/format; no STT-MRAM device or hardware cost.

## Returned original-optimum mean gap (%) — LOWER is better

| Original graph | FP64 | FP4 | FP5 | FP6 | FP8 | INT4 | INT5 | INT6 | INT8 | BFP4 | BFP5 | BFP6 | BFP8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| w01_100.0 (integer control) | 0.7744 | 1.3761 | 1.0689 | 0.9089 | 1.0241 | 1.1841 | 0.7744 | 0.7744 | 0.7744 | 0.9409 | 0.7744 | 0.7744 | 0.7744 |
| t2g10_5555 (wide sparse) | 3.2000 | 3.5012 | 3.3504 | 3.6097 | 3.5908 | 3.5288 | 2.9111 | 3.3231 | 3.4142 | 3.4736 | 3.2627 | 3.1913 | 3.2381 |
| ising2.5-100_5555 (wide dense) | 4.3449 | 6.7931 | 5.7361 | 4.1369 | 4.3582 | 6.9877 | 6.2885 | 4.4665 | 4.6655 | 8.1628 | 6.7974 | 4.8365 | 4.7575 |

All numbers above transcribed from the actual supplied NUS console output; not externally regenerated.

### Paired mean additional gap (pp) vs freshly paired FP64

| Graph / configuration | Mean delta (pp) | 95% seed bootstrap CI (pp) | Predeclared +1 pp *within-graph* screen |
|---|---:|---|---|
| ising2.5 FP5 | +1.391 | [+0.754, +2.127] | NOT passed |
| ising2.5 FP6 | **−0.208** | [−0.529, +0.090] | Preliminary pass |
| ising2.5 FP8 | +0.013 | [−0.440, +0.551] | Preliminary pass |
| ising2.5 INT5 | +1.944 | [+1.367, +2.560] | NOT passed |
| ising2.5 INT6 | +0.122 | [−0.361, +0.536] | Preliminary pass |
| ising2.5 INT8 | +0.321 | [−0.049, +0.680] | Preliminary pass |
| ising2.5 BFP6 | +0.492 | [−0.206, +1.248] | NOT passed/uncertain |
| ising2.5 BFP8 | +0.413 | [+0.052, +0.777] | Preliminary pass |
| w01 FP4 | +0.602 | [+0.160, +1.005] | NOT passed/uncertain (borderline) |
| w01 INT5/6/8 | 0.000 | [0, 0] | Exact identity with FP64 |
| t2g10 FP6 | +0.410 | [−0.408, +1.254] | NOT passed/uncertain |
| t2g10 INT5 | −0.289 | [−1.080, +0.566] | Preliminary pass |
| t2g10 BFP6 | −0.009 | [−0.719, +0.685] | Preliminary pass |

**Important interpretation:** On the dense wide-dynamic-range calibration graph, `FP5 → FP6` had much greater mean quality gain than `FP6 → FP8`, suggesting a *candidate* precision knee near 6 bits **for this one graph, one global scale, one ideal Gibbs response and chosen budget**. The FP6 paired CI crosses zero: it does **not** show statistically established FP6 superiority over FP64, despite a better point estimate. Against INT6/BFP and cross-graph performance, no overall format winner is established. The `t2g10` graph has a different rank/order and relatively wide seed uncertainty. Small integer `w01` INT5/6/8 reproduces FP64 exactly per seed (an important fair-baseline control).

Predeclared screen is `95% paired bootstrap upper bound on mean additional original-optimum gap <= +1.0 absolute percentage point`; `NO_OR_UNCERTAIN` is **not proof that a format is worse than threshold** when CI crosses threshold. These are per-graph seed-bootstrap intervals, not graph-population CIs, not multiplicity corrected, and not hardware energy/area results.

## Source integrity and artifacts

The NUS script printed:
- `M1 GLOBAL PRECISION IDEAL COMPLETE 936 runs`, with exactly three graph-specific SVG precision plots.
- **manifest.json SHA256** `c634cf6b5de417cf171cde6cee5711221f882a46f268f450c2dbafbb6635f25a`.
- **precision_paired_runs.csv SHA256** `27556b10bc9d2a778af28b2d007f28e34dedd47b14c0701fc444b5285e466b97`.
- **precision_summary.csv SHA256** `96475d8854c4f8837e7a478ae3c4ddda0d5b6abfd7b1ad4f135bc88575a0d8d4`.
- Figures: `plots/gap_vs_bits_w01_100_0.svg`, `plots/gap_vs_bits_t2g10_5555.svg`, `plots/gap_vs_bits_ising2_5-100_5555.svg`.

**Raw NUS CSV/plots remain in the user's NUS workspace**; their SHA256 and console summary are recorded here, not falsely represented as uploaded to GitHub. The synthetic 78-run end-to-end self-test printed before the real graph output is *not* part of the 936 real runs.

## Next evidence gate

Study whether the dense-graph precision transition persists under independent held-out graph instances and documented STT-MRAM p-bit gain/offset/correlation distortions; compare **symmetry-safe** global/tile grouping and real FP/INT/BFP coefficient memory/access/adder and interface costs. Do not infer physical p-bit nonideality or energy per solution from ideal-Gibbs curves. The supervisor-approved application stays original Biq Mac weighted Max-Cut only.
