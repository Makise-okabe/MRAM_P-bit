# M0 PT candidate — 2026-11-06

**Evidence class:** new E1 ideal-device software experiment, not a physical p-bit model. This code is NOT an H1/H2 precision result and NOT accepted as final M0 solver.

## Motivation and NUS diagnostic
User's fresh M0 3-city TSP sample diagnostics at A=20, beta 0.50: one unique state in 3,000 samples, valid and ground-hit fraction 100%, TV ~0.8333; the 6 symmetric valid 3-city tours all have identical length. Beta .05 had 263 unique states, 26.37% valid and TV ~0.1274; beta .15 had 81 unique states, 94.80% valid, TV ~0.2264. This demonstrates mixing versus constraint-validity tension in one small illustrative instance, not any advantage of floating-point precision.

## Candidate mechanism
Multiple replicas with increasing inverse temperatures, single-spin ideal Gibbs updates in each, adjacent swaps with log acceptance ratio:
`(beta_low - beta_high) * (energy_low - energy_high)`.
Both local updates and swaps use the same solver Hamiltonian; the original unquantized task determines *only* the reported optimization target. Cold-chain sampling correctness is checked against exact probabilities for N<=16. Cold-only target checks avoid free hot-replica best-of-N selection.

## Cost and limitations
Count **all** attempted local updates across all replicas, attempted and accepted swaps, cold checkpoints, and initialization draws. These are software work units, not hardware timing or energy; swapping complete states, routing, scale conversion and scheduling require independent architecture accounting. Sampling TV uses correlated cold-chain samples and is only a diagnostic; confidence requires independent seeds, instance-level replication and convergence checks. 3-city symmetric TSP is not a useful optimization benchmark; at least 4-city independent instances needed. Exact enumeration limits N<=16.

## Suggested gate commands
```bash
python3 -m unittest discover -s tests -v
python3 experiments/m0_parallel_tempering.py --family tsp --size 3 --burnin 500 --collect 1000 --output results/m0_pt_tsp3_seed20261107
python3 experiments/m0_parallel_tempering.py --family tsp --size 4 --burnin 1000 --collect 2000 --output results/m0_pt_tsp4_seed20261107
python3 experiments/m0_parallel_tempering.py --family maxcut --size 8 --burnin 1000 --collect 2000 --output results/m0_pt_maxcut8_seed20261107
```
Outputs are non-overwriting directories, with SHA256. Future statistical comparison must pair seeds and independently generated instances and include same-budget non-PT controls. No predetermined PT winner.

## Active FYP benchmark rule (6 November reset)
Keep all TSP code and corresponding user-run results only as historical M0 mathematical mapping and mixing diagnostics. It is not an application benchmark or evidence for H1/H2/H3. Formal experiments now use weighted Max-Cut, balanced graph partitioning (to be implemented), and held-out signed spin-glass controls. No PT solver finding alone is a device-aware coupling contribution.
