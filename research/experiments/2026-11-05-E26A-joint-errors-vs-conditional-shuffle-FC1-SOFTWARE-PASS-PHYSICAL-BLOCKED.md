## Reproducibility update: executable now tracked
Exact source `experiments/e26a_joint_error_gate.py` has now been committed to public `main` (SHA-256 `3fa6042e2ae91c76c6d08794c4acd10969b4da0d4ce619d2a912c8b3b407d714`; commit `5fa48f68b561a28c60315212561a3645fa114ed2`). Older notes below saying source is available only in the chat ZIP are now superseded. Still NO physical joint 2T1MTJ data.

## Additional null-model scientific caveat
The existing shuffle conditions on **exact (m, ideal n)** per read lane only. This preserves those conditional empirical marginal errors but **does not preserve dependence on finer spatial input position (e.g. suffixQ, centroid), weight/MTJ geometry or fixed-chip state**. A physically observed joint-vs-shuffled difference could reflect these omitted single-read covariates, not specifically intrinsic cross-column/bitplane covariance. Before any scientific claim, compare against stronger **position-conditioned** and fixed-chip controls and run an adequately powered multiple-column extracted pilot. A synthetic-demo difference is not evidence for any of these mechanisms.

# NUS EXECUTION CONFIRMED — 2026-11-05

**User's actual NUS Singularity output** confirms E26A `selftest`, `preflight` and `demo` all finished. Frozen E01 packet SHA256 `400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a`; true 256 MNIST development parents × 128 FC1 outputs, packed-array signed-bitplane reconstruction exactly equals direct dot; reported signed weight range -7..5. This is **real E01 arithmetic, not MRAM current simulation**.

The user-executed *synthetic* demo (NO GF currents, PEX, physical MTJ correlation or real classifier):
| Metric | Intentionally coherent synthetic | Conditional-shuffled synthetic (8 repeat mean) |
|---|---:|---:|
| FC1 MAE | 259.21875 | 259.21875 |
| FC1 RMSE | 637.4699993 | 555.8694880 |
| FC1 max absolute integer error | 3072 | 2304 |
| Images with any FC1 error | 0.234375 | 0.99560546875 |
| Nonzero FC1 output fraction | 0.18609619140625 | 0.23238754272460938 |
| ReLU gate flip fraction | 0.02178955078125 | 0.022308349609375 |

`E26A_SHUFFLE_EFFECTIVE_CHANGED 8819.25`. Private report path: `~/mram_private/E26/E26A_SYNTHETIC_CONTROL.json`. **Do not label these differences a physical discovery**: the demo explicitly constructs a common latent error event across images and shuffles it to test code behavior.

**Blocking physical evidence**: complete actual correlated count-error tensor from same fixed-chip actual 2T1MTJ parallel read, across columns, groups, bitplanes and parents; 32-row manually assumed-R E24 single-column data is insufficient. **Blocking task evidence:** E01 packet alone contains FC1, not downstream FC2/FC3/logits/held-out final test.

**Immediate next action:** readonly NUS file-discovery for true extracted 4×4 2T1MTJ DSPF and original complete frozen W4A8 checkpoint; validate one multiple-column parallel-read pilot before scaling. Do not generate fabricated correlated arrays or infer physical covariance from E26A mock demo.

---

# E26A — Joint physical MRAM count errors versus conditional-marginal shuffle (first executable gate)

**Date:** 2026-11-05. **Status:** E01 real-workload **software reconstruction and synthetic comparison completed locally**. **Physical joint-error hypothesis UNTESTED — blocking missing physically coupled 2T1MTJ multi-column read-error tensor. Full MNIST classification UNTESTED — E01 packet is FC1 only.**

## Core falsifiable scientific question
For a *fixed 2T1MTJ chip and matched input image*, does preserving actual joint errors across physical columns, row groups and signed activation/weight bitplanes produce a different **FC1 and eventually full DNN output error** from an independent-error control that retains the *same per-read conditional marginal distribution*?

This is **computation-level behavior**, not a proposal to optimize the ADC sense margin. An observed covariance effect is itself not new; it must motivate a concrete compute-level algorithm, novel versus full-stack hardware-aware training, Dyn-A-Map, DIB-CIM and selective protection.

## What is genuinely executed and verifiable
- **Frozen real NUS E01 packet**: `review_packet.zip`, SHA256 `400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a`. 256 MNIST DEVELOPMENT parents, 8 activation bitplanes, 8 packed 256×256 binary weight arrays, 128 FC1 outputs, 4 row blocks (the final with 240 zero padding rows). Signed coefficients include +1,+2,+4,-8.
- Local Python+NumPy software preflight: **PASS**. All 8 arrays reconstructed as physical 32-row groups; exact W4A8 FC1 integer MAC vector shape **(256,128)**; **group-bitplane reconstruction EXACTLY matches an independent direct integer dot-product** reconstructed from E01 X and signed weights. This is ACTUAL E01 frozen MNIST workload arithmetic, **NOT Spectre, PEX or downstream classification**.
- Synthetic software comparison: **PASS**. An intentionally constructed sparse coherent perturbation of per-read decoded count is injected into the ACTUAL E01 FC1 traces to test the integrity of the two comparison arms. This is **deliberately SYNTHETIC CONTROL ONLY**; it must **never** be reported as physical MRAM error/correlation. Local test with 3 shuffle repeats: coherent injection FC1 mean absolute perturbation 259.21875 and mean shuffle perturbation 259.21875 (equal by construction and linear absolute sign), coherent FC1 RMSE 637.47 vs conditional-shuffle RMSE ~554.98, illustrating that the comparison pipeline can detect altered joint structure in constructed data, not that actual hardware behaves this way. 256 development parents already inspected; not pristine final test set. No classified accuracy.
- Code: `e26a_joint_error_gate.py` and README distributed in user-visible ChatGPT artifact `E26A_joint_error_FC1_gate.zip`. Source SHA256 `3fa6042e2ae91c76c6d08794c4acd10969b4da0d4ce619d2a912c8b3b407d714`. Archive SHA256 `8602b7d20061c3616ac1f352953cc50ec484129b5e6dbe92b16a37f24c7e5c97`. **Source is not yet tracked in this public GitHub repo**; do not invent a link to GitHub script.
- Python modes: `selftest`, `preflight --packet <frozen E01 packet>`, `demo --packet ... --repeat 8 --out <private report>`, `analyze --packet ... --errors <complete physical joint count-error npz> --attestation <provenance json> --repeat 32 --out ...`. Demo's status explicitly labels `SYNTHETIC_DEMONSTRATION_NOT_GF_OR_PEX`.

## Paired causal/null comparison design
One *complete* physically justified integer read-error array with tensor shape `(8,256,8,8,256)` [packed weight array, development parent ID, activation bitplane, 32-row group, physical column] is required. Each entry is **decoded count − ideal count** for the REAL same fixed-chip physical read, with column+bitplane joint behavior intact.

- **B: joint physical arm**: use the recorded error tensor unchanged; propagate it with the actual E01 signed bitplane coefficients into integer FC1, checking ReLU gate flips.
- **A: conditional shuffle**: shuffle the per-lane error values among parents, **within exact `(active_rows m, ideal_count n)` strata**, for every physical [array, activation bitplane, row group, column] lane. This preserves empirical per-lane conditional error magnitudes/signs/counts and bit significance, while breaking residual co-occurrence across lanes. Run several random shuffles; report how many events actually move. Offline conditioning on known truth n is a statistical null-control only, not a runtime algorithm.
- Compare FC1 error MAE/RMSE/max, fraction nonzero, fraction development images with any FC1 error, and FC1 ReLU gating changes. This contrasts **joint covariance conditional on m,n** against a marginal-preserving null. Small populations per stratum can make the test uninformative; if shuffling moves no error events, STOP.
- **No logits/accuracy from E01 alone:** entire frozen quantized model + biases/downstream layers and new held-out test split are required to make full-network inference claims. Do not silently replace them with a guessed PyTorch architecture.

## Strict blocker and next physical integration
E24 provides **GF access NFET compact transistor** + student static MTJ single-column DC currents and error counts with *assumed* wire resistors — not joint across 256 columns, not the previously completed 4×4 local-floating 2T1MTJ DSPF, and not actual GF full 256×256 PEX. The existing E24 aggregates cannot be converted into a physically coupled error tensor. An artificial correlated tensor, iid per-column replicas, or reused E24 marginals cannot certify physical covariance.

Recover actual 4×4 PEX `M047_GF_2x2_PEX`/4×4 xACT DSPF, validate legal parallel-read path with 2T1MTJ BL/SL/WL connectivity; build a physically grounded multi-column kernel/hierarchical representation preserving one fixed-chip multi-bitplane error joint distribution. Do not run millions of flat Spectre decks without validating a small pilot. Only then advance E26A to an **actual physical comparison** and complete W4A8 inference.

## Predeclared decision
- Joint physically sampled data differs from conditional shuffle in validated held-out neural outcomes: investigate precisely defined, equal-budget compute-level policy against simple significance scheduling, standard calibration/Q correction, DIB, Dyn-A-Map and selective protection.
- No difference: correlation hypothesis *for that operating regime* unsupported — report null, do not invent algorithm.
- Missing source tensor, actual PEX or downstream model: **BLOCKED**. Successful software selftest is not physical result or proof of novelty.
