# E20 — Decide whether spatial current correction rescues E15 or retire it
Date 2026-11-04. **PENDING user execution on existing E19 GF current JSON**. Python3.6-compatible `experiments/e20_mask_suffix_gf_calibration.py` is committed in GitHub and self-tested against a mock E19 JSON schema. **No NUS E20 output/real GF corrected result claimed yet.**

## E19C failure that motivates this attempt
On E19 actual GF-NFET+student MTJ *with explicitly assumed* 5Ω/segment line resistance:
- Original CAL-midpoint errors 2/8 and 2/24 held-out; CAL-optimized single threshold still 2/8 and 2/24.
- Ambiguity gate produced 0 errors only on automatically-decided cases, by **deferring 3/8 (37.5%) and 5/24 (20.83%)**. No second read was performed and the deferred counts remain unresolved. Do NOT report zero total decoding errors.
- With R=0Ω/1Ω midpoint already 0/8 and 0/24; ambiguity gate also unnecessarily defers many cases, including 12/24 at R=0 in the confirmation run.
- E15 2-bit-codebook ideal comparison saving was **0.10957 fewer comparator decisions/potential event** on the held-out frozen MNIST packet. That is not directly comparable to E19's selected difficult 7/8 stress distribution, but a high reread fraction is obviously a poor energy starting point.

## Physically derived no-reread repair candidate
Given the public *input mask only*, compute
`Q_x=sum_{l=1}^{32}(sum_{j>=l}x_j)^2`. This is a suffix-load moment, not the hidden stored-weight intersection `n=sum x_j w_j`. In a first-order shared-resistance ladder, signal droop scales with Q of active conductance. Fit a **single coefficient** on E19 CAL currents (using known true n CAL labels); compare:
- RAW input-independent CAL-class midpoint threshold;
- Near-half active-row count, akin to input-distribution detection;
- Input activation centroid (weighted position);
- **SuffixQ** position-moment correction.
All share the same CAL/DEV division; no weight-position information, true DEV n or DEV results are used to compute the correction. The test reports adjusted current overlap and DEV errors per R for both independent E19 datasets.

This technique is a **conventional position-aware IR-drop compensation idea**, not inherently novel. If centroid or near-count performs comparably, do not give the suffixQ a novelty claim; if Q demands a costly 32-row suffix computation, charge that overhead against E15's tiny ideal comparator savings.

## Independent constructed-ladder screen (actually executed, NOT GF)
Generated fresh m=k=16 n=7/8 CAL and disjoint DEV patterns; **5000 CAL + 5000 DEV per class**. Passive ladder Rp=5k,Rap=10k, assumed segment r and ideal input access. Fit each scalar correction on CAL, test DEV:
| assumed r Ω/segment | raw DEV errors /10000 | near count | centroid | suffixQ |
|---|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0 | 0 |
| 2 | 79 | 2 | 0 | 0 |
| **5** | **1631** | 744 | 275 | **132** |
| 10 | 3089 | 2397 | 1725 | 1412 |
| 25 | 4169 | 3895 | 3542 | 3255 |

These results establish a real *mathematical* opportunity for spatial correction, **not a licensed GF transistor-level current repair or a new invention**. The model neglects NFETs, PEX, actual sense circuit, ADC reference costs, device mismatch, dynamic MTJs and energy. Since data were generated with random masks, trained-network correlations are not represented.

Source `/mnt/data/e20_position_correction_stress.py` and `/mnt/data/e20_synthetic_stress_results.txt` were executed in the model environment; the GitHub E20 controller is standalone Python3.6 without NumPy and needs only user-private E19 JSON on NUS.

## Pre-registered decision (before looking at GF DEV under correction)
- **Evidence of repair** if suffixQ reduces held-out n7/n8 errors versus RAW in both independent GF E19 runs at assumed 5Ω, does not worsen R0/R1, and meaningfully beats simple centroid/near-count. Even that only permits a full-count/PVT/ADC/cost experiment; it does NOT certify E15 novelty.
- **Retire E15 as main FYP candidate** if suffixQ fails to outperform cheap controls, CAL sample size makes the result unstable, or dynamic metadata/control/DAC energy plausibly exceeds the 0.11-comparison/event saving. Retain E15 E17 ideal result and E19/E19C/E20 negative evidence for CA2.
- A 0/24 score is statistically insufficient to claim physical zero-error guaranteed decoding. Any improved 7-versus-8 accuracy cannot prove all 17 possible counts distinguishable or 256x256 PEX behaviour.

## Run on NUS with no new Spectre
```bash
cd ~/MRAM_Path_Finding && git pull --ff-only
python3 -m py_compile experiments/e20_mask_suffix_gf_calibration.py
python3 -u experiments/e20_mask_suffix_gf_calibration.py --selftest
python3 -u experiments/e20_mask_suffix_gf_calibration.py \
 "$HOME/mram_private/E02_256x256/E19/E19_GF_NFET_MRAM_20261104T144120_179/e19_results.json" \
 "$HOME/mram_private/E02_256x256/E19/E19_GF_NFET_MRAM_20261104T144132_384/e19_results.json" \
 --out "$HOME/mram_private/E02_256x256/E19/E20_GATED_CORRECTION.json"
```
Only paste terminal summary; no proprietary PDK or mask decks should be shared publicly.


## NUS E20 completed run — decision (user terminal, 2026-11-04)

**Source evidence:** student executed existing E19 Spectre-current JSON through GitHub `experiments/e20_mask_suffix_gf_calibration.py`; no additional Spectre solver run in E20. Script `E20_SELFTEST_PASS`. Input activation mask only used for spatial predictors, CAL labels fit coefficients, DEV labels score independent outcomes. Two NUS E19 archives, each evaluated at *assumed* wire segment R=0,1,5Ω.

| Assumed R/segment | DEV cases first / confirmation | Raw midpoint wrong | Near/far wrong | Centroid wrong | SuffixQ wrong | Raw DEV current overlap |
|---|---|---|---|---|---|---|
| 0Ω | 8 / 24 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 |
| 1Ω | 8 / 24 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 |
| **5Ω** | **8 / 24** | **2 / 2** | **0 / 0** | **0 / 0** | **0 / 0** | **0.311722µA / 0.201222µA** |

The corrected DEV current-range overlap was reported as **0** for near/far, centroid, and suffixQ in both 5Ω experiments. At 5Ω the fitted current-vs-position coefficients were:
- first run (CAL 8): near_count +2.62e-7 A/count, centroid -2.169e-8 A/index, suffixQ -1.561e-9 A/unitQ;
- confirmation (CAL 24): near_count +3.764e-7 A/count, centroid -2.192e-8 A/index, suffixQ -1.296e-9 A/unitQ.
These are data-fit parameters, not process constants. Sample size still small (0/24 not proof of zero BER), two runs have distinct seeds but same synthetic wiring design; fixed m=k=16, n=7/8, nominal static P/AP only.

**Decision under pre-registered go/no-go:** **RETIRE the special suffixQ repair and E15 + E20 as PRIMARY FYP novelty**. Reason: the strong simpler input-only near/far-count and centroid baselines also eliminate all observed 5Ω DEV misclassifications, so no unique held-out task gain from suffixQ, while E15's ideal-only conversion saving is small and hardware uncosted. Do **not** claim the physical repair failed: the CAL spatial repair works for tested nominal GF NFET + static MTJ currents under assumed R. Do not claim the independent E15 ideal ADC algorithm was disproven: its 8.8838% ideal comparator-saving hypothesis remains a supplementary analytical result, not an established real energy benefit.

**Important DIB overlap:** near/far input-position imbalance is conceptually similar to DIB's I3D spatial input distribution detector; generic geometric compensation and IR-drop correction are prior-art-rich. The demonstrated repair is useful engineering but does **not** prove a new algorithm.

**CA2 conclusion:** E19 uncovered an input-placement-dependent count-current ambiguity; E19C showed CAL threshold shift alone cannot fix it, while a deferred/abstaining policy leaves many unresolved cases; E20 shows CAL-only input-position correction remedies tested current-overlap at no additional sense event, but the *simplest* near/far/centroid corrections match the sophisticated suffixQ algorithm. Explicitly archive as negative-novelty result, rather than concealing it or cherry-picking earlier passive-ladder E20 toy win.

**Private E20 output:** `~/mram_private/E02_256x256/E19/E20_mask_correction_results.json`. No licensed PDK or private mask-level currents uploaded.

