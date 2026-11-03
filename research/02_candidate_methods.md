# Candidate methods: equal-depth research cards

These are explicit development targets. None is certified new or demonstrated effective.
Source IDs refer to [the evidence register](literature/evidence.json).

## F1. Event-aware inference-failure estimation

**Problem/value.** Repeated full perturbed-network evaluations can make new operating
points expensive to assess. A useful estimator predicts the requested failure probability
or design decision at less total computation, including characterization and setup.

**Candidate procedure.** Represent dominant shared, persistent circuit parameters as z;
keep remaining variation conditional on z. Partition important z directions at actual ADC
decoding transitions, integrate tractable pieces, and sample residual uncertainty with
variance reduction. Reuse compatible boundaries across operating-point distributions.
Keep each chip assignment across all reads. Evaluate full-network consequences where
linearization is insufficient. This is conditional integration, not new mathematics.

For signed bit planes, delta_y = sum_b a_b e_b. Its variance contains
sum_b a_b^2 Var(e_b) + 2 sum_{b<c} a_b a_c Cov(e_b,e_c). A count-error marginal cannot
determine this covariance or failure probability. The proposed compression must retain
enough of the joint structure to predict a useful decision.

**Closest/difference to establish.** S08 calibrated MRAM macro models; S09 precision
bounds; S10 single-bit floating-point fault analysis; S11 region-probability bounds.
S22 is an inaccessible submission warning, not proof of method equivalence. The residual
claim is a specific circuit-derived representation and a demonstrated accuracy/cost gain.

**Physical case.** A shared offset or cell assignment can repeatedly move correlated
bit-plane reads across decoding edges. Establish it in the target model, not by assuming
an arbitrary heavy-tailed distribution.

**First comparison / falsifier.** E06: calibrated simulation with randomized quasi-Monte
Carlo or stratification at equal error/confidence; region verification when compatible.
Measure setup and amortization across new operating points. Stop if boundary growth or
model-fitting overhead eliminates the gain. A Gaussian-only win does not pass.

## F2. Spatially informed polarity or encoding

**Problem/value.** Exact equivalent computations can impose different electrical loads.
For 0/1 bit planes, W^T x = K - W^T(1-x), K_j=sum_i W_ij. Adapt decoding separately for
XNOR/differential circuits. Ordinary minority inversion is a baseline, not the invention.

**Candidate derivation.** If a validated first-order electrical proxy is J(a)=a^T H a
with symmetric H, then J(x)-J(1-x)=(2x-1)^T H 1. Precompute lambda=H1 and choose polarity
with one weighted input sum. The formula is exact for that proxy, not a proof of lower
decoded error or energy. H may depend on weights, geometry and operating point; an
aggregate objective can hide a weak column.

**Closest/difference to establish.** S20 complement disclosure, S21 activity-based bus
inversion, S06 mapping/calibration and S07 fault-aware mapping. Position-specific selection
needs an encoding-focused comparison. Lin's use of 'weight' means number of ones and
does not establish the position-weighted criterion.

**Physical case.** Equal-popcount masks activate different shared current paths. Obtain
the preferred polarity from paired target circuit reads, then test the cheap predictor on
held-out patterns. Never compute the exact requested dot product digitally for a supposedly
free control decision.

**First comparison / falsifier.** E04 versus direct calibrated read, minority inversion,
load-balanced mapping and an offline oracle polarity. Count selection, metadata and
subtraction. K alone uses 9x256=2,304 bits per binary array. Stop if a simple baseline
matches the gain or the predictor improves only its own proxy.

The conditional count support L=1+min(m,256-m,K,256-K) is invariant to complementation.
An automatic ADC-bit reduction therefore cannot be inferred from minority activation.

## F3. Reliability-constrained mapping and readout

**Problem/value.** Grouping may expose zero reads while concentrating the remaining
electrical load. That tension is a hypothesis about the target, not an observed result.

**Analytical starting point.** With fixed total activity M and C nonempty reads,
mean activity per executed read is M/C. This identity proves concentration, not a
reliability penalty. For a simplified count-error cost c(m), combining two loads changes
expected cost by c(a+b)-c(a)-c(b). If c(m)=alpha*m, expected total count-error cost is
unchanged; a convex cost can penalize concentration. Actual cost also depends on weights,
position, calibration, time and the joint errors. Task error needs its own propagation.

**Candidate procedure.** Initialize from faithful CAR and balanced mappings. Score whole
calibration traces using a validated target response model and total resource model.
For fixed architecture/readout choices, accept bounded cross-group row swaps that lower
cost while meeting a predeclared reconstructed-error constraint. Freeze mapping and
readout; evaluate independent inputs and chips. No global-optimality claim.

**Closest/difference to establish.** S01 already groups co-zero dimensions; S02 adjusts
input blocks and ADC precision; S03/S28 exploit input sparsity in conversion; S05 tunes
parallelism/weight splitting. S29 adds a strong MRAM correction comparator. Generic
reliability constraints plus row swapping are insufficient as an algorithmic novelty claim.
The intended contribution is a derived circuit-dependent grouping rule and useful method.

**First comparison / falsifier.** E01 structure, E02 physics, E03 paired mapping comparison.
Compare retuned CAR, original order, random, zero-rate sorting, quiet-then-balanced,
load-balanced plus calibration/SEC-style correction and adaptive blocks. Remove/pack
known permanently inactive dimensions as a control. Stop if there is no relevant conflict
or a simpler tuned comparator reaches the same Pareto curve.

Logical batches retain the physical wiring. Isolated sectors require actual hardware.
A 256 x 256 matrix assembled from small-group error tables is not target validation.

**4 November refinement.** The [decoded-covariance candidate](novelty/2026-11-04-covariance-mapping.md)
specifies a narrower F3 mechanism and an offline pair-moment score. A constructed calibrated
example has identical read counts, activities and marginal error laws but different
reconstructed MSE; its continuous-readout control is invariant. This mathematical check
does not establish target benefit or a novelty pass. The general mapper is prospective.

## F4. Decision-directed neural refinement

**Problem/value.** Full arithmetic precision can be unnecessary for a stable class decision.
Begin with the final classifier so that computing bounds does not require a whole second
network execution. Savings may then be limited by that layer's energy share.

**Candidate procedure.** Compute coarse final scores and validated intervals [l_j,u_j].
Accept class c only if l_c > max_{j!=c} u_j; otherwise refine contributing bit planes or
flagged reads under a fixed schedule. Bounds include quantization, omitted terms and the
declared hardware error envelope. Statistical envelopes need an explicit failure budget
valid under adaptive refinement; an ordinary repeatedly queried confidence interval is
not a deterministic guarantee. The reference is the full clean quantized computation.

**Closest/difference to establish.** S13 speculative slicing/recovery, S14 double-reference
recompute, S12 mixed precision, S30 confidence early stopping. S30's formal tail bound and
normalization require independent checking before reuse. A distinct low-cost analog-MRAM
bound/implementation and total-cost gain are needed, not the argmax interval test alone.

**First comparison / falsifier.** E05 against best fixed precision, per-layer mixed
precision, activity-based conversion and detector/recompute. Count bound logic, state,
repeated array excitation and fallback. Stop if bounds are too loose, most operations
refine, or overhead exceeds saved work. This remains a competing core topic.

## F5. Analog-digital-hybrid crossover

**Problem/value.** Determine which permitted computation mode is cheaper at fixed useful
precision, reliability and throughput on the target macro.

**Candidate procedure.** Characterize E_A(m,R,B,t,z) and E_D(m,z), including normal readout,
ADC, data movement, additions and control. Derive where E_A<E_D subject to quality,
latency and area constraints, then implement a small feasible mode-selection table or
controller if the architecture supports both. z denotes a declared calibration/chip class.

**Closest/difference to establish.** S05 optimization, S13 arithmetic tradeoffs, S15/S16
precision and ADC cost modelling, S17 digital MRAM and S29 correction. A predictive,
validated circuit-specific rule or deployable hybrid is needed beyond plotting sweeps.

**Physical case.** Conversion overhead can dominate one regime, while repeated readout
or digital accumulation dominates another. Use actual permitted circuits and scheduling;
do not switch modes for free in a software model.

**First comparison / falsifier.** E07 best fixed analog, fixed digital and simple static
hybrid under matched constraints. Use model uncertainty sensitivity before new peripheral
design. Stop if one simple mode dominates or extra periphery removes the crossover benefit.

## F6. Information limit and minimal extra observable

**Problem/value.** Identify when extra quantizer resolution helps and when the available
analog observable cannot reliably identify the count after permitted calibration.

**Candidate derivation/procedure.** Condition class densities f_k(v) on metadata available
to the readout and compute the Bayes error floor 1-integral max_k pi_k*f_k(v) dv. This
identity is established decision theory, not the contribution. Derive a useful target-
circuit separation/identifiability condition, then choose a second sample time, reference
or read configuration only if it provides independent information at acceptable cost.
Do not give the controller true k as metadata; that would solve the requested operation.

**Closest/difference to establish.** S15 intrinsic precision limits, S08/S29 calibration,
S14 detection. Multi-read load identification must first specify identifiable unknowns;
an extra read need not resolve cell mismatch or an unknown bias.

**First comparison / falsifier.** E08 optimized references/decoding, increased ADC precision,
simple calibration and one additional observable. Test held-out physical cases. Stop if
there is no relevant ambiguity or a cheaper baseline resolves it. A negative overlap
screen alone is not the desired new method contribution.

## F7. Ising field persistence, organization and refinement

### F7a. Conditional persistence and field-operator diagnostic

Following the user's revision-15 discussion, retain D17 as a bounded diagnostic and
possible alternative/companion route. It first distinguishes fixed manufacturing
variation, physically justified temporal read noise, a matched-law decorrelation control
and drift in incrementally cached fields. Matching average read-error rates is not
sufficient. Full-field analog summation and ordinary incremental binary-coupling reads
are distinct physical operators and require separate cost/error models.

E09A's exact references are implemented and verified; E09B/C wait for the target kernel.
Incremental updates are prior art [S32,S33]; generic coupling-error sensitivity is covered
by S18. No original Ising contribution has been established. A companion chapter requires
a surviving specific question, a transferable mechanism/method and scope agreement.
See the [queue](04_screening_queue.md) and [source review](reviews/2026-11-04-claude-revision15.md).

### F7b. Decision-directed refinement reserve

**Problem/value.** Reduce local-field read work while preserving a specified stochastic
update. Stable MRAM stores couplings; a digital random generator can supply randomness.
A storage MTJ is not automatically an appropriate stochastic p-bit.

**Candidate procedure.** For a monotone p(h), draw one u. Given valid [L,U], commit '+'
if u<p(L), '-' if u>=p(U), otherwise refine while retaining u. Fix update order,
temperature and randomness when checking exact decisions. A noisy circuit needs a valid
envelope or an explicitly controlled transition-error budget. More ADC bits cannot repair
an unknown persistent bias; digital fallback must include real cost.

**Closest/difference to establish.** S18 device precision in analog optimization and S19
sampling-time/precision schedules. Exact/lazy sampling has prior mathematical literature;
the separate algorithmic comparison is incomplete. The update test is not claimed new.

**First comparison / falsifier.** E09 exact reference, best fixed precision, scheduled
precision and simple field heuristics, matched solver quality/transition error. Count
RNG, interval calculation and fallback. Stop if intervals require nearly full work.
Proceed as a separate application only if it matches supervisory and project scope.
It may alternatively form a gated companion if the same surviving method transfers;
a shared noise model or another sensitivity plot alone is insufficient.
