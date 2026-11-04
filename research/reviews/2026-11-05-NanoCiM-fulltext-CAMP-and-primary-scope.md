# NanoCiM full-text review: method comparison and research disposition

**Review date: 5 November 2026, Singapore.** Read the complete user-supplied
13-page paper and visually verified the mapping equations/figures and outcome
tables. This is a literature review, not a new simulation or a novelty pass.

**Current scope:** [ADR-0006](../decisions/ADR-0006-coupled-precision-failure-boundary-primary.md)
adopts coupled precision and physical-nonideality failure boundaries as the
primary research direction. CAMP and Ising are archived alternatives. The older
post-E20 recommendation to give CAMP priority is historical and is superseded.
Reading this paper does not reactivate a mapping experiment.

## Source and access

Chihiro Matsui, Ayumu Yamada, Shota Suzuki, Naoko Misawa and Ken Takeuchi,
"NanoCiM: Nano-ReRAM Computation-in-Memory with Neural Network Weight-Aware
X-Address Scrambling to Suppress IR Drop-Oriented Bit-Line MAC Current
Variation," IEEE Transactions on Circuits and Systems for Artificial
Intelligence, 3(3), pp. 190-202, June 2026.
DOI: [10.1109/TCASAI.2026.3661436](https://doi.org/10.1109/TCASAI.2026.3661436).

User-supplied PDF: 13 pages; SHA256
`70ab47f9b2a4864cd7bc2cce5286452dfdac04ddbd2ba00efc24ff6f80eeab5e`.
The NUS-licensed PDF, extracted full text and figure images remain private.
This repository receives an original review and source receipt only.

PDF page 1 corresponds to printed p.190; PDF page 7 to p.196; PDF page 10 to
p.199. Page references below give both where useful.

## What NanoCiM actually does

1. It applies one offline row permutation to the trained weight matrix and
   permutes input coordinates consistently during inference. The paper's Fig.2
   describes an input tracking vector/controller. Thus preserving the ideal
   matrix-vector product by paired weight/input permutation is established.
2. Its mapping controls are original ordering, random row permutation, row
   weight-magnitude sorting, and a weight-aware TSP-based ordering.
3. Its proposed TSP ordering avoids adjacent rows with overlapping LRS cells,
   aiming to reduce differences in BL current across different stored patterns.
   It is not solely a method to maximize absolute BL current.
4. It separately studies SL amplitude inputs, SL inputs with inactive WLs
   disabled, and WL pulse-width inputs. Disabling inactive selectors suppresses
   reverse/countercurrent paths caused by local BL voltage rise.
5. It evaluates a ReRAM/CMOS circuit model and quantized MNIST networks, including
   cell/interconnect variation assumptions. These are the paper's external
   results, not GF MRAM measurements or results of this project.

Evidence: Section I and Fig.2 (PDF pp.1-2); Section IV and Figs.11-12
(pp.6-8); Section V and Figs.13-14 (pp.7-9); Section VI (pp.9-11).

## Exact mapping formula: an overlap score, not Euclidean distance

In Section IV-A, printed pp.195-196 (PDF pp.6-7), a row vector is
`w_i=(w_i1,...,w_iM)`. The printed equations are:

\[
s_i=\left(\sum_j w_{ij}w_{ij}\right)^{1/2},\qquad
d_{ik}=\left(\sum_j w_{ij}w_{kj}\right)^{1/2}.
\]

Equation (5) is a square root of a row inner product. For the nonnegative/binary
weight patterns illustrated, it measures overlapping LRS/one positions. It is
**not** `sqrt(sum_j (w_ij-w_kj)^2)`. The text says smaller `d_ik` corresponds to
less overlap and places such rows next to each other through a TSP formulation.
Do not silently substitute ordinary Euclidean distance or invert the intended
overlap ordering in a supposed reproduction.

The article does not provide implementation-level TSP pseudocode, a solver
configuration, tie rules, a tour-to-linear-BL cut/orientation rule or author code
in the supplied PDF. It references ReRAM simulated annealing for solving TSP.
The exact solver and endpoint handling therefore remain unspecified here.
A nearest-neighbor/2-opt implementation would be a declared adaptation, not a
bit-for-bit reproduction of the authors' algorithm. For signed multibit MRAM,
one must also declare the nonnegative physical bit-column encoding used to
form this score rather than applying its square root to arbitrary signed row
inner products.

## Comparison with the archived CAMP proposal

The archived CAMP-light objective uses CAL activation second moments
`C_ik=E_CAL[x_i x_k]` and an assumed shared-wire loss kernel:

\[
J(\pi)=\sum_{i,k} C_{ik}\,\bar g_i\bar g_k
\min(\operatorname{pos}_\pi(i),\operatorname{pos}_\pi(k)).
\]

CAMP-full replaces the product of mean conductances with a cross-column/plane
mean of conductance products. This review does not propose adopting that extra
complexity. The previous independent-Bernoulli correction remains required:
`C_ii=p_i`, and `C_ik=p_i p_k` only for distinct independent rows.

| Item | NanoCiM as specified | Archived CAMP candidate |
|---|---|---|
| Pair information used to select a map | Weight-row overlap `sqrt(sum_j w_ij w_kj)` | CAL input coactivation times stored-conductance statistics |
| Dependence on input distribution | Actual inputs are reordered/evaluated; no explicit CAL activation coactivation matrix enters the stated TSP rule | `E_CAL[x_i x_k]` enters the mapping objective explicitly |
| Position objective | Put low-overlap rows adjacent through TSP; reduce pattern-dependent BL-current spread | Weight every row pair by shared path length `min(pos_i,pos_k)` to minimize expected first-order loss |
| Permutation domain | Whole stated weight matrix; no fixed-32-row skip/read-budget constraint specified | Restrict each permutation to an existing 32-row group's fixed membership |
| Ideal arithmetic | Paired weight/input permutation preserves it | Preserves it, and additionally preserves each group's m, k, n and empty-read schedule |
| Calibration in the proposed mapper evaluation | Discusses prior conductance calibration in related work and uses low-bit training; does not include the same CAL-fitted centroid/output-count decoder used in our CAMP screen | Compared after shared CAL-only decoder/correction; objective itself is expected raw wire loss, not directly decoded MSE |
| Demonstrated endpoint | Circuit-model BL-current spread and quantized MNIST inference | Existing assumed-network partial-block arithmetic MSE only; no fresh GF/PEX or full-network benefit |

**What is supported:** the stated NanoCiM TSP edge rule and the stated CAMP
objective are not the same mathematical decision rule. NanoCiM's printed rule
does not include `C_ik` or the all-pair shared-wire-length kernel.

**What is not supported:** this does not establish first-in-literature novelty
for CAMP, an absence of activation-aware mapping elsewhere, or useful superiority
over a faithful NanoCiM-inspired baseline. NanoCiM is already pairwise
weight-aware row scrambling, so claims of inventing pairwise mapping, spatial
IR-drop mitigation, input-coordinate permutation or cheap offline reordering
are unavailable. Merely changing ReRAM to MRAM is not a method contribution.
Restricting an existing mapper to fixed groups is also an available comparator.

## Strong control already present in NanoCiM's own results

Table V, printed p.199 (PDF p.10), reports at BL half pitch 40 nm and BL length
1 mm:

| Mapping | BL-current spread in the constructed example | MNIST recognition accuracy |
|---|---:|---:|
| Original | 0.71 mA / 87% | 50.6% |
| Random | 0.061 mA / 24% | 83.1% |
| Sorting | 0.29 mA / 43% | 60.9% |
| TSP | 0.064 mA / 27% | 79.9% |

Section VII, printed p.200 (PDF p.11), explicitly identifies the Table V
accuracy row with the MLP and the entire MNIST digit dataset. Separately,
Table IV and Figs.16-17 examine selected digit examples and variation trials.
Do not dismiss the entire paper as evaluating only ten images, or substitute
Table IV's 9/10 example outcome for Table V's dataset result.

Random beats TSP on the reported Table V accuracy and current-spread point.
The authors discuss TSP's avoidance of unfavorable seed-dependent arrangements;
that argument is not an all-condition superiority result. A fair future mapper
comparison must include multiple random resident orders and report seed
variation/selection cost, not only the original and sorting controls.

The inference metric and current-spread metric concern different evaluations;
their entries must not be converted into a causal per-image accuracy law.

## Physical and cost boundaries

- Section III-B (printed p.194/PDF p.5) uses a 1024-cell column, LRS=10 kOhm,
  HRS=1 MOhm, and a Rohm 0.18 um access transistor with L=0.18 um, W=2 um in
  HSPICE. Its small-pitch interconnect RC is estimated, not a measured 10 nm
  ReRAM macro or our GF 22FDX PEX.
- The source line and bit line both matter in its chosen interface. Our
  single-ended passive ladder and student static-MTJ/GF selector model are
  different evidence tiers and topologies. Published paper percentages cannot
  be compared numerically to our partial-block MSE percentages as if the tests
  were matched.
- ReRAM HRS/LRS contrast is about 100 in the stated example. Our illustrative
  MRAM conductances have a much lower state contrast and appreciable AP
  current; a matched physical-bit/conductance representation is necessary.
  This is a modeling reason to compare devices, not proof of MRAM-only novelty.
- Table I's memory-area/read-energy comparison explicitly excludes detailed
  pre-layout/post-layout validation and is scoped to memory cells. Fig.2 also
  requires input permutation. Do not adopt an unqualified claim of zero
  controller/address-routing/metadata overhead for our design from the paper.

## Relevance to the adopted coupled-precision primary direction

Section VI-A (printed p.198/PDF p.9) fixes input/weight/output precision at
2/4/4 bits and uses low-bit range training, reference [47], LIORAT. It combines
quantization, wiring effects and variation in an inference study. Therefore
neither "hardware nonidealities affect quantized inference" nor "jointly
consider precision and IR drop" is a new broad research subject.

The paper does not present the current project's proposed systematic
ADC-resolution/range versus matched spatial-mask failure-boundary experiment,
or a trained/validated held-out boundary predictor against current-margin,
offset-only and near/far controls. That is a narrower question not answered in
this paper; its originality across the rest of the literature remains open.

Follow-up closest methods from this paper's bibliography include SWANN [24],
X-CHANGR [34] and LIORAT [47]. They are review leads, not implementations
established as equivalent or different by this NanoCiM-only full-text review.

## Disposition and next action

1. Complete the NanoCiM access gate: record that the full text has now been
   read and distinguish its weight-overlap adjacency objective from CAMP's
   input-coactivation/shared-wire objective.
2. Keep CAMP archived under ADR-0006. Do not run or promote the older
   CAMP-E23 microgate solely because this paper does not contain `C_ik`.
   The existing stronger-calibration/model sensitivity and original-group
   failures remain unresolved.
3. Continue the **current coupled-precision E22** pilot already registered in
   `2026-11-05-E22-coupled-precision-17count-GF-PENDING.md`. It is prepared,
   not executed as of the inspected `b19a4a0` repository snapshot. Establish
   real current levels, saturation and simple-correction controls before
   claiming an interaction or a new boundary predictor.
4. If mapping is later reauthorized, first compare CAMP against the printed
   overlap-score TSP family, joint-activity sorting, corrected independent
   moments and multiple random maps under the same group membership,
   CAL/DEV budget, calibrator, ADC and total resource assumptions. A modified
   solver must be labelled an adaptation. An expected-Q improvement alone is
   insufficient; require decoded/task utility after calibration and costs.

This review resolves what this particular source specifies. It introduces no
new physical result, no baseline performance result of our own, no supervisor
approval and no publication-level novelty certification.
