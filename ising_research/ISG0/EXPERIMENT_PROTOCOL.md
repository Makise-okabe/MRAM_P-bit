# ISG program — separate from the existing FYP

## Fixed research question

Does a physically valid signed read operator built from the available GF MRAM device produce field-dependent stochastic-update errors that (a) survive simple fixed symmetric-coupling calibration and (b) justify an inexpensive new correction or placement rule?

**Decision rule:** no new optimization controller until the physical mechanism is measured and cheaper baselines fail. Neither synthetic validation nor arbitrary added-noise studies qualify.

## Firewall and provenance

- Independent root directory: `~/Ising_MRAM_Sandbox/`.
- Optional later Git remote: **new repository only**; no commit, branch, PR, or push to current FYP repos.
- Source from current FYP/PDK, if needed later: immutable *copy* with SHA256 and provenance; never modify original. Use only if permitted by PDK/project restrictions. Private GF licensed data **must not** be uploaded to public GitHub.
- Ising results get `ISG-*` naming. Store measured raw PEX/Spectre files only in approved private storage.
- Include `source=...` on every result: SYNTHETIC, SCHEMATIC, PEX, or MEASURED. Never combine them in a single performance claim.

## ISG-0: exact mathematical diagnostic (completed in this package)

Data: four synthetic fixtures with one fixed intended 4-spin J and 16 states; 64 field records per fixture. Random-scan single-site Gibbs update, beta=1.3. Sample probability from sigmoid(2 beta field). Exact stationary distribution from 16×16 linear system; no random Monte Carlo error.

Synthetic scenarios:
1. Ideal symmetric Ising field.
2. Fixed symmetric coupling and bias perturbation.
3. Fixed antisymmetric directed perturbation on top of #2.
4. Add a manufactured state-dependent Q interaction to #3.

The directed-plus-Q model exactly contains scenario #4 **by construction**. Its perfect synthetic fit is a plumbing check, not evidence that Q is novel or relevant to physical MRAM.

Gate: ideal must have zero stationarity error; symmetric perturbation zero compatibility curl; directed perturbation nonzero curl; directed pairwise fit detects the fixed directed case; nonlinear term must survive the directed-pairwise fit. All required automated checks run in `ising0.py demo`.

## ISG-1a: feasibility gate for a *physical* signed local-field read (not executed)

Before any actual GF result, produce a one-page wiring diagram and circuit proof of:

- **Representation:** one spin s=±1; physically legal representation of +J, -J and J=0. Binary P/AP state alone does not directly give arbitrary signed or zero couplings. Differential encoding may use extra cells, reads and routing.
- **Selection:** exactly which WL, BL, SL and bias lines are active per local-field computation; whether it sums multiple cells concurrently or sequentially.
- **Safe read:** demonstrated read voltage and pulse width, without state disturb, and any permitted simultaneous reads (avoid asserting Kirchhoff sum equals an ideal MAC without verifying load and wire RC).
- **Signed calibration:** measured `I_P`, `I_AP`, baseline/subtraction and field normalization `h = F(I, code, ...)`, with a fixed transformation that is **not** fitted on held-out states.
- **Budget:** number of cells, read events, ADC conversions, extra reference circuits and any digital arithmetic for one spin update.

Do not infer full 4-spin analog MAC from existing individual read-current simulations. The 4-spin *mathematical* problem need not map one-to-one onto a physical 4×4 layout: dual-rail signs may require more cells than available. If parallel local-field read is unsupported, explicitly evaluate serial signed reads as a separate, costed architecture, compared with a digital solution.

Stop hardware direction if signed read or undisturbed addition cannot be demonstrated. Do not fabricate a netlist for unknown GF PDK pins.

## ISG-1b: real GF circuit characterization (not executed)

Assuming ISG-1a passes, freeze J, J placement and chip-fixed mismatch; sweep 16 states and four update sites, ideally with repeated independent read measurements and at least three additional unseen coupling placements or programmed patterns.

- Capture raw waveform or sampled currents for each physical read, with source netlist/cell names, PDK/stack/version, corners, temperature, Vread, pulse width and random seed.
- Use a prespecified signed mapping to normalize currents into dimensionless fields; preserve raw A and normalized fields as distinct columns/files.
- In each target-site conditional read, toggle the *old spin at the target* while keeping all others unchanged: field should not depend on the old target spin for heat-bath conditional logic. A failure is a distinct mechanism and should not be averaged away.
- Freeze device assignment across **all** states and repeats. Sample independent transient read noise only if an actual temporal noise source/model has been validated. Static device mismatch is not stochastic read noise.
- Label reference-field values from the intended symmetric J, not from a corrected measured field.

**Initial no-go decision:** if every residual fits a fixed symmetric coupling+bias model within independently established uncertainty, there is no observed non-Hamiltonian mechanism to correct.

## ISG-2: algorithmic hypothesis (only after ISG-1)

Candidate A: implementable reciprocity-aware placement/compensation with bounded metadata and declared per-update cost. Candidate B: error-budgeted precision selection with supported ADC modes. Neither receives a novelty claim unless it improves fully tuned simple controls on held-out *fixed resident* placements/couplings.

Mandatory baselines: raw read; fixed symmetric calibration; directed calibration as a diagnostic (may be expensive/incompatible); basic gain/offset; cheap position/occupancy model; correctly tuned temperature-only precision schedule (for B); exact digital incremental fields where applicable. Compare equal calibration data and equal hardware budgets.

Primary endpoint: 16-state stationary distribution TV and KL from intended Boltzmann target, plus compatibility defects and mixing. Only after physical feasibility should we expand to optimization time-to-target/quality with matched budgets and tuned solver schedules.

## Scientific safeguards

- Compatibility defect is not itself equal to target stationary-distribution error: explicitly solve the Markov chain.
- Fixed nonzero compatibility defect is evidence of incompatible one-site conditional laws; stationary distributions can depend on update order. Nonreversible transition kernels are possible and do not automatically imply incorrect stationary distributions.
- No exact per-update true h, exact residual, intended optimum or ground state is a free online controller input.
- Distinguish temporal randomness needed by the algorithm from fixed device mismatch and fluctuating read noise.
- Any synthetic dataset is useful for numerical verification only, never proof of a GF physical effect.
