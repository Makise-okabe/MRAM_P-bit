# LOCKED FYP RESEARCH ROADMAP — 2026-11-06

## Question
How should coupling precision and scale granularity be chosen for nonideal MRAM p-bit systems to preserve useful optimization performance at lower implementation cost?

Target contribution: a device-aware format/scale **configuration rule** and a coupling macro, supported by implementation and scaling evidence. Floating point is a central candidate, not an assumed winner.

## Hypotheses
- H1 — device-dependent useful precision (headline): does the minimum useful coupling precision vary with p-bit nonideality type/severity? Require a predeclared absolute task-quality floor.
- H2 — scale granularity (main design): when do per-element exponents justify their cost against optimized global/row/tile/block scaled integers and shared-exponent block floating point? Preserve effective coupling symmetry.
- H3 — size dependence (conditional): for each specified instance family, study precision vs size without assuming either integer growth or floating-point constancy.

## Strong C1 baseline
High-precision reference; tuned scaled integer with format/group-specific scale; shared-exponent tile/BFP; defined per-element low-bit float. Include applicable normalization/dynamic-range reduction. Count coefficient and bias J+h, scale/exponent metadata, alignment, accumulation, bandwidth and replica costs. J-only quantization is a documented isolated ablation. Retain J_ij=J_ji and J_ii=0 after quantization, e.g. via symmetric tiles.

## Evaluation
**Benchmark scope, locked 2026-11-06:** Primary **weighted Max-Cut** (control graph degree, density, sparsity, coefficient dynamic range including within-row scales). Secondary **balanced graph partitioning / minimum bisection** with explicit cardinality penalty, to challenge objective-vs-constraint precision and J+h scaling. Independent **weighted spin-glass Ising instances** serve as structural controls, with frustration, signed couplings and held-out coefficient distributions. **TSP is excluded from all formal H1/H2/H3 comparisons, application claims and performance scaling**; existing small-N TSP code remains only to validate QUBO mappings and test general-purpose solver invariants. No group TSP results, parameters or benchmark instances are imported. Score the ORIGINAL unquantized task with validity requirements. Primary: time-to-target including all updates, replica exchanges and final selection (software update counts are not hardware time/energy). Secondary: task gap, validity, paired hit rates, small-N exact distribution check, implementation-backed cost. Pair seeds within independent instances, cluster uncertainty by instance, freeze calibration/held-out splits. Use one consistent quantized Hamiltonian for ideal update and exchange; nonideal physical updates do not automatically sample an exact equilibrium distribution.

## Milestones
| M | Deliverable | Completion gate |
|---|---|---|
| M0 | Reference solver, metrics, new independent benchmarks, provenance | Exact mappings, ideal Gibbs test, task baseline, held-out split and response-model source audit |
| M1 | Joint precision x nonideality vs tuned integer/BFP/float | H1/H2 evidence or bounds, paired independent-instance uncertainty, absolute quality target |
| M2 | Device-aware configuration rule and macro analytical cost | No held-out tuning; counts alignment, storage, scales, accumulation, replicas |
| M3 | Bit-true 64–128-spin tile and synthesis | Arithmetic validation, synthesis-backed timing/area |
| M4 | Held-out devices/tasks and larger systems | Failure boundaries and supported scaling |
| M5 | Architecture/design rules/thesis | Every claim traceable to reproducible evidence |

M1 never requires floating point to win; supported limits or an integer-favoring rule are scientifically useful.

## Schedule
14 active working weeks + two weeks buffer with reduced capacity around exams. Indicative M0 weeks 1–2, M1 3–5, M2 6–8 (CA3 target M1/M2), M3 9–11, M4 12–13, M5 week 14. Not a guaranteed calendar. FPGA board optional.

## NEW EVIDENCE BASE — HARD RESET
Prior CIM/ADC/sensing-margin experiments, reported TSP FP4=61% vs INT4=48%, and assistant's previous nonideality pilot are all **excluded**. Do not import their scripts, instance matrices, fitted coefficients, calibration, runtime measurements, or outcomes. Old work is preserved on historical Git branches for CA2 only. Math definitions and properly cited published research are allowed as background, not empirical evidence.

## Physical gate
No ideal pseudo-random generator counts as MRAM device evidence. Document physical switching mode, real p-bit probability curve, variation and correlations from appropriately licensed/authorized source before device-grounded claims. No GF PDK material on public GitHub.