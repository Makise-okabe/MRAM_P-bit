# FYP Decision Feedback Loop — standing project rule (7 November 2026)

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
