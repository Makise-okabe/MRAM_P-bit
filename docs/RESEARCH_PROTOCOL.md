# P-Bit Experiment Protocol — v0.1

## Hypotheses (not findings)
H1. Low-bit floating point can retain small interactions in selected high-dynamic-range problems where a globally scaled integer code loses them.
H2. A real p-bit's probability transfer curve changes how field quantization affects the computation.
H3. Exponent alignment and scaling hardware can erase numerical storage savings.

## Predeclared gates
P00: full-text prior-art audit; validate stochastic device model and provenance.
P01: exact energy enumeration, symmetry, independent seeds, Gibbs correctness at N<=16.
P02: match total budget; compare FP32/64 reference, optimized fixed-point, small floating-point, and shared exponent.
P03: ideal vs behavioral response; treat physically validated device data as a separate class.
P04: bit-true coefficient store, sign-select, scale/exponent alignment, accumulator, scheduler.
P05: scale and held-out instances without post-hoc cherry-picking.

## Metrics
Original Hamiltonian ground-state energy gap; solution hit probability; attempted updates to reach a target; distribution divergence for enumerated systems; coefficient/bias/scaling bits; effective bandwidth; accumulator width; implementation-backed power/area/latency only when established.

## Evidence guardrails
- Distinguish mathematical, seeded software, behavioral response, device simulation, extracted circuit, and physical measurements.
- All energy gaps use the **unquantized original** J.
- Use asynchronous single-spin updates for an equilibrium Boltzmann baseline.
- Never infer physical area/energy from arbitrary software operations.
- Stop or redirect if tuned integer arithmetic matches float at lower cost.
- No historical device calibration, data, reports, or foundry material imported.
