# STT-MRAM p-bit FYP — Biq Mac Weighted Max-Cut

**Mandatory decision gate:** [FYP Decision Feedback Loop](docs/FYP_DECISION_FEEDBACK_LOOP.md). Every research step must have explicit FYP alignment, evidence level, prior-art check, smallest falsifiable test and STOP condition; return to the gate after observing results. This requirement applies across future project sessions.

## Active benchmark
Original **Biq Mac Library / Mac weighted Max-Cut**, 100-spin calibration graphs. The problem maps as `J_ij=J_ji=-w_ij`, `J_ii=0`, `h_i=0`. The research compares 4/5/6/8-bit FP/INT/BFP couplings under a consistent p-bit solver, then separately evaluates physical device response and real hardware cost.

## Real NUS evidence
- **M0:** 10/10 official source audits passed, original files SHA256-verified.
- **M1 FP64:** 144 solver calibration runs; 50k linear-beta selected by preregistered equal-graph gap/cost rule, observed 2.343% mean optimality gap across four calibration graphs.
- **M1 global precision:** 936 actual original Max-Cut solver runs completed: 3 calibration graphs × 13 configs (FP64 and FP/INT/BFP at 4/5/6/8 bits) × 24 fresh paired seeds, 50k linear attempted updates. Findings remain restricted to these calibration graphs; the +1pp paired-bootstrap quality screen is not a cross-graph proof.
- **Hardware:** row arithmetic and represented-energy retention are generic verified components, NOT an integrated Max-Cut p-bit ASIC or device characterization.

## Active scripts
- `experiments/biqmac_maxcut.py`: exact original-source graph import and Ising mapping.
- `experiments/m1_precision_codebooks.py`: finite-only FP, symmetric INT, global BFP codebooks.
- `experiments/m1_biqmac_precision_sweep.py`: paired 50k-linear original-cut gap experiment.
- `scripts/m1_biqmac_precision_sweep.sh`: reproducible NUS runner.
- `docs/BIQMAC_OFFICIAL_OPTIMA_2007.json`: source-hash-matched published references.
- `docs/M1_GLOBAL_PRECISION_FREEZE_20261107.md`: frozen codebooks, seeds, +1pp criterion.

Authoritative FYP report: https://github.com/Makise-okabe/MRAM_FYP_Overleaf . The active repository contains **no alternative application scripts**. Older history remains recoverable in Git history without being part of this active worktree.

## Next bounded gate (only mathematical transfer preflight)
A 2026 experimental STT-MTJ Ising p-bit paper reports a nominal sigmoid example, and already demonstrates Biq Mac Max-Cut; it is a close prior-art collision. [STT-MTJ transfer preflight](experiments/m2_stt_pbit_transfer_preflight.py) validates only the algebraic conditional-field-to-voltage map with explicitly passed, provenance-dependent nonideal parameters; it is NOT device-characterized E3 or a new 936-run sweep. See the decision feedback protocol for STOP/GO and novelty warning.
