# Targeted related-work audit — 21 November 2026

This is a source-verified literature checkpoint for the fixed Ising stored-J FYP. Source visibility means **full** (author/publisher open full text), **abstract** (publisher abstract only), or **limited** (search-index details; no full article). Reading status is not a claim of comprehensive systematic review.

| BibTeX key | Verified source / DOI | Access reviewed | Specific relevant result | Boundary against this FYP |
|---|---|---|---|---|
| PbitLundowCampbell2016 | P. H. Lundow, I. A. Campbell, *Bimodal and Gaussian Ising spin glasses in dimension two*, Physical Review E 93 022119 (2016), https://doi.org/10.1103/PhysRevE.93.022119 | Publisher **abstract** | Bimodal ±J ground-state landscape is highly degenerate whereas Gaussian counterpart is nondegenerate (modulo global spin reversal). | Conceptual precedent for coarse/discrete energy ties; no claim that our six-bit data obey exactly the ±J universality class. |
| PbitXu2017 | N. Xu, K.-H. Wu, S. J. Rubin, Y.-J. Kao, A. W. Sandvik, *Dynamic scaling in the two-dimensional Ising spin glass with normal-distributed couplings*, Physical Review E 96 052102 (2017), https://doi.org/10.1103/PhysRevE.96.052102 | Publisher **abstract** | Explicit distinction between Gaussian unique ground state and bimodal massive degeneracy; dynamics differs. | Motivates testing ties, but spin-glass scaling and our fixed-budget 100-spin Max-Cut Gibbs controller are different. |
| PbitAyanzadeh2021 | R. Ayanzadeh, J. Dorband, M. Halem, T. Finin, *Multi-qubit correction for quantum annealers*, Scientific Reports 11 16119 (2021), https://doi.org/10.1038/s41598-021-95482-w | **Full text**, PMC8352911 | Classical post-processing of quantum-annealer samples is an established technique; authors combine excited-state samples to improve quality. | Our passive top-16 original-J rescoring does not synthesize new states; the *post-processing idea is not novel*. Our result measures how different legal codes and output policies trade selection loss. |
| PbitYao2026 | B. Yao, D. Ebler, X. Shi, J. Wang, F. Zhang, W. Zhang, J. Sun, *Precision meets speed through an FPGA-based natively sparse Ising machine for combinatorial optimization*, Nature Communications 17 8549 (2026), https://doi.org/10.1038/s41467-026-75119-0 | **Abstract / indexed full-text excerpts**; publisher full-text access inconsistent | FPGA digital Ising machine evaluates INT8 quantization against float32 quality and tests graph-weight distributions; hardware quantization and precision tradeoffs are already covered. | **Close overlap:** it is not novel to compare integer quantization with floating-point solver behavior for Ising optimizers. Distinction must be same-width sub-eight-bit FP/INT stored-J codes under paired stochastic p-bit dynamics, the registered weak-tail intervention, and decomposition of finite-budget access vs selection. Avoid implying no prior weighted Max-Cut precision comparison exists. |

## Interpretation and caveats

- The role of coefficient quantization in changing energy ties is physically and mathematically plausible; *counting nonzero edges alone* is not a complete explanation, as shown by the registered six-bit intervention checkpoint. No spin-glass paper proves our specific quantitative result.
- We must not describe ordinary host objective rescoring as a new algorithm or free hardware output. Its measured benefit, controller dependence, and original-J storage/transfer requirement are the useful contribution.
- The 2026 Yao et al. article materially narrows the precision novelty. Our report should explicitly cite it rather than calling hardware precision comparisons absent.
- Yang et al. and other physical p-bit device papers do not validate the synthetic uniform residual offset distribution. Stage B remains a *software sensitivity study*.
- Prior paper citation updates go into `references.bib`. The 31 unreferenced compute-in-memory `S01`–`S31` entries were removed; cited S32 and S33 were retained.

## Further verification needed

A full dedicated search for original-objective rescoring of *quantized* Ising/QUBO sample buffers may reveal more exact overlaps; the above post-processing paper is **not** asserted to be exact methodological prior art. No claim of priority or comprehensive coverage is made here.
