# Weak-tail checkpoint interpretation — 21 November 2026

The bounded prospective experiment is complete. Both registered ring contrasts are supported. Removing the accurately represented weak tail from FP6 increases live-trajectory selection loss; restoring the same tail values to INT6 reduces it. This establishes an effect of these particular tail interventions under the fixed six-bit, ideal-response controller. It does not establish that nonzero-edge count alone determines loss, or that every FP format benefits by the same amount.

The analysed dataset contains 48 fresh graphs (24 per family), 64 paired seeds and six arms: 18,432 unique trajectories. The scientific code and analysis were frozen at 54c06ff593c8acded95f7e4ce6f04a347c6164f7. Independent artifact verification recomputed 1,728 graph-mean cells and both confirmatory point estimates from the raw records, with no solver calls.

| Registered ring intervention | Mean change in selection loss, pp | Confirmatory 98.75% one-sided lower bound | Decision |
|---|---:|---:|---|
| C1: fp6_mask − fp6 | 0.07562 | 0.04719 | SUPPORTED |
| C2: int6 − int6_tail | 0.09132 | 0.06210 | SUPPORTED |

The two tests each use one-sided alpha 0.0125, 500,000 whole-graph studentized bootstrap resamples and the registered familywise budget 0.025. Both had zero invalid studentizations. Upper bounds and all ordinary descriptive intervals are in the full report.

Selection loss means that a run visits a solution with a better original cut than the solution its quantized objective returns. The prospective results are not simply the nonnegative V−R identity: the confirmatory effects compare that loss between arms while adding or removing exactly the same accurate weak-tail values.

The factorial means below separate selection from search. All are original-weight, control-reference-normalized percentage points, averaged equally over the 24 graphs. Extra loss equals access A plus selection Rz. These are point estimates; the complete descriptive intervals are preserved in the report.

| Family | Arm | Selection Rz | Access A | Extra loss |
|---|---|---:|---:|---:|
| ring | fp6 | 0.01803 | 0.08764 | 0.10567 |
| ring | fp6_mask | 0.09365 | 0.19155 | 0.28520 |
| ring | int6_tail | 0.07208 | 0.06636 | 0.13844 |
| ring | int6 | 0.16339 | 0.15801 | 0.32141 |
| torus | fp6 | 0.02231 | 0.09552 | 0.11783 |
| torus | fp6_mask | 0.02636 | 0.08717 | 0.11354 |
| torus | int6_tail | 0.02397 | 0.02637 | 0.05034 |
| torus | int6 | 0.02672 | 0.00685 | 0.03357 |

Several qualifications sharpen the contribution.

1. The strong values still matter. On the new ring graphs, FP6 and INT6_tail preserve the same support (mean 746.08 edges), yet their mean selection losses are 0.01803 and 0.07208 pp. FP6_mask and INT6 also share a support (mean 251.92 edges), with losses 0.09365 and 0.16339 pp. Retained-edge count is therefore an incomplete explanation. Strong-coupling values and the states visited also contribute. The descriptive total-selection interaction is −0.01570 pp [−0.06842,+0.01172]; this does not establish independence or zero interaction.

2. The two interventions affect different parts of the observed mean loss. For FP6, masking raises represented-objective selection loss V−M from 0.01613 to 0.08370 pp and tie loss M−R from 0.00190 to 0.00995 pp. For INT6, restoring the tail leaves V−M almost unchanged (0.06938 to 0.06921 pp), while tie loss falls from 0.09402 to 0.00287 pp. About 99.8% of the latter mean selection improvement is accounted for by the tie term. These are descriptive decompositions, not identification of a unique path-independent mechanism.

3. The shared-bank result is clearest for masking FP6. On the exact same pooled candidate bank, mean loss rises from 0.03943 pp for FP6 to 0.32278 pp for FP6_mask: 16 graphs worsen, none improve and eight tie. Restoring the tail to INT6 lowers mean bank loss from 0.25010 to 0.18164 pp, but individual results are mixed (seven improve, five worsen and twelve tie). Thus the fixed-bank evidence does not support uniform ranking improvement for every intervention on every instance. Several zero-heavy bank/tie endpoints have unresolved studentized intervals; keep their point values descriptive. FP64 bank selection loss is mathematically zero by construction.

4. A small output buffer recovers most live selection loss. On the ring, host rescoring of the passive top 16 represented-energy candidates recovers 99.97% of FP6's mean selection loss, 96.87% for FP6_mask, 98.12% for INT6_tail and 93.93% for INT6. These percentages are ratios of family means, not average per-run percentages or new statistical tests. For FP6 versus INT6 the mean extra-loss difference falls from 0.21574 to 0.08029 pp after rescoring, a descriptive reduction of about 63%. This does not establish post-buffer equivalence, re-certify the FP5 bit saving, or prove a free hardware improvement. It requires original J accessible on the host and extra scoring/transfer work.

5. The torus responds much less. Its mean removal/restoration effects on Rz are 0.00405 and 0.00275 pp, compared with 0.07562 and 0.09132 pp on the ring. The four factorial torus arms recover all their measured mean selection loss with top-16 rescoring in this finite dataset. This is consistent with the descriptive negative-control expectation; no practical-equivalence claim was registered or established.

6. The inflation diagnostic behaves very differently. Ring INT6_keep retains all source edges but has 4.47547 pp selection loss and 11.12086 pp extra loss. Forcing tiny weights to one integer step is not a faithful restoration and cannot refute the accurate-tail hypothesis. Its poor result also prevents any recommendation to keep edges merely to increase their count.

The supported engineering insight is that coupling encoding and output selection must be evaluated together. Accurate weak-tail values can reduce selection loss at six bits, while host rescoring can recover much of that loss. The contribution remains a conditional measurement and design rule for the specified controller and source families; it is not a universal explanation of Ising precision, a measured STT-MTJ result, or an established hardware saving.

The broader FYP direction is unchanged. The earlier ideal study's FP5/INT6 ring and FP5/INT5 torus choices remain recorded for the later offset stage. No offset, gain-variation or hardware work was run at this checkpoint.

Execution provenance is explicit. The original workspace failed after at least 19 completed bundles had been observed; its final count was unrecoverable and none of its outputs were pooled. The same prescribed keys were re-executed on GitHub Actions. Scientific run 44797500337 completed the solver and analysis but failed at the final git-add step because results directories are ignored. Artifact 14659628343 retained all outputs. Archive-only run 44799133098 verified and committed that artifact with zero additional solver calls. The total number of physical computations across the failed workspace and cloud replay is unknown; the analysed dataset contains exactly 18,432 unique prescribed trajectories.

Evidence: [full checkpoint report](../results/fyp_tail_probe_20261121/RESULTS.md), [confirmatory bounds](../results/fyp_tail_probe_20261121/analysis/confirmatory.csv), [graph-level data](../results/fyp_tail_probe_20261121/analysis/graph_summary.csv), [independent artifact audit](../results/fyp_tail_preflight_20261121/artifact_archive_recovery.json), [scientific execution](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/44797500337), and [archive-only recovery](https://github.com/Makise-okabe/MRAM_P-bit/actions/runs/44799133098).
