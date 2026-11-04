# Prof Fong — 5 Nov 2026: provisional E22 research direction (not novelty-certified)

## Candidate: Coactivation-Aware MRAM Row Placement (CAMP-light)
**Specific research question:** Can we reduce *nonlinear position-dependent MRAM read errors* **without increasing ADC read count** by using **pairwise activation co-occurrence** for offline within-block row placement, rather than mapping rows from marginal activation frequency or static fault susceptibility?

## Physics-to-algorithm chain
In a one-ended resistive bitline, source current under small wire R satisfies a leading term I≈V(G-rQ), Q=∑_l(∑_{j≥l}x_jg_j)^2. Holding each 32-row group exactly fixed, minimizing the *expected Q* involves pairwise input coactivation C_ij=E_CAL[x_i x_j] and physical shared-line length min(pos_i,pos_j). Use the low-cost approximation S_ij=C_ij·gbar_i·gbar_j where gbar is the mean weight-bit conductance across signed bitplanes and output columns. Offline greedy swaps within each 32-row group; all grouped read counts remain exactly invariant, so the resource claim is not bought with additional analog reads.

This is **NOT** an invention of IR-drop, stochastic reliability-aware mapping or correlated input handling. Important prior art includes 2026 SOT-MRAM Dyn-A-Map (fault-susceptible FOW relocation), 2023 hardware-aware analog-CIM work (ordered-weight IR drop), and DIB-CIM (input imbalance-adaptive WL parallelism). The precise pairwise intra-block objective and strong matched-baseline difference require an exhaustive close-prior-art check before claiming novelty.

## Executed evidence (software constructed physical model, NOT fresh GF)
Frozen verified E01 packet, 128 CAL and independent 256 DEV MNIST parent images; only first 256 logical FC1 rows, eight output channels, eight activation bits, signed W4 bitplanes. All candidates preserve each fixed 32-row group's logical membership. On a constructed exact Kirchhoff resistive 32-shunt network with assumed R=5Ω/segment and identical CAL-fitted centroid correction:
- Fixed zero-rate grouping: conductance-sorted DEV partial-block signed arithmetic MSE 28,332.5; **CAMP-light 25,508.2 (9.97% lower)**. 
- Fixed CAR alpha0 grouping: conductance sort 28,105.8; **CAMP-light 25,316.2 (9.93% lower)**.
- Same greedy optimizer with marginal-independent C_ij=p_i p_j gives 29,129.2 and 28,258.8, respectively, separating the benefit of pairwise coactivation rather than optimizer strength.
- Exploratory paired parent bootstrap 95% intervals for absolute MSE benefit over conductance sort: [1,185,4,666] (zero-rate) and [1,128,4,564] (CAR). The DEV split was examined during method development; independent prospective testing still needed.
- **No consistent improvement in individual count errors or partial-block zero-bias sign flips; in CAR sign flips can worsen. This is NOT evidence of full-network MNIST classification accuracy.** No PEX/actual GF circuit/ADC energy measured.

## Rejected algorithms kept for CA2
- E13 dynamic ReLU read scheduling: ~0.04 percentage points extra skip vs static policy, controller burden large.
- E15/E20 ADC/search-tree and spatial suffix-Q: ideal comparison-saving mathematically positive, but E20 GF current correction matched by simpler near/far/centroid methods, no compelling unique advantage.
- E21 signed-bitplane orientation: 4.4% improvement in one R/group setting, tied or lost elsewhere.
- E22 full coactivation × weight conductance covariance adds little over lighter product-of-means method; avoid extra complexity.

## Immediate next physical gate (E23 READY, NOT YET RUN)
Ready-to-run private E23 package in conversation. Reuses **licensed GF hvtnfet + student static MTJ**, not GF-native dynamic MTJ and not 256x256 physical PEX. Maps the SAME E01 logical CAL/DEV reads to mean-conductance sort vs CAMP-light, with R=0 null and assumed R=5Ω per segment. Measures **matched physical read-current droop** on NUS Spectre; first run 384 cases total, 4 CAL+8 DEV parents, one CAL-selected group. Must see R0 invariance and R5 benefit to continue. If missing, **reject**. Even if R5 improves, final neural decision/energy/real RC and proof against literature are outstanding.

## Meeting phrasing
“I rejected several read-side corrections after simple baselines matched them. I now have a precise proposed mapping algorithm derived from the pairwise quadratic source-wire loss, rather than simply putting sensitive weights in reliable regions. It rearranges rows *within fixed CIM read groups* according to CAL-measured pairwise activation co-occurrence, so analog read count is unchanged. With independently held-out MNIST inputs in an exact passive Kirchhoff model, it lowers reconstructed signed arithmetic MSE by roughly ten percent versus mean-conductance row sorting under both CAR and zero-rate groupings. This is still not GF PEX or end-to-end accuracy, and I am executing a matched GF+MTJ current test before calling it a contribution. I need to check closest prior art before claiming novelty.” 

Evidence [E21–E23](../experiments/2026-11-04-E21-E23-coactivation-mapping-discovery-and-GF-gate.md).
