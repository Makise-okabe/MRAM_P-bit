# Weak-tail mechanism checkpoint — 21 November 2026

Scientific freeze: 54c06ff593c8acded95f7e4ce6f04a347c6164f7. All 18,432 prescribed unique trajectories completed on GitHub Actions.

## Execution recovery

The original Codex workspace execution became inaccessible after at least 19 graph bundles (7,296 trajectories) had been observed complete. The environment then reported an executor startup protocol failure. Its final completion count and remaining outputs could not be recovered. No fresh quality outcomes had been inspected before that failure.

This cloud execution re-executed exactly the same 48 committed graph files, six arms, 64 paired seeds and frozen analysis. The inaccessible local outputs were not pooled or treated as extra observations. There are 18,432 unique scientific keys in the analysed dataset. Actual total computational work includes an unknown amount of duplicated local computation; no claim of only 18,432 total physical solver invocations is made.

The cloud run first passed all nine synthetic test methods and 21 full archived replay controls, with the frozen NumPy version. Native git-show and every frozen file SHA256 were checked before execution. The operational recovery changed no scientific code, graph, seed, threshold or endpoint.

## Registered ring contrasts

Each contrast uses one-sided alpha 0.0125, 500,000 studentized graph-vector bootstrap resamples and 24 independent graphs. The lower bound below is the confirmatory 98.75% one-sided lower bound. The upper bound is displayed for context; together the displayed bounds form a nominal 97.5% two-sided interval.

| Contrast | Meaning | Mean, pp | Lower bound | Upper for context | Decision |
|---|---|---:|---:|---:|---|
| C1 | Remove the accurate FP6 weak tail | +0.07562 | +0.04719 | +0.13349 | SUPPORTED |
| C2 | Restore the accurate tail to INT6 | +0.09132 | +0.06210 | +0.14488 | SUPPORTED |

SUPPORTED requires the lower bound to exceed zero. NOT_ESTABLISHED does not establish zero effect, prove a probability-error explanation, or justify independent device and precision budgets. The intervention concerns these specific weak-tail values, not edge count in isolation.

## Live-trajectory search and selection

All following intervals are ordinary descriptive 95% graph-resampled intervals. Each graph mean averages its 64 paired seeds. The reference denominator is the frozen best observed original cut from FP64/FP6/INT6 x64 on that graph, not a known optimum. Probe arms may outperform this fixed reference.

Extra loss = access A + total selection Rz. Rz = represented-objective loss (V-M) + earliest-tie loss (M-R). FP64 selection is zero by construction. Constant or undefined studentization is shown as unresolved; its point value is still reported.

### Ring

| Arm | Extra, pp [95%] | Access A, pp [95%] | Selection Rz, pp [95%] | V-M, pp [95%] | M-R, pp [95%] |
|---|---|---|---|---|---|
| ref64 | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] |
| fp6 | +0.10567 [+0.02803, +0.18328] | +0.08764 [+0.01030, +0.16456] | +0.01803 [+0.01238, +0.02705] | +0.01613 [+0.01103, +0.02443] | +0.00190 [+0.00098, +0.00327] |
| fp6_mask | +0.28520 [+0.16967, +0.40633] | +0.19155 [+0.09003, +0.30360] | +0.09365 [+0.06676, +0.13961] | +0.08370 [+0.05741, +0.13412] | +0.00995 [+0.00396, +0.03022] |
| int6 | +0.32141 [+0.17856, +0.46019] | +0.15801 [+0.02346, +0.27623] | +0.16339 [+0.12448, +0.22047] | +0.06938 [+0.04426, +0.11820] | +0.09402 [+0.07258, +0.13033] |
| int6_tail | +0.13844 [+0.00620, +0.26338] | +0.06636 [-0.06300, +0.18539] | +0.07208 [+0.05338, +0.10219] | +0.06921 [+0.05141, +0.10020] | +0.00287 [unresolved, unresolved] |
| int6_keep | +11.12086 [+9.92319, +12.22987] | +6.64539 [+5.80710, +7.45765] | +4.47547 [+4.10257, +4.82731] | +4.14182 [+3.78342, +4.47148] | +0.33365 [+0.27971, +0.39137] |

### Torus

| Arm | Extra, pp [95%] | Access A, pp [95%] | Selection Rz, pp [95%] | V-M, pp [95%] | M-R, pp [95%] |
|---|---|---|---|---|---|
| ref64 | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] |
| fp6 | +0.11783 [-0.01988, +0.26748] | +0.09552 [-0.04142, +0.24627] | +0.02231 [+0.01772, +0.03084] | +0.02023 [+0.01563, +0.02974] | +0.00208 [+0.00123, +0.00323] |
| fp6_mask | +0.11354 [-0.03445, +0.27867] | +0.08717 [-0.06049, +0.25298] | +0.02636 [+0.02106, +0.03476] | +0.02317 [+0.01767, +0.03275] | +0.00320 [+0.00200, +0.00465] |
| int6 | +0.03357 [-0.07313, +0.14932] | +0.00685 [-0.10053, +0.12513] | +0.02672 [+0.02010, +0.03844] | +0.01110 [+0.00778, +0.01706] | +0.01562 [+0.01125, +0.02228] |
| int6_tail | +0.05034 [-0.05691, +0.16454] | +0.02637 [-0.08062, +0.14227] | +0.02397 [+0.01774, +0.03362] | +0.01720 [+0.01254, +0.02484] | +0.00677 [+0.00415, +0.01229] |
| int6_keep | +0.04218 [-0.07544, +0.17177] | +0.00837 [-0.10704, +0.13858] | +0.03381 [+0.02589, +0.04484] | +0.01891 [+0.01298, +0.02990] | +0.01490 [+0.01138, +0.01882] |

## Descriptive factorial interaction

Interaction is (FP6_mask-FP6)-(INT6-INT6_tail): the difference between tail-removal effects with FP6 and INT6 strong-coupling values.

| Family | Metric | Mean, pp | Descriptive 95% interval |
|---|---|---:|---|
| ring | Rz_pp | -0.01570 | [-0.06842, +0.01172] |
| ring | A_pp | +0.01226 | [-0.08342, +0.11066] |
| ring | extra_pp | -0.00344 | [-0.10926, +0.11115] |
| torus | Rz_pp | +0.00131 | [-0.00434, +0.00644] |
| torus | A_pp | +0.01118 | [-0.02801, +0.05583] |
| torus | extra_pp | +0.01248 | [-0.02551, +0.05562] |

## Shared-bank ranking and passive top-16 recovery

Each graph bank pools the top-16 states from all six arms and all 64 seeds, deduplicating raw spin vectors. Every encoding ranks this same bank. Smallest state integer resolves bank ties independently of original cut. These are conditional bank comparisons, not proof about every possible state.

The live buffer retains states by represented energy and earliest first visit only. Original quality never selects a buffer member. Best-of-16 rescoring requires original J accessible on the host and additional state transfer and scoring. The oracle M need not fit in the buffer. Global inversions remain distinct raw spin vectors.


### Ring output measurements

| Arm | Bank selection loss, pp [95%] | Bank V-M, pp [95%] | Bank M-R, pp [95%] | Top16 gain over actual return, pp [95%] | Residual extra loss after rescoring, pp [95%] | Mean tied minimum states [95%] |
|---|---|---|---|---|---|---|
| ref64 | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +1.00000 [unresolved, unresolved] |
| fp6 | +0.03943 [unresolved, unresolved] | +0.03943 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.01802 [+0.01238, +0.02704] | +0.08765 [+0.01030, +0.16457] | +1.06380 [+1.03798, +1.10220] |
| fp6_mask | +0.32278 [+0.21125, +0.47489] | +0.30925 [+0.20280, +0.46388] | +0.01354 [unresolved, unresolved] | +0.09072 [+0.06480, +0.13546] | +0.19448 [+0.09269, +0.30633] | +1.13216 [+1.05551, +1.29013] |
| int6 | +0.25010 [+0.15922, +0.37915] | +0.18014 [+0.10829, +0.27403] | +0.06996 [unresolved, unresolved] | +0.15347 [+0.11891, +0.20220] | +0.16794 [+0.03253, +0.28885] | +2.59766 [+2.09777, +3.48037] |
| int6_tail | +0.18164 [+0.09819, +0.32098] | +0.18164 [+0.09819, +0.32098] | +0.00000 [unresolved, unresolved] | +0.07073 [+0.05242, +0.09933] | +0.06771 [-0.06145, +0.18684] | +1.02474 [+1.01225, +1.04486] |
| int6_keep | +14.71250 [+12.74777, +16.61060] | +13.87848 [+11.99414, +15.73828] | +0.83402 [unresolved, unresolved] | +2.57116 [+2.35603, +2.84439] | +8.54970 [+7.53453, +9.49011] | +1.52799 [+1.47832, +1.59364] |

### Torus output measurements

| Arm | Bank selection loss, pp [95%] | Bank V-M, pp [95%] | Bank M-R, pp [95%] | Top16 gain over actual return, pp [95%] | Residual extra loss after rescoring, pp [95%] | Mean tied minimum states [95%] |
|---|---|---|---|---|---|---|
| ref64 | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +1.00000 [unresolved, unresolved] |
| fp6 | +0.03623 [unresolved, unresolved] | +0.03623 [unresolved, unresolved] | +0.00000 [unresolved, unresolved] | +0.02231 [+0.01772, +0.03084] | +0.09552 [-0.04142, +0.24627] | +1.04622 [+1.02771, +1.08194] |
| fp6_mask | +0.06028 [+0.02747, +0.13813] | +0.05441 [+0.02337, +0.13971] | +0.00586 [unresolved, unresolved] | +0.02636 [+0.02106, +0.03476] | +0.08717 [-0.06049, +0.25298] | +1.06836 [+1.04125, +1.10770] |
| int6 | +0.05366 [+0.02432, +0.11385] | +0.02334 [unresolved, unresolved] | +0.03032 [unresolved, unresolved] | +0.02672 [+0.02010, +0.03844] | +0.00685 [-0.10053, +0.12513] | +1.25716 [+1.21467, +1.30717] |
| int6_tail | +0.04229 [unresolved, unresolved] | +0.02243 [unresolved, unresolved] | +0.01986 [unresolved, unresolved] | +0.02397 [+0.01774, +0.03362] | +0.02637 [-0.08062, +0.14227] | +1.13411 [+1.09667, +1.18352] |
| int6_keep | +0.06782 [unresolved, unresolved] | +0.02418 [unresolved, unresolved] | +0.04364 [unresolved, unresolved] | +0.03380 [+0.02588, +0.04480] | +0.00838 [-0.10702, +0.13860] | +1.25911 [+1.21340, +1.31199] |

## Interpretation limits and checkpoint

FP6_mask and INT6_tail are mechanism probes; no implementable low-bit format or hardware saving is claimed for them. INT6_keep is diagnostic only because it inflates weak weights. Torus near-null behavior is a descriptive expectation without a registered equivalence margin.

Both p-bit transition probabilities and objective rankings can change under these interventions. The common bank controls candidate identity for ranking comparisons, while the live contrasts include the trajectories each arm actually visits. A positive live contrast alone does not uniquely identify a ranking-only cause.

This experiment uses six-bit controls. It does not directly re-certify FP5 versus INT6 under a modified output policy. The earlier 18-contrast ideal study and its selected offset triples remain unchanged.

All responses here are ideal (gain 1, offset 0). No measured STT-MTJ, offset, gain-variation or hardware result is added. The study is stopped at the mechanism checkpoint.

Raw per-graph records, top-16 payloads, common-bank states and bundle manifests are committed in the ring/ and torus/ directories. Source graphs are under data/fyp_tail_probe_20261121. Detailed tables are in analysis/.

## Reproduction

Use NumPy 2.3.5. The GitHub workflow verifies the published freeze and cross-environment parity before execution. A full replay should use a fresh clone and first move the already archived results/fyp_tail_probe_20261121 directory to a separate location; the solver refuses existing scientific output directories. Keep the committed freeze_receipt.json in the preflight directory. Run the frozen fyp_tail_probe module with --run --freeze-commit 54c06ff593c8acded95f7e4ce6f04a347c6164f7 --workers 6, then the fyp_tail_analysis module with the same freeze SHA. All repeated computation must be identified as reproduction, not additional independent observations.
