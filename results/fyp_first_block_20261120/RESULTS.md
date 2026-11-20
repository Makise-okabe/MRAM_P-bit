# First viewed-dense block — results

Scope: two *viewed* official Biq Mac dense instances, 128 paired fresh solver seeds each, ideal sigmoid at gain 1 and offset 0. No MTJ measurements or family-level inference.

| Graph | Raw FP5–INT6 gap (pp), 95% CI | beta/a gap (pp), 95% CI | Paired calibration change (pp), 95% CI |
| --- | ---: | ---: | ---: |
| 5555 | +0.470 [+0.186, +0.751] | +0.466 [+0.188, +0.740] | -0.004 [-0.084, +0.094] |
| 7777 | -0.349 [-0.554, -0.142] | -0.311 [-0.519, -0.099] | +0.039 [-0.019, +0.113] |

Negative FP5–INT6 indicates FP5 yielded a smaller original-optimum gap. The calibration interaction is tested *directly*, not inferred from different significance labels.

The trajectory-components and fidelity CSVs explain where mean loss occurs. Components partition each run's gap exactly; they do not independently prove energetic-barrier causality.

Statistical superiority: upper interval < 0; true >0.5pp benefit: upper interval < -0.5; non-inferiority: upper interval < +0.5; equivalence: full interval inside [-0.5,+0.5]. These are descriptive 95% within-graph statements, NOT the later 18-contrast familywise inference.

Next under locked plan: generated independent ring/torus ensemble and official six-anchor ideal study, then selected-candidate assumed offset-bank validation and memory-inclusive architectural comparison. The _6666 anchors remain untouched until the later freeze.

Sources: frozen_settings.json, records.jsonl, fidelity.jsonl. The fixed 1,280-run cap closes this block regardless of sign.
