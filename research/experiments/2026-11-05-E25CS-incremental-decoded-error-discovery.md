# E25CS — implemented decoded-error swap mapper and incremental circuit oracle

5 November 2026 (Singapore). **Executed software discovery**, not GF/PEX, actual
ADC, end-to-end network result or novelty pass. The user explicitly requested
larger runnable command batches and ideas from computer-science algorithms.

## Executed small real-trace result

Frozen E01 packet hash 400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a;
first 256 FC1 rows, eight outputs, 128 CAL/256 previously inspected DEV parents.
Split CAL 64 correction-fit/64 swap-selection. Same per-group m+centroid correction,
same exact legal count support, same group memberships and nonempty read counts.
ASSUMED one-ended 32-row passive ladder, g_AP=36.704uS, g_P=73.408uS. Map search
trained ONLY at assumed R5, with seed 250511, 96 proposal swaps/group. R0/1/5/10
evaluation did not remap using DEV. Full nodal recursion, sparse recursion and
segment-tree backends return exactly matching accepted swaps/maps/results.

At assumed R5, DEV signed reconstructed arithmetic MSE:

| Fixed grouping | Conductance sort | Independent graph (correct Bernoulli diagonal) | CAMP-light | Continue Q with same swap stream | Decoded-MSE mapper |
|---|---:|---:|---:|---:|---:|
| Zero-rate | 26332.337 | 25757.028 | 23279.458 | 23179.291 | **19802.732** |
| CAR | 25130.062 | 25254.325 | 23582.553 | 22555.159 | **20432.028** |

Decoded-error search reduces MSE vs CAMP by 14.93%/13.36%, or vs continued Q
by 14.57%/9.41%. This is a **partial-layer constructed-model** result. CAL accepts
33/20 swaps respectively; all three exact evaluators choose the same sequence.

## Negative results that must accompany that table

- Individual wrong-count totals INCREASE at R5: zero-rate CAMP 4235 vs decoded-MSE
  4729; CAR 4192 vs4715. Lower signed arithmetic MSE is not fewer wrong reads.
- R1 MSE worsens: zero-rate CAMP67.735 vs decoded86.424; CAR54.993 vs99.634.
- R10 CAR worsens: CAMP132332.626 vs decoded147042.969. No robust advantage across
  operating conditions is established.
- **Expanded-output negative control:** trained fitness on first eight outputs but
  evaluated all 128 outputs across all four FC1 row blocks, zero-rate grouping/R5:
  CAMP full-FC1 MSE116609.516 vs decoded132738.042 (approximately13.83% WORSE);
  continued Q115715.018. A narrow output proxy does not generalize. Do not present
  the small table as a full-layer improvement. All-128-output SEARCH is prepared
  in the NUS batch and has NOT been executed in this environment.
- Current per-group calibration differs from E22's pooled two-feature fit; compare
  methods within this E25CS experiment only.
- DEV has been used during discovery; descriptive evidence, not prospective test.

## What the CS contribution candidate actually does

It starts from a coactivation graph placement (an established QAP family), then
optimizes actual decoded W4A8 arithmetic error under the declared circuit operator.
A swap touches two rows. Samples with equal active conductance in both rows have
unchanged circuit response and centroid, so sparse dependency filtering skips them.
An associative product of 2x2 fractional-linear transfer maps supports a segment
tree with O(log B) changed nodes per affected sample, as opposed to O(B) ladder
recursion. Both are exact for the assumed passive network; neither simulates GF MOS.

This is NOT a novel invention of graph optimization, segment trees, current
compensation, or counterexample-guided synthesis. No formal CEGIS guarantee is
claimed. A potential FYP method would require a distinct useful incremental
placement algorithm, stronger prior-art comparison and target/task validation.

## Timing and verification

Independent KCL matrix solve vs recursion passes; random accepted/rejected swaps
match full/sparse/tree at B3,8,32,64,128,256; R0 null, fixed group membership,
signed W4A8 reconstruction, and no DEV-truth dependence pass. Python3.6 syntax and
shell syntax pass. Neural adapter arithmetic was tested with CONSTRUCTED weights;
actual frozen student checkpoint is absent here, so neural outcome is BLOCKED.

The preliminary sparse/tree CPU measurements differ substantially under host load;
do NOT promote a stable speedup number. Sparse recursion is a strong control and
often preferable at B32. The tree has extra O(E*B) memory. Setup, calibration and
decoder timing are reported, not hidden. CPU timing is not MRAM read energy.

## Prepared NUS batch and exact source

`experiments/e25_incremental_adc_mapping.py`, source SHA256
d751f0ec13e2bf60714f0273e2c77db2ee32601b01cdab3da4e9c529dbc430eb.
`scripts/run_e25cs_batch.sh` runs selftests, existing full-E22 GF diagnostics when
available, a synthetic backend benchmark, small matched replication, then a
full-FC1 128-output SEARCH and evaluation. `--task-auto` propagates FC1 errors
through the hash-pinned frozen network if local checkpoint/PyTorch is available.
Missing neural resources are explicit, never replaced by a newly trained model.
Private NPZ errors support later `--task-only` propagation without rerunning search.

All parameters and gates are in [E25CS protocol](../protocols/E25CS-incremental-decoded-error-placement.md).
Public summaries contain no packet, raw weights/checkpoint, raw GF currents,
netlists or PDK source. Local full-output-search/network/GF E25CS results remain
pending; no prepared command is reported as an executed experiment.

## Relation to latest GF evidence

The separate user-executed full E22 GF current audit (17 counts, fixed m=k=16)
reports 25/204 R5 errors after strong per-R CAL range and near correction, while
R2 is zero in the tested seven-bit cases. Those are current-decoding results under
assumed wiring, not evidence for the E25CS passive kernel on varying MNIST m/k.
E22C/E23A are strong cheap diagnostic controls before proposing more correction.
No inference of an extracted256x256 read law is made.

## Disposition

Keep E25CS as a **specific implemented CS-informed hypothesis**. The first pilot
is positive on its chosen arithmetic endpoint and negative on output-transfer and
some wire conditions. The all-output and actual frozen-network experiment is the
next necessary check. Generic algorithm reuse does not certify novelty, and this
result must not be described as a confirmed original MRAM architecture.
