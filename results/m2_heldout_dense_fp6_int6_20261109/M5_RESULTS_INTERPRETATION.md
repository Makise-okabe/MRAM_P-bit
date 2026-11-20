# M5 — Held-Out Dense Max-Cut Validation

## Experimental Setup

- Graph: Biq Mac `ising2.5-100_7777`
- Vertices: 100
- Raw edges: 4,950; nonzero edges: 4,869
- Published Max-Cut optimum: 3,363,230
- Coupling formats: FP64, FP6, INT6
- Offset halfspans: 0.0, 0.8, 1.6
- Paired seeds: 24 per condition
- Solver updates: 50,000 per run
- Completed solver runs: 216/216
- Device model: one fixed synthetic STT-MRAM p-bit offset population

## 1. Original-Weight Max-Cut Quality

Lower optimum gap is better.

| Offset | FP64 gap | FP6 gap | INT6 gap |
|---|---:|---:|---:|
| 0.0 | 3.890% | 3.817% | 4.603% |
| 0.8 | 3.982% | 3.683% | 4.670% |
| 1.6 | 4.128% | 4.435% | 4.569% |

### Paired FP6 minus INT6 optimum-gap differences

| Offset | Mean difference (pp) | 95% CI |
|---|---:|---|
| 0.0 | -0.786 | [-1.271, -0.289] |
| 0.8 | -0.987 | [-1.639, -0.412] |
| 1.6 | -0.135 | [-0.835, +0.500] |

FP6 achieves a statistically supported lower gap at offsets
0.0 and 0.8. At 1.6, the confidence interval includes zero.

### Frozen eligibility screening

Eligibility requires both the upper 95% CI on absolute
optimum gap to be at most 5%, and the upper paired CI
on additional gap versus FP64 to be at most 1 pp.

- FP64: passes all three tested conditions.
- FP6: passes at d=0.0 and d=0.8.
- FP6: fails at d=1.6 (absolute-gap CI upper = 5.286%).
- INT6: fails all three tested conditions.

These are design-screening outcomes, not proof of universal
superiority across other graphs or device populations.

## 2. Static Switching-Probability Fidelity

Diagnostics use common FP64-returned states.

| Offset | FP6 mean abs dP | INT6 mean abs dP |
|---|---:|---:|
| 0.0 | 0.001684 | 0.004019 |
| 0.8 | 0.001594 | 0.003830 |
| 1.6 | 0.001747 | 0.003846 |

FP6 exhibits lower absolute switching-probability
distortion in all three conditions. The paired
bootstrap confidence intervals exclude zero.

### Paired FP6 minus INT6 probability-distortion difference

| Offset | Mean difference | 95% CI |
|---|---:|---|
| 0.0 | -0.002335 | [-0.003154, -0.001530] |
| 0.8 | -0.002236 | [-0.003045, -0.001481] |
| 1.6 | -0.002099 | [-0.002787, -0.001436] |

## 3. Local-Field Error

| Offset | FP6 mean abs dH | INT6 mean abs dH |
|---|---:|---:|
| 0.0 | 3481.19 | 4969.83 |
| 0.8 | 3507.04 | 4883.83 |
| 1.6 | 3515.48 | 4918.40 |

FP6 produces lower average local-field errors.
The nonlinear sigmoid transfer function maps these
field errors into switching-probability distortions.

## 4. Post-Hoc Mechanism Analysis

The exploratory transition region was defined as:

    |2 beta H_FP64 + offset| <= 2

Only around 1.7–1.8% of evaluated spin-state observations
fall within this region, but this region accounts for a
disproportionate fraction of absolute probability distortion.

The first-order approximation is:

    |dP| approximately P(1-P) |2 beta dH|

Mean first-order approximation values:

| Offset | FP6 predicted | INT6 predicted |
|---|---:|---:|
| 0.0 | 0.001667 | 0.005599 |
| 0.8 | 0.001531 | 0.005570 |
| 1.6 | 0.001569 | 0.005857 |

The approximation is substantially less accurate for INT6
on these evaluated states. Exact sigmoid differences
remain the primary fidelity metric.

This mechanism analysis is post-hoc and static.
It does not establish which spin updates caused
differences in final Max-Cut solution quality.

## 5. Offset Interaction

Difference-in-differences versus ideal response:

| Offset | Interaction (pp) | 95% CI |
|---|---:|---|
| 0.8 | -0.201 | [-0.772, +0.380] |
| 1.6 | +0.651 | [-0.087, +1.371] |

Both confidence intervals include zero.

Therefore the data do not establish that device offset
changes the relative FP6-versus-INT6 optimization advantage.

## 6. Hardware-Cost Interpretation

The earlier mapped RTL row-plus-interface results indicate
approximately 30% more area for FP6 versus INT6 under the
specified synthesis setup.

This is a mapped-cell area comparison, not fabricated-chip
area, measured power, or energy efficiency.

The research trade-off is whether the improved coupling
and probability fidelity justifies the implementation cost.

## 7. Limitations and Evidence Boundary

- One held-out dense graph.
- One assumed device-offset population.
- Twenty-four paired solver seeds per condition.
- Confidence intervals do not cover graph-population variation.
- No measured physical STT-MRAM device population.
- Static diagnostics are not complete solver trajectory statistics.
- No direct experimental evidence of energy or power savings.
- The zero-weight-edge topology correction was documented
  as a post-freeze implementation amendment.

## 8. Research Conclusion

Low-bit floating-point coupling preserves static p-bit
switching probabilities more accurately than matched
6-bit integer coupling on the evaluated dense graph.

This advantage persists under tested synthetic offset
conditions, but final optimization quality does not
show a statistically established FP6 advantage under
the strongest tested offset.

The next research question is how coupling precision
and shared-scale granularity should be selected to
preserve useful optimization performance at lower cost.

