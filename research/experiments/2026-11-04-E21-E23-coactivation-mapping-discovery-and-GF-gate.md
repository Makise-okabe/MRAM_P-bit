# E21–E23: coactivation-aware 32-row MRAM placement — discovery and GF validation gate
**4 November 2026.** E21/E22B/E22C/E22D/E22E **executed locally on frozen MNIST bitplanes and constructed resistive networks**. **E23 GF NUS Spectre NOT EXECUTED**. Neither hardware novelty, 256x256 PEX, nor network accuracy is established.

## Why we changed course
After E15/E20 retirement (position-aware GF current correction worked, but simple near/far/centroid corrections matched the complex Q correction), test whether *offline within-read-block row placement* can reduce **uncompensated residual wire interactions without changing the number of read events**. In contrast to CAR/group mapping, each 32-row group retains identical membership. This preserves group activation count, logical read masks, ideal dot products and bitplane/column data alignment.

**Relevant 2026 prior art:** Dyn-A-Map (Chowdhury, Zand, Salehi, June 2026, DOI https://doi.org/10.1038/s44335-026-00072-6) already ranks vulnerable SOT-MRAM FOWs and moves critical weights. No generic sensitivity-aware MRAM row mapping novelty can be claimed. **Other prior art:** 2023 hardware-aware AIMC training (https://doi.org/10.1038/s41467-023-40770-4) recognizes correlated-input, row-order-sensitive IR-drop; DIB-CIM 2026 adapts WL group size using input imbalance. The **particular quadratic second-order coactivation placement objective** needs a deeper exact-match prior-art search before asserting publication novelty.

## The specific algorithm candidate (CAMP: coactivation-aware MRAM placement)
For a one-ended resistive ladder with r Ω/segment, active row conductances a_i=x_i g_i and rows ordered from source to far end, first-order source current is I~V(G-rQ), with
Q=sum_{l=1..32}(sum_{i>=l} a_i)^2.
For an offline permutation π of the **same** 32 logical rows, expected first-order Q =
sum_{i,j} C_ij G_ij min(posπ(i),posπ(j)),
where C_ij=E_CAL[x_i x_j]. For the shared many-bitplane/column mapper, two approximations were tested:
- **CAMP-light** S_ij=C_ij * mean_{p,o}(g_i)*mean_{p,o}(g_j): 32x32 CAL coactivation matrix plus mean stored-bit conductance per logical row. Greedy pair swaps descending an S-row-sum initial order, up to seven passes.
- **CAMP-full** S_ij=C_ij * mean_{p,o}(g_i*g_j): includes full cross-bitplane and cross-column conductance products.

Other matched-cost controls: E01 original, CAR alpha0, zero-rate sorted; **activity rate sorting**; **mean-activity×conductance sorting**; same greedy optimization under **independent activations C_ij≈p_i p_j**; coactivation-only (means) vs full conductance covariance. All methods independently select offline row order using CAL only, hold each 32-row group membership fixed, and share the same CAL-fitted 2-feature centroid correction at evaluation.

## E21 signed-bitplane orientation: negative result (retain)
All 2^8 ways of reversing the eight 32-row groups of the first 256 FC1 rows were evaluated under first-order wire current with the same legal-count clamped ADC and CAL-only centroid calibration. Signed cross-plane cancellation beats marginal count-error orientation by only **4.41% DEV partial-block arithmetic MSE** on zero-rate mapping at ASSUMED 5Ω/segment, but ties CAR at R5, ties at R1 and can lose at other conditions. **REJECT E21** as a standalone contribution, not a robust algorithm.

## E22B exploratory placement screen
Data: verified frozen E01 review_packet.zip SHA256 400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a; 128 CAL and disjoint 256 DEV MNIST input parents; **only first 256 FC1 rows and 8 output channels**, 8 activation and 4 signed W4 weight bitplanes. Source nominal effective shunt conductances gAP=36.704µS, gP=73.408µS are **illustrative**, chosen on the general scale of previous n7/n8 GF current differences, NOT measured full access-NFET state conductance across V/PVT. R in 1,5,10Ω/segment are **assumed**, NOT extracted PEX. Count decoder rounds first-order nonideal current to a legal integer count, **giving ALL policies the same ideal m,k support**; all can use the same two-feature CAL-only centroid current correction.

First-order model, R5 and centroid-corrected, DEV reconstructed signed first-block MSE:
| Fixed E01 group membership | Conductance sort | Same optimizer, independent activation | CAMP-light | CAMP-full | Read-count change |
|---|---:|---:|---:|---:|---|
| Zero-rate sorted | 32,071.6 | 32,641.3 | 28,895.2 | 28,095.5 | **0** |
| CAR alpha0 | 32,447.8 | 32,210.4 | 28,946.0 | 28,122.7 | **0** |

CAMP-full vs light additional gain only ~2.8% at this setting; at R10 and some mapping sources, full is worse. **Do not advocate CAMP-full's extra complexity as justified.** Using the E01 original group order, CAMP-light is sometimes worse than marginal activity sorting after centroid correction.

## E22D / E22E more stringent exact passive Kirchhoff test
Replaced the first-order approximation with an **exact nodal admittance recursion** for the same one-ended **passive** 32-shunt network, r=ASSUMED 5Ω/segment. Refit same simple two-feature centroid correction on CAL for each mapping. This is *not* GF NFET Spectre.

| E01 fixed grouping | Conductance sort DEV arithmetic MSE | Marginal-independent pairwise | **CAMP-light** | CAMP-full | CAMP-light gain over conductance |
|---|---:|---:|---:|---:|---:|
| Zero-rate | 28,332.5 | 29,129.2 | **25,508.2** | 25,356.2 | **9.968%** |
| CAR | 28,105.8 | 28,258.8 | **25,316.2** | 25,235.4 | **9.925%** |

Exploratory 5,000-replicate **paired DEV-input-parent bootstrap**, absolute MSE improvement of CAMP-light over conductance sort (256 independent parents, 8 outputs per parent, correlated):
- Zero-rate mean benefit 2,824.3 MSE units; percentile 95% CI **[1,184.99,4,666.44]**.
- CAR mean benefit 2,789.6; percentile 95% CI **[1,127.57,4,563.97]**.
- Since DEV aggregate outcomes were inspected during idea development, these are **descriptive intervals, not prospective hypothesis-test confirmation**.

**Major scientific caveat:** At R5 under exact passive KCL, individual event-level wrong integer counts are almost unchanged: zero-rate 4656 (conductance) vs **4638 (CAMP-light)**; CAR 4670 vs **4664**. Partial-block zero-bias sign flips do not consistently improve (zero-rate 7 vs8; CAR 8 vs10, sometimes worse). **The observed gain is signed arithmetic MSE only**, not actual ReLU/inference reliability. No layer bias/full network or unseen final test set. No measured circuit energy or row-reprogramming overhead. Real PEX may reverse the ranking.

## E23 physically constrained GF microgate: PREPARED ONLY
User-private experiment package **E21_E23_CAMP_candidate.zip**, SHA256 a6a93bdf0f912a8b3961626c06f6452e1919b9fbda5100688534a8a6c0e43561, contains:
- E21, E22B, E22C, E22D, E22E full executable Python scripts, JSON outputs and private user-supplied E01 packet.
- `e23_gf_coactivation_read_probe.py` SHA256 d34ba3f03e65cea500aecba28a65b2e642920a26855693b13d1666be98988b89 plus verified E19 v2 hardware deck generator. **The code and private trace packet are in the conversation ZIP; they are NOT committed to this public GitHub repo.**
- NUS E23 uses **actual GF hvtnfet** l=20nm w=80nm + student static MTJ and **explicitly assumed** R0/R5Ω/segment bitline, nominal historic VREAD=.05 V and VWL=.8 V; *not 2T1MTJ PEX or a nondisturb qualification*. It constructs CAL-only 32-row CAMP and strong conductance-sort maps; tests exactly the **same logical (x,w,n,m,k)** events on both placements. It selects high-stress group(s) using CAL only, then measures independently held-out DEV.
- First microgate defaults to **group 7 (from first-block CAL)** and 4 CAL +8 DEV parents: 192 case profiles for each R, 384 actual individual circuit cases over R0 and R5, excluding inactive events. On local checks, all event pairs have equal ideal n,m,k, the mapper/group conservation selftest passed, and the mock GF deck parser constructed two 32-MOS patterns. **NO NEW NUS E23 Spectre has actually run; no GF result is claimed**.
- Mandatory R0 null: sense current should be invariant to permutation. DEV R5 metric: **paired actual sense-current droop** ((I_R0-I_R5)/I_R0) and reduction vs conductance sort, *not* imaginary reduction in ADC energy or inference error.

Run instructions are in the private package README. If R0 null fails, debug the deck. If real GF compact-model R5 droop benefit fails vs conductance sort, reject CAMP early. If it succeeds, continue to calibrated group count decoder, GF-parasitic extraction, mismatch/PVT and task-level inference, and cost accounting. A successful E23 STILL does not prove general publication novelty.

## CA2 disposition
**E21 rejected. E22 CAMP-light retained strictly as a promising, mathematically specific, cheap offline placement hypothesis with a ~10% held-out *constructed passive-ladder signed arithmetic MSE* improvement at fixed read count; physical/GF and actual neural inference gates open.** The full correlated-weight variant has no convincing payoff over the simpler light variant. Do not treat exploratory results as independent physical confirmation or hide original-mapping and R10 negative conditions.
