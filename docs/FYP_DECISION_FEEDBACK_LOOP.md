# FYP Decision Feedback Loop — current lock, 8 November 2026

**The user has LOCKED one joint research question:** coupling precision (design choice) × STT-MRAM p-bit switching nonideality (physical condition), evaluated on original Biq Mac weighted Max-Cut.

Read the [authoritative locked roadmap](ROADMAP_LOCKED_2026-11-06.md) first. It takes precedence over all dated “next gate”, parked-response, hardware-first, three-graph or mandatory-BFP instructions preserved below.

## Current decision

- **Target / alignment:** precision-response regime maps, a conditional precision-selection rule, two held-out graph checks and one bounded supporting cost table.
- **Evidence:** retain the 936 ideal CAL runs, graph-to-RTL verification, Sky130 row mapping and M4B digital interface. These are not physical MTJ/device-population or full-chip energy evidence.
- **Hypothesis:** offset or gain variation may shift useful coupling precision, or leave it stable within the tested range. Neither FP superiority nor a ranking reversal is required.
- **Scope:** two CAL + two held-out 100-spin graphs; core FP/INT 4/5/6 + FP64; existing 8-bit candidates under the predeclared rule. Preserve BFP evidence and the authored all-width gain pilot; optional BFP6 is a supporting control, not a new format/grouping search.
- **Next minimum experiment:** preserve E2-GAIN-01 as currently authored: one dense CAL graph, 13 existing configurations, two new gain levels, 24 paired seeds, 624 new runs and matching ideal rows reused. Interpret that plot before the larger, separately studied gain and offset slices.
- **Model:** three assumed nonzero E2 levels plus ideal in the main campaign, gain and offset separate. Full numerical values, fixed populations, absolute quality thresholds, corrected run counts and extension rules are in the roadmap. Never call assumed stresses measured residuals.
- **Expected observable:** original-optimum gaps and conditional CIs, accepted/degraded/failed/uncertain regimes, same-response numerical penalty, and whether the lowest qualifying bit width changes.
- **Prior art:** precision, p-bit variation and calibration already have literature; the specific validated conditional selection rule is the candidate contribution. No unsupported “nobody has studied it” claim.
- **STOP / opportunity cost:** stop Genus/library repair, disk searches, extra RTL and alternate applications/solvers. Stop extending stress levels to rescue FP. Preserve negative and uncertain findings. Do not report a moved bit-width threshold from six-bit-only data or a whole-chip benefit from row area.
- **Decision:** GO joint precision-response science. Hardware remains supporting evidence; no new hardware prerequisite. No solver/device run is performed by this documentation lock.

## Compact feedback loop

Before a scientific step answer relevance, evidence, closest prior art, opportunity cost and stop condition. Afterward: prediction → observed evidence → fairness/counterexamples → continue/change/stop. Existing necessary correctness checks remain; another PASS label, report rewrite or environment check alone is not a research milestone.

## Historical record

The chronological entries below are preserved as evidence of completed work and past decisions. Their old prospective instructions do not override the locked roadmap.

## Historical decisions and evidence — retained for provenance

**MANDATORY for every subsequent scientific/engineering choice.**
This file is the durable cross-chat record of the user's direct instruction:
*before accepting a new action, check whether it directly advances the FYP; after receiving evidence, close the loop and change course or stop instead of digging a research hole.*

## Frozen FYP target
**Original Biq Mac Mac weighted Max-Cut** solved by an **STT-MRAM p-bit Ising architecture**, assessing **FP/INT/BFP low-order symmetric coupling representation**, *separately evidenced* **STT-MTJ switching nonidealities**, and **actual quality versus full hardware implementation cost**. h=0 for the mathematical problem, J=-w; runtime retention uses represented energy. Benchmark changes require explicit user/supervisor reapproval.

## Before every next-step decision: five compulsory questions
1. **Relevance:** Which ONE statement in the above FYP target will this decision test? Is it an original-cut/precision/device/hardware question, rather than infrastructure or generic optimizer improvement?
2. **Evidence:** Is the premise observed NUS data, independently verified published work, tested mathematical code, or an untested hypothesis? Separate E0 exact, E1 ideal algorithm, E2 illustrative response, E3 characterized/sourced device distributions, E4 physical circuit, E5 verified RTL/synthesis. NEVER promote tiers.
3. **Novelty collision:** Which closest existing paper already addressed this? What exactly remains untested? If no distinction survives, do NOT claim novelty; choose a sharper but still on-scope question.
4. **Cost/opportunity:** What is the smallest discriminating run or code change? What essential FYP milestone does it displace? Use one experiment at a time; no unbounded beta sweeps, representation families, novel benchmarks, or arbitrary device parameters.
5. **STOP/GO:** Predeclare positive/negative outcomes, follow-up or termination threshold, seed/graph units, artifact checks and what specific claim will be removed if the hypothesis fails.

## Required feedback loop on return
`Observed result → compare with preregistered expectation → audit fairness/counterexamples → recheck relevance and novelty → GO / PIVOT WITHIN SCOPE / STOP → name one next falsifiable question`.

**Each assistant decision must include a compact decision record** with fields: `Target, Evidence, Hypothesis, Minimal test, Expected observable, Failure/stop condition, Novelty/prior-art check, FYP alignment, Decision`. Report negative data and counterexamples. A result that is merely "more code/graphs/plots" without isolating a scientific uncertainty is **NOT progress**.

### Hole detector: automatically STOP and reassess if
- Another experiment only changes beta/seeds/format hyperparameters without new science or adequate paired calibration.
- "FP wins" rests on one already-seen graph, one nominal global scale, a seed CI crossing zero, or no matched INT/BFP control.
- A physical STT-MRAM claim relies on a generic sigmoid with invented nonideality parameters, a high-barrier storage model relabeled as free-running stochastic MTJ, or undocumented voltage-to-field conversion.
- Symmetry J_ij=J_ji, original-weight evaluation, same compute budget, or earliest best-*represented*-energy retention is lost.
- Hardware "cost" omits scale metadata, coefficient storage/read bandwidth, local-field datapath, schedule/control, MTJ and interface cost.
- A new complex optimizer (parallel tempering, SQA, hybrid algorithm) is proposed before a precision×device response question warrants it.
- Research reports or manifests keep accumulating while no discriminating original-cut/response/cost result is produced.
- A claimed contribution is clearly in published prior art.

## Closed decisions
- **Benchmark:** original Biq Mac weighted Max-Cut (supervisor approved); no alternate benchmark.
- **Solver CAL:** FP64 reference 144 runs; 50k linear beta chosen by preregistered equal-graph gap-versus-budget rule. Do not tune again for the next paired precision stage.
- **Global precision CAL:** 936 actual paired ideal software runs completed. Dense `ising2.5` FP5 5.7361% vs FP6 4.1369%, FP64 4.3449%, INT6 4.4665% gaps; FP6−FP64 delta −0.208 pp 95% seed CI [−0.529,+0.090]. Candidate six-bit knee ONLY on that already-seen dense graph; no overall FP winner or device behavior established.
- **Next scientific dependency:** sourced pulse-driven STT-MTJ probability transfer, realistic residual mismatch after calibration, then response-dependent paired solution-quality curves and full arithmetic/memory/MTJ costs. No fabricated physical parameters.

## One bounded decision NOW: device response interface gate
**Target:** identify how represented local field enters a physically motivated STT-MTJ pulse-switching probability, without changing the Max-Cut solver benchmark.
**Closest prior art / novelty risk:**
- Yang, Grimaldi, Bao et al. (2026), *250 magnetic tunnel junctions-based probabilistic Ising machine*, Nature Communications 17:5368, DOI 10.1038/s41467-026-72020-8: experimental pulse-driven STT-MTJ p-bits, calibrated sigmoid, **Biq Mac Max-Cut**, stochastic variation and advanced annealing. This already covers the combination of STT-MTJ + Max-Cut + device variability; our novelty, if any, must be *precision representation × response × full cost*.
- Yang, Bao, Humianto et al. (2026), *A parallel magnetic tunnel junction-based probabilistic Ising processor for efficient quadratic optimization*, Nature Communications 17:4616, DOI 10.1038/s41467-026-71128-1: 144 measured STT-MTJs, 4 us perturb pulses, 0.68–1.34 V sweep in their setup, device-specific sigmoid calibration. This validates variability and calibration as already studied, not a new contribution by itself.
- Bao, Yang, Humianto, Yang (2026), *Magnetic-Tunnel-Junction-Based Probabilistic Processor for Efficient Embodied Evolution*, Nano Letters 26:5731–5739, DOI 10.1021/acs.nanolett.6c00275: 256-MTJ p-bit hardware; supplementary describes device sigmoid calibration.
**Physical interface example from first paper (Fig. 1e):** `P(+1|V)=sigmoid(128.8*(V_in-1.852 V))` for a reported measured aggregate/example curve, NOT 250 individually archived calibration constants and NOT a GF22FDX cell model. Ideal desired probability is `P(+1|H_i)=sigmoid(2*beta*H_i)`; example nominal voltage transformation is `V=1.852+(2*beta*H_i)/128.8`. These are algebraically identical for the nominal curve, so doing this alone will **not** produce nonideal results.
**GO now:** implement and mathematically test this VOLTAGE/LOGIT interface (no solver run, no invented residual).
**STOP condition:** if actual measured per-device residual slopes/offsets or an openly labeled E2 sensitivity range cannot be obtained/declared, do NOT call any resulting plot an E3 device-aware result. Source-precise device parameters or credible measured data remain an unmet research dependency.
**FYP alignment check:** direct bridge from existing quantized coupling H_i to actual stochastic STT-MTJ P(+1), no benchmark/solver reset, tiny implementation footprint, clear falsifiable calibration parity test. GO for interface *only*.

### Reminder for future assistant sessions
Consult this file and the latest actual experimental result before suggesting a new step. Record one new GO/STOP decision and the outcome after every experimental gate. If the next suggestion fails any five-question check, stop it.

## Feedback closure — STT-MTJ nominal transfer preflight, 7 Nov 2026
- **Observed:** `experiments/m2_stt_pbit_transfer_preflight.py` and `tests/test_m2_stt_pbit_transfer_preflight.py` authored; GitHub Actions run 42288072400 PASS, including all 5 tests: literature slope/midpoint identity, nominal `sigmoid(2βH)` parity, monotonicity, required explicit residual parameters and invalid-input rejection.
- **Interpretation:** nominal voltage mapping is algebraically consistent, but is exactly equivalent to ideal Gibbs. This proves NO Max-Cut quality improvement, NO residual mismatch, and NO device-characterized switching response. The published representative sigmoid does not provide a 100-device residual distribution.
- **Hole detector:** Repeating 936 Max-Cut runs under the perfectly calibrated nominal transfer would reproduce ideal stochastic results, adding no scientific information and wasting NUS compute. STOP that sweep. Do not invent per-device residual distributions and call them E3.
- **Next evidence dependency:** source explicit post-calibration device-specific residuals, or define an openly labeled E2 sensitivity envelope with documented parameter provenance. Then design ONE economical paired representation×response comparison, accounting for pulse reset/perturb and physical time. First assess 2026 250-STT-MTJ BiqMac prior art before novelty claims.
- **Decision:** GO literature-grounded mathematical interface only (completed); HOLD E2/E3 full graph resimulation until physical residuals or a defensible E2 assumptions envelope are established.

## Feedback closure — novelty collision audit (7 Nov 2026)
- **Hypothesis:** the 250-STT-MTJ Biq Mac processor paper demonstrates the physical application but does not necessarily test numerical storage precision of each coupling `J_ij`.
- **Observed:** its main text quantizes the accumulated local field `I_i` to index a random-bit FIFO in a proposed chiplet; this is distinct from low-order FP/INT/BFP coupling codebooks. Separate 2026 Ising literature already compares INT8 vs FP32 Max-Cut quality/throughput, and a 2026 FPGA p-computer examines fixed-coefficient width vs resources. The precise novelty is therefore narrower than the combination of STT-MTJ + Max-Cut + quantization.
- **Unresolved:** the paper's Supplementary Information file is identified but could not be retrieved; do NOT assert that its supplementary circuit never studies coefficient quantization. See `docs/PRIOR_ART_COLLISION_PRECISION_STTMTJ_20261107.md`.
- **Hole check:** this is a claim audit, not a new benchmark or device simulation. Do not spend compute on nominal sigmoid re-runs; wait for defensible source-specific device residuals or explicitly scoped E2 sensitivity.
- **Decision:** GO with supervisor-approved original Biq Mac weighted Max-Cut; focus claimed contribution on *low-bit J representation x p-bit residual response x full cost*, keep priority claim provisional until supplementary review.

## Correction — coupling-format value does not require response ranking reversal (7 Nov 2026)

**Target:** determine which low-order symmetric FP/INT/BFP `J_ij` representation meets a preregistered *original-weight* Biq Mac weighted Max-Cut quality threshold at minimum **whole-solution** hardware cost in an STT-MRAM p-bit architecture. Device response is a specified operating condition and robustness check, NOT a required mechanism for FP superiority. Keep the locked benchmark, frozen solver and represented-energy retention.

**Evidence:** 936 NUS runs are E1 ideal Gibbs *CAL* results; they do not show a general FP6 win, device robustness or hardware savings. Nominal pulse transfer is mathematically ideal. Published per-device sigmoid calibration does not restore `J` coefficients erased/distorted by coupling quantization. Small Gaussian-generator KL divergence from separate literature is not a measured Max-Cut post-calibration residual.

**Hypothesis:** formats have different representation-quality-cost frontiers even for well-calibrated p-bits; device gain/offset residuals *may or may not* change those frontiers. Neither a sign change in FP-vs-INT ranking nor a nonzero format-by-response interaction is required to establish a useful conditional selection rule.

**Minimal test / next gate:** verify one bounded source/model record for post-calibration response, then choose measured E3 parameters if supported, otherwise openly assumed E2 gain/offset envelope with documented assumptions (do not block the project indefinitely). Freeze the selected model **before** numerical inspection. Six-bit screening only: FP64, FP6, INT6, BFP6 × original three CAL graphs × 24 paired seeds = **288 new response-conditioned solver runs for one specified response condition**, contingent on matching the existing ideal-run codebooks, scales, seed stream, schedule and retention policy. Persist each spin/device residual throughout each run and reuse the *same device realization* across formats. Maintain separate device RNG from solver RNG; verify zero-residual response parity before relying on reused ideal baseline. Do NOT claim this screen establishes a shifted bit-width knee. No extra solver/beta tuning or new benchmark.

**Expected observable:** (a) per-format **absolute** original-optimum gap and quality-threshold attainment, (b) paired additional gap vs matched FP64 in each response condition, (c) diagnostic interaction `D=[gap(FP6)-gap(INT6)]_response-[gap(FP6)-gap(INT6)]_ideal` with paired uncertainty across solver seeds/device realizations. A confidently bounded practically small `D` supports tested stability; a wide CI crossing zero is **inconclusive**, not evidence of no interaction. Any equivalence margin must be specified before the test. Across-graph generalization requires independent held-out graphs: three CAL graphs and many solver seeds do not create independent graph samples.

**Cost / opportunity:** FP6 vs INT6 have equal nominal coefficient payload width; no storage advantage is established. A viable FP claim must show fewer total bits at matched quality, better quality at matched full cost, or lower total energy/time (including repeated attempts) for the *same original-cut target*. Count coefficient memory and bandwidth, FP/INT/BFP arithmetic and metadata, control/schedule, STT-MTJ and interfaces, latency and area; do not substitute Python float64 or a one-copy storage proxy for mapped hardware.

**Failure / STOP:** if response interaction is absent, stop asserting response-dependent format superiority but **continue** testing the main representation-quality-cost question. If an E2 range is assumed, report only conditional sensitivity, never E3 measured validation. If FP fails the matched full-cost criterion, report INT/BFP as preferable within tested conditions rather than searching for an FP-favouring residual. Do not repeat nominal-sigmoid sweeps or change the frozen solver.

**Novelty/prior art:** device calibration, Max-Cut on STT-MTJ, and reduced precision in Ising/p-computers are already studied; priority over matched low-bit FP/INT/BFP *J-storage* selection rules remains provisional pending the 250-MTJ paper's Supplementary Information. The quantized local-field/FIFO index is not automatically evidence of `J_ij` format comparison.

**FYP alignment / decision:** **GO** original FP coupling FYP; **GO** bounded source/model selection and conditional E2 or E3 screen; **HOLD** any fabricated measured-device or uncosted FP-superiority claim. Interaction `D` is diagnostic, not a gate for whether the whole FYP survives.

## Feedback closure — E2 response screening code gate (7 Nov 2026)

- **Target:** assess whether a *specified, admitted-assumed* response condition changes relative six-bit coupling quality, without requiring interaction or an FP win.
- **Evidence:** source check confirms a nominal STT-MTJ transfer and local-field FIFO-index quantizer; supplementary PDF and post-calibration *population residuals* remain unverified. **E2**, not E3, has therefore been frozen as one transparent software sensitivity stress; numerical bounds ±5% gain, ±0.10 logit offset are *chosen assumptions*, NOT published measurements. Details: \`docs/M2_E2_RESPONSE_SCREEN_FREEZE_20261107.md\`.
- **Minimal implementation:** \`experiments/m2_e2_response_gate.py\` adds a bounded 288-run **NUS-only** gate conditioned on exact original 936-run CSV SHA256, original graph hashes, unchanged J source-only scales, original-cut scoring and 50k linear solver. Exactly one persistent seeded 100-spin realization, matched across FP64/FP6/INT6/BFP6 and all 24 solver seeds. The synthetic tiny tests do not run the actual NUS experiment.
- **Observed verification:** GitHub Actions [42299340532](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42299340532) **PASS** on new nominal parity, deterministic device identity, bounds, raw E1 integrity gate, and all existing M0/M1 tests. The first CI edit briefly failed YAML parsing and was fixed before this passing run. No E2 Max-Cut result exists yet.
- **Expected observable:** absolute original-weight gap; paired response-vs-FP64 gap; FP6-vs-INT6 diagnostic difference-in-differences with paired 95% seed bootstrap. Device-population and graph-level uncertainty are NOT represented.
- **Novelty/prior art:** no new priority claim; previous 250-STT-MTJ supplementary not inspected, local-field output quantization != automatically stored coupling J-format study.
- **Opportunity/STOP:** no old solver rewrite, tuning, 936-run ideal repeat, alternative benchmark or made-up E3 calibration. If FP fails matched quality and fully costed implementation, report the INT/BFP preference. If D CI wide or zero, do not manufacture a rank reversal; core quality-cost study continues.
- **Decision:** **GO** to one user-run NUS 288-run E2 sensitivity experiment after the existing source-data checksum passes; **HOLD** device-characterized and hardware-cost conclusions pending their respective evidence. E2 code gate PASS; NUS scientific result **NOT RUN**.

## Feedback closure — M3 genuine FP6/INT6/BFP6 local-field row (7 Nov 2026)

- **Target:** put stored FP coupling back at the center of the FYP; determine the actual relative complexity of bit-true coefficient decode plus integer local-field accumulation at fixed six-bit width, with fair INT/BFP controls. Device response and solver remain unchanged.
- **Observed / evidence:** `rtl/m3_local_field_row.v` and bit-true `experiments/m3_sixbit_encoding.py` plus tests were written. [M3 Actions run 42352449618](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42352449618) **PASS** Python tests, 99-term Icarus RTL vectors for each fixed compile-time format, and identical-flow Yosys 0.33 generic synth. Downloaded synthesis logs show FP6 **274 cells /17 FF**, INT6 **138 /13 FF**, BFP6 **138 /13 FF**, for one streamed row `MAX_TERMS=99`. FP6 has finite-only E3M2 sign/exponent/mantissa stored coupling and a Q4-integer decoded accumulation. INT/BFP use symmetric signed integer decoding, BFP global power-of-two exponent remains external to the row.
- **Existing E1 quality context:** `ising2.5` CAL dense FP6 gap 4.1369%, INT6 4.4665%, BFP6 4.8365%; on the small-integer and wide-sparse CAL graphs INT6 gap is lower than FP6. Generic row cell counts are not technology-mapped area/power, and no cross-graph FP superiority or complete-system quality–cost advantage has been established.
- **Minimal test completed:** 3 formats, exactly one matched 99-term row and generic synth comparison. No solver, held-out Max-Cut, device model, calibration or beta retuning.
- **Novelty/prior art:** coefficient-format effects and precision-vs-resource studies are not new individually; the conditional original-cut quality vs **full implementation/whole-solution cost** rule remains the potential narrower contribution, still pending evidence.
- **Opportunity/STOP:** do not introduce more E2 response sweeps or claim 274/138 is a real PDK area ratio. Stop claiming a format-wide FP win when two calibration graphs favor INT6. 
- **Next falsifiable question:** Can frozen M1 graph-specific quantized `J_ij` be encoded once into the actual FP6/INT6/BFP6 RTL row, preserving `H_i=sum_j Jhat_ij*s_j` after external shared-scale application? Then include shared-scale/memory/interface costs and independent held-out quality.
- **Decision:** **GO** FP6 hardware integrity and complete cost gate; response robustness later, retained as secondary. **No** generic Yosys cell count should be described as measured silicon area/energy.

## Feedback closure — FP hardware original-graph and mapped-area gates (7 Nov 2026)

- **Target/FYP alignment:** ensure FP6 stored sign/exponent/mantissa couplings, not device residual fitting, drive an actual integer local-field accumulator; compare matched INT6/BFP6 in a common physical standard-cell *library-mapping* proxy.
- **Observed:** [original Biq Mac graph-to-RTL workflow 42353562894](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42353562894) **PASS** for 3 source-SHA-verified 100-spin CAL graphs × FP6/INT6/BFP6 × 99 row-0 terms, bit-true cumulative checks; M1 represented local field equals decoded RTL integer sum times correct global scale exactly for all 9 sample cases. **Not full graph solver RTL.**
- **Further observed:** [Sky130 mapped-area workflow 42354259889](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/42354259889) **PASS**, OpenROAD-pinned Sky130 HD TT library, Yosys 0.33, 39 excluded specialty cells. Row-only FP6 171 mapped cells/17 FF/**1438.88 µm²**, INT6 107/13/**929.6416 µm²**, BFP6 107/13/**929.6416 µm²**. 1.55× FP6-versus-INT6 **row-area penalty only**; no GF22FDX area, STA, PPA, memory, interface or power claim. See `docs/M3_FP6_INT6_BFP6_ROW_RESULT_20261107.md`.
- **Novelty risk:** showing a lower-bit representation and resource tradeoff by itself has prior art. FP value depends on original-weight quality **and total cost**, not on adding artificial p-bit nonidealities.
- **GO/STOP:** GO a single frozen memory + shared-scale/logit interface cost gate. STOP assuming a 1.55× row penalty implies whole-machine 1.55× area/power. STOP claiming FP6 is generally superior from one dense CAL graph. E2 remains parked and solver frozen.
- **Next falsifiable question:** for `A_i=sum_j q6_ij*s_j`, the ideal logit can be calculated as `x_i=G_fmt(t)*A_i` with `G_fp6=2*beta(t)*S_fp6/16`, `G_int6=2*beta(t)*S_int6`, `G_bfp6=2*beta(t)*2^k`. A single once-per-update scale interface can replace per-edge FP arithmetic. Under an identical declared output logit precision/voltage target and identical 50k-attempt architecture, what are the **total** area, access and interface costs? Do not silently choose unequal precision/latency or assert physical MTJ E3 data.
