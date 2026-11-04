# E25CS — computer-science-informed, circuit-local decoded-error placement

5 November 2026, Singapore. Discovery protocol; no publication novelty pass.

## What changes and what stays fixed

The research problem remains MRAM neural inference under coupled precision and
hardware nonidealities. This is one proposed offline mapper/scorer, extending
E22. It does not create a new Ising or read-reference project.

E22 minimizes a continuous wire-load proxy. E25CS makes an actual different
decision: accept a within-group swap only if it reduces **CAL reconstructed signed
W4A8 arithmetic MSE after integer count decoding and ordinary centroid calibration**.
This can reject a swap that reduces analog error but crosses a costly decoder
threshold, or accept a swap that changes signed reconstructed error favorably.
It is not yet a classification-risk optimizer.

For each fixed group the same physical permutation is shared by activation
bitplanes, all four signed weight planes and every mapped output column. Logical
group membership and nonempty activation-group reads remain exactly unchanged.
Four 256-row blocks represent the 784 FC1 input dimensions plus explicit padding;
this is storage bookkeeping, not an extracted 256x256 macro.

## CS ingredients and attribution

1. **Quadratic assignment / graph layout.** The CAMP initialization uses a CAL
   coactivation graph and the shared-wire kernel min(position_i,position_j).
   QAP and greedy 2-swap solvers are established. See Vogelstein et al. (2015),
   https://doi.org/10.1371/journal.pone.0121002. E25CS does not implement FAQ or
   claim that using a graph is an invention.
2. **Incremental view maintenance / sparse dependency updates.** A swap modifies
   only two logical rows. Any read sample whose two active conductances are equal
   has exactly unchanged passive current and input centroid, so it is skipped.
3. **Segment-tree monoid products.** A ladder segment is a fractional-linear
   two-port map. Store products in a segment tree to update only changed paths.
   This is a standard data structure applied to a declared circuit oracle, not a
   new data-structure invention. Sparse full recursion is a mandatory competitor.

Potential research contribution, CONDITIONAL: a validated incremental circuit-query
method that makes practical decoded-error-aware MRAM placement more efficient at
unchanged read count. It must beat direct and sparse reevaluation, useful mapping
baselines, and close physical-aware scrambling work. NanoCiM full-method comparison
is still open. Existing fast circuit solvers also require comparison; this is not
the first fast IR-drop model (e.g. the TED 2022 publisher record
https://ieeexplore.ieee.org/document/9693956/).

## Exact mathematical oracle, and its restricted scope

ASSUMED shunts: g_AP=36.704 uS, g_P=73.408 uS. These are not fitted GF access-MOS
state currents. A one-ended wire has r ohms before every shunt, including the first.
For tail admittance y and shunt g,

    T_g(y)=(y+g)/(1+r(y+g)).

With z=r*y and q=r*g, the transfer is represented by

    M(q)=[[1,q],[1,1+q]],
    z_source=(M_1 ... M_B)[0,1]/(M_1 ... M_B)[1,1].

I=V*z_source/r. Products are associative. A two-row swap changes at most two leaves,
and O(log B) nodes per affected read sample. Build time is O(E*B); cache memory is
O(E*B), compared with O(E) scratch for sparse recursion, for E sampled reads.
At small B, cache traffic/matrix arithmetic can outweigh the asymptotic advantage.
Timing must include setup, decoding, calibration fitting and memory. R=0 uses a
sum and is the mandatory permutation-invariance null.

This oracle is exact ONLY for its passive linear ladder. It does not model GF
NFET nonlinearity, 2T1MTJ source routing, settling, actual RC extraction, mismatch,
physical reference/ADC circuits, neighboring columns, or energy. It is not a
validated GF surrogate. No new Spectre result is introduced.

## Frozen data and leakage controls

- E01 review_packet.zip SHA256
  400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a;
  validate every packet member against its manifest.
- 128 CAL and previously inspected 256 DEV parents. DEV remains DEVELOPMENT,
  not a fresh final test set. No DEV-driven map/range/seed selection.
- First 64 CAL parents fit each group's two-feature (m, centroid) correction;
  remaining 64 choose swaps. Every arm gets the same per-group calibrator.
  This differs from E22's globally pooled calibration, so compare within E25CS.
- All graph initializations may use CAL input statistics and stored weights.
- Training wire R is fixed at ASSUMED 5 ohm/segment. Freeze the resulting mapping,
  refit identical CAL-only calibrators at evaluation R=0,1,5,10; no per-R remapping.
- Random seed 250511; 96 swap proposals/group; seven initialization graph passes.
  Proposed-pair sequences are identical for full/sparse/tree backends.
- Independence control retains E[x_i^2]=p_i on its diagonal; only off-diagonal
  coactivation is replaced by p_i*p_j. Squaring diagonal p would be an invalid
  independent Bernoulli baseline.

## Required controls

Input activity sort; activation-times-mean-conductance sort; independent-activation
graph; CAMP-light; continued Q minimization from the same CAMP initialization and
same swap stream; decoded-MSE search with (a) full recursion, (b) sparse recursion,
and (c) segment-tree updates. Same decoder and exact legal support are provided to
all arms. Support metadata and online correction implementation are not free-energy
claims. These are model-based count thresholds, not a characterized finite-bit ADC.
The decoded estimate is explicitly Y_seen/g_AP minus known active-row count m plus
CAL correction, followed by legal-support rounding. DEV true n is used only to
score the result. A selftest perturbs held-out truth with calibration frozen and
verifies that predictions do not change.

Full/sparse/segment search must return the exact same accepted swaps and row mapping.
Compare wall time including setup, query time, decoding time and peak tree-cache
bytes. Equal proposal count is NOT an equal-CPU mapping benchmark. A faster backend
giving identical quality is a separate result from whether a better mapping exists.

## Batch stages

Run `scripts/run_e25cs_batch.sh` in Singularity using the NumPy-capable Stage4A
environment. It locates only the hash-pinned existing packet under mram_private
(or use E25_PACKET), performs mathematical selftests, benchmarks synthetic sparse
queries, replicates the first 256 rows/eight-output pilot, and then runs all four
FC1 row blocks/all 128 outputs. Full search uses sparse recursion because a B=32
tree benefit is not assumed. All outputs go to a unique private directory.
When the saved full 17-count GF E22 file is present, it also runs existing E22C and
E23A current diagnostics before mapping. These are analyses of prior user-executed
GF currents, not new circuit simulations or an implicit GF validation of E25CS.

The optional `--task-auto` step checks the exact E01 checkpoint and quantizer hashes
at documented local model directories. If available, it propagates integer FC1
errors through the frozen model with real scales/biases and ideal W4A8 FC2/FC3.
It reports prediction disagreement from the clean model, logit MSE and margins;
with hash-pinned original labels, also reports accuracy and lost/recovered correct
predictions. Partial pilot coverage is explicitly different from all-FC1 coverage.
No retraining, new dataset, resplitting, or package installation is done.

If checkpoint/PyTorch is missing, report BLOCKED and DO NOT invent network results.
The run saves integer errors. Later run `--task-only RUN_DIRECTORY --packet PACKET
--task-model-dir MODEL_DIRECTORY --out NEW_JSON` to propagate them without another
mapping search. Local selftests validate neural arithmetic with constructed
weights; they do not execute the user's trained network.

## Interpretation and stopping conditions

- Numerical or R0 identity failure: debug code, do not call it research failure.
- No speed benefit beyond sparse recursion: reject the tree as preferred scorer.
- Lower MSE but no useful neural change: retain arithmetic result only; do not
  claim inference reliability or energy gains.
- Benefit only at R5, worse at R1/R10: report operating-point specificity. Do not
  search another noise level for a favorable headline.
- Improvement from ordinary direct decoded-MSE search alone does not certify
  novelty. The optimizer, incrementality and circuit model all have prior families.
- Circuit timing is CPU time, not MRAM energy or latency. New physical confirmation
  requires GF/NUS and later justified routing/RC; this batch does not consume Cadence.

## E24B closure from user terminal log

The two NUS E19 input JSON hashes in the supplied E24B log are
53f5eee150132654c08823f63053b37f6e63ec2304edd99eb24247552de48901 and
f0217209427c4b1895cf1e9a8b1cfe40cc99d06f0a4c0bd4cc76ed234c66d714.
R0/R1 show zero errors at 3-8 bits on the sampled n7/n8 cases. The small eight-DEV
run has CAL-fit regressions at R5 that inherited coarse decoding avoids. The
24-DEV confirmation has no CAL-fit worsening as bits increase: most R5 settings
remain 2/24, with one 3-bit 4/24 improving to 2/24. One range reports SAT=1 and must
not support a non-monotonicity claim. No intrinsic information-loss novelty is shown.
