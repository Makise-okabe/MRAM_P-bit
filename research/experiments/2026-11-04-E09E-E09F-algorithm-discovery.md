# E09E/E09F — Ising algorithm discovery: cache equivalence and decision certificate

Date: 4 November 2026 (Singapore). **Synthetic Python software experiments only; not measured 256×256 MRAM.** Scripts, full JSON results, and the previous E09D dependency were supplied in the conversation as `e09e_e09f_ising_discovery.zip`, SHA-256 `1ffbf500a3c0178cacca2da2921691c048e8146cf45850fc931fa4718f4cf963`. Do not treat that archive as having been committed to this repo.

## E09E: decisive falsifier for reversal-consistent cache

Hypothesis: pin an imperfect coupling column until the spin returns, then use the same measurement for the inverse update. If all B pins are occupied, use exact digital coefficient reads for both halves of the bypassed excursion.

We independently implemented a conventional **locked cache with exact bypass**. It matches the proposed pinned implementation at every attempted update: exact spins, field values, cache hits and read counters. Thus the implementation is ordinary cache locking under those rules; cancellation is a valid invariant but **not a distinct algorithm**.

An independently run 16-spin random weighted Max-Cut instance, exact optimum, 100 paired restart seeds, eight heat-bath sweeps, and hypothetical independent temporal Gaussian coefficient read errors (sigma=0.6 abstract units) gave:

| Policy | Cache slots | Optimum hits / 100 | Hypothetical cost (analog read=1, exact digital read=2) |
|---|---:|---:|---:|
| Exact digital incremental | — | 31 | 39.0 |
| Ordinary LRU | 2 | 15 | 20.52 |
| Pinned reversal + exact bypass | 2 | 32 | 34.87 |
| Independent ordinary locked + exact bypass | 2 | 32 | 34.87 |
| Locked with noisy bypass (no exact fallback) | 2 | 7 | 20.35 |
| Ordinary LRU | 16 | 20 | 12.94 |
| Pinned reversal | 16 | 18 | 14.81 |

This apparent small-cache gain uses many exact digital reads. Larger-cache LRU is competitive and cheaper on this point sample. The B=16 paired success difference (pinned-LRU) is -0.02; approximate 95% CI [-0.068, 0.028]. A fixed periodic refresh comparator also ran, but refresh cadence was **not optimized**; these are not complete Pareto frontiers.

The synthetic two-read residual `2(eta2-eta1)` has variance `8 sigma^2 (1-rho)` for errors with variance sigma^2 and correlation rho. Numerical 100,000-pair draws with sigma=0.6 verified 2.883 (rho=0), 1.449 (rho=0.5), 0.289 (rho=0.9), 0 (rho=1), consistent with 2.88, 1.44, 0.288, 0 analytically. Strong read-to-read correlation already suppresses reversal drift **without retention**.

**Disposition:** stop treating this particular cache-locking rule as a novelty candidate. Its error cancellation is true but insufficient. Neither persistent MTJ mismatch nor an analog dot-product error is automatically a temporally fresh coupling-column read error.

## E09F: bound-certified stochastic spin update, an alternative comparator (not claimed novel)

Given an externally justified bound `|h-hhat| <= delta` and heat-bath draw `u`, calculate `p_lo=p(hhat-delta)`, `p_hi=p(hhat+delta)`, and accept the approximate spin decision when `u < p_lo` or `u >= p_hi`. Otherwise compute the exact field. This guarantees identical decisions to exact digital under the bound. It is closely related to established decision-aware precision/refinement; novelty would require an additional MRAM-specific mechanism and useful comparator advantage.

On a synthetic 16-spin weighted Max-Cut instance, 160 independent paired seeds, eight sweeps (128 update attempts per restart), uniform **bounded field error**:

| Assumed bound delta | Certified updates | Mean exact full-field fallbacks / 128 attempts | Hypothetical break-even exact digital column cost / analog field read cost |
|---|---:|---:|---:|
| 0.25 | 98.58% | 1.81 | > 7.22 |
| 0.75 | 95.47% | 5.79 | > 9.31 |
| 1.5 | 90.26% | 12.47 | > 18.11 |
| 3.0 | 79.69% | 25.99 | none for this operation-count model |

Here an exact digital incremental solver uses a mean 19.54 exact coupling-column reads per restart, while the certificate uses 128 analog field reads plus fallbacks. The cost ratios are ***assumed normalized operation prices***, not energy/latency data. All certified trajectories exactly match the digital reference; no hardware bound has been characterized. Note that noisy annealing can sometimes improve success on a particular graph, so differences in success hits are not monotonic evidence of algorithm quality.

## Research decision and gating

- Prefer discovering a different method, rather than turning cache locking or generic decision refinement into a new FYP claim.
- The question for a stronger Ising candidate: does a **specific physically implemented read operation** produce a predictable spatial/temporal error structure which an implementable low-overhead adaptive field algorithm can exploit **beyond** locked caching, periodic refresh, accurate digital incremental fields and established precision-refinement?
- Before another large campaign, freeze the read operator (whole coupling column versus analog dot product), error type, hardware cost ratios, available error information, independent graph/chip splits, and matching baseline search budgets.
- Do not commit PDK files, raw foundry models, or retired eight-cell currents to public GitHub.

Related closest work: Snowball (2026, https://arxiv.org/abs/2601.21058) already implements incremental fields; SACHI (2024, https://ieeexplore.ieee.org/abstract/document/10476402) already implements near-cache reuse. This targeted comparison does not prove absence of other literature.
