# STT-MRAM p-bit FYP — Biq Mac Weighted Max-Cut

## Active benchmark
Original **Biq Mac Library / Mac weighted Max-Cut**, 100-spin calibration graphs. The problem maps as `J_ij=J_ji=-w_ij`, `J_ii=0`, `h_i=0`. The research compares 4/5/6/8-bit FP/INT/BFP couplings under a consistent p-bit solver, then separately evaluates physical device response and real hardware cost.

## Real NUS evidence
- **M0:** 10/10 official source audits passed, original files SHA256-verified.
- **M1 FP64:** 144 solver calibration runs; 50k linear-beta selected by preregistered equal-graph gap/cost rule, observed 2.343% mean optimality gap across four calibration graphs.
- **M1 global precision:** 936 actual original Max-Cut solver runs completed: 3 calibration graphs × 13 configs (FP64 and FP/INT/BFP at 4/5/6/8 bits) × 24 fresh paired seeds, 50k linear attempted updates. Findings remain restricted to these calibration graphs; the +1pp paired-bootstrap quality screen is not a cross-graph proof.
- **Hardware:** row arithmetic and represented-energy retention are generic verified components, NOT an integrated Max-Cut p-bit ASIC or device characterization.

## Where to find the active implementation

The current weighted Max-Cut scripts are in [Draft PR #19](https://github.com/Makise-okabe/MRAM_P-bit/pull/19) on branch `research/m0-biqmac-maxcut-20261106`. This default branch is the clean scope/documentation baseline until the research PR is reviewed and merged; run active experiments from the PR branch.

## Active scripts (on the research branch)
- `experiments/biqmac_maxcut.py`: exact original-source graph import and Ising mapping.
- `experiments/m1_precision_codebooks.py`: finite-only FP, symmetric INT, global BFP codebooks.
- `experiments/m1_biqmac_precision_sweep.py`: paired 50k-linear original-cut gap experiment.
- `scripts/m1_biqmac_precision_sweep.sh`: reproducible NUS runner.
- `docs/BIQMAC_OFFICIAL_OPTIMA_2007.json`: source-hash-matched published references.
- `docs/M1_GLOBAL_PRECISION_FREEZE_20261107.md`: frozen codebooks, seeds, +1pp criterion.

Authoritative FYP report: https://github.com/Makise-okabe/MRAM_FYP_Overleaf . The active repository contains **no alternative application scripts**. Older history remains recoverable in Git history without being part of this active worktree.
