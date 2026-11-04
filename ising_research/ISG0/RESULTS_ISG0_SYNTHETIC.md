# ISG-0 completed — synthetic mathematical smoke tests only

Executed with Python 3 and NumPy on 2026-11-05. All values below are **synthetic** and deliberately constructed; no GF Spectre or MRAM device simulation was run.

| Fixture | Mean absolute field error | Mean absolute probability error | Stationary TV vs target | Max compatibility defect | Symmetric heldout field MAE | Directed heldout field MAE | Directed+Q heldout MAE |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ideal | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0.000000 | 0.000000 | 0.000000 |
| Fixed symmetric | 0.08813 | 0.01645 | 0.04173 | 0.00000 | 0.000000 | 0.000000 | 0.000000 |
| Fixed asymmetric | 0.16625 | 0.03707 | 0.12639 | 1.56000 | 0.230446 | 0.000000 | 0.000000 |
| Asymmetric + nonlinear | 0.19474 | 0.04677 | 0.13175 | 2.94233 | 0.209082 | 0.178333 | 0.000000 |

Interpretation: the test correctly distinguishes a fixed symmetric Hamiltonian perturbation from an asymmetric one, and a nonlinear error from fixed directed pairwise fields. This is code-level verification, **not** the discovery of a real GF nonideality or a research contribution. `Q` wins by construction in the last fixture, so its zero error is not evidence of novelty or out-of-distribution performance.

### Test outcome

The ten embedded mathematical checks passed. The actual next gate is to establish a signed local-field read operation from physically valid GF MRAM netlists, without altering existing FYP work. See `EXPERIMENT_PROTOCOL.md`.
