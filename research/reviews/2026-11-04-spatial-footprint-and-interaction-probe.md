# Assessment of the physical-first / spatial-footprint proposal

4 November 2026 (Singapore). Source: the user's uploaded text, identified by the
adjacent source receipt. This is a review and proposed diagnostic, not an executed
experiment, selected final contribution or novelty pass.

## Decision

Retain the physical-first mechanism check and the separation of constructed E03Q
evidence from target results. Spatial-footprint control is a candidate, not a proven
improvement over F3. One fresh physical model can support both questions; Ising remains
conditional. Reproducing the same Python output establishes execution reproducibility,
not independent implementation or physical validation.

The sharper method question is whether an inexpensive activation-mask description
predicts useful residual errors after practical calibration well enough to choose a
supported read schedule more economically than tuned correction plus activity control.
Neither position-dependent IR drop nor a generic constrained controller is claimed new.

## Primary-source check

- [Rasch et al., Nature Communications 2023](https://www.nature.com/articles/s41467-023-40770-4),
  Methods, IR-drop and equations 15-18: the retrieved primary method describes a spatial
  bitline system and a position-weighted approximation depending on inputs and weights.
  A near/far current difference is therefore a mechanism check, not a novelty claim.
- [Roy et al., JSSC 2025 institutional record](https://experts.illinois.edu/en/publications/compute-sndr-boosted-22-nm-mram-based-in-memory-computing-macro-u/):
  the primary abstract already establishes low-overhead correction of BL/SL parasitic
  nonlinearity. Full compensation implementation has not been checked in this review.
- [DIB-CIM publisher abstract](https://ieeexplore.ieee.org/abstract/document/11672681):
  adaptive active-WL allocation, input-bit significance/distribution and ADC resolution
  are already supported. Do not assert that its full controller ignores spatial effects
  from abstract-only access. The combined applicable correction/control baseline matters.

A newly located public SEC companion site supplies further reading leads; its narrative
is not substituted for a verified full-paper implementation comparison.

## What the footprint formula can and cannot establish

The negative current perturbation in the supplied expression is consistent with a
first-order expansion of a passive one-ended resistive ladder with fixed selected
conductances and an ideal return. Its dimensions are current. It is a DC approximation;
it does not establish the transfer or settling of the actual access/SL/driver network.

For binary activations and R_i equal to the resistance from the sensing end to row i:

    Phi(a) = sum_i R_i*a_i + 2*sum_{i<j} R_i*a_i*a_j.

The second term motivates testing coactivation interactions after accounting for fixed
row attenuation. This expansion is elementary algebra, not a new theorem. Replacing
the actual P/AP/access conductances by one representative conductance is an additional
approximation. A mask-only predictor must survive different programmed weights; a
controller must not calculate all exact weight/input products digitally for free.

## Proposed first diagnostic: interaction after single-row calibration

Measure the same analog observable, read waveform, bias, sample rule, initialization
and fixed programmed state for no selected row, row i alone, row j alone and both:

    C_ij = I_{i,j} - I_i - I_j + I_0.

For an additive fixed-row response I(a)=I_0+sum_i c_i*a_i, this residual is exactly zero.
It subtracts the isolated contribution of each row, including its individual position
loss. Nonzero residual identifies nonadditivity of the tested read operator; it does
not by itself identify wire resistance, defeat SEC, imply a decoder error or earn novelty.
Driver/sensor saturation and transient conditions are alternative causes to control.

A bounded first set uses four fixed rows: two electrically near the sense terminal
(nP,nAP) and two far (fP,fAP), with the indicated nominal states in the selected column.
Measure nine masks:

| Arm | Selected rows | Role |
|---|---|---|
| Z0 | none | Common analog offset/leakage reference |
| NP, NAP | nP alone; nAP alone | Near single-row responses |
| FP, FAP | fP alone; fAP alone | Far single-row responses |
| NN | nP+nAP | Near mixed-state pair |
| FF | fP+fAP | Far mixed-state pair |
| NF | nP+fAP | Mixed near/far pair |
| FN | fP+nAP | Reversed state-position pairing |

All four pair arms have the same active count and P/AP composition. Use the new
physically declared 256x256 environment; a small active mask does not shrink the array.
Translate these labels through the actual electrical row order, not a guessed pin map.

For parallel conducting columns, match their ideal P/AP compositions as well. One
controlled fixture assigns row vectors U to nP/fP and 1-U to nAP/fAP, with the remaining
stored states fixed. Every pair then has the same ideal count vector across columns.
This is a mechanism-isolation fixture, not a representative neural workload or benefit.
Other column-bias policies require their own matched loading/controls.

Record C_ij at a common sampling rule and in the settled limit. Compare the actual
wire network with a declared wire-resistance control, retaining the same periphery.
Check initialization and solver convergence. A common count-only nonlinearity can also
produce C_ij: variation across matched pairs and residual after practical calibration
are the useful questions. Later add equal-centroid masks to distinguish the footprint
from cheaper count/centroid descriptors. Compare longer fixed sampling, gain/offset,
references and the strongest applicable correction/adaptive-read combination.

## Build feasibility and ordering

Keep the active GF access-NFET plus student-owned MTJ policy. Do not select a foundry
native 2T1MTJ merely because an older layout used it. The actual topology, interfaces,
permitted biases and any layout/LVS views must be verified before a tile commitment.
A behavioral MTJ source alone does not establish that the proposed physical-view flow
is available. Explicit full-array circuit sensitivity studies with declared RC assumptions
may inform the build while extraction is prepared; they remain model studies until the
E02 validation gates are satisfied and must not be called full-macro PEX.

The first NUS session should establish the cell/readout interfaces and tools, with the
frozen-neural E01 runner proceeding as workload evidence. Build the smallest defensible
fresh array model, run the nominal interaction/placement diagnostic, then expand only
for a useful residual. Any controller must earn a held-out decoded/task-quality versus
total-cost advantage. No large layout or Ising chapter is committed by this review.
