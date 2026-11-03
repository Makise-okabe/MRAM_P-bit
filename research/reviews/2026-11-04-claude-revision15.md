# Review of Claude revision 15

4 November 2026 (Singapore). Initial source: the user's pasted revision-15 excerpt and
[artifact link](https://claude.ai/artifact/Mt5Ay99Wcw56szxxfJQ4n9). The artifact could not
be retrieved. The subsequently uploaded 48-page PDF was checked against the earlier
46-page version; see the receipt below. The simulator, graph list, seeds and raw outcomes
were not supplied or independently reproduced.

## Accepted direction and evidence boundary

The shared organizing question is useful: how do physical read organization and error
persistence affect a workload's decisions? Mapping is the main candidate under
development; Ising persistence is a conditional diagnostic and possible companion.
One common read-error model does not by itself establish a unified two-workload method.
An Ising chapter needs a surviving question, a useful result and supervisory/scope fit.
No three-to-four-week chapter commitment or fifty-graph campaign follows from this review.

The supplied neural and Ising numbers are external, unreproduced illustrative-model
claims using a retired small-group-like model. They are not calibration, validation or
motivation evidence for the fresh physical 256x256 target. No claimed neural outcome is
copied into the active report. The Ising success percentages motivate audit questions,
not a target-array conclusion or a proven novelty claim.

The excerpt reports ideal/perturbed success rates of 58%, 42% and 17%, and fresh versus
frozen rates of 25% versus 42%, with only 24 runs mentioned for the last comparison.
The population of graphs, independent chips, paired starts and certified targets is
unspecified. These rounded external values are retained here solely to identify what
needs checking, not as our experimental results.

## Primary-source checks

- Snowball, arXiv:2601.21058v1, Section IV-B.2 explicitly initializes local fields using
  row-major bit planes and incrementally updates them using column-major bit planes
  after a spin flip. It is a digital FPGA implementation. The mathematical incremental
  update and duplicated access layouts are established comparators, not proposed MRAM
  inventions. [Primary method](https://arxiv.org/html/2601.21058v1).
- Volpe et al., DOI 10.1002/aisy.70521, Section 3.1 describes initialized fields updated
  whenever a spin flips, and Section 3.2 discusses pipelined field updates. Method
  passages were inspected; no claim to reproduce the complete architecture is made.
  [Publisher](https://advanced.onlinelibrary.wiley.com/doi/10.1002/aisy.70521).
- Hizzani et al., DOI 10.1038/s44335-026-00082-4, the primary indexed abstract,
  introduction and method-summary passages describe programming-error models, changes
  in the landscape and wrong spin updates, hardware measurements and mitigations.
  Direct full-text retrieval remains blocked; a full-read claim or exact temporal-noise
  equivalence verdict would be unsupported.
  [Publisher](https://www.nature.com/articles/s44335-026-00082-4).

The statement that VARA and DIB-CIM architects assume equally reliable reads is too broad.
DIB-CIM explicitly addresses the activated-WL/read-margin trade-off and input-bit
significance. Our gap must survive its actual supported policies, not an accuracy-blind
straw baseline. Likewise, inference estimation and calibration are occupied families,
not proof that every precise new method in those families is impossible.

## Essential separation: three different error experiments

1. **Physical persistence:** keep manufacturing variation fixed per chip and add a
   separately justified temporal read-noise process. Its magnitude, spectrum/correlation,
   read interval and calibration must come from the target conditions.
2. **Matched-marginal counterfactual:** deliberately redraw a post-calibration error
   realization to remove persistence while retaining the same fixed-state marginal law.
   This is a diagnostic; it does not turn manufacturing spread into measured read noise.
3. **Cached incremental arithmetic:** noisy coefficient reads update stored local fields.
   Repeated update errors can accumulate. This is a different operator from recomputing
   a complete noisy local field every time.

Holding an average count-error rate equal does not match error magnitude, bias, bit
significance, state dependence, calibration information or temporal correlation. Audit
the conditional error law on fixed probe states chosen independently of chip variation.
On an adaptive trajectory, state visitation can depend on frozen variation, so even
matched interventional fixed-state marginals need not produce equal observed read rates.

## Why fresh noise might look worse: an exact cache control

For f=J*s, changing spin k by delta_s gives f'=f+J[:,k]*delta_s. This is a standard
identity. With a fixed consistent matrix J_tilde and a consistent initialization,
incremental updates telescope and equal J_tilde*s, even after many flips (absent
rounding/overflow). Symmetry is additionally needed to identify the conventional Ising
Hamiltonian; a state-dependent nonlinear field need not be any fixed J_tilde*s.

If a coefficient read instead has fresh error eta_t, one flip followed by its reversal
returns the spins to their original state but leaves the cache residual

    2*s_k_old*(eta_2-eta_1).

For independent zero-mean errors with variance sigma^2, its variance is 8*sigma^2.
For an identical frozen coefficient error both times, the residual is zero. E09A
checks this with exact finite enumeration of unit-sign errors, not a hardware-noise
model or a solver-success experiment. It provides an immediate diagnostic for cache
drift before attributing an outcome to a temperature floor.

Run full-recomputation, incremental-update, exact-refresh and cache-reset controls.
If the difference follows accumulated update error or a reset policy, the interpretation
must reflect that. Reusing an erroneous initial field with otherwise exact coefficient
updates is another distinct arm and must not be silently merged with the others.

Even for full recomputation, additive local-field noise is not generally exactly a new
temperature. For heat-bath p_plus=sigmoid(2*beta*(h+eta)), increasing beta indefinitely
leaves P(h+eta>0), with half the mass at a tie. A Gaussian eta gives a probit curve,
not generally one logistic curve for all h. This mathematical limit is a hypothesis
diagnostic, not evidence that the supplied Ising runs reached such a regime.

## Strong baseline and physical-access boundary

An incremental implementation needs the affected coupling column, initialization,
enough cache precision, and any refreshes. A transposed or duplicated layout consumes
capacity/routing. When the coefficients are stored as binary MTJs, fetching individual
coupling bits with ordinary digital sensing can avoid repeated many-row analog sums.
Its error law and cost cannot be borrowed from a full-field analog count read.

Compare exact digital full recomputation, exact incremental cached fields, quantized
digital couplings, calibrated analog full recomputation and a feasible incremental
MRAM-backed implementation where available. Count initial field generation, transpose/
duplicate storage, every coupling fetch, cache updates, control and refresh. Our E09A
checks the arithmetic baseline only, not any hardware architecture or Snowball's engine.

## Target and statistics corrections

Use exact optima for the first small graphs. A best-observed cut is not automatically
the maximum cut. For larger benchmark graphs, distinguish a certified optimum, a
published best-known target and the best found by the present solver. Score the true
graph Hamiltonian, not an accidentally perturbed objective.

Record graph, chip, solver restart, update order and random-stream identities separately.
The independent units are not all individual reads or spin updates. Pair policies on
graphs/chips and common random inputs where applicable, then use paired/hierarchical
uncertainty. A fixed chip can be restarted without becoming a new independent chip.

At fixed run duration tau and success probability p, the continuous restart TTS proxy
for 99% success is tau*log(0.01)/log(1-p); an actual whole-run budget uses the ceiling.
Using the rounded quoted values, 58% to 17% implies a proxy ratio of about 4.66, whereas
42% to 17% implies about 2.92. The quoted 'three times' needs its reference and run
duration specified. These are algebraic interpretations of external percentages, not
new TTS measurements. Compute chip-conditional TTS before summarizing a chip population;
plugging a pooled mean success rate into this nonlinear formula changes its meaning.

## Decision

Adopt the [bounded queue](../04_screening_queue.md). E09A exact software controls are
implemented and checked. E09B audits conditional errors, persistence and cache drift
after target response/temporal-noise validation; E09C is a small exact-target pilot
before any broad graph sweep. The inference mapper remains the main development
candidate, and Ising remains eligible as an alternative or a gated companion. Neither
the toy success figures nor a shared story supplies a novelty pass.

## Follow-up: uploaded 48-page version

The attached `MRAM CIM — Field Survey and Self-Evaluated Research Direction (3).pdf`
now supplies the revision-15 text directly. Its [source receipt](2026-11-04-claude-revision15.source.json)
records the exact hash and comparison. Extracted all 48 pages, inspected every changed
text span against the previously reviewed 46-page PDF, and rendered pages 1-2 to check
the new tables. The substantive addition is the revision-15 synthesis already pasted
by the user. The earlier revisions and paper register are retained; most remaining
text differences reflect repagination and table extraction order. No new simulator
implementation, graph list, seeds or raw results are supplied by this PDF.

The review decision is unchanged. In particular, page 3's proposal to assemble a logical
256x256 array from the retired small-group model does not meet the physical target.
The old tables must not enter E01-E03 target calibration or validation. Page 2's large
Ising campaign is deferred until the conditional-error and field-operator checks pass.
The fresh-versus-frozen interpretation still needs separate physical temporal-noise,
matched-law counterfactual and cache-drift controls. This receipt adds source access,
not experimental evidence, a novelty verdict or a new core selection.
