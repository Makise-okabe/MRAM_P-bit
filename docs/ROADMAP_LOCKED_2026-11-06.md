# LOCKED FYP ROADMAP — Low-order Floating-Point MRAM p-bit Couplings

**Locked 6 November 2026.** Changes in this revision affect the APPLICATION BENCHMARK only. Research problem, H1/H2/H3, M0–M5 implementation and evidence standards remain the same.

## Research question
**How should coupling precision and scale granularity be chosen for nonideal MRAM p-bit systems to preserve useful optimization performance at lower implementation cost?**

## Central design — NOT optional
Build and evaluate **LOW-ORDER FLOATING-POINT COUPLING** representations in nonideal MRAM p-bit machines. Nominal candidate encodings: explicitly defined FP4 (E2M1), FP6 (E3M2), FP8 (E4M3), with complete sign/exponent/mantissa rules, zeros, overflow, underflow, rounding, optional scaling and accumulator design. Test per-element exponent storage against shared tile/block/row scale methods. Integer formats are **strong comparison baselines**, not replacement direction. We do not predeclare that floating point must outperform tuned integer everywhere.

## H1 / H2 / H3 — unchanged
- **H1: Device-dependent useful precision.** Minimum coupling precision to preserve an absolute acceptable BER / task-quality target varies with the type and severity of a physically justified p-bit response.
- **H2: Scale granularity.** Trade off FP per-element exponent and more compact block/tile/row scales, including metadata, exponent alignment, local-field accumulation, bias precision and wiring.
- **H3: Conditional size dependence.** Measure precision requirements by MIMO transmitter count Nt, receiver count Nr, antenna ratio, SNR and channel conditioning; presume neither FP nor INT scaling advantage.

## Formal application: BPSK MIMO detection ONLY
- Complex baseband y=Hx+n, H in C^(Nr×Nt), x in {-1,+1}^Nt; define complex Rayleigh variance and complex AWGN convention.
- ML residual R(s) = ||y-Hs||²; preserve original unquantized H and y for scoring.
- Ising convention E(s)=C−Σ_(i<j) Jij si sj−Σ_i hi si. Let G=Re(HᴴH), b=Re(Hᴴy). Set Jij=−2 Gij (i≠j), Jii=0, hi=2 bi, C=||y||² + Σ_i Gii; require exact state-wise matching at small Nt.
- Communication metric: **BER versus transmitted bits** over SNR; other metrics: original ML residual gap, exact ML-state hit rate at small Nt, and all-inclusive time-to-target at prescribed residual-quality threshold. ML hit is not equivalent to zero BER because noisy ML can differ from transmitted x.
- Independent channel/noise frames with frozen seeds, Rx/Tx regimes, calibration/held-out split and nested solver RNG. No changing the workload to engineer a format winner.
- No TSP, Max-Cut, balanced partitioning or spin-glass formal application benchmarks. Tiny generic Ising exact-enumeration/Gibbs unit tests are permitted as software checks; old application codes/results are preserved in archive/pre-mimo-benchmark-20261106 and excluded from H1/H2/H3.

## Format baseline and hardware accounting
- High precision FP32/FP64 numerical reference.
- FP4 E2M1, FP6 E3M2 and FP8 E4M3 custom **low-order FP coupling** formats; compare at specified effective storage and cost, not bit-label only.
- Calibrated scaled INT4/INT6/INT8 and block-floating/shared-exponent representations with identical calibration data.
- Preserve effective symmetric J, zero diagonal and a coherent J+h implementation; J-only quantization is an explicitly labeled ablation.
- Count coefficient/bias storage, scales/exponent metadata, sign multiply/select, exponent alignment, accumulation and overflow, memory bandwidth, replicas, swaps, routing and scheduling. Full bit-true simulation in M3 followed by synthesis-backed resources and timing. Software update counts are not watts or seconds.

## Evidence guardrails
E0 exact math; E1 independent seeded software; E2 illustrative nonideal p-bit response; E3 sourced validated stochastic p-bit response; E4 authorized circuit; E5 bit-true/synthesis or hardware. Device response assumptions cannot be relabeled physical results. No prior ADC/CIM, TSP pilot, past assistant nonideality pilots or parasitic-return measurements may be recycled. Parasitic shared-line coupling is a separate out-of-scope proposal.

## Milestones (unchanged)
| M | Deliverable | Exit |
|---|---|---|
| M0 | Fresh MIMO-to-Ising reference, ML/BER/solver checks, independent channels and response-model provenance | Exact state-wise equality, credible ideal solver and frozen workload |
| M1 | FP4/FP6/FP8 vs optimized integer/shared-scale under p-bit nonidealities | H1/H2 bounds and independent-frame paired uncertainty above absolute BER threshold |
| M2 | Device-aware low-order FP format/scale selection rule and coupling-macro specification | Honest analytical coefficient, exponent alignment, accumulator and replica cost |
| M3 | Bit-true 64–128 spin tile, RTL/synthesis comparison | Verified arithmetic and implementation-backed area/timing |
| M4 | Held-out BPSK MIMO and device populations at larger Nt/Nr | Tested operating limits and conditional scaling H3 |
| M5 | Final architecture, configuration rules and CA/report | Every contribution traced to reproducible evidence |

14 active working weeks plus 2 weeks buffer around exams. Target M1/M2 for CA3, synthesis at M3, board deployment optional.

## Prior art and intended novelty
Singh et al., *Ising Machines' Dynamics and Regularization for Near-Optimal MIMO Detection*, IEEE TWC 2022, DOI 10.1109/TWC.2022.3189604, already studied finite-precision Ising couplings for MIMO. Our target is **device-response-aware low-order floating-point coupling and scale granularity with implementation-backed cost**, not a new MIMO algorithm or a generic finite-bit observation.
