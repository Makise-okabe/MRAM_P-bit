# E11E — Cross-segment adaptive field-read falsifier and Spectre model-only check

Date 4 November 2026. **Independent assistant-executed software experiment only so far; NUS Spectre E11E remains not executed.** This note is based on a freshly written 485-line Python3.6-compatible stdlib script, which includes self-tests, a signed-Ising benchmark and model-only Spectre deck generation/current parsing. Full executable source + results supplied as a conversation download `e11e_ising_spectre_validation.zip`, SHA256 `fd6e5dbb6d71230beb3f9e855006f89befa953a9f2bf0f1deb06e6faad636d93`, source SHA256 `863f1d3f0ce41801caf51fa7a4d1c09725e44856a414927bd80f42ce0aae218f`. The ZIP source itself has **not** been committed to GitHub.

## E11E synthetic signed Ising benchmark

- Six policy arms at matched intervention opportunity, plus exact digital incremental and all/no-split controls: exact, no split, split-all, random 25% split, near×far count, centroid, full-mask suffix Q and weight-blind cross-segment interaction `2 n_far M_near`.
- Twelve spins, signed J in {-1, 0, +1}, **idealized differential conductance columns** (positive and negative coefficients stored in separate columns), stable behavioural Rp 5k values and ideal OFF/disconnect. Exact Kirchhoff N=12 passive ladder, `r=25 Ω/segment` *assumed*; `V=1 mV` model-only diagnostic. No ADC, NFET, BL/SL PEX, actual switching, stochastic MTJ, periphery/energy.
- CAL graphs disjoint from five DEV graph instances, forty independently seeded restarts per graph = **200 paired runs per arm**, eight sweeps = 96 attempted spin updates each. Common external random schedule and uniform draws. Online selector has exactly four extra split decisions per block of 16 attempts, so every selective arm consumes 240 idealized analog source reads/restart; no future mask look-ahead.
- Exact digital arm uses correctly audited **incremental local-field cache**, with average 67.6 initial nonzero coefficient terms + 102.8 update terms. Coefficient terms and analog source reads have NOT been put on an equal physical cost scale.
- Exact optimum hits /200: digital 150, no split 151, split all 146, random 151, near×far count 150, centroid 150, suffix Q 149, cross moment 151.
- Mean absolute field error: no split 0.2195; all split 0.1768; random 0.2100; near×far count **0.2092**; cross moment **0.2093** (normalized local-field coefficient units).
- Online CAL threshold often exhausted intervention budget inefficiently; mean forced quota decisions ≈15.9 /24 for cross moment vs 15.4 /24 for count. Better causal budget scheduler might be needed; **do not tune it on DEV**.
- Graph-cluster paired bootstrap 95% interval for cross minus count optimum-hit rate [0, +0.015] on this small sample; far too little to claim distinctive benefit.
- `r=0` exact linear null on three independent evaluation graphs × 12 restarts: all eight arms produced identical exact-best solution/outcomes on *every paired restart*. Selftest also verifies the cross-segment Q identity over all 495 four-active-row masks, one-shunt KCL and a PSF ASCII parser test fixture.

**Conclusion:** The earlier E11D analogue-current prediction improvement does NOT transfer automatically to Ising decisions. Reject a claim of superior Ising success for the current online trigger under this test. E11E is a useful model falsifier, not a thesis selection win.

## Next NUS Spectre step (not executed yet)

The same script includes `spectre` subcommand. It constructs 31 P/AP mask patterns (9 standard near/far checks, A/B matched-count/centroid witness, 20 independent deterministic patterns), each with FULL, NEAR-only and FAR-only cases. This yields 93 separate 12-segment ladder circuits in **one Spectre DC deck** with 1 mV source, *assumed* 25 Ω/segment wire, and the verified local student `mtj_read_v0` Verilog-A model (`p_state=1` P, `p_state=0` AP). It requires the exact user-provided local student source SHA and never copies model code. A private NUS run saves source currents, measured FULL/SPLIT differences and KCL solver parity.

This is **only a Spectre numerical verification of a constructed resistive ladder**; it is NOT a GF access-transistor+MTJ cell, correctly extracted 256×256 BL/SL/WL RC, safe read, ADC, Ising field computation or a valid physical novelty claim.

Before a real Ising track decision, audit `cim_c03_dot2.py`, `cim_c04_dot4.py`, `cim_c2_fanin.py` locally and create a *new* validated access-NFET+student-MTJ read experiment with actual shared wiring/loads, signed encoding and read periphery. Compare full-sym/SEC, position calibration, count-based adaptive split, and exact digital incremental on independent masks at matched total costs. Keep mapping+predictor as the more mature fallback.

## Reproducibility / integrity
The runnable ZIP is delivered with this conversation, not automatically present in NUS or GitHub. Do not use old eight-cell or one-column numbers as target evidence. The MATLAB/PSF test fixture in the selftest is synthetic parser verification, not fabricated Spectre output. Source and zip hashes are recorded above.
