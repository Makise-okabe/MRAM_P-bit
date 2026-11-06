# STT-MRAM p-bit FYP — Low-order floating-point coupling / weighted Max-Cut

**Current benchmark decision, 6 November 2026:** weighted Max-Cut using the **Mac (Max-Cut) instances in the Biq Mac Library**. The user confirmed this choice after discussion with the supervisor. MIMO is no longer an active application benchmark; SAT/MaxSAT are not the selected implementation route.

**Research core remains:** low-order floating-point coupling representation and scale granularity under nonideal **STT-MRAM p-bit** responses, with optimized integer and shared-exponent/BFP controls and an implementation-backed quality–cost comparison.

**Research question:** Which coupling configuration preserves useful weighted-Max-Cut solution quality under a specified STT-MRAM p-bit response at lower implementation cost?

Representation determines numerical error and digital implementation cost. Device nonidealities determine deviations in the p-bit response. Their joint effect on solution quality is to be tested, not assumed.

## Active sources of scope
- [Supervisor-approved benchmark decision and mapping](docs/BENCHMARK_DECISION_WEIGHTED_MAXCUT_20261106.md)
- [Current roadmap](docs/ROADMAP_LOCKED_2026-11-06.md)
- [Evidence rules](docs/RESEARCH_PROTOCOL.md)
- [Official Biq Mac Library](https://biqmac.aau.at/biqmaclib.html)

## What changes
- One graph vertex corresponds to one spin. Native weighted Max-Cut uses pairwise couplings, no auxiliary spins, and zero problem bias h.
- Score returned states with the **original graph weights**: cut value, gap to a verified optimum/bound, and fixed-budget target success.
- Communication BER, QAM significance grouping and AWGN-posterior beta are not weighted-Max-Cut metrics or operating-point rules.
- Existing formats, generic Ising arithmetic and row RTL are reusable components. The MIMO-specific FP6-bias conclusion does not carry over to h=0.

## Current implementation status
The supervisor-approved main-branch scope change is now supported by a separate M0 draft branch containing an authored Rudy loader, tests, and an E0 import script (all pending actual NUS execution). Existing main-branch application scripts and CI still include the historical MIMO implementation. No Biq Mac import, weighted-Max-Cut result or new physical-MRAM result is claimed here. Do not start further MIMO performance sweeps.

Prior MIMO, TSP, CIM/ADC and older Max-Cut pilots remain historical evidence only. The new benchmark requires fresh, identified Biq Mac instances and runs; old archived graph results are not retrospectively promoted. Preserve the M2 hardware work and its component verification without relabeling it as a complete Max-Cut accelerator.

M0–M5 remain the research stages: mapping/reference, joint representation–response evaluation, design rule and cost specification, bit-true/synthesized hardware, held-out scaling, final report. The planned 64–128-spin coupling hardware remains in scope; neither fabricated stochastic MTJs nor a GF22FDX implementation are claimed. No new format search, toolchain expansion or simulation was introduced by this decision.

## First M0 weighted Max-Cut code gate (draft)
The current code migration is on branch research/m0-biqmac-maxcut-20261106 and documented in [M0 source protocol](docs/M0_BIQMAC_SOURCE_PROTOCOL.md). Its source-audit tests are **not yet NUS-executed**. Original graph optimum references and Max-Cut solver quality are still absent; earlier MIMO scripts remain preserved as historical only.


## New locked benchmark contrast: LOW versus WIDE original edge-weight range

Retain `Mac/rudy` 100-node small-integer graphs as **low-range controls**. Add two **unmodified official `Mac/ising` 100-node wide-range calibration examples, `t2g10_5555` (200 edges; 460 to 294541 in |weight|) and `ising2.5-100_5555` (4950 edges; includes |weight|=1 and -101237). Do not mistake the name `ising` for a non-Max-Cut source: these are official **Mac** graph inputs. `scripts/m0_fetch_biqmac_wide.sh` downloads and exactly validates these sources; `experiments/biqmac_weight_audit.py` generates SHA256/weight-distribution and simple descriptive INT6 fullscale diagnostics. All reports remain E0; no solver or FP improvement claim. See [M0 source protocol](docs/M0_BIQMAC_SOURCE_PROTOCOL.md).
