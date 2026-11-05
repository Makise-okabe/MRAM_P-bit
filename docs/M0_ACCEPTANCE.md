# M0 reference gate — OPEN

Fresh mathematical solver does not establish FYP novelty, device model, or format efficiency.

- [x] New exact Ising mapping and seeded ideal Gibbs scaffolding, independent of all old results.
- [x] Unit tests for symmetry, Max-Cut mapping, TSP QUBO/Ising equivalence, small-N ideal Gibbs, and reproducibility.
- [x] Deterministic run manifests and SHA256 hashes (new nonoverwriting directories).
- [ ] Freeze independent calibration/held-out weighted Max-Cut and constrained TSP benchmark sets.
- [ ] Demonstrate credible task-specific baseline optimization and define target/feasibility/time-to-target.
- [ ] Define replica exchange correctness and full budget accounting before using PT.
- [ ] Audit provenance/working region of stochastic MRAM p-bit response or limit conclusions to behavioral study.
- [ ] Complete direct prior-art review with quantified hardware-cost assumptions.

Commands:
    python3 -m unittest discover -s tests -v
    python3 experiments/m0_reference.py --family maxcut --size 8 --output results/m0_maxcut_demo
    python3 experiments/m0_reference.py --family tsp --size 3 --output results/m0_tsp_demo

Example outputs are E1 software-only smoke tests; no H1/H2/H3 conclusions.