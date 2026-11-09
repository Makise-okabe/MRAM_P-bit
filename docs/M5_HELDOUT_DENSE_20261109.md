# M5 held-out dense six-bit validation — verified closeout (9 Nov 2026)

**Status:** 216/216 completed solver runs; 216 unique seed/condition keys; raw `runs.csv` SHA256 matched its local manifest. Derived post-hoc mechanism CSV rebuilt after NUL-byte corruption; all six mean `|ΔP|` values independently matched `snapshot_summary.csv`. The 144/144 reconstructed records and PDF/PNG were verified. No additional solver runs were launched.

**Experiment:** Biq Mac `ising2.5-100_7777`, 100 vertices, 4950 raw edges, 4869 retained nonzero, 81 zero-weight; published original-weight optimum 3,363,230. `ref64`, FP6 E3M2 and INT6, frozen global source-MSE scale; assumed logit offset halfspan `d=0,0.8,1.6` and one fixed synthetic device population; 24 matched seeds × 50,000 attempted Gibbs updates per condition. Score final retained states with original signed weights.

## Original-weight optimum-gap results

| Offset d | FP64 mean gap (%) | FP6 mean gap (%) | INT6 mean gap (%) |
|---|---:|---:|---:|
| 0.0 | 3.890077 | 3.816876 | 4.602918 |
| 0.8 | 3.981978 | 3.682681 | 4.669792 |
| 1.6 | 4.128334 | 4.434675 | 4.569409 |

The frozen eligibility rule requires upper 95% CI absolute mean gap ≤5% **and** upper paired CI for additional gap versus same-offset FP64 ≤+1 percentage point. FP64: passes all; FP6: passes at 0/0.8, fails at 1.6 (absolute-gap upper CI 5.286%); INT6: fails all three. "Fail" means unable to certify both screens; it does not imply a universally bad format.

| Offset d | FP6–INT6 mean gap (pp) | 95% paired CI (pp) | Offset difference-in-differences vs d=0 (pp), 95% CI |
|---|---:|---|---|
| 0.0 | -0.786041 | [-1.270594, -0.288797] | Baseline |
| 0.8 | -0.987110 | [-1.639398, -0.411623] | -0.201069 [-0.771663, 0.379563] |
| 1.6 | -0.134734 | [-0.834897, 0.499577] | +0.651307 [-0.086523, 1.370722] |

The FP6 paired quality advantage is supported at d=0/0.8, **not** statistically established at d=1.6. Neither offset interaction CI excludes zero; do not claim a proven offset-by-format interaction. The ideal condition already favours FP6, so device offset did not create that advantage.

## Static p-bit response fidelity

The 144 post-hoc format-by-reference-state rows evaluate each format at the same 24 FP64-returned states per offset (not 144 independent devices). Probability error is the **exact** logistic difference on those states, not the measured disagreement rate of independent solver trajectories.

| d | FP6 mean abs ΔP | INT6 mean abs ΔP | FP6 mean abs ΔH | INT6 mean abs ΔH |
|---|---:|---:|---:|---:|
| 0.0 | 0.001684103 | 0.004018867 | 3481.186 | 4969.826 |
| 0.8 | 0.001594345 | 0.003830003 | 3507.042 | 4883.827 |
| 1.6 | 0.001747120 | 0.003846156 | 3515.478 | 4918.404 |

FP6 minus INT6 mean abs ΔP, paired 95% CI:
- d=0: -0.002334764 [-0.003154449, -0.001530219]
- d=0.8: -0.002235658 [-0.003045078, -0.001481450]
- d=1.6: -0.002099036 [-0.002786586, -0.001436149]

All probability-distortion paired intervals exclude zero, supporting the **pre-held-out** directionally frozen prediction for the dense graph.

## Post-hoc mechanism and scientific limits

Using exploratory `|2β H_ref + offset| <= 2`, roughly 1.7–1.8% of evaluated spin-state observations fall in the sigmoid's transition band, accounting for a disproportionate share (approximately 68–70% at d=0) of total absolute distortion. At d=0, mean first-order approximation `P(1-P)|2βΔH|` gives 0.001667 (FP6) and 0.005599 (INT6) versus exact 0.001684/0.004019; linearisation is notably less accurate for INT6 in these snapshots. These are **post-hoc**, not causal trajectory findings.

The existing mapped common row-plus-interface area is approximately 23,481.27 µm² (FP6) versus 18,061.07 µm² (INT6), about **+30% FP6** for that digital component in the cited mapping library; not full-chip area, energy, or measured STT-MRAM silicon.

**Boundaries:** one held-out dense graph; one fixed synthetic offset population; 24 seed-bootstrap replicates per condition; no graph-level CI, measured device residual distribution, or causal mapping from static error to solver quality. `t2g10_7777` remains untouched. Post-freeze graph-topology acceptance amendment is separately audited; M5 has 81 zero-weight source entries, and the 4869 nonzero retained entries are consistent with the 4950 raw entries.

## Provenance and synchronization

All numeric summaries above are transcribed from the user's source-verified completed M5 audit. The following original, **host-local files have not been uploaded by this documentation commit**:

```text
results/m2_heldout_dense_fp6_int6_20261109/
  protocol.json
  protocol_amendment_topology.json
  manifest.json
  runs.csv
  quality_summary.csv
  paired_contrasts.csv
  snapshot_rows.csv
  snapshot_summary.csv
  M5_RESULTS_INTERPRETATION.md
  mechanism_posthoc/per_seed_mechanism.csv
  mechanism_posthoc/mechanism_contribution.{png,pdf}
```

The corrupted NUL CSV was preserved separately as `per_seed_mechanism.corrupt_20261109.csv` on host and must **not** be treated as evidence or committed. The experiment script `experiments/m2_heldout_dense_sixbit.py` and CAL interval recovery script `scripts/recover_cal_intervals.py` were still untracked locally at last reported `git status`; keep the frozen original script and audit when pushing scientific data. Do not overwrite source-verified artifacts, rerun M5, or silently alter the predeclared hypothesis.

**Next:** interpret the quality–fidelity–mapped-area trade-off, then design a separate frozen H2 comparison of per-element FP6 versus shared-scale INT6/BFP6. The current results do not prove FP6 universally superior.
