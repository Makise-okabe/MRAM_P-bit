# First-block decision-label clarification — 20 November 2026

**Scope:** Interpretation-only correction after the fully completed and frozen 1,280-run dataset (source commit `79bb061654d8fdf92b2645183023ac7f0780dea7`, raw-results commit `abe699f996ff77070d3c60608a36e3d76407efa5`). No new solver runs, no changed seeds, matrices, observations, numerical means, or confidence limits. The original SHA256-sealed manifest and CSV are preserved.

The originally generated `paired_contrasts.csv` classifies `unresolved` too narrowly: it used whether the 95% interval crossed **zero**, rather than whether the **+0.5 pp non-inferiority boundary** was settled. Use the following corrected *descriptive within-graph* interpretations:

| Graph | Condition | FP5 − INT6 mean gap (pp) | Paired 95% CI | Direction | +0.5 pp non-inferiority | True benefit exceeding 0.5 pp |
| --- | --- | ---: | --- | --- | --- | --- |
| `_5555` | Raw | +0.470 | [+0.186, +0.751] | INT6 significantly better | **Unresolved** | Not established |
| `_5555` | beta/a | +0.466 | [+0.188, +0.740] | INT6 significantly better | **Unresolved** | Not established |
| `_7777` | Raw | −0.349 | [−0.554, −0.142] | FP5 significantly better | **Supported** | Not established |
| `_7777` | beta/a | −0.311 | [−0.519, −0.099] | FP5 significantly better | **Supported** | Not established |

Neither graph supports a *true FP benefit exceeding 0.5 pp*, and the calibrated-versus-raw changes have intervals containing zero on both graphs. The point-estimate threshold (−0.5 pp) is not crossed on either graph.

A future reuse of `claims()` now reports both `statistical_inferiority` and `noninferiority_unresolved`. The original analysis implementation remains reproducible at source commit `79bb061`. Do not alter the frozen result files or their manifest to retrofit an interpretation flag. The completed workflow is changed to manual-only to prevent a second automatic campaign on an already closed block.
