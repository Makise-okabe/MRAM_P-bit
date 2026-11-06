# Active benchmark decision: Biq Mac weighted Max-Cut

**Effective 6 November 2026.** The user confirmed the supervisor-approved application choice: **weighted Max-Cut**, with instances from the **Biq Mac Library, Mac section**. This decision defines the sole application benchmark for this repository. The central research direction remains low-order floating-point coupling and STT-MRAM p-bit nonidealities.

## Dataset and problem are separate
Biq Mac Library is a collection of optimization problem instances, not a CMOS standard-cell library and not a coupling number format. It includes both binary quadratic programs (Biq) and Max-Cut graphs (Mac); the active application uses the latter. The official documentation provides graph descriptions and optimal values or bounds. Selected instance families and calibration/held-out membership are still to be specified.

Official sources:
- https://biqmac.aau.at/biqmaclib.html
- https://biqmac.aau.at/biqmaclib.pdf

The Mac collection includes unweighted, small signed-weight, integer-weight and statistical-physics graph families. “Weighted” does not imply noninteger weights or establish that floating point is advantageous. Retain the source weights and compare against strong integer and BFP controls. Do not modify weight ranges to manufacture an FP advantage. Do not mix arbitrary Biq/QUBO inputs into this benchmark without an explicitly separate decision.

## Native pairwise mapping
For each undirected edge (i,j), let w_ij be its original weight and let s_i in {-1,+1} indicate the side of the cut.

    Cut_w(s) = sum_(i<j) w_ij * (1 - s_i*s_j) / 2
    E_J(s)   = -sum_(i<j) J_ij*s_i*s_j - sum_i h_i*s_i
    J_ij     = -w_ij
    J_ji     = J_ij; J_ii = 0; h_i = 0
    E_J(s)   = sum_(i<j) w_ij - 2*Cut_w(s)

Thus minimizing the stated Ising energy maximizes the original cut. Each original vertex requires one spin; no auxiliary spin is required for this native Max-Cut mapping. Some higher-order SAT-to-pairwise reductions need auxiliary variables, but that is not a requirement imposed by native Max-Cut.

The explicit sign/scale convention matters to the p-bit input response. If an alternative overall normalization is used, record it and apply the same interpretation consistently. Verify the convention of any published objective/optimum before comparing: a Laplacian quadratic form can differ from an edge-cut sum by a constant factor.

Problem h=0 does not mean physical device offset is zero. Model device offsets separately from the objective.

## Research question and measurements
Compare the existing low-order FP coupling candidate with matched calibrated INT and BFP/shared-exponent controls under ideal and specified nonideal STT-MRAM p-bit responses. Test grouping and useful precision without presuming an FP win. Cost is an implementation property; the response model constrains achievable solution quality.

Evaluate returned solutions on the ORIGINAL graph:
- original cut weight and absolute gap to a verified optimum;
- explicitly labeled reference/bound gap where the exact optimum is unavailable;
- probability of returning a state meeting a fixed original-cut target within a fixed update budget;
- implementation storage, arithmetic, memory/access and output-selection costs.

A visited target is not automatically the returned output. Runtime candidate retention must use its declared implementable represented-energy policy; original objective/reference values are for external evaluation unless any rescoring hardware is explicitly included.

Preserve signed weights. Use relative optimum gaps only where their denominator is meaningful. Do not assume every listed reference value is a certified optimum.

## Existing work and limits
- Run and report only weighted Max-Cut for the active application benchmark.
- Retain generic Ising routines, number-format definitions, bit-true row tests and synthesis tooling.
- Reconcile the actual fixed-point scale encoding with the software representation. Configure h=0 and account fairly for removal/tie-off of unnecessary bias arithmetic before quoting a Max-Cut datapath area. Bias-inclusive component areas cannot establish Max-Cut-specific area.
- The 64–128-spin hardware goal remains. Graph size is the number of original vertices, not a QAM antenna/symbol count.
- Use small graphs only for independent mathematical/software checks where needed. Cropped or modified graphs are not unmodified Biq Mac instances and cannot inherit their published optima. Full Biq Mac benchmark runs do not require constructing an exponentially large exact Markov chain.
- Keep the STT-MRAM response evidence boundary: illustrative curves, literature-informed models and process-specific measured device data are distinct.

## Status
Benchmark choice is confirmed. Dataset import, instance shortlist, mapped quality results and end-to-end hardware validation for this benchmark are **pending**. This decision adds documentation only: no new experiment, codebook, CI gate or performance result.

## Dataset expansion within the approved Mac collection (7 Nov 2026)
The active benchmark includes low-dynamic-range `Mac/rudy` integer controls and high-dynamic-range `Mac/ising` examples. `t2g10_5555` has 100 nodes/200 edges and official coefficients with nonzero magnitudes 460 through 294541; `ising2.5-100_5555` has 100 nodes/4950 edges and contains 1 and -101237 (a confirmed lower bound on magnitude span of 101237). Source weight ranges must be recomputed and hashed by the loader on NUS; do not interpret those inputs as a floating-point advantage or exact optimality. See M0 source protocol and separate wide-input audit script. Old h=0 and original-cut scoring rules unchanged.
