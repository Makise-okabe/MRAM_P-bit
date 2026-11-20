# Locked ideal-response checkpoint

This analysis stops before offset, gain or hardware work.
Generated values are shortfalls relative to the frozen best-observed B_g, not optimum gaps. All nine contrasts per family (18 total) use the registered simultaneous bounds.

| Family | Contrast | Mean pp | Bounds pp | +0.5 pp NI |
| --- | --- | ---: | --- | --- |
| ring | fp6-int6 | -0.169820 | [-0.297938, -0.046931] | PASS |
| ring | fp5-int6 | +0.078394 | [-0.056003, +0.195208] | PASS |
| ring | fp6-int7 | -0.023524 | [-0.133002, +0.082811] | PASS |
| ring | fp5-ref64 | +0.312442 | [+0.188834, +0.460736] | PASS |
| ring | fp6-ref64 | +0.064228 | [-0.021936, +0.149014] | PASS |
| ring | int5-ref64 | +0.689623 | [+0.539917, +0.870462] | FAIL |
| ring | int6-ref64 | +0.234048 | [+0.138171, +0.342775] | PASS |
| ring | int7-ref64 | +0.087752 | [+0.017487, +0.159911] | PASS |
| ring | int8-ref64 | +0.044851 | [+0.007616, +0.090526] | PASS |
| torus | fp6-int6 | +0.071585 | [-0.025370, +0.160199] | PASS |
| torus | fp5-int6 | +0.079279 | [-0.039044, +0.197670] | PASS |
| torus | fp6-int7 | +0.095759 | [+0.001682, +0.201907] | PASS |
| torus | fp5-ref64 | +0.094937 | [-0.017558, +0.237773] | PASS |
| torus | fp6-ref64 | +0.087244 | [-0.008214, +0.181476] | PASS |
| torus | int5-ref64 | +0.164651 | [+0.048465, +0.298240] | PASS |
| torus | int6-ref64 | +0.015659 | [-0.077280, +0.108338] | PASS |
| torus | int7-ref64 | -0.008516 | [-0.077853, +0.061356] | PASS |
| torus | int8-ref64 | -0.011649 | [-0.080347, +0.059565] | PASS |

## Selected choices for the later offset stage (not run)

- ring: certified FP=fp5; certified INT=int6; selected=fp5/int6/FP64; diagnostic fallback=False.
- torus: certified FP=fp5; certified INT=int5; selected=fp5/int5/FP64; diagnostic fallback=False.

## Descriptive mechanism

Rz is nonnegative by construction. Its sign alone is not evidence of a mechanism. The comparisons below concern differences between encodings. Access differences are A_FP-A_INT; negative favors FP access.

| Family | Contrast | Endpoint | Mean pp | 95% bounds | Graph signs + / - / 0 | Prediction status |
| --- | --- | --- | ---: | --- | --- | --- |
| ring | fp5-int6 | Rz_pp | +0.043619 | [+0.023825, +0.071644] | 49/23/0 | DESCRIPTIVE_POSITIVE |
| ring | fp5-int6 | A_pp | +0.034775 | [-0.045756, +0.108569] | 41/31/0 | NO_DIRECTION_PREDICTED |
| ring | fp6-int7 | Rz_pp | -0.042574 | [-0.054813, -0.033697] | 5/67/0 | DESCRIPTIVE_OPPOSITE |
| ring | fp6-int7 | A_pp | +0.019051 | [-0.047719, +0.086170] | 38/34/0 | NO_DIRECTION_PREDICTED |
| ring | fp6-int6 | Rz_pp | -0.133742 | [-0.155928, -0.115382] | 0/72/0 | NO_DIRECTION_PREDICTED |
| ring | fp6-int6 | A_pp | -0.036078 | [-0.112341, +0.038903] | 31/41/0 | NO_DIRECTION_PREDICTED |
| torus | fp5-int6 | Rz_pp | +0.021644 | [+0.017027, +0.026717] | 66/6/0 | DESCRIPTIVE_POSITIVE |
| torus | fp5-int6 | A_pp | +0.057634 | [-0.016372, +0.131288] | 43/29/0 | NO_DIRECTION_PREDICTED |
| torus | fp6-int7 | Rz_pp | +0.018560 | [+0.015819, +0.022361] | 70/2/0 | DESCRIPTIVE_POSITIVE |
| torus | fp6-int7 | A_pp | +0.077199 | [+0.017176, +0.142663] | 42/30/0 | NO_DIRECTION_PREDICTED |
| torus | fp6-int6 | Rz_pp | +0.002899 | [-0.001285, +0.007281] | 42/30/0 | NO_DIRECTION_PREDICTED |
| torus | fp6-int6 | A_pp | +0.068686 | [+0.009723, +0.124027] | 50/22/0 | NO_DIRECTION_PREDICTED |

Per-candidate Spearman correlations, graph-mean SDs, median within-graph SEs and signed R_last-R are in the accompanying CSVs. Missing R_last for reused first-block rows is retained as missing. Correlations and mechanism intervals are descriptive and consume none of the core alpha.

## Official-anchor spread

anchor_spread.csv compares all nine reference-normalized anchor contrasts against the full generated range and 2.5/97.5 percentiles. anchor_quality_spread.csv does the same for each candidate's reference shortfall. Both retain published-optimum-normalized anchor values and B_anchor. These are descriptive comparisons, not prediction intervals. B_anchor is the largest V from 7*128 anchor trajectories (896), while B_g uses 7*64 main plus 128 independent references (576); the pool-size difference limits direct calibration.
