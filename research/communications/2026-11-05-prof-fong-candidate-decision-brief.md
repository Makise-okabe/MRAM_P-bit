# Discussion brief for Prof Kelvin Fong — 5 November 2026

**Research-stage decision, not a thesis result.** Prepared from user-executed NUS E11C and earlier explicitly synthetic E01/E03/E09/E10 experiments. Research direction is NOT approved by the supervisor. The original FYP topic involved precision, hardware nonidealities, and reliable MRAM compute/inference. The current proposed physical array remains 256x256; the older 4x4 tile is a reusable *intra-tile extracted* building block with ideal joins, NOT a physically extracted 256x256 macro.

## 1. Newest verified electrical evidence — E11C

User executed `experiments/e11c_two_state_model_spectre.py --bias-mv 1.0 --run` on NUS Singularity, Spectre 23.1.0.403.isr6; all four cases exit 0, zero warnings. Raw outputs saved privately under `~/mram_private/E02_256x256/E11/E11C_model_only_20261104T115718_694/`.

Two *student Verilog-A behavioural models* gave the same direct two-terminal 1 mV DC currents:
- `mtj_read`: state 0 -1.0e-7 A source current; state 1 -2.0e-7 A.
- `mtj_read_v0`: state 0 -1.0e-7 A; state 1 -2.0e-7 A.

From inspected model equations: Rp=5 kOhm, TMR=1, state 1=P, 0=AP (10 kOhm). The current sign is the voltage-source reference convention. The shown model equations implement fixed resistances controlled by the `p_state` parameter. **No transistor, BL/SL/WL parasitics, ADC, multibit signed coupling operator, switching, stochastic MTJ dynamics, read retention, or analog Ising-field computation were validated.** A 1 mV numerical diagnostic is not a validated nondisturb operating point.

Historical local scripts `cim_c03_dot2.py`, `cim_c04_dot4.py`, `cim_c2_fanin.py` mention VREAD=0.05 V and WL=0.8 V, but these values were used in older test setups, not newly demonstrated as a safe 256x256 target operating point. Reuse their circuit topology/examples only after audit; do not reuse retired currents as target evidence.

## 2. Paths on the table

**Directions 1+2 — Mapping + failure estimator.** Evidence: real frozen-MNIST E01 traces and six resident row maps; under a declared synthetic persistent-error and quantized-decoder model, row grouping changes read counts and arithmetic MSE. The exact combinatorial count bounds were added. E03S implemented Gaussian marginal scoring and first-order cross-read Hermite approximation, but E03T finds no convincing fixed-budget benefit over marginal-only score or equal-budget MC; rare full-network inference failure is untested. A physical read/ADC kernel with wiring/loading remains unvalidated. More parameter sweeps would not demonstrate novelty. The desired output is a practical one-map algorithm + cheap scorer that beats sorting, CAR, strong calibration and matched-budget sampling on held-out inference failure per total cost.

**Direction 3 — Ising field-maintenance.** Interest in time-evolving spin decisions; E09A exactly verifies digital incremental fields, E09E shows reversal-pinned cache is equivalent to ordinary locked cache with the same bypass, E09F reproduces exact update decisions under assumed error bounds but requires large hypothetical analog/digital cost advantage, E10A synthetic selective asymmetry correction has no advantage over simple full symmetrization/error-ranking. E11C verifies a static resistive MTJ model only; this is storage for J, not a stochastic spin device. The research question is whether an actually implementable MRAM read operator yields a measurable and consequential local-field error structure that a distinctive controller can address more economically than accurate digital incremental computation and conventional calibration/refresh.

**Current outcome:** no validated thesis novelty or winner. Mapping/predictor is the safer provisional direction because of task evaluation infrastructure; Ising is the more exploratory alternative under the user's interest. This is a recommendation for supervisor discussion, not a project lock.

## 3. Two supervisor decisions to request

1. **Which computation is a credible FYP target with the accessible device model?** Ising coefficient read + digital field maintenance, or a demonstrable analog CIM local field with signed couplings, validated readout and acceptable ADC/periphery cost? Would Prof Fong expect a dynamic stochastic MTJ model, or is a stable-MTJ storage array with external stochastic digital spin engine appropriate? What PDK/source/licensing boundaries apply?
2. **What is the expected distinctive technical contribution for CA2?** Is the covariance-aware static mapper plus a validated fast failure scorer (if it outperforms strong comparators) closer to the original proposal, or would a new Ising field-maintenance policy be feasible within the FYP scope? Which specific physical extraction/readout and algorithm baselines would he consider necessary?

## 4. Concrete next gate, not an open-ended implementation request

- Reuse `cim_c03_dot2.py`/`cim_c04_dot4.py` as *topology leads*, verify authorized NFET+custom-MTJ model interface and previously tested read bias on a fresh small array. Measure distinct P/AP currents, common sense path, simultaneous rows and near/far order, and current nonadditivity. These are preliminary circuit results only, not 256x256 physical nonidealities.
- If an analog Ising-field operation is feasible: freeze one low-cost algorithmic rule before fitting to actual circuit response, compare exact digital incremental, calibrated/symmetrized readout, and fixed/periodic correction at a matched total budget. Reject if no distinctive operating-point advantage.
- Otherwise propose the mapping + predictor study: repair the joint decoded covariance estimator's high-correlation failure; compare with exact equal-time MC and full-network quality under a physically supported read/ADC kernel, with the legal-count decoder and tuned CAR/zero-rate baselines.
- Choose **provisional** topic after these feasibility and algorithm gates, not after broad synthetic parameter sweeps.

## 5. Spoken 45-second summary

“I'm exploring two related directions for the MRAM FYP. First, a reliability-aware row mapper and a cheap failure estimator: I used frozen MNIST traces to quantify a read-count versus decoded-error tradeoff, but my current covariance score has not beaten simpler estimators at a fixed cost. Second, an Ising local-field controller: I verified the exact digital update baseline and tested several specific correction rules, but caching and basic correction were already matched by strong existing controls. I have now verified two student Verilog-A MTJ models in Spectre at both resistance states, but they are only static resistive models so far. I would like your advice on whether we have a credible analog MRAM Ising-field read operator and which method would be sufficiently novel and feasible for the remaining FYP.” 

## Evidence discipline

All model-only E11C currents came from user NUS logs and have a private source directory; no current was generated by the assistant. E03/E09/E10 software outcomes involve synthetic perturbations and cannot establish GF hardware error, inference failure, silicon energy, or a research novelty pass. No third-party proprietary model or deck is included here.
