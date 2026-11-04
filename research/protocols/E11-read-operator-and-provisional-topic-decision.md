# E11 — next physical operator and research-path decision gate

Status: **PROTOCOL ONLY; NOT EXECUTED**. Set after E10A/E03T negative discovery screens on 2026-11-04. Not an approval to use an unlicensed model or an assertion of final research novelty.

## The decision to force

Before further Ising software optimization, choose and validate one implementable operation on the intended student-owned-MTJ / GF-access-transistor target:

1. **Coefficient read**: a noisy retrieval of one (or one column of) encoded J coefficients followed by an accurate digital field update, versus exact digital incremental-field cache. Need state encoding, read sense, ADC, random/persistent mismatch, read cost, and actual residual error. A persistent read of one same coefficient does *not* imply independent additive error on each spin flip.
2. **Full analog local field**: one physical read computes h_i(s)=sum J_ij s_j through simultaneous active rows, sign handling, and a *real* readout/ADC. Need selected/unselected connectivity, BL/SL/WL loading, near/far composition, finite sample, and per-field energy/latency. A 256-column connection manifest and old zero-bias simulation do **not** implement this operator. The existing zero-bias 16×16 PEX-tile integration is a smoke test, and inter-tile wires have no PEX.

A stable MRAM storage MTJ is distinct from a stochastic p-bit or VCMA-MTJ spin unit. No comparable spin-update energy/speed is claimed.

## Minimal physical screen to answer the operator choice

Use authorized model and legal biases only; resolve the student-owned MTJ versus older foundry-native `mtj_fls` source-policy mismatch *before* claiming target readings. Use a small, explicitly declared electrical tile rather than run the unverified full 256×256. Preserve all local SL branches and load. Pair under the same initial P/AP state assignment.

- Z: no selected row / baseline leakage and zero state.
- P-near / AP-near: one row in each nominal state.
- P-far / AP-far: another electrically distant row in each state.
- Pair-near/far with identical intended P/AP composition in all participating conducting columns.
- Repeat for two matched input counts, with unchanged columns, sense path, WL/SL bias and common read sampling time.
- Record I_sense(t), BL/SL/WL sense/remote node voltages, retention state, stable and sampled contrasts, DC/KCL checks, solver convergence. Analyze the interaction residual C_ij=I_ij-I_i-I_j+I_0 (diagnostic, NOT novel algorithm).
- Compare ideal inter-tile join to an explicitly parameterized RC ladder with provenance, then separately validate the ladder using DRC/LVS/PEX of a larger representative tile before spatial claims.
- Measure or source analog field attempt cost and digital column-fetch cost; list ADC/control/initialization/calibration expenses. Do not label source assumptions as measured energy.

## Decision gates, not dates

**Gate A: physically consequential operator.** If no safe, credible many-row analog field read exists and only coefficient retrieval is viable, Ising must confront the very strong exact digital incremental reference; update noise need not matter. If a real analog local field exists and residuals survive calibration, the next software test can use *its measured response*, not invented Gaussian skew.

**Gate B: new decision rule and strong comparison.** Freeze one concrete algorithm using measured error features before testing held-out masks/graph-chip pairs. Compare equal-cost tuned calibration/SEC, full symmetrization where physically legal, periodic refresh, decision-aware refinement, and exact digital incremental. If its rule is just ordinary cache locking, error ranking, or full symmetrization, reject as novel; no renaming.

**F3/F1 fallback:** E03T shows the current Hermite1 scorer does not improve fixed-budget selection against marginal-only or fair MC. Choose an F3/F1 method only after a different estimator/mapper gives reliable marginal selection advantage plus a full-network task benefit with a validated E02 read kernel. The real MNIST infrastructure makes this the lower-scope-risk provisional route, not a proven original contribution.

**Topic status:** Both remain OPEN; supervisor discussion can choose a provisional track after Gate A + a small matched-cost Gate B, followed by distinct novelty/prior-art validation. Stop indefinite toy parameter sweeps.

See [E10A/E03T executed decision evidence](../experiments/2026-11-04-E10A-E03T-two-path-decision-screen.md).
