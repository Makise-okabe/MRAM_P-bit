# E03Q: finite ADC and reference placement — executed illustrative pilot

**Date:** 4 November 2026 (SGT).  
**Status:** completed as a **constructed-model** experiment, not as E02 or a physically validated MRAM readout.

## Hypothesis

The mathematical E03M covariance comparison uses an ideal count decoder. A real finite ADC changes the nonlinear code boundaries; the same theoretical mapping difference may change magnitude or disappear. Before claiming a covariance-aware mapper we need a declared ADC transfer and fair calibration.

## Frozen experiment

The full 256x256 fixture (generated afresh from seed 4107) uses four 64-row logical groups, two activation bit cycles, 8 vector reads and 16 active rows per read. **Only one predeclared column is evaluated by Monte Carlo.** Cell means are 1 and 2 *normalized current units*, with illustrative iid Gaussian CV 3% assigned persistently per chip. No retired readout data or foundry parameters enter the calculation.

The prior E03M oracle full-group conditional-mean correction is retained identically for both policies, but its measurement/implementation cost is not modelled. This is a limitation, not deployable calibration.

The simulated ADC is **midrise**, in normalized current units, full scale \`[16 + offset, 32 + offset]\`, B=4,5,6,7 bits. It floors the normalized input to a clipped code. Count decoding finds the nearest **quantized nominal reference** for the known 16 selected rows, breaking ties toward the lower count and clipping to 0..16. Three phase offsets \`-0.25, 0, +0.25\` LSB are tested. For each B and each mapping, select its calibration-optimal phase using **65,536 independent calibration chips**; evaluate unchanged on **131,072 independent held-out chips**. The paired A/B evaluation shares each simulated chip assignment and bit-cycle persistence.

## Measured software outcomes

| Decoder | Concentrated (A) reconstructed MSE | Balanced (B) MSE | B relative improvement |
|---|---:|---:|---:|
| Ideal midpoint | 0.068687 | 0.048462 | 29.4% |
| Fixed 6-bit, phase 0 | 2.261963 | 1.917000 | 15.3% |
| Tuned 6-bit, 3-phase search | 0.122276 | 0.087631 | 28.3% |
| Tuned 7-bit, 3-phase search | 0.081520 | 0.057892 | 29.0% |

For tuned 6-bit, paired MSE(A-B)=0.03465, independent-chip normal-approximation 95% interval **[0.02906,0.04023]**. The constructed mappings have equal *theoretical* per-read marginal current-error laws; independent finite samples show slight differences in empirical marginal error rates. Consequently interpret the data as a reproducible diagnostic, not physical proof that covariance alone yields a given advantage after an implemented ADC.

At fixed 4-bit and 5-bit phase 0, nominal input 24 falls directly on a quantizer threshold: about 50% of reads are misdecoded for these particular code/tie conventions. A quarter-LSB phase shift largely removes that pathological alignment. **ADC calibration is a dominant control and mandatory strong baseline.** The numerical result must not be marketed as an MRAM-specific novelty claim.

## Provenance

- **Exact script:** \`experiments/e03q_finite_adc_pilot.py\`, SHA256 \`9afd60c36bb260eb7fb3914e84bf494615474c3741a04f677c2a64ccdae8410c\`.
- **Full raw output:** SHA256 \`0541221d31a3cff41ea78b3ab936535b993447a09d02c7ba310217048cfa758a\`; machine-readable GitHub summary in \`experiments/results/E03Q_20261104_finite_adc_summary.json\`. Full raw JSON delivered in conversation artifact ZIP, and reproducible from the script.
- **Command:** \`OPENBLAS_NUM_THREADS=1 python3 experiments/e03q_finite_adc_pilot.py --out experiments/runs/E03Q_my_run/finite_adc.json --cal-samples 65536 --eval-samples 131072\`; use a **new** path on rerun.
- **Evidence:** constructed model, software sampling, no electrical response. Source hash and RNG seeds frozen. No target 256x256 netlist, extracted parasitics, device read-noise law, neural prediction, measured current or energy.

## Decision

**Continue only to E02 physical gate and strong mapping-baseline comparisons.** E03Q shows the chosen constructed example is sensitive to finite ADC thresholds yet retains a bounded reduction after one allowed calibration scheme. It does not establish an implementable mapper or general effectiveness; both E03M and E03Q can be defeated by target readout behaviour or a tuned baseline. Next target experiment: authorized 256x256 electrical architecture E02, begin with cell validity and patterned read/settling, independent held-out patterns and declared readout. E09 Ising remains a separate conditional branch.
