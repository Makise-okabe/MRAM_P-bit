# ADR-0004 — F3 first bounded method candidate; E03Q decoder sensitivity

**Date:** 4 November 2026 (SGT)  
**Decision:** Development priority, **not** novelty certification or final thesis lock.

## Accepted from uploaded 17-page working draft
1. Retain original proposal title and precision/nonideality regime analysis as the governing subject.
2. Prioritize F3 covariance-aware **one resident row permutation** for a bounded screen. F1 estimator remains supporting; F7 Ising cache/persistence remains conditional and independent. Other F1–F7 families are not retroactively declared disproven.
3. Require two random controls: one fixed seeded random mapping and best-of-equal-budget random search. Compare channel shuffling, CAR, activity balancing, calibration/reference tuning and adaptive read scheduling. No hidden per-input map oracle.
4. Treat \(R(P)=E[(b^T e)^2]\) as reconstructed-MSE **surrogate**, not exact neural failure probability.
5. Before a mapping claim, assess ADC transfer, code convention, saturation, calibration and reference placement (E03Q), then physically validate the new 256×256 target E02.
6. External assistant reports of task or Ising results are unreplicated leads, not experiments completed here.

## New observation (not in the uploaded draft)

Executed software-only E03Q with independent calibration and evaluation synthetic chips; phase calibration substantially changes finite-ADC reconstructed errors. See \`research/experiments/2026-11-04-E03Q-finite-adc-screen.md\`.

**No target circuit evidence.** All previous physical read-current data remain excluded. The E03M fixture and E03Q are constructed, not foundry-calibrated. The previously mentioned digits256 E01 pilot is a separate exploratory workload, not a target-array device experiment.

## Gate and falsifier

The next *physical* experiment is E02: an authorized cell/access model, distributed BL/SL/WL interface, drivers and nominal patterned-read/settling checks. Reject any electrical claim without held-out target validations. Reject F3 as a new method if tuned random/zero-rate/CAR/shuffling/adaptive-sensing baselines match useful quality/cost after accounting for setup and routing. Keep Ising E09B for a specific field-operator diagnostic only.
