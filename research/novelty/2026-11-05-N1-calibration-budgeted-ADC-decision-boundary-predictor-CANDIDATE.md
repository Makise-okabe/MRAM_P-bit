# STATUS — RETIRED AS CORE NOVELTY (2026-11-05)
User relayed Prof Kelvin Fong's advice to avoid sensing/read-margin research due to heavy prior art. The candidate below is too close to ADC-threshold sensing-margin prediction and reference/precision optimization, so it **must not remain the proposed core novelty**. Preserve as historical rejected reasoning and an optional circuit-level measurement tool. See [ADR-0008](../decisions/ADR-0008-deprioritize-read-margin-novelty-focus-on-computational-failure.md) for a more distinct, still-unvalidated system-level research hypothesis about correlated signed-bitplane errors and neural inference. **No new core algorithm has been demonstrated or approved.**

---

# Novelty hypothesis N1 — Calibration-budgeted, decision-boundary-aware physical failure predictor
**Prepared 2026-11-05. STATUS: candidate only; NOT invented, validated, approved or claimed novel.**
**Main FYP:** Characterizing Reliability and Failure Regimes of Memory-Centric Neural Inference Under Coupled Precision and Hardware Non-Idealities.

## Why current E22–E24 results are NOT the novelty
- Physical current IR-drop is standard. A quadratic downstream-load moment `Q_x=sum_l(sum_(j>=l)x_j)^2` is physically motivated but not established as an original algorithm. Its familiar structure is a first-order line dissipation/loading effect.
- User-executed E24 3168 GF transistor current cases (32-branch one-access-FET student MTJ model, **assumed** wire Rs, mathematical ADC) showed 7bit at assumed R5: raw 124/528 wrong counts, near59, centroid26, Q-transfer7. The Q spatial coefficient was frozen from m16 CAL and transferred across m8/12/20/24; BUT per-m/R CAL count centroids and ADC fullscale were newly fitted for all policies. Thus it is *coefficient* transfer, not calibration-free ADC operation.
- Earlier FYP completed a separate 4x4 GF local-floating **2T1MTJ PEX**, which has not yet been used in E24. E02 256x256 ideal-joined topology is NOT 256x256 full PEX.
- Closest relevant work: NanoCiM weight-aware X-address scrambling for IR-drop (DOI 10.1109/TCASAI.2026.3661436); DIB-CIM SOT-MRAM dynamic input block and ADC resolution (DOI 10.1109/TCSI.2026.3726936); adaptive memristor ADC thresholds (https://www.nature.com/articles/s41467-025-65233-w); CIM nonideality calibration and DVAQ. Existing systems also predict/correct nonidealities; mere composition is not unique.

## Candidate research question (conditional)
**Can a small set of physically extracted 2T1MTJ calibration measurements, augmented with known input-position and extracted interconnect topology, predict *which ADC count decisions fail* under joint parasitics + MTJ variability, across unseen patterns/chips/array regions, sufficiently well to reduce needed calibration/reference settings or ADC effort at fixed inference accuracy?**

A failed physical topology gate requires rejecting or reformulating candidate, not silently replacing extracted circuit with the easier E24 surrogate.

## Specific proposal N1: decision-margin + physically bounded uncertainty
Define trained physical current model for count hypothesis `n` and input-mask `x`:
 `I_hat(n,x ; theta, PEX) = I0_hat(n,m,k) - beta_PEX * Q_PEX(x) + higher-order residuals if actually justified`.
`Q_PEX` must follow actual BL and SL extracted network/branch conductances; E24 input-only suffix Q is a first comparator, not assumed correct for a local-floating dual-access structure.
For mathematical ADC b with programmed thresholds `T_{n-1/2},T_{n+1/2}`, define the *predicted decision margin*:
`M(n,x,b) = min(I_hat(n,x)-T_{n-1/2}, T_{n+1/2}-I_hat(n,x)) - Delta(n,x)`,
where `Delta` is empirically calibrated uncertainty from fixed-chip MTJ resistance variation, fit residuals, and read/ADC offsets. The margins are signed, not guaranteed confidence bounds unless `Delta` coverage is separately established. At runtime the unknown true n is unavailable: evaluate each possible n hypothesis from known x + measured low-bit ADC code (or conservatively over plausible n), NEVER use DEV true count as feature.
Candidate DESIGN RULE chooses least costly bit depth/reference bank or spatial correction by ensuring estimated failure probability or conservative margin meets a predetermined error target; if a second read/converter reference change is required, charge physical cost. A simpler **design-time** safe-configuration map (no runtime adaptation) may be more feasible and less overhead.

## Direct distinction to test
- NanoCiM minimizes IR-drop variation via row scrambling; N1 would predict **count-threshold-crossing risk after full ADC and correction**, without changing row placement.
- DIB adapts input distribution, block and ADC precision; N1 would use **extracted position/BL–SL physics and independently validated count-boundary uncertainty** to decide **where/when** precision or correction is needed, and account for calibration effort. NOT enough to relabel I3D as Q.
- Conventional ADC calibration improves a known current distribution. N1's claimed added value must be **transfer to unseen positions, chips and physical geometry using fewer training measurements/reference settings**, or a demonstrably better fixed-error cost tradeoff. This additional value has not been measured.

## Minimum credible falsification plan
1. **P0/P1** recover actual GF 4x4 local-floating 2T1MTJ PEX DSPF and test single- versus parallel-word-line read with identical sense path. Verify write-disturb/read assumptions, measured extracted BL/SL R/C. Do not continue if topology does not support the proposed analog sum.
2. **P2** representative physically extracted 16/32-row 2T1MTJ segment; verify effective current model and residuals with *independent* mask patterns, multiple k, multi-column coupling where relevant. Establish real physical R scale, not postulate 5Ω.
3. **P3** fix per-chip MTJ resistance variation (nominal 5% is an assumption until validated) plus process/mismatch where available; use independent chips and residual coverage checks. Explicit ADC transfer/cost.
4. **P4** benchmark frozen N1 predictor vs (i) fixed b/calibration, (ii) CAL per-count centroid/offset, (iii) near, (iv) centroid, (v) Q correction, (vi) best simple calibrated margin/noise model, (vii) DIB-style input-aware ADC policy where implementable, all with matched CAL measurements/energy/latency and no hidden true n.
5. **P5** full signed W4A8 MNIST with all trained layers/bias and valid physical bitplane occupancy; report count error, predicted failure probability/margin, task accuracy and cost separately.
6. Falsify N1 if ordinary Q+per-condition CAL or a simple margin predictor ties at comparable cost, or if extracted topology shows negligible nonideality in operating range. In that case, present rigorous FYP failure characterization as engineering contribution only after supervisor scope agreement.

## Presentable claim today (exact scope)
"We have a GF access-transistor *model* screen showing that a physically motivated input-position statistic transfers its correction coefficient to new activation populations, producing 7/528 versus centroid 26/528 misdecoded counts under assumed 5Ω/segment and mathematical 7bit ADC. This is neither extracted physical MRAM nor demonstrated algorithm novelty. Our proposed distinctive next step is to characterize extracted-2T1MTJ failure margins and test whether a limited-calibration model can predict errors and configure precision better than ordinary current calibration. The research question is explicitly open."
