# 2026-11-05 E27B actual null control; E28S four-column GF electrical-coupling experiment

## Why reset the immediate experiment
The user correctly challenged excessive preflights. **E27B is NOT the research hypothesis test.** In actual NUS Spectre, under **nominal GF access NFET + student static MTJ, four independent conceptual columns, 0Ω manually assumed wire**, all 16 m=2,k=2,n=1 cases had the identical current \`8.794641854237579 µA\` to floating precision (maximum within-column spread ~\`3.39e-12 nA\`). This exactly follows from ideal symmetry and is only a **sanity/null control**. No physical 1T1 PEX, joint four-column electrical coupling, stochastic correlation, neural inference, or novel algorithm was demonstrated. Actual private E27B result:
\`~/mram_private/E27_1T1/E27B/E27B_GF_R0_20261105T020407Z_391/e27b_nominal_16cases.json\`.

**Stop repeating R=0 ideal-wire m2/n1 controls.** A researcher needs an observable actual *joint* electrical effect and then downstream compute impact, not another isolated read-margin proxy.

## New E28S — actually simultaneous four-column GF electrical model (PENDING NUS run)
- Code [\`experiments/e28s_shared_sl_four_column_gf.py\`](../../experiments/e28s_shared_sl_four_column_gf.py).
- One-shot [\`experiments/run_e28s_nus.sh\`](../../experiments/run_e28s_nus.sh).
- Reuses exactly SHA-checked E19 v2 GF 22FDX access-NFET + **student static MTJ** source generator, 4 rows each, 7 masks/state-scenarios × 4 columns=**28 branches/cases** in a single DC Spectre deck.
- All four columns in a given scenario share ONE added source-line return resistor; independent return (original E19 generated), shared **0.01 Ω**, **5 Ω**, **20 Ω** arms. These are **ASSUMED R**, NOT extracted RC or a proposed actual GF macro layout. Every other source case/scenario isolated. The four columns use equal ideal read-bias/gate waveforms; **no shared finite-impedance WL** and no BL-to-BL coupling is modeled. Physically **same return node for four columns**, unlike separate E27B independent cases.
- **Strict automatic topology audit:** script finds original independent \`VC####\` sources, traces each FET drain↔source and MTJ top↔bottom (excluding ground), validates exactly 4 NFET, 4 MTJ and 4 direct return-ground contacts for each of 28 cases, then rewires **ONLY** verified conduction-return device ground terminals to a scenario-specific common SL and adds one resistor to ground. Hard stop if topology/pin structure differs; do not blindly manipulate licensed PDK netlists. The PDK and source decks remain NUS PRIVATE.
- Student static model 376B SHA \`1d22984b7be5135c07bb5e392d73aa53e1ad42b7c4bdc6d2fc11bb3f313b9a88\`; verified E19 v2 SHA \`b6bec40bc234fac406d191229146354a5fe47c6969fb6db6a672e607ddf83e54\`; historical **screening** read biases 50 mV and WL 0.8 V are NOT a new read-disturb qualification.
- **Physical hypothesis (model-specific):** holding observed C0 at **m=2,n=1** under unchanged row-selection and P/AP state while changing other columns' \(n\in\{0,1,2\}\) should change C0 current if and only if there is appreciable shared-return interaction under the chosen assumed R. Compare \`NEAR_LOW\` versus \`NEAR_HIGH\` neighbor loading. \`NEAR_MIX_A\` vs \`NEAR_MIX_B\` have equal aggregate neighbor P count and are a control for lumped SL sum; near/far paired controls are also included. If the zero-return circuit already differs, do not attribute deviation to coupling.
- **Strong built-in control:** 0.01Ω return must agree with direct independent ground baseline within 0.1% maximum normalized current; otherwise STOP. \(R_\mathrm{SL}=5,20Ω\) arms are a bounded sensitivity test, not physically justified GF wire resistance.
- Real Spectre current source vectors from all four columns are recorded **jointly**, each scenario sharing an actual source node in the modified simulator deck. Report per-column \`I_coupled-I_independent\`, C0 \`neighbor_high−neighbor_low\`, individual decoded count error via frozen independent ideal count centroids (offline mathematical nearest-level decoder), and an **illustrative** four-plane signed-W4 toy MAC with coefficients \([1,2,4,-8]\). Not the user's full E01 frozen W4A8 MNIST classifier or proof of algorithm improvement. No mismatch/chip variation; therefore a deterministic neighbor effect is **NOT cross-chip statistical correlation**.
- **Data evidence gate**:
  - E28S shows neighbor influence at plausible *assumed* impedance: follow with actual 1T1MTJ 4×4 DRC/LVS/xACT extraction; measure *actual* source-line/BL/WL coupling and available operating bias, then repeat same matched conditions. If no extracted common return geometry, the effect is not justified.
  - E28S shows zero/negligible influence even at 20Ω: drop the simple shared-SL hypothesis; do not expand fictitious errors. Revisit physically extracted effects or other sources.
  - Any count/MAC error in E28S is *an assumed-R prototype*, not new physical 1T1 data.
- After **real** 1T1 layout+PEX and meaningful multi-column vectors with variation, compare conditional-shuffled vs physically joint errors using E26A and the **full** quantized W4A8 model. Do not claim algorithm novelty without a concrete cost-matched mitigation relative to DIB, Dyn-A-Map, NanoCiM and calibration baseline.

## Commands
\`\`\`bash
cd "$HOME/MRAM_Path_Finding"
git pull --ff-only
bash experiments/run_e28s_nus.sh
\`\`\`
**As of commit:** E28S code not yet executed by NUS user; no E28S current results exist. Its Python mock selftest is not Spectre. If the strict topology return-contact audit fails, report the blocker, not an electrical result.

## Supervisor report sentence
"I confirmed the 1T1-like GF transistor ideal-wire control behaves as expected: 16 equal-count cases all gave 8.79464 µA. That is a sanity test, not a contribution. I am now testing a specific electrical coupling mechanism in a four-column simultaneous GF Spectre circuit using explicitly assumed shared-source impedance. Actual 1T1 layout extraction is required before treating the coupling amplitude as a physical GF MRAM result. The research outcome will be whether such coupling materially changes signed multibit MAC failures and motivates a new computation-level algorithm beyond established approaches."
