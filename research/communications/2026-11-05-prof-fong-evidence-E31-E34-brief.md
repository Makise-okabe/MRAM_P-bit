# CORRECTION FOR PROF FONG — 2026-11-05, AFTER E31; NO WHOLE-MACRO LOW-ERROR CONCLUSION

**Do NOT say “MRAM has too little error” or “we should drop recovery because Q gets 0/36”.** We have **not** demonstrated reliability of the target 256×256 macro. E31's “256” is **row depth**; only 4 columns were jointly circuit-solved, 24/256 rows active, n11–13 in C0, one nominal fixed resident P/AP distribution, GF compact NFET + static student MTJ, **ASSUMED** 0.25Ω/segment BL and 0.25Ω common SL, ideal row-gate and continuous DC measurement. Global decoder **15/36 wrong** (hypothetical BL resistance); frozen CAL-Q **0/36** (a *particular* corrected nominal regime). No physical 1T1 PEX or realistic ADC/variation/timing; the 36 samples are input masks, not independent chips.

The existing **real frozen E01 W4A8 workload** (software grouping, not confirmed physical simultaneous WLs) already reports CAR active-row maxima **32** for 32-row groups, **63** for 64-row groups and **110** for 128-row groups (and means 8.708, 15.282, 25.190 among nonempty reads). Therefore **m=24 is not a universal operating point**. The user is right to insist on wider activity ranges and full 256x256 electrical sharing. Load and width are not interchangeable: additional columns only change a given read through physically modeled shared return, supply, wordline, sensing, coupling and drivers.

**Immediate runnable diagnostics** are E33 mathematical ADC precision plus E34 all-four-column existing GF read vectors (`bash experiments/run_e33_e34_nus.sh`) and E35A frozen E01 packet activity schema/histogram audit (source [E35A](../../experiments/e35a_frozen_e01_activity_audit.py), not yet user run). **E32 extracted 1T1-specific metal R/C is the binding physical milestone**. High-m GF test generator / width scaling needs a new preregistered model and is NOT already implemented. Q-feature, ADC, calibration and digital-recompute costs must be counted before declaring “cheap”. MRAM-CIM prior work already includes statistical BL/SL error compensation and ADC offset correction, e.g. [Roy et al JSSC 2025](https://doi.org/10.1109/JSSC.2024.3442013) and [Roy–Shanbhag JxCDC 2024](https://doi.org/10.1109/JXCDC.2024.3381888). Simply correcting row position is not automatically novel.

**Suggested short speaking paragraph:**

> “My earlier 256-row, four-column GF-transistor simulation found substantial position-dependent decoding errors under assumed wiring, but a Q-based calibration trained on only nine patterns corrected 36 new C0 masks. That does not mean the full 256-by-256 MRAM-CIM system is reliable or does not need advanced algorithms: only 24 rows were active, with three target counts, and no real ADC, mismatch, timing or physical wire extraction. In fact, the frozen neural workload has candidate read-group activities reaching 63 and 110 simultaneous logical active rows, so we have not examined the full operating range. I am now testing converter quantization and cross-column calibration, auditing true workload activity, and advancing physical 1T1 interconnect extraction. The contribution question remains whether *physically justified post-calibration signed neural-computation failures* can be predicted and mitigated better than strong calibration or conventional equal-cost correction.”

[Full decision and evidence boundaries](../decisions/ADR-0011-E31-not-whole-256x256-workload-activity-and-physical-gates.md).

---

# Prof Fong meeting brief — 1T1MTJ MRAM-CIM research pathfinding (5 Nov 2026)

**Prepared before E33/E34 user execution.** A transparent narrative for the three ORIGINAL directions, completed NUS evidence, negative controls, exact next experiments, and missing novelty proof. The complete NUS Spectre and licensed PDK files remain private; only safe, high-level evidence goes in this public research repo.

## 1. Three top-level directions, one active investigation

- **F1 inference-failure prediction — CURRENT PRIMARY.** Can inexpensive CAL-informed known-input features predict when nonideal 1T1MTJ-CIM read currents become wrong decoded counts, signed partial sums, and eventually wrong DNN predictions? Does a policy guided by this predictor improve reliability *at equal total correction/digital computation cost* compared with standard margin/Q/near-far/independent scores?
- **F3 reliability-aware mapping — RESERVED MITIGATION.** Keep a resident mapper only if it beats simple zero-rate sorting, CAR, ordinary spatial calibration and matched-budget search on physically plausible signed-W4A8 outcomes. Early mapping controls did not establish robust extra benefit.
- **F7 Ising computing — PAUSED SEPARATE IDEA.** Existing exact incremental digital fields and cache controls remain strong; no distinct physical advantage/cost-quality improvement yet shown.

**Q correction, ADC adjustment and N2 selective digital recomputation are candidate methods within F1, not fourth/fifth thesis directions.** [Formal hierarchy ADR-0010](../decisions/ADR-0010-three-direction-hierarchy-after-E31.md).

## 2. What was actually measured/simulated

| Study / date | What NUS actually did | Strongest supportable conclusion | Strict limitation / next gate |
|---|---|---|---|
| E19–E24, 4 Nov | Actual GF access-NFET + student's static MTJ nominal Spectre read-current studies; 32-row model with assumed BL resistor | Position-dependent read distortion exists in the constructed circuit; simple spatial/centroid/Q correction is strong | Not 1T1 physical PEX or complete 256x256 |
| E28S, 5 Nov | Four columns simultaneously sharing **assumed** SL resistor (0.01–20Ω), GF transistor currents solved | Neighbor activity changes C0 current; at 20Ω C0 high-v-low neighbor shift −38.79nA | 0/28 wrong counts in tested patterns; no physical source-line RC or bitplane covariance |
| E30, 5 Nov | **256 rows ×4 columns, 1,024 GF NFET+MTJ branch pairs** per scenario, 24 rows active, three arms (ideal; assumed distributed 0.25Ω/segment BL; same BL plus 0.25Ω shared SL) | Continuous nominal current distortion depends strongly on activation row location. Same n12 low-v-high region ~9.486µA = ~5.17 ideal count intervals | Original global decoder wrong 6/9 DEV in both assumed-R arms; NOT physical BER; one nominal chip |
| E30P, 5 Nov | CAL-only baselines on the same actual GF currents | CAL area-offset, area-count bank and input-Q each 0/9 DEV; naive 6/9 is mostly *calibratable* spatial bias | 9 CAL, 9 DEV, not independent chip/device draws |
| **E31, 5 Nov COMPLETE** | Frozen E30 Q calibration (9 CAL), **36 new GF read masks**, 18 familiar +18 new spatial families, same resident weight map | With assumed BL/SL: pooled global decoder **15/36 wrong**, categorical area-offset **6/36**, **Q 0/36**; ideal-wire all 0/36 | Still C0, m=24, n11–13, one nominal weight map; no physical ADC, process noise, PEX, full W4A8 |
| **E33 PENDING** | Reuse E30/E31 currents through PREDECLARED hypothetical ideal ADC (4/5/6/7/8/9/10/12 bits), fullscale fixed by E30 ideal CAL only | Test whether finite quantization creates post-Q count failures and whether Q beats continuous row-centroid/near-far baselines | Model ADC only, no real converter, no Spectre rerun |
| **E34 PENDING** | Reanalyze the four actual simultaneously solved GF read columns from E30/E31, not just C0, using nine E30 CAL per column | Test column-specific Q/mean-row/near-far linear calibration on **144 E31 column-read observations**, including n extrapolation | Four columns are NOT the four signed-W4 bitplanes; not 144 independent chips |
| **E32 PHYSICAL PENDING** | Actual new 1T1-specific GF CMOS+BL/WL/SL metal routing and extracted RC; external static MTJ model if necessary | Establish if 0.25Ω/segment and other modeled effects are *physical* under the selected 1T1 architecture | Must not borrow old 2T1 local-floating-SL PEX as 1T1; DRC/LVS/xACT support must be checked |

**NUS source E30 frozen SHA256:** `f5646f0248207df56f7b9c0bb53fb126fa6200bc42f5a7ba3e881df1204aeb52`. Actual E31 private file `~/mram_private/E31_1T1/E31_256x4_20261105T033721Z_2792/E31_RESULTS.json`. C0 Q 0/36 from original CAL is a **nominal constructed-model generalization**, not an empirical BER confidence interval.

## 3. Precise causal story

**Observed:** The constructed 256-row BL ladder produces a position-dependent current bias. As a result, a *global* count-to-current decoder mixes signals from distinct row regions and misclassifies them. **Falsification:** Before proposing an expensive recovery controller, test conventional CAL-only spatial corrections. E30P and E31 show continuous Q calibration removes those particular errors, including unseen row-distribution masks. This eliminates the naive novelty story “MRAM has spatial errors, so we invented a joint recovery algorithm.”

**New uncertainty:** Will ADC quantization, calibration sparsity on different resident columns, CMOS/MTJ variation, or layout-extracted wire/driver constraints leave harmful signed-computation residuals after strong cheap calibration? If not, physical and conventional calibration may already be adequate and F1 should deliver honest negative/characterization conclusions instead of artificial errors.

**Potential F1 contribution (not yet established):** A deployable low-cost predictor of *post-CAL actual signed-W4A8 inference failure* using physically grounded and runtime-observable features, optionally assigning selective recomputation *at equal cost*. Need to beat CAL-Q, mean/near-far, ADC-margin prediction, independent scoring, optimized significance-order correction, and no repair. N2 mathematical joint selector and its cost-adjusted tie with contextual prefix is software proof-of-concept only, not a reported physical advantage.

## 4. What to say in the meeting (≈90 seconds)

> Prof, I have narrowed the earlier three alternatives — reliability-aware mapping, inference-failure prediction, and MRAM Ising — to focus primarily on failure prediction for reliable 1T1MTJ neural computation. Mapping stays as a possible mitigation; Ising is paused because I have not yet demonstrated an advantage over strong digital updates.
>
> I progressed from a 32-row constructed GF transistor read circuit to a 256-row, four-column network, using actual NUS Spectre transistor currents and a static MTJ model. The current interconnect ladder is still assumed, not physical PEX, and the model is not a complete 256-by-256 physical macro.
>
> A global current-to-count decoder showed large position-dependent errors under the assumed 256-row bitline resistance. But once I fitted conventional position-aware correction on nine calibration patterns, the Q-based decoder made no mistakes across 36 new input patterns, including spatial distributions absent from calibration. This was an important negative control: the errors were not evidence that a complex digital-recovery algorithm was necessary.
>
> My next experiments test two remaining weaknesses of that conclusion: whether finite ADC quantization changes the result, and whether it generalises from the first column to all four distinct resident weight patterns. In parallel, I need a true 1T1-specific layout or valid metal-only RC extraction to replace the assumed bitline resistance.
>
> The proposed contribution is still conditional: if physically grounded residual errors affect the reconstructed signed W4A8 neural computation, I will test whether a lightweight failure predictor and cost-constrained correction policy beats standard calibration, marginal error predictors and significance-first recomputation. I am deliberately not claiming that this algorithm has already won.

## 5. Five questions Prof may reasonably ask

1. **Where are physical MRAM results?** They do not exist for the new 1T1 physical array yet. GF transistor compact models are real, but 1T1 wire geometry and MTJ layout qualification remain missing. E32 is the gating step.
2. **Why 0.25Ω/segment?** It was a declared sensitivity assumption to expose spatial mechanism, not a measured/calibrated value. We will replace it with actual extracted R/C; do not extrapolate the 5.17-count shift to a foundry macro.
3. **Why 256×4, not 256×256?** It tests the full 256-row BL depth and four columns at manageable circuit scale. A full macro needs physical WL/BL/SL network and credible drivers; more schematic instances alone do not equal full PEX.
4. **Is Q new?** Not claimed. It is a strong conventional/low-cost spatial calibration control. E33/E34 test its limitations; only a better *inference-failure prediction and decision at equal cost* could become an original method.
5. **Where is the neural-network result?** E01 W4A8 FC1 arithmetic is verified, but there are no legitimate physically aligned four-plane error traces or full-network noisy outputs from this new 1T1 model. We must not assemble an invented covariance from unrelated columns.

## 6. Immediate NUS command and evidence workflow

```bash
cd ~/MRAM_Path_Finding
git pull --ff-only
bash experiments/run_e33_e34_nus.sh
```

Each script is committed before experiment execution, so the outcomes cannot be retroactively chosen. The runner creates private, timestamped `E33_ADC_SWEEP.json`, `E34_RESULTS.json`, two sanitized `E33_FOR_PROF_FONG.md` / `E34_FOR_PROF_FONG.md` files, and logs; **actual results are NOT yet known**. Paste the safe outputs back into the chat, and update this public evidence log with exact counts/hashes and a decision. Do not upload foundry decks, device model contents, confidential layout files or private library credentials to public GitHub.
