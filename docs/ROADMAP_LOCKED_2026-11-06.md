# Current FYP roadmap — Low-order FP coupling for STT-MRAM p-bits

**Benchmark updated 6 November 2026:** supervisor-approved weighted Max-Cut using the Mac portion of the Biq Mac Library. See the [active decision](BENCHMARK_DECISION_WEIGHTED_MAXCUT_20261106.md), which supersedes previous MIMO-specific benchmark instructions. The research core and M0–M5 stages remain.

## Research question
How should coupling precision and scale granularity be chosen for nonideal STT-MRAM p-bit systems to preserve useful weighted-Max-Cut solution quality at lower implementation cost?

Low-order floating-point coupling is the design focus. Optimized scaled integers and BFP/shared-exponent representations are fair controls. Use the already defined candidate formats; this benchmark change does not authorize an open-ended codebook search or predetermine a floating-point advantage.

## Hypotheses
- **H1 — Response and useful precision:** assess whether the benefit of existing coupling-precision choices changes with a specified, justified STT-MRAM p-bit response while maintaining an absolute useful-quality target.
- **H2 — Scale granularity and cost:** compare per-element floating-point representation with calibrated shared-scale/group configurations; preserve symmetric effective couplings and include metadata, alignment, accumulation and access overhead. QAM bit-significance grouping is no longer an application-specific rationale.
- **H3 — Conditional scaling:** evaluate effects of graph vertex count, density and source weight distribution on useful representation and system cost. Presume neither a monotonic FP advantage nor a flat precision requirement.

Numerical representation error and device response nonideality are distinct. Their interaction in output quality is an experimental question; representation choice does not itself establish a physical MTJ nonideality mechanism.

## Formal benchmark and scoring
- Weighted Max-Cut: maximize Cut_w(s)=sum_(i<j) w_ij*(1-s_i*s_j)/2 for s_i in {-1,+1}.
- Under E=-sum_(i<j)J_ij*s_i*s_j-sum_i h_i*s_i, choose J_ij=-w_ij, symmetric zero-diagonal J and h=0. Then E=sum w-2*Cut_w. Native mapping needs no auxiliary spins.
- Use fresh identified Biq Mac Mac instances, preserved original weights and verified optimum/bound conventions. Biq/QUBO instances are not silently treated as Max-Cut graphs.
- Score original cut, reference gap and finite-budget RETURNED-target success. Declare readout and represented-energy retention policies. Any-visit probability is a diagnostic.
- Split calibration and held-out graphs; nest solver seeds and device populations. Large graph state spaces are not exact-enumeration/Markov-chain requirements.
- MIMO BER, likelihood beta and antenna-based scaling are historical. Earlier archived graph pilots remain excluded as evidence for the new runs.

## Hardware and response scope
Reuse the existing local-field row and representation definitions where appropriate. The application has h=0, so reconsider bias-code storage and hardware rather than carrying over the MIMO FP6-h design conclusion. Device offsets remain separate response parameters.

Retain the intended 64–128-spin coupling hardware and bit-true exponent/scale handling, bounded accumulation, p-bit interface and implementation-backed cost. A one-row engine, a tile, and a complete accelerator are different scopes. Count the actual number of row engines, scheduler, stored states, coefficient memory/access, output-retention and conversion/interface overhead. Cell-area estimates alone are not full-system area, energy or performance.

Any suitable authorized CMOS standard-cell library may support a clearly labeled first digital comparison; GF22FDX is not mandatory. Digital synthesis does not validate a stochastic STT-MTJ response or establish process-compatible co-integration. A conventional stable-storage MTJ model is not automatically a validated stochastic p-bit model. True in-array CIM is not assumed.

## Evidence and milestones
E0 exact theory; E1 seeded algorithmic simulations; E2 illustrative response; E3 sourced/validated device response; E4 authorized circuit simulation; E5 bit-true/synthesis/hardware. Keep these distinctions explicit and do not reuse restricted or unrelated old data.

| Stage | Deliverable |
|---|---|
| M0 | Weighted-Max-Cut loader/mapping and independent original-cut checks; bounded baseline validation |
| M1 | Existing coupling representations under ideal/nonideal responses, paired by graph; H1/H2 quality bounds |
| M2 | STT-MRAM-aware coupling configuration and costed local-field/output-policy specification |
| M3 | Bit-true coupling hardware and synthesis-backed area/timing with full stated scope |
| M4 | Held-out graph families/sizes and device populations; conditional H3 |
| M5 | Supported design rules, operating limits and final report |

Existing component verification remains evidence for that component. Neither previous MIMO results nor the existence of RTL constitutes a completed Biq Mac benchmark. Keep prior results intact; no new simulation or infrastructure expansion is implied by this scope update.

## First actual M0 code gate (pending execution)
The draft branch research/m0-biqmac-maxcut-20261106 contains a source-preserving Rudy parser, an independent tiny signed Max-Cut test suite, and a fixed official-instance import script. See [M0 source protocol](M0_BIQMAC_SOURCE_PROTOCOL.md). No original Mac graphs have been executed on NUS yet; no benchmark optimization quality or Max-Cut-specific synthesis can be reported.

**Data regime explicitly added 7 Nov:** low-range Mac/rudy integer controls AND wide-range original Mac/ising physics graphs `t2g10_5555` (100/200) and `ising2.5-100_5555` (100/4950). Weight range is an input characteristic, NOT FP superiority evidence. Keep a matched solver/format/hardware cost protocol and reserve independent graph seeds for held-out. The M0 import/test script reports E0 only. See M0 source protocol.
