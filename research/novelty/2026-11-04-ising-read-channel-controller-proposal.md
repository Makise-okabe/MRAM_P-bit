# Ising brainstorming: compiling MRAM reads into stochastic decisions

Date: 4 November 2026 (Singapore).
Status: **research proposal and mathematical design, not a selected topic, original-method certification, target simulation, or hardware performance result.**
This develops H3 within the existing Ising investigation. It does not create another top-level FYP direction.

## Immediate division of work

The assistant handles candidate derivations, closest-method checks, software prototypes, strong-baseline comparisons and the evolving contribution statement. The student executes the NUS circuit experiments and supplies their outputs, checks the physical assumptions and owns the final research decisions and explanation. Algorithm discovery need not wait for full 256x256 extraction.

At the latest inspected main commit, the E11C supervisor brief reports four successful student-executed model-only DC cases, with distinct fixed-resistance states. It is unnecessary to repeat the model-interface search to begin this brainstorming. These static models can support an initial access-device/interconnect read study. They cannot establish switching, magnetic read disturb, or temporal MTJ noise. Digital logic can supply the Ising randomness; a stochastic MTJ is not required for the proposed stable-coupling-storage architecture.

The next useful electrical input is a small, complete access-transistor + MTJ read operation with a defined sense interface, programmed states, selected-row masks and waveform/current output. E11C does not yet supply its error/cost channel. Existing retired electrical results remain excluded.

## The candidate question

Can a small controller, compiled from a calibrated MRAM readout channel, reproduce a requested stochastic spin-update law with less total sensing work than accurate digital incremental fields and strong existing correction/refinement policies?

The proposed artifact is:
1. a physically grounded read-channel representation;
2. a test of which requested update probabilities are achievable with the available read information;
3. a compact decision/additional-read controller compiled offline under an explicit cost and transition-error budget.

Correcting a stochastic transition probability is a different objective from reproducing the exact spin decision for every shared uniform draw. Equal conditional update probabilities do not imply identical coupled trajectories. Success on Max-Cut must still be measured against the original graph objective and tuned solver schedules.

## Why the obvious version is insufficient

Noise-corrected Monte Carlo is established. Ceperley and Dewing's penalty method modifies Metropolis acceptance for Gaussian energy-estimation noise. Seita et al. correct noisy Barker acceptance using an additive correction distribution. Ordinary sigmoid/temperature/offset calibration and arbitrary one-read lookup tables are strong alternatives. A linear program, a lookup table, and basic noise compensation are not novelty claims.

The possible residual contribution is an economical compilation/control procedure for *quantized, context-dependent MRAM observations*, with physically valid joint read behavior under persistent device variation. It must make useful read decisions beyond tuned one-read LUT calibration, standard decision refinement and generic channel-aware sequential policies. If it merely reproduces one of those policies, retire it as a core contribution.

## A precise single-read formulation

For a sequential heat-bath update at known inverse temperature beta,

    p_beta(h) = (1 + tanh(beta*h))/2.

Let theta identify a calibration case: its true local field h_theta, chip, programmed couplings, input mask and relevant history. Let c be a cheap runtime-observable context, such as the selected read mode or bounded input-mask features. Do not allow c to contain an exact local field calculated digitally for free.

For the first read, let Q_theta(z) be the conditional probability of ADC code z. An offline table q_c,beta(z) in [0,1] specifies the probability of choosing spin +1 after code z. The realized conditional probability is

    p_real(theta) = sum_z Q_theta(z) q_c,beta(z).

A minimax linear program minimizes epsilon subject to

    |p_real(theta) - p_beta(h_theta)| <= epsilon
    0 <= q_c,beta(z) <= 1

for the declared cases sharing context c. At runtime, the table and a digital random draw implement the update. The unknown true field is used only as paid calibration/validation ground truth.

This is a candidate synthesis building block, not an original mathematical technique.

## An information-loss check

For two cases theta and phi that use the same decoder context,

    |p_real(theta)-p_real(phi)| <= TV(Q_theta,Q_phi),

where TV(P,Q)=0.5 sum_z |P(z)-Q(z)|.

Therefore exact matching requires the target probability difference to be no greater than the distinguishability of the read distributions. With uniform approximation error epsilon, a necessary condition is

    |p_beta(h_theta)-p_beta(h_phi)| <= TV(Q_theta,Q_phi) + 2*epsilon.

If two different fields produce identical observations and require different update probabilities, no single-read table can fix that aliasing. More information, another legal read operation, a relaxed transition-error target, or a different operating point is required.

This elementary inequality is a standard information-processing argument. A potential FYP contribution would be the physically validated, useful design rule and controller it supports, not claiming this inequality as newly invented.

## A concrete two-stage controller

Allow at most one additional, physically supported read. It could be a later sample of the same excitation, a different reference, or a legal alternative input encoding; its availability and incremental cost must first be demonstrated. Do not assume an arbitrary read can remove persistent error.

For first code z, compile:
- a_z: probability of immediately choosing +1;
- r_z: probability of requesting the additional read;
- 1-a_z-r_z: probability of immediately choosing -1.

For second code v, use t_zv = r_z times the probability of choosing +1 on continuation. Linear constraints are

    a_z >= 0, r_z >= 0, a_z+r_z <= 1,
    0 <= t_zv <= r_z.

Given the physically conditional joint distribution Q_theta(z,v),

    p_real(theta)
      = sum_z Q_theta(z) a_z
        + sum_zv Q_theta(z,v) t_zv.

Match the requested transition probabilities within a declared error budget while minimizing expected additional-read cost, using a CAL-only case distribution or an explicitly defined worst-case cost objective. Include LUT storage/access, RNG, mode selection, input transformation, ADC conversion and calibration overhead. For a later sample, charge the incremental held-bias time rather than double-counting the entire read.

At runtime the controller sees c, beta, z and, on continuation, v. It does not see theta, the true field, chip-error realization or a cost-free reference calculation.

The LP permits practical implementation and explicit infeasibility tests. It does not by itself establish a new optimal-stopping algorithm. Compare against strong channel-aware sequential baselines, not only a naive threshold.

## Persistent-error requirement

Never estimate Q across chips and silently use that population average as the conditional observation law during a fixed-chip adaptive solver trajectory.

A claimed exact kernel needs valid conditional laws at the operating chip/state/history, or a justified robust envelope covering them. A finite calibration set supplies tested coverage, not a universal guarantee over unseen spin states.

Repeated identical reads of deterministic fixed errors add no independent information. The joint Q(z,v) must preserve that fact. If the present MTJ model is static and device/readout temporal noise is absent, use deterministic state-dependent responses and declared chip variation; do not invent fresh Gaussian noise for every read.

## Mathematical checks actually performed in this brainstorming

Only finite-channel algebra was checked locally; no Spectre or Ising success experiment was introduced.

A two-state binary-symmetric observation channel with crossover 0.1 and requested probabilities (0.2,0.8) admits decoder probabilities (0.125,0.875). An ordinary adjusted-temperature decoder gives the same result. Thus the simple symmetric example establishes no distinct method advantage.

On that channel, requested probabilities (0.05,0.95) are infeasible with one read. Two cases with identical code distributions but requested probabilities (0.2,0.8) are also infeasible. SciPy linear-program feasibility checks agreed with these algebraic conclusions.

These controls explicitly expose both a baseline equivalence and an information limit. They are not favorable MRAM toy performance results.

## Closest-work register and the difference still to establish

| Work | Established contribution | Required distinction |
|---|---|---|
| Ceperley & Dewing, 1999, penalty method | Exact noisy-energy Metropolis sampling under stated Gaussian assumptions | Finite quantized MRAM channel, conditional context/persistence, legal read actions and complete hardware cost |
| Seita et al., UAI 2017 | Barker acceptance correction for noisy minibatch statistics, including a precomputed correction distribution | Demonstrated benefit beyond an applicable noise-correction adaptation; non-Gaussian/state-dependent channel alone is not automatically sufficient |
| Muller et al., PRX 2023; Muller & Janke, PRL 2026 | Bounds/refinement determining the same update under the same random draw | Conditional transition-law control and physically supported additional sensing; compare against tuned refinement rather than naming the objective differently |
| P-bit variation calibration, 2025 | Compensation of stochastic-device transfer variation | Stable coupling-storage readout rather than assuming a stochastic MTJ; best calibrated LUT remains a mandatory comparator |
| Ising-CIM, JSSC 2022 | Implemented analog field computation and reference/read timing | A new measured policy/cost benefit; reference tuning and analog Ising hardware are already occupied |

Primary sources inspected:
- https://experts.illinois.edu/en/publications/the-penalty-method-for-random-walks-with-uncertain-energies/ (primary institutional abstract).
- https://people.eecs.berkeley.edu/~jfc/papers/17/UAI2017.pdf (method text inspected).
- https://journals.aps.org/prx/pdf/10.1103/PhysRevX.13.031006 (bound/refinement method inspected earlier in this thread).
- https://doi.org/10.1103/29yw-9grr (primary abstract and indexed method).
- https://www.mdpi.com/2072-666X/16/2/133 (indexed primary method passages; direct access later rate-limited).
- https://sites.utexas.edu/CRL/wp-content/uploads/sites/4417/2022/06/Ising_CIM_JSSC2022.pdf (indexed primary circuit/timing passage).

This targeted search does not establish absence of an equivalent published controller. In particular, generic calibrated randomized decoding and sequential experimental design may subsume the proposed compilation. That is an unresolved novelty risk to check before a large evaluation.

## Minimal experiment request and stopping rules

Immediate: use the existing E11C outcome and obtain the next small access-device/MTJ shared-read result. No full 256x256 PEX is needed to derive this proposal.

When that read exists, the useful data are:
- known programmed states/masks and true signed arithmetic;
- sampled and settled response under a common sense path;
- matched-arithmetic masks with different loading/position;
- repeated fixed-state reads only under an actually supported temporal-noise process;
- one supported additional-read mode and its conditional joint response/cost.

CAL controls: tuned references/gain/offset, legal-count decoding, longer sensing, calibrated temperature and an unrestricted one-read stochastic LUT. Control candidates: established noise-corrected acceptance, applicable bound-based refinement, best fixed read mode, simple staged sensing and exact digital incremental fields. A generic channel-aware sequential policy is a serious algorithmic comparator.

Stop this proposal if:
- one-read calibration or temperature adjustment matches the useful frontier;
- repeated readings provide no useful additional information;
- context dependence cannot be represented cheaply or validated;
- compilation/calibration/controller costs consume any read saving;
- corrected transitions do not improve the declared original-graph solution target per total cost;
- a closest existing method implements the same decisions at the same cost.

No improvement percentage, newness certification, supervisor approval or final contribution is asserted. A conditional contribution statement is:
"A calibrated read-channel analysis and compact controller that selects MRAM sensing work to meet a specified Ising transition-quality target, with a validated advantage over tuned calibration/refinement and an exact digital incremental baseline."

## Secondary mechanism to keep in reserve

If the real read circuit exhibits RC settling history, a separate possible lever is to predict residual transients from known recent spin changes and choose sensing time accordingly. This must confront ordinary self-timed/adaptive reads, longer sensing, reset/precharge policies and continuous-bias energy. It is not a second concurrent project or a novelty pass.
