# M0 reference gate — OPEN

Fresh mathematical solver does not establish FYP novelty, device model, or format efficiency.

- [x] New exact Ising mapping and seeded ideal Gibbs scaffolding, independent of all old results.
- [x] Unit tests for symmetry, Max-Cut mapping, TSP QUBO/Ising equivalence, small-N ideal Gibbs, and reproducibility.
- [x] Deterministic run manifests and SHA256 hashes (new nonoverwriting directories).
- [ ] Freeze independent calibration/held-out **weighted Max-Cut and balanced graph partitioning** benchmark sets; add separate held-out signed spin-glass controls.
- [ ] Demonstrate credible task-specific baseline optimization and define target/feasibility/time-to-target.
- [ ] Define replica exchange correctness and full budget accounting before using PT.
- [ ] Audit provenance/working region of stochastic MRAM p-bit response or limit conclusions to behavioral study.
- [ ] Complete direct prior-art review with quantified hardware-cost assumptions.

Commands:
    python3 -m unittest discover -s tests -v
    python3 experiments/m0_reference.py --family maxcut --size 8 --output results/m0_maxcut_demo
    python3 experiments/m0_paired_solver_gate.py --family maxcut --size 8 --instances 4 --trials 4 --cycles 250 --output results/m0_paired_maxcut_demo

TSP unit tests remain in the code solely as mathematical/solver diagnostics; balanced partitioning implementation and tests have **not** yet been built.

Example outputs are E1 software-only smoke tests; no H1/H2/H3 conclusions.