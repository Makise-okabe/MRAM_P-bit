# M0 paired solver gate — 6 November 2026

**Fresh E1 software M0 only.** No historical CIM, previously reported TSP-format numbers, or earlier artificial device response data.

Goal: remedy the last comparison's missing Gibbs time-to-target, using independent newly generated problem instances and nested paired seed labels. This tests baseline solver suitability, not precision/nonideality H1/H2.

- Family: maxcut 2–16 spins or TSP n=3/4, exact optimal original task target via exhaustive enumeration. 3-city symmetric TSP only validates math; 4-city is a mixing diagnostic not a scaling result.
- PT: 8 replicas by default, monotonically increasing beta, 1 attempted full sweep of n spins per replica per cycle, adjacent even/odd exchange. Check cold replica after each PT cycle, using original task feasibility/quality. Spin updates and swaps fully recorded.
- Gibbs: cold beta only, same **total attempted spin updates** as all PT replicas. Check state after every n attempted spin updates, giving Gibbs more evaluation opportunities per update than PT. Original objective and constraints determine hits.
- Both run the full assigned budget even if first hit occurs, to keep workload accounting simple. First-hit costs exclude later updates; report swap attempts and per-replica state overhead separately.
- Pair solver seeds within independent instances; PT and Gibbs are not guaranteed identical random draws. Statistics must cluster uncertainty by instance, not treat nested seeds as independent instances.
- Results are not hardware throughput/energy/area. Coefficient representation is unchanged; no floating point comparisons are made.

Commands:
```bash
python3 -m unittest discover -s tests -v
python3 experiments/m0_paired_solver_gate.py --family tsp --size 4 --instances 4 --trials 4 --cycles 250 --output results/m0_paired_tsp4_first
python3 experiments/m0_paired_solver_gate.py --family maxcut --size 8 --instances 4 --trials 4 --cycles 250 --output results/m0_paired_maxcut8_first
```

Default PT (8 replicas) at TSP n=4 and cycles=250 is 32,000 attempted spin updates per trial, matched to 32,000 for Gibbs; swap overhead is additional. The full dataset includes per-run first-hit spin-update counts and paired outcome counts. These example settings are exploratory (NOT frozen M1 benchmarks).