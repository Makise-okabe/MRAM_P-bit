# Descriptive mechanism amendment — 20 November 2026

Authority: the student's staged continuation instruction following research
commit `6f22bfde4e27e1262cc2e4a08157430ec53c1bcb`. The authoritative study is
[FYP_STUDY_LOCK_20261120.md](FYP_STUDY_LOCK_20261120.md). This amendment changes
documentation and descriptive analysis endpoints only; it does not change the
scientific question, formats, solver, generator, reference pool, tolerance,
18-contrast core registry, alpha, seed namespaces or run caps.

## Reason and viewed-data motivation

The completed first block shows that the FP5/INT6 returned-quality contrast
reverses sign between the two viewed dense graphs. Selection loss and access
differences can be calculated from the archived trajectories without choosing a
new solver or making a barrier-causality claim. On raw first-block trajectories,
mean selection loss `Rz` is approximately 0.670 pp for FP5 and 0.285 pp for INT6
on `_5555`, and 0.135 versus 0.088 pp on `_7777`. Access differences change sign
between graphs. These are descriptive motivations from viewed instances, not
independent confirmations of the prospective directional predictions.

The frozen first-block records, numerical results, manifest and decision-label
addendum stand. No campaign rerun or retrospective replacement is authorized.

## Per-run definitions and identity

Let `V` be the largest original cut visited, `M` the largest original cut among
states attaining the minimum represented energy, and `R` the actual returned
original cut. Pair each candidate with the FP64 trajectory using the same graph
and solver seed. Use denominator `C` equal to the published optimum on official
anchors, and the locked fixed-pool best-observed feasible reference `B_g` on
generated graphs.

```
A_candidate = 100 * (V_FP64 - V_candidate) / C
Rz_candidate = 100 * (V_candidate - R_candidate) / C
represented_selection = 100 * (V_candidate - M_candidate) / C
earliest_tie = 100 * (M_candidate - R_candidate) / C
Rz_candidate = represented_selection + earliest_tie

extra_shortfall_vs_FP64 = A_candidate + Rz_candidate - Rz_FP64
```

`Rz >= 0` follows from its definition. Its nonnegative sign is not evidence for
a mechanism. Retain the FP64 selection term in the identity even when it is
identically zero for the ideal source objective. `A` is signed. In a format
contrast, `A_FP - A_INT = 100*(V_INT - V_FP)/C`; positive means worse FP access.
All identities concern the sampled path and the unchanged return policy, not
global optimum preservation, equilibrium sampling or an identified barrier.

## Prospective descriptive registry

There are three named mechanism comparisons in each generated family:

| Contrast | Tentative prediction for mean Rz difference |
| --- | --- |
| FP5 minus INT6 | Positive: Rz(FP5) > Rz(INT6) |
| FP6 minus INT7 | Positive: Rz(FP6) > Rz(INT7) |
| FP6 minus INT6 | **No predicted direction** |

FP6 and INT6 each have 31 positive nonzero levels. Level count motivates the
directional comparisons but does not prove them; code spacing, scaling and
visited states also differ. The FP6/INT7 prediction is tentative and is not an
already-observed first-block result.

For each family and each named comparison, report:

- Mean per-graph `Rz_FP - Rz_INT`, with a descriptive 95% interval resampling
  whole graph vectors, plus counts of positive, zero and negative graph means.
- Mean per-graph `A_FP - A_INT`, with the corresponding descriptive interval.
- Between-graph SD of graph means alongside the typical within-graph standard
  error (the median of paired-seed standard errors, with its spread stated).
- Whether the tentative prediction agrees with the point estimate, has a 95%
  interval entirely in the predicted direction, is contradicted, or is
  unresolved. These labels are descriptive, not multiplicity-protected claims.

For each candidate separately within each family, report Spearman correlations
across graph means between each of `Rz` and `A` and:

1. common-state mean absolute probability error `mean |DeltaP|`;
2. common-state field RMS error;
3. zeroed absolute source-weight mass fraction
   `sum(|w_e| for quantized coefficient == 0) / sum(|w_e|)`.

Common-state quantities are first aggregated over spins/checkpoints/seeds for a
graph. Correlations do not pool formats into artificial independent samples and
do not establish causality. Constant-variable correlations are undefined, not
zero. No claim is based on treating spins, checkpoints, seed pairs or vertex
permutations as independent graph instances.

## Passive latest-minimum endpoint

Add only the passive field `R_last`: the original cut of the **latest** state
attaining the trajectory's minimum represented energy. Initialize it with the
initial state, replace it at a strict new represented-energy minimum, and update
it at every later equal-minimum state. Its recording must not change RNG
consumption, represented-field operations, trajectory, energy retention or the
returned state.

Report signed `R_last - R` per candidate (raw cut units, and normalized pp where
appropriate). It can be positive or negative. It is a counterfactual tie-policy
diagnostic; it does not replace the solver's earliest-minimum return rule.

The archived first block did not record this field. Preserve its records and
report the field as unavailable for reused first-block rows. Authorized sampled
parity replays are a verification panel, not a new 1280-run dataset or a reason
to backfill every missing endpoint.

## Inference and scope

All endpoints in this amendment are **descriptive** and consume no alpha from
the nine registered core comparisons per family (18 total). Their 95% intervals
must be visually and verbally distinguished from the core Bonferroni bounds.
First-block smoke-test summaries use paired seeds within each fixed viewed
graph and do not turn the two labels into a family-level sample.

No distinct-energies-among-the-best-one-percent endpoint is included. No new
schedule, precision, device-response or hardware experiment follows from an
unexpected descriptive result. The next authorized stopping point is the ideal
campaign checkpoint; offset, gain and hardware work wait for confirmation.
