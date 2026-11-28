# FYP coupling-matrix research synthesis — literature, numerical mechanism, and held-out hypothesis

**Research pause memorandum | 8 November 2026 | CAL only | No new solver runs**

## Executive decision

**Decision: GO for literature-backed mechanism interpretation; HOLD all additional solver runs and held-out instance inspection.** Retain the weighted Max-Cut problem, the frozen coupling formats/scales and the frozen asynchronous Gibbs solver. Keep the existing RTL and storage estimates as supporting cost evidence, not as a fabricated STT-MTJ implementation.

**Research question:** How do low-order floating-point coupling-matrix representations affect local-field accuracy, stochastic p-bit response, and weighted Max-Cut solution quality under specified STT-MRAM nonidealities?

The completed CAL experiment supports a conditional, graph-specific precision assessment. It does NOT establish that FP is generally superior to INT; it does NOT establish a statistically reliable FP-vs-INT *offset interaction*; and it does NOT establish a measured STT-MRAM variability distribution. Our strongest advance is the explicitly connected and audited chain from quantized J to H to P to the observed, finite-budget quality, with transparent limits on the causal inference.

This is the **deep-dive subset** of a broader FYP literature survey, not a claim to have reviewed every relevant paper. Source URLs below were checked for relevance and authorship/topic on 8 November 2026. Claims about the local code and results are based on the frozen branch and the user's NUS summary outputs, rather than independent rerunning of the full 936/240/576/192 experiments.

## 1. Computing object and numerical methodology

Original weighted Max-Cut instance: 100 spins s_i in {-1,+1}, 100x100 symmetric J with J_ij = -w_ij, J_ji=J_ij, J_ii=0, and original *problem* bias h=0. For i<j each undirected coupling is quantized once and mirrored. The software stores the matrix sparsely as edges plus adjacency lists. This implements the same local field as H(s)=Jhat s, but it is not a fabricated physical 100x100 memory/MAC array.

Original objective:
C_w(s)=sum_{i<j} w_ij(1-s_i s_j)/2.
E_J(s)=-sum_{i<j}J_ij s_i s_j = sum w_ij-2 C_w(s).
Score solutions by C_w with the ORIGINAL weights; select the runtime incumbent by the earliest lowest energy computed from Jhat, not by an original-cut oracle.

Two source-original Biq Mac CAL examples:
- t2g10_5555: 100 spins, 200 nonzero undirected couplings (sparse 2D toroidal-grid family).
- ising2.5-100_5555: 100 spins, 4,950 nonzero undirected couplings (fully populated off-diagonal in this instance).
Their distinct connectivity and signed weight distributions are relevant *graph-specific confounders*; two CAL instances do not establish a population-wide format ranking. Official benchmark family descriptions: https://biqmac.aau.at/biqmaclib.html

**Frozen coefficients:** Software globally fits a scale using source-only (not outcome-fitted) coefficient MSE on nonzero input edge weights; there is one binary32 scale for an FP/INT matrix, not per-row or per-32-element scaling. Existing codebooks: FP4 E2M1, FP5 E2M2, FP6 E3M2, custom FP8 finite-only E4M3, and matched signed INT4/5/6/8. Original comparisons with global power-of-two BFP are retained as an explicitly limited control. The source code's FP4 E2M1 and FP6 E3M2 element value sets have OCP precedent; this is **not an OCP MX implementation** (the OCP concrete MX systems use 32-element blocks and E8M0 shared scaling). FP5 is a custom element format; FP8 finite-only max unscaled=480 differs from OCP E4M3 with a reserved NaN pattern and maximum 448. FP8 cannot be called a fully OCP-standard FP8 here.

**Three independent precision dimensions:**
1. Coupling-matrix coefficient representation (varied in this experiment).
2. Local-field accumulation arithmetic (high-precision software; not experimentally bit-true constrained).
3. Probability-control interface/DAC/pulse or MTJ input mapping (behavioral sigmoid; not experimentally bit-true constrained).

Stored coefficients and scale metadata are not equivalent to on-chip read ports, memories, bandwidth, accumulator gates, operating frequency, thermal noise, ADC/DAC energy, or full-chip power. The nominal one-copy dense upper-triangle coefficient footprint at N=100 is 4,950*b bits plus one 32-bit global scale, i.e. 19,832/29,732/39,632 bits for b=4/6/8; the physical choice of sparse vs dense memory access and any symmetry/control overhead are not established by this nominal count. FP and INT use equal coefficient widths under the same b but need not have equal arithmetic/decode cost.

## 2. Fifteen directly relevant publications: what they did, what they did NOT prove for us

Grouped by scientific relevance, not journal prestige. The source field links directly to the publication or original preprint. The last column is our evidence/novelty boundary.

| # | Study and verified source | Specific relevant contribution | Boundary / implication for this FYP |
|---|---|---|---|
| 1 | **Hizzani et al., 2026**, *Impact of memory device precision in analog combinatorial optimization solvers*, npj Unconventional Computing. https://doi.org/10.1038/s44335-026-00082-4 | Coupling programming deviations change updates and energy landscapes; some nonzero deviations preserve true optimum but reshape local traps; larger errors can destabilize the ground state. Includes memristor empirical wrong-update behavior. | **Closest numerical-mechanism precedent.** Cannot claim coupling errors affecting optimization is new. Their analog coupling/noise, task choices and hardware are not our FP-vs-INT global-codebook comparison on pulse-driven STT-MRAM p-bits. |
| 2 | **Mücke, Gerlach & Piatkowski, 2025** (online 2024), *Optimum-preserving QUBO parameter compression*, Quantum Machine Intelligence. https://doi.org/10.1007/s42484-024-00219-3 | Characterizes how coefficient distortion, dynamic range and parameter transformations can change or preserve minimizing states. | Coefficient MSE is not a guarantee on Ising optimum preservation or time-to-solution; preserving the exact minimizer and obtaining a near-optimal sample within 50k updates are different questions. |
| 3 | **Zhang et al., 2025**, *Automatic Extraction and Compensation of P-Bit Device Variations in Large Array Utilizing Boltzmann Machine Training*, Micromachines. https://doi.org/10.3390/mi16020133 | Models p-bit variation using slope/gain and voltage-offset terms, extracts device variation, and rederives coupling/bias weights to compensate it. | **Closest device-model/weight-matrix novelty collision.** We did NOT invent gain/offset mismatch or weight compensation. Our experiment intentionally DOES NOT perform their reweighting/calibration; it compares pre-fixed bit-width representations under a stated assumed residual. They study SOT p-bits; do not transfer their measured variation range to our STT-pulse device. |
| 4 | **Liu et al., DAC 2023**, *Ising-CF: A Pathbreaking Collaborative Filtering Method Through Efficient Ising Machine Learning*. https://doi.org/10.1109/DAC56929.2023.10247860 ; author PDF https://yunany.github.io/Publications/25_Ising_CF.pdf | Learns Ising couplings for collaborative filtering and develops an Ising-specific logarithmic quantization tailored to the learned coefficient distribution and hardware. | Nonuniform coupling coding is existing prior art; their learned J and resistor-inference stack are not original signed Biq Mac Max-Cut J. No broad novelty claim that FP is the first nonuniform coding. |
| 5 | **Tao, Zhang & Han, 2023**, *Approximate Parallel Annealing Ising Machines (APAIMs): Controller and Arithmetic Design*. https://www.ece.ualberta.ca/~jhan8/publications/CNNA_Sept13_CR.pdf | Uses FP16 arithmetic for Ising coefficients/local-field accumulation and approximates floating addition for area/timing. | Floating-point Ising arithmetic is not new; our current Python accumulation says nothing about the FP-adder hardware overhead they quantify. |
| 6 | **Volpe et al., 2026**, *A Scalable and Resource-Efficient Pipelined p-Computer for Probabilistic Ising Machines*, Advanced Intelligent Systems. https://doi.org/10.1002/aisy.70521 | Codesigns fixed-point coefficient J memory, bandwidth-aware access, pipelined local-field updates, update rate and graph density; uses example 16/10/2-bit coefficients. | Strong **hardware architectural comparator**: width cannot be justified using coefficient storage bits alone; reuse their cost categories, not their measured frequency or energy numbers as our own. |
| 7 | **Hong, Jeong & Jang, 2026**, *Snowball*, arXiv preprint. https://arxiv.org/abs/2601.21058 | Provides bit-plane decomposition of coupling coefficients, row/column memory organization and incremental local-field updates in a digital all-to-all Ising accelerator. | Existing incremental fields/bit-plane coupling precedents; our adjacency-list update mechanism is not novel. Published status here is preprint as of this check; do not imply peer-reviewed journal validation. |
| 8 | **Yang, Grimaldi, Bao et al., 2026**, *250 magnetic tunnel junctions-based probabilistic Ising machine*, Nature Communications. https://doi.org/10.1038/s41467-026-72020-8 | Experimental pulse-driven STT-MTJ probabilistic Ising processing with measured switching-response behavior, calibration and Ising/optimization application. | Key closest **device-platform precedent** and motivation for nominal sigmoid. Its reported switching curves do not establish our particular synthetic 100-device offset vector or +/-0.8/1.6 logit as measured post-calibration residuals. |
| 9 | **Yang, Bao, Humianto et al., 2026**, *A parallel magnetic tunnel junction-based probabilistic Ising processor for efficient quadratic optimization*, Nature Communications. https://doi.org/10.1038/s41467-026-71128-1 | 144 STT-MTJ tunable random sources, measured voltage-dependent switching curves and per-device slope/midpoint calibration; parallel quadratic optimization architecture. | Independently validates calibration as real implementation work; does not establish our simulated gain/offset distribution or bit-width rule. Their 4-microsecond pulses and voltage range belong to their device architecture, not a general p-bit spec. |
| 10 | **Iftakher et al., 2026**, *Intrinsic annealing in a hybrid memristor-magnetic tunnel junction Ising machine*, Nature Communications. https://doi.org/10.1038/s41467-026-71844-8 | Couples multi-level memristor J/MAC storage to stochastic SMTJ spins; demonstrates weighted Max-Cut and voltage-controlled intrinsic annealing. | Shows coupling storage and stochastic spin elements can be physically distinct. Their thermally fluctuating SMTJ and analog crossbar differ from our pulse-driven assumed response + digital J-codebook model. |
| 11 | **Duffee et al., 2025**, *An integrated-circuit-based probabilistic computer that uses voltage-controlled magnetic tunnel junctions as its entropy source*, Nature Electronics. https://doi.org/10.1038/s41928-025-01439-6 | CMOS ASIC plus voltage-controlled MTJ entropy, highlighting expensive input-control circuitry and a practical device/CMOS division. | Supports cost/physical-interface caution; not a measurement of the proposed FP6/INT6 coupling-interface hardware. |
| 12 | **Gibeault et al., 2024**, *Programmable electrical coupling between stochastic magnetic tunnel junctions*, experimental p-bit-coupling work. https://www.nist.gov/publications/programmable-electrical-coupling-between-stochastic-magnetic-tunnel-junctions | Demonstrates programmable electrical coupling between an SMTJ p-bit pair. | Coupled p-bits are a physical computing concept, not exclusively a software abstraction; pair-scale experiments do not establish our 100-spin processor performance. |
| 13 | **Camsari, Faria, Sutton & Datta, 2017**, *Stochastic p-Bits for Invertible Logic*, Physical Review X. https://doi.org/10.1103/PhysRevX.7.031014 | Foundational tunable stochastic bits and interconnection to support probabilistic logical correlations. | Establishes p-bit principles, not an argument for FP coefficient precision or pulse-STT population residuals. |
| 14 | **Borders et al., 2019**, *Integer factorization using stochastic magnetic tunnel junctions*, Nature. https://doi.org/10.1038/s41586-019-1557-9 | Experimental spintronic p-bits showing coupled optimization/factorization using nanoscale stochastic MTJs. | Physical p-bit precedent; different application/topology/device operation. Do not treat our high-barrier storage-MRAM cell as automatically identical to their stochastic device. |
| 15 | **Onizawa et al., 2026**, *A unified performance-cost landscape of parallel p-bit Ising machines based on update dynamics*, Scientific Reports. https://doi.org/10.1038/s41598-026-47285-0 | Simulates update dynamics, time multiplexing and precision of p-bit *input DACs* including 3–4-bit constraints. | Input-DAC precision is NOT matrix coefficient J precision. Their algorithmic behavioral p-bit model is supporting context, not measured device-specific residuals. |

**Specification (not a scientific experiment):** OCP Microscaling Formats (MX), v1.0, 2023: https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf . This supports element-layout definitions but not our source-MSE global scaling as an OCP standard. **Benchmark library (not proof of FP superiority):** https://biqmac.aau.at/biqmaclib.html .

### What the closest literature collectively precludes

Do not claim as new: the Ising J matrix-vector local field; p-bit probability functions; FP Ising computation; nonuniform/log coupling coding; digital fixed-point coupling memories; incremental local-field updates; device gain/offset models or compensation; significance of coupling errors for dynamics/ground state.

Our **potential narrower contribution**, subject to held-out confirmation and hardware bounds, is a reproducible same-bit FP/INT comparative design rule for a defined coupling-matrix codebook, with conditional STT-MRAM-inspired response stress, field/probability analysis and original-weight solution scoring. There may be additional prior art; do not describe this as the first ever such study.

## 3. Physical device interpretation: what is derived, what is measured, what is assumed

A measured switching-curve approximation can have the form

P_i(+1|V)=sigmoid( a_i (V - V50_i) ).

Assume a *nominal* field-to-voltage transformation

V = V50_0 + 2 beta(t) Hhat_i / a_0.

Substitution, without any experimental fitting, yields

P_i(+1)=sigmoid( (a_i/a_0) 2 beta(t) Hhat_i + a_i (V50_0 - V50_i) ).

Therefore g_i=a_i/a_0 has a *slope mismatch* interpretation, and
delta_i=a_i(V50_0 - V50_i) a *switching-midpoint mismatch in logit* interpretation. Their values are device- and calibration-dependent. The published 2026 STT-MTJ works support measured and calibratable switching curves, NOT our actual post-calibration distributions.

**Frozen E2 assumption:** use g_i=1 for offset-only, delta_i=d v_i for d=0, 0.8, 1.6; one persistent 100-spin v population generated from the existing E2 seed and shared across graph/format/seed pairs. The gain-only pilots use their separately frozen g_i=1+a u_i and zero offset. Unmeasured synthetic LOGIT ranges must not be converted directly into volts or described as device yield, PDK characterization or residual mismatch measurements. A single device population gives conditional Monte Carlo seed CIs, not a manufacturing variability CI.

**Physical caveat:** pulse-driven switching probabilities, independently fluctuating low-retention SMTJs, and MRAM bit-storage writes are distinct physical mechanisms. A real instrumented STT-MRAM p-bit interface would need verified pulse duration, reset/readout scheme, latency, voltage/temperature transfer, DAC range, update rate and calibration; none is established by these Python runs.

## 4. Three mathematical mechanisms, with what each can and cannot prove

### 4A. Matrix coefficient error is not solver energy/optimum preservation

For a fixed s, delta J = Jhat-J and

delta H_i(s)=sum_j delta J_ij s_j.

The represented Ising energy error for that same state is
delta E(s) = -sum_{i<j} delta J_ij s_i s_j.
Hence the deterministic upper bound:
|delta E(s)| <= sum_{i<j} |delta J_ij|.

For two configurations s and t, the error in their *energy difference* is at most 2*sum_{i<j}|delta J_ij|. Therefore, as an elementary sufficient (not necessary) preservation condition, if the exact gap from an optimum to **every nonoptimal state** is larger than 2*sum|delta J_ij|, the original optimum cannot be overtaken by quantization. That gap is unknown here; no 100-spin optimum-preservation certificate was calculated. Also, the preserved exact optimum would not guarantee a 50k-update stochastic solver finds it.

Source-MSE fitting measures expected squared coefficient distortion, not these energy-ordering gaps or sampled state visitation. The QUBO compression literature is a more rigorous lens for interpreting this limitation.

### 4B. Field distortion maps nonlinearly to one-step decision distortion

At fixed state, device offset and beta checkpoint, define

ell_i = 2 beta H_i + delta_i,  delta_ell_i = 2 beta delta H_i,

delta P_i = sigmoid(ell_i+delta_ell_i)-sigmoid(ell_i).

For small delta_ell, the first-order approximation is
delta P_i ≈ sigmoid(ell_i)*(1-sigmoid(ell_i))*delta_ell_i.
It is strongest near the switching midpoint ell=0 and weaker on saturated branches. Because the logistic derivative is bounded by 1/4,

|delta P_i| <= (1/4)|delta_ell_i| = beta |delta H_i|/2.

This means even RMS field error is insufficient to rank probability distortion across formats: *where* the error falls along the switching curve matters. It does NOT imply a lower-precision format with small mean |delta P| necessarily finds better final Max-Cut solutions.

### 4C. One-step probability mismatch has an exact paired-randomness meaning

For the SAME spin, state, beta, offset and independent uniform draw u~U[0,1],
the quantized and original heat-bath updates choose +1 iff u is below P_q/P_ref respectively. The probability that the two proposed updates disagree is EXACTLY

P(disagreement | s,i,beta,delta, shared u) = |P_q-P_ref|.

This is a powerful interpretation of the snapshot mean absolute |delta P| as a **state-conditioned one-attempt update disagreement rate**, if selected spins are averaged uniformly over those states and beta conditions. It is **NOT** a measured wrong-update count over the 50,000-step anneal. Once one update differs, states and later fields diverge. Nor is the reference P_ref itself the 'physical truth' under a nonzero synthetic offset: it is the *same-offset FP64-model comparator*.

## 5. Completed CAL evidence: four specific distinctions

The following outputs are transcribed from the user's completed NUS terminal results. Raw confidence intervals from E1/E2 were calculated by the NUS runners; this synthesis does not claim to have independently recomputed every CI from individual rows.

**Experimental integrity:** E1 original ideal=936 runs; FP64-only offset scout=240 new; offset primary=576 new; conditional FP8/INT8=192 new. Frozen local-field diagnostic evaluated 144 saved FP64-returned states over nine J representations and three static beta checkpoints (3,888 derived diagnostic rows; NOT independent trials). Tests and archival audits passed in the NUS console. M1 E1 ideal+offset references reused; no additional solver work was performed in the snapshot study.

**5A. Coupling distortion and probability distortion can rank formats differently.**
Dense CAL, d=1.6 LOGIT, beta multiplier 2.0, all formats evaluated on the same FP64 states:

| J representation | Relative RMS delta H | Mean abs delta P (same offset) | Existing solver original-cut gap |
|---|---:|---:|---:|
| ref64 | 0 | 0 | 5.030% |
| FP6 | 3.991% | 0.00384 | 4.892% |
| INT6 | 5.347% | 0.01369 | 5.666% |
| FP8 | 1.603% | 0.00181 | 5.363% |
| INT8 | 1.845% | 0.00640 | 5.208% |

INT8 has LESS field error than FP6, yet GREATER mean abs probability distortion on these sampled states. It is consistent with different field-error placement relative to sigmoid-sensitive locations, but this is a mechanism HYPOTHESIS: the terminal summary alone does not give spin-level field-margin histograms or paired-CI support.

**5B. Even smaller snapshot probability error does not certify better final quality.**
Here FP8 mean abs delta P=0.00181 is less than FP6=0.00384, yet its mean finite-budget final original-cut gap=5.363% exceeds FP6=4.892%. These quality figures arise from separate stochastic trajectories. Never read the rightmost column as a measured outcome of the common reference states: the snapshot uses FP64-returned states while low-bit quality comes from the separately frozen solver runs. The difference is descriptive, not proof of 'excess precision hurts'.

**5C. Severe offset can dominate absolute quality even without quantization.**
Sparse CAL original FP64 ideal mean gap=3.200%; with d=1.6 it was 5.447% and mean paired deterioration +2.247 pp, original scout paired 95% CI [+1.098,+3.337] pp. With d=1.6, INT8 field RMS discrepancy was only 0.457% and mean abs delta P=0.00094, yet mean original-cut gap remained 5.425%; even ref64 did not clearly satisfy a 5% absolute-quality CI upper bound. This is compatible with a response-limited finite-budget regime. It is not proof that increasing coefficient bits is useless in all nonideal conditions.

**5D. Direct differences are NOT response-by-format interactions.**
In the low-bit CAL primary study, sparse d=0.8 FP5-INT5 mean gap delta was +0.777 pp (nominal paired CI [+0.24,+1.32]), and dense d=1.6 FP6-INT6 was -0.775 pp (nominal paired CI [-1.48,-0.04]). These are exploratory direct paired comparisons among multiple tests. All 12 corresponding offset-induced difference-in-differences D intervals for 4/5/6 bits included zero, so the CAL data do not establish that offset *changes* the FP-minus-INT relative response. For 8 bits, inspect the saved full paired CSV before asserting inferential results; mean alone is not a CI.

## 6. Current conditional CAL design map (not a general physical design rule)

Frozen screens for each graph/format/response cell:
(A) 95% seed-bootstrap UPPER bound for absolute original-cut optimum gap <=5%.
(B) 95% matched-FP64 paired quantization-loss UPPER bound <=+1 percentage point.
Both must pass; the solver trial CI is conditional on ONE device realization.

| CAL graph and offset | Lowest tested eligible FP | Lowest tested eligible INT | Caveat |
|---|---|---|---|
| Sparse d=0.8 | FP4 | INT5 | FP8 is NOT eligible under the paired +1pp upper-CI screen; nonmonotone statuses are genuine under the frozen protocol |
| Sparse d=1.6 | Not established | Not established | Absolute quality uncertified even for FP64 |
| Dense d=0.8 | Not established | Not established | Absolute quality commonly uncertain against 5% |
| Dense d=1.6 | Not established | Not established | No tested 4/5/6/8-bit representation clearly passed both frozen screens |

**Do not conflate** noneligible (failure to certify both gates) with a demonstrated original-cut failure regime (>7.5% gap CI lower bound); do not infer that all bit-widths have proven equal; do not treat the CAL-selected map as validated design guidance for new graphs.

## 7. What can be concluded about causality now?

**Supported by code and mathematical algebra:**
- Each original source edge is symmetrically represented in Jhat and contributes to the correct H = Jhat*s in the behavioral software.
- The frozen software computes quantization-induced field and one-step probability differences on common FP64-returned states.
- The exact paired-randomness update disagreement identity and sigmoid derivative bound above.

**Supported descriptively by completed CAL experiments:**
- Actual stochastic solution quality varies with format, graph and assumed offset level; more coefficient bits are not guaranteed to improve finite-budget Max-Cut quality monotonically.
- In the selected dense CAL snapshots, FP6 gives smaller static mean abs delta P than INT6.
- Under high assumed offset, even full-precision J cannot be certified to meet the chosen absolute quality goal in some CAL conditions.

**Not supported:**
- A demonstrated statistically significant gain/offset-by-format interaction, universal FP advantage, production STT-MRAM parameter range, chip-level energy/area saving, global optimum-preservation certificate, or causal explanation of trajectories solely from terminal snapshot metrics.
- A well-calibrated relation between coefficient bits, finite-precision field accumulator, and delivered pulse/input precision.

## 8. Mechanism-focused research pause: analyze, do not rerun

Three questions to answer using the existing papers and archived numeric outputs, *without editing original experiment artifacts*:

**Representation.** Why does FP6 E3M2 versus signed INT6 place representation errors differently in the 4,950-coefficient dense J versus the 200-edge sparse J? Inspect the already available codebook, global scale, relative coefficient error, zeroed-edge rate, signed weight histogram and saturation/clipping *as definitions and archived metrics*. Avoid inventing new FP exponent layouts, per-row scales or learned problem-dependent reweighting.

**Response.** Which measured switching-curve properties actually correspond to gain and logit offset in the cited STT-MTJ experiments? Clearly distinguish measured pre-/post-calibration device fit, representative sigmoid curve, and our fixed synthetic E2 population. The 2025 Zhang compensation paper is a mandatory novelty comparator; their numerical device compensation is outside our current frozen experiment.

**Mechanism.** Interpret the existing static delta H/delta P alongside original-cut gaps, emphasizing the mismatch between a single common-reference state and full stochastic trajectories. Explain the role of sigmoid sensitivity near zero using the exact one-step disagreement probability, not a fake estimate of wrong flips over 50k steps. The 3,888 derived rows share seeds/devices/graphs and are NOT 3,888 independent experiments.

This synthesis is the deliverable for this research pause. Further code, even if it only produces more plots, must answer a specific unaddressed mechanism question before it becomes worthwhile.

## 9. Proposed falsifiable held-out predictions — NOT YET EXECUTED

Do NOT inspect the two original held-out instances while using this section to set a prediction. This memorandum is a proposal for a fixed validation plan, not authorization to start runs. Held-out instance labels are the already locked ising2.5-100_7777 (dense, graph index 4) and t2g10_7777 (sparse, graph index 3), with original seed rule 20261201+100000*graph_index+k, k=0..23.

**Prediction H1 (primary mechanism, dense).**
At original-graph beta multiplier 2.0 on matched FP64-returned state snapshots, for EACH held-out dense condition d=0.8 and d=1.6 considered separately, the mean over 24 paired seeds and spins of absolute same-offset probability distortion should be lower for FP6 than for INT6: mean(|delta P_FP6| - |delta P_INT6|)<0. This is **predicted from dense CAL** but may fail if coefficient/state distributions differ. Use per-seed paired differences and seed-level bootstrap CI. A negative point estimate supports the directional pattern; a 95% CI upper below zero provides conditional seed-level evidence; a CI spanning zero remains inconclusive.

**Prediction H2 (solver-quality distinction).**
Even when FP6 has lower static probability distortion than INT6 on held-out dense, it need not have a smaller absolute gap to the original optimum. Report the paired original-gap FP6-INT6 difference and its CI under each d independently, and do not treat H1 confirmation as H2 confirmation. No asserted direction is pre-registered for H2; it is an explicit discriminating observation, not a disguised claim of an FP win.

**Prediction H3 (sparse/quality robustness).**
Apply exactly the already frozen two-screen eligibility rule to the held-out sparse graph without using its results to adjust scale-search policy, beta, response levels or thresholds. Check whether any low-bit representation is certified at d=0.8 and whether no representation is certified at d=1.6; report deviations openly. The CAL sparse 'FP4 vs INT5 lowest width' map is an empirical hypothesis, NOT guaranteed or universally expected. This result informs how transferable the CAL rule is over these TWO additional graphs only.

Before any held-out run: freeze graph hashes/optimum convention, exact family/width pool, static-snapshot definition and beta multiplier, common seeds/population, whether all 8-bit cells or conditional cells will be tested, plus multiple-testing caveat. The 2025–2026 literature above must not be used to revise the observed CAL quality thresholds.

## 10. Supporting-cost and CA2 reporting boundaries

A defensible cost discussion uses the same problem size/connectivity and matches at least coefficient storage, one-copy symmetry assumptions, scale metadata, coefficient decoding, local-field updates, accumulator precision, read bandwidth/ports, p-bit input interface and annealing control. **Do not combine nominal software storage-bit counts with unrelated FP/INT RTL row areas to invent whole-chip TTS/W.** Historical Sky130 row/RTL and bit-true datapath results are supporting blocks only.

Suggested CA2 scientific narrative:
1. **Motivation:** J is a precision- and bandwidth-sensitive interface between optimization problem and stochastic spins; both width and response nonideality matter (Volpe; Hizzani; Yang; Iftakher).
2. **Gap:** Prior work already studies FP Ising arithmetic, log quantization, coupling errors and device compensation. What remains to test on the *specific frozen comparison* is whether FP/INT global scaled J codebooks exhibit reproducible conditional local-field/decision fidelity and task-quality differences under a constrained STT-inspired response model.
3. **Model:** Define Jhat, original-cut scoring, ideal accumulator and interface, and derived physical interpretation of assumed gain/offset.
4. **Existing evidence:** State the four CAL findings and uncertainty/counterexamples in sections 5–6. The snapshot is an explanatory analysis, not a trajectory observation.
5. **Next gate:** held-out H1/H2/H3 after the research pause, followed by bounded hardware cost accounting. Negative or inconclusive findings are valid FYP outcomes.

### Decision log

- Target: coupling-matrix numerical representation, local-field sensitivity, stochastic p-bit response, finite-budget weighted Max-Cut quality.
- Evidence: authoritative external literature + actual frozen repository logic + user-returned NUS CAL outputs.
- Hypothesis: lower static probability distortion may be representation- and graph-specific; neither universal precision knee nor robust FP supremacy is pre-assumed.
- Minimal test NOW: none; this is a literature and mechanism synthesis only.
- Expected observable LATER: independent held-out paired delta-P difference, paired final-gap difference, two-screen certification, conditional seed CIs.
- Failure/stop condition: H1 sign reverses or CI remains unresolved; quality does not generalize; prior art makes narrower contribution non-novel. Report the result, do not add format/stress axes to force confirmation.
- FYP alignment: direct J --> H --> P --> Max-Cut mechanism; physical claims explicitly E2-assumed.
- Decision: **STOP NEW CAL WORK; RESEARCH SYNTHESIS COMPLETE; HELD-OUT NOT STARTED.**

---

## Sources and verification caveat

All 15 works and two supplementary sources above are direct publisher/author/NIST/preprint or standards/library URLs, not citations invented from memory. Source scope is checked against abstracts/full text where openly accessible. This memorandum does not claim a systematic exhaustive literature review, detailed verification of all numerical hardware implementation claims, independent rebootstrap from the raw NUS files, or direct extraction of per-device post-calibration curves. Publication status for Snowball is described as a preprint; the OCP MX document is a technical specification. Any figures from the external papers should be reused in CA2 only with source attribution and appropriate usage rights.
