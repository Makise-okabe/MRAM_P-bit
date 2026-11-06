# Bounded novelty collision audit — STT-MTJ p-bit and coupling precision (7 Nov 2026)

## FYP target and decision
**GO / retain original Biq Mac Mac weighted Max-Cut with symmetric low-bit FP/INT/BFP couplings.** The comparison with prior STT-MTJ processor studies does NOT prove the proposed coupling-format/quality/cost contribution has already been published. Equally, merely combining low-bit FP, Max-Cut and device variability is NOT established novelty. Any priority statement must be limited to what was actually checked.

The scientific endpoint remains: for original weighted Max-Cut, the lowest fully costed coupling representation (including coefficient storage/memory accesses, arithmetic, shared-scale metadata, controller, p-bit/interface and time) meeting a preregistered original-cut quality target **under specified, evidenced stochastic response**.

## Direct paper-by-paper comparison

| Primary source | Verified claim | Relation to proposed FYP | Confidence / unresolved |
|---|---|---|---|
| S. Yang et al., **250 magnetic tunnel junctions-based probabilistic Ising machine**, Nature Communications 17:5368 (17 April 2026), DOI [10.1038/s41467-026-72020-8](https://doi.org/10.1038/s41467-026-72020-8) | 250 pulse-reset/perturb STT-MTJs + FPGA; Biq Mac Max-Cut, parallel updates, annealing, device-to-device calibration/robustness; main article additionally describes **quantizing accumulated local-field input I** into FIFO access indices in a proposed chiplet architecture | Local-field-output/FIFO-index quantization is **not identical** to codebook/bit width of each stored symmetric coupling J_ij. Thus shared device and graph benchmark do not invalidate proposed J-format study. However it already covers STT-MTJ-Max-Cut and variability per se. | **Main article examined. Supplementary Information NOT retrieved/inspected in this audit**. PMC identifies supplementary file `41467_2026_72020_MOESM1_ESM.pdf`, but retrieval was blocked. A definitive negative claim about its coupling precision experiments is NOT justified. |
| **Precision meets speed through an FPGA-based natively sparse Ising machine for combinatorial optimization**, Nature Communications (2026), DOI [10.1038/s41467-026-75119-0](https://doi.org/10.1038/s41467-026-75119-0) | Reported comparison of **Int8 quantized** simulated-bifurcation Ising against **Float32**, with independent graph distributions and hardware/memory throughput; solver parameter tuning affects quality | **Direct precision-vs-quality/cost prior art**. We must not claim first Ising quantization or first precision-vs-Max-Cut study. Different solver (bifurcation), different hardware (FPGA) and format width/control from proposed STT-MTJ low-bit FP/INT/BFP interaction. | Main paper indexed/verified; Supplementary Figure 12 and Note 5 not yet independently audited. |
| D. Volpe et al., **A Scalable and Resource-Efficient Pipelined p-Computer for Probabilistic Ising Machines**, Advanced Intelligent Systems (25 Aug 2026), DOI [10.1002/aisy.70521](https://doi.org/10.1002/aisy.70521) | Pipelined FPGA p-computer, coefficient/bias memory and variable fixed-point widths; example 512 spins at 16-bit, 1024 at 10-bit, 2048 at 2-bit, reporting resource/throughput tradeoff | **Important p-bit precision/hardware prior art**. Hardware precision and storage tradeoff are not novel by themselves. Low-bit float-vs-matched-INT/BFP quality under STT-MTJ response remains an unverified but plausible narrower gap. | Abstract/full article accessible in part; exact coupling-format analysis should be checked before first-claim wording. |

## What has actually been learned (rather than merely listed)
1. **STT-MTJ technology + Biq Mac Max-Cut + device variability** is ALREADY demonstrated experimentally. Do not claim those elements as independent novelties.
2. **Quantization and reduced-precision hardware** in Ising solvers and p-computers are ALREADY studied. Do not claim first numerical-precision investigation.
3. The proposed **specific data path** must be made explicit: original J weights -> symmetric quantized FP/INT/BFP J storage -> local-field accumulation -> pulse probability transfer -> returned original-cut quality -> end-to-end implementation cost.
4. The strongest plausible contribution is a **response- and resource-dependent selection rule** for low-order formats including a robust matched baseline, not unconditional FP superiority.
5. Our NUS 936-run ideal Gibbs CAL pilot establishes a candidate FP6 precision knee only in one dense wide-range graph; it **cannot** prove superiority over INT/BFP or novel device-aware architecture.
6. The literature's quantizer of accumulated local-field I is distinct from coupling J format, but this distinction does not preclude them analyzing J storage in supplementary implementation. **The supplementary file has not been inspected**.

## Specific follow-up with a STOP condition
**One bounded literature follow-up:** inspect **Supplementary Notes 1–4 and 8–12** of Yang et al., especially coupling storage format, MAC coefficient precision, energy/controller cost and calibrated device curves. If J codebook or low-bit representation studies are reported there, update this collision matrix and narrow the claim. Do NOT re-run any solver to compensate for not having a PDF.

Once source limitations are resolved, move to **one bounded format × response test**, distinguishing device-sourced (E3) from explicitly illustrative (E2) parameter variation; do not label one nominal sigmoid as a validated residual distribution. Then **cost only formats that meet an original-cut quality threshold**. This preserves the user's rule: scientific uncertainty -> minimum experiment -> review -> GO/STOP; no endless experiment/configuration search.

## Closure for this decision
- **Evidence:** direct main-paper check + closely relevant 2026 quantitative precision and FPGA p-computer literature.
- **FYP alignment:** yes; novelty claim calibration, no benchmark change.
- **Opportunity cost:** a small literature audit, not a new codebase or solver sweep.
- **Stop condition:** if credible published matched STT-MTJ low-bit FP/INT/BFP coupling design-quality-cost rule already exists, stop presenting that rule as novel; reinterpret new work as replication or narrow specific physically supported design difference.
- **Decision:** **GO with existing locked FYP; preserve pending Supplementary review as explicit uncertainty.**

## Scope clarification — device nonideality is not required for low-bit FP value (7 Nov 2026)

**Correction to framing:** A response-dependent *rank reversal* is **not necessary** for the contribution. Well-calibrated STT-MTJs still see the quantized local field from stored `J_ij`; calibration of the voltage-to-probability transfer does not recover erased/rounded coupling information. The primary result sought is a conditional **original-cut quality versus fully accounted implementation/whole-solution cost** selection rule for matched low-bit FP/INT/BFP coupling formats across specified response conditions. Format-by-response interaction is an informative secondary robustness/operating-condition diagnostic, not a prerequisite for a valuable result.

**Evidence boundaries:** real post-calibration residual data -> results under that sourced device model (subject to its coverage); expressly chosen hypothetical gain/offset parameters -> **E2 sensitivity only**, not device-validated robustness; nominal calibrated sigmoid -> ideal E1 equivalence only. Reconstructed **pre-calibration** device spread must never be called measured **post-calibration** residual spread.

**Fairness/STOP:** compare original-cut absolute gaps and preregistered quality target (not only paired differences against a possibly degraded FP64); use common graph/seeds and persistent, shared device realizations across formats; matched coefficient scales/metadata; full memory/arithmetic/controller/p-bit/interface energy, time, area, retries. A fixed six-bit screen cannot establish where the best bit-width knee moves. Absence of a proven interaction only stops *interaction-specific* claims; it does not stop the locked FP representation FYP. Existing prior-art priority qualifications and the pending 250-STT-MTJ Supplementary audit remain unchanged.
