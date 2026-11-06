# NUS E1 FP64 reference solver-quality gate — 7 November 2026

## Verified status and provenance

**NUS user-run PASS:** `scripts/m1_biqmac_reference_quality_smoke.sh`, checkout `eacd2b2`, result folder `results/m1_fp64_reference_quality_20261106T191244Z_3167258`. The experiment emitted `REFERENCE QUALITY PROBE COMPLETE` for **144** calibration runs. Its six unit tests PASS. Source graphs were the four previously SHA256-audited Biq Mac `Mac` files: `w01_100.0`, `pw01_100.0`, `t2g10_5555`, `ising2.5-100_5555`. Exact original-weight published references were imported separately in `docs/BIQMAC_OFFICIAL_OPTIMA_2007.json`, with original source-hash matches enforced. No graph data or solver outputs have been committed.

**Protocol:** six paired seeds per graph, fixed or linear ideal-Gibbs beta, budgets 5k/20k/50k attempted single-spin updates, best *represented*-energy state selection, original-weight objective for evaluation. All four calibration graphs receive equal weight in summary. This experiment uses **ref64 coefficients only**, not any format comparison, not a hardware or stochastic-MTJ device result.

## Equal-graph mean optimality gap (%), lower is better

| Gibbs profile | 5,000 updates | 20,000 updates | 50,000 updates |
| --- | ---: | ---: | ---: |
| Fixed beta | 10.039 | 6.890 | 5.402 |
| Linear beta (0.5 to 2.0 x beta_G) | 5.502 | 3.704 | **2.343** |

These values are arithmetic equal-graph means of the six-seed per-graph mean percentages below; values rounded to three decimals.

## Per-graph official optimum and mean gap (%)

| Original graph | Official C* | Fixed 5k | Fixed 20k | Fixed 50k | Linear 5k | Linear 20k | Linear 50k |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| w01_100.0 | 651 | 14.593 | 9.370 | 7.040 | 4.352 | 1.997 | **1.101** |
| pw01_100.0 | 2,019 | 4.631 | 2.864 | 2.386 | 2.336 | 1.313 | **0.396** |
| t2g10_5555 | 6,049,461 | 13.823 | 9.972 | 7.839 | 7.381 | 5.473 | **2.728** |
| ising2.5-100_5555 | 2,460,049 | 7.108 | 5.354 | **4.341** | 7.938 | 6.034 | 5.146 |

At 50k, the dense wide-range `ising2.5` graph favors fixed over linear by ~0.805 absolute percentage points; this graph-specific counterexample MUST remain visible.

## Predeclared decision and limitations

The predeclared `operating_point_recommendation.json` rule: choose the **smallest attempted-update budget** within **1.0 absolute percentage point** of the best four-graph equal-weight average gap; at the same budget prefer fixed. Here linear 20k = 3.704% > (2.343+1.0)%, so it fails the allowed quality margin. **Decision: linear annealing, 50,000 attempted updates, beta(t) = beta_G * [0.5 + 1.5 t/(U-1)], U=50,000**. Freeze this for the FIRST calibrated multi-format precision experiment; do not rescale beta separately per quantized format or optimize schedules based on format performance. The calibration tolerance is NOT a requirement to hit within 1% of the optimal cut.

**Critical caveat:** The selected budget is the largest of the tested three. It does not establish convergence or a global optimal schedule. Linear-anneal hardware must eventually cost beta/timing control, not treat it as free. Six paired seeds are NOT six independent problem instances. The four already-viewed calibration graphs remain CAL, not held-out.

For first width-profile E1, use original source weights for external cut and published optimum for gap, and return the lowest **represented** energy visited state. Implement and validate explicit FP b∈{4,5,6,8} exponent/mantissa layouts; do not call the old FP4-J/FP6-h hardware row area an FP6-J Max-Cut accelerator area. Compare INT/BFP on the same actual graph instances with explicitly justified global/undirected-edge symmetric scales and overhead. Subsequent physically documented p-bit response results must be labeled separately.

## NUS evidence location

```
results/m1_fp64_reference_quality_20261106T191244Z_3167258/
  reference_runs.csv
  reference_summary.csv
  operating_point_recommendation.json
  manifest.json
```

This ledger is a transcription of the user-supplied NUS terminal output, not a claim that the raw CSV files were uploaded to GitHub. Numerical values in the table are rounded from console means; per-seed uncertainties should be read from NUS `reference_runs.csv`.
