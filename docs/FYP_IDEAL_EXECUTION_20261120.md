# Locked ideal campaign: executable and sharded execution

20 November 2026. This document describes execution of the existing study lock
and its dated descriptive-mechanism amendment. It introduces no candidate,
seed namespace, graph, response condition, schedule or quality criterion.

The authoritative scientific specification is
[FYP_STUDY_LOCK_20261120.md](FYP_STUDY_LOCK_20261120.md). The executable freeze is
`docs/FYP_IDEAL_FREEZE_20261120.json`, committed before opening either official
`_6666` weight file or running a generated-instance trajectory. A run must name
the full 40-character commit containing that freeze. Read-only verification
must pass before any campaign action.

## Immutable inputs and source extraction

All 144 graph draws were generated, saved and individually hashed before
solver execution. The committed archive is
`data/fyp_locked_20261120/sources.tar.gz`. Its members are exactly
`ring/000.rudy` through `ring/071.rudy` and `torus/000.rudy` through
`torus/071.rudy`; extraction places them under
`data/fyp_locked_20261120/`. `source_manifest.json` records every individual
SHA256 and the pinned NumPy 2.3.5/PCG64DXSM generation procedure. Raw zero-weight
entries remain in these sources. The source generator must not be rerun to
replace, select or repair a draw during the campaign.

Extract the committed archive and run the freeze gate before downloading the
two held-out official files:

```bash
python -m experiments.fyp_ideal_campaign \
  --freeze docs/FYP_IDEAL_FREEZE_20261120.json \
  --freeze-commit FULL_40_CHARACTER_FREEZE_COMMIT --verify-freeze
python -m experiments.fyp_ideal_sources --verify
```

The gate also verifies the four previously viewed official source files, which
are committed under `data/biqmac/raw/ising`. The two official `_6666` sources
are fetched only after this gate from the same official Mac/ising directory.
Their first post-freeze fetch hashes are recorded as acquisition provenance;
they are not falsely described as known before the freeze. A single shared
official-source artifact supplies all six anchor jobs. The known hashes of the
four viewed sources are checked, and every shard verifies the shared six-file
hash manifest. Source files must never change within a campaign.

## Work partitions and fixed counts

The workflow `.github/workflows/fyp-ideal-locked.yml` has a manual
`workflow_dispatch` trigger only. Its required `frozen_commit` input is the
full executable-freeze SHA, checked out in every job. It does not execute on
push or pull request. It is a reproducible execution alternative, not a second
copy of a campaign already completed locally.

One matrix contains 18 shards and permits at most six simultaneous jobs. The
generated shards use half-open graph-index ranges:

| Family | Graph-index ranges | Jobs | Registered trajectories per job |
| --- | --- | ---: | ---: |
| Ring, family 0 | `[0,12)`, `[12,24)`, `[24,36)`, `[36,48)`, `[48,60)`, `[60,72)` | 6 | 6912 |
| Torus, family 1 | Same six ranges | 6 | 6912 |
| Official anchors | One anchor index per job, 0 through 5 | 6 | 896 represented records |

Each generated graph has 448 main trajectories (64 seeds times seven
candidates) and 128 independent FP64 reference trajectories, hence 576 per
graph and 6912 per 12-graph job. Generated totals are 64,512 main trajectories
and 18,432 reference trajectories. Each anchor has 128 seeds times seven
candidates, hence 896 records and 5,376 records across six anchors. The 768
raw FP64/FP5/INT6 first-block records on dense 5555 and 7777 are reused; those
two anchor jobs execute only their four missing candidates, 512 new trajectories
each. Other anchor jobs execute 896 new trajectories each. The ideal campaign
therefore comprises 88,320 represented records and 87,552 new trajectories,
excluding the archived 512 beta/a controls from campaign counts.

The exact ordering of anchor indices is:

| Index | Official graph |
| ---: | --- |
| 0 | `ising2.5-100_5555` |
| 1 | `ising2.5-100_6666` |
| 2 | `ising2.5-100_7777` |
| 3 | `t2g10_5555` |
| 4 | `t2g10_6666` |
| 5 | `t2g10_7777` |

Example registered shard commands, with exclusive `--stop`:

```bash
python -m experiments.fyp_ideal_campaign \
  --freeze docs/FYP_IDEAL_FREEZE_20261120.json \
  --freeze-commit FULL_40_CHARACTER_FREEZE_COMMIT \
  --family 0 --start 0 --stop 12

python -m experiments.fyp_ideal_campaign \
  --freeze docs/FYP_IDEAL_FREEZE_20261120.json \
  --freeze-commit FULL_40_CHARACTER_FREEZE_COMMIT --anchor-index 0
```

The solver seed domains remain exactly:

- Reference: `1000000000000 + 100000*family + 1000*index + replicate`,
  with replicates 0 through 127.
- Main: `2000000000000 + 100000*family + 1000*index + replicate`,
  with replicates 0 through 63.
- Anchors: `3000000000000 + 10000*anchor_index + replicate`,
  with replicates 0 through 127.

Partitioning jobs does not alter graph order, candidates, paired seeds, run
caps, update arithmetic or reference-pool membership. Every trajectory has
gain 1 and offset 0. No offset, gain or hardware step is present in the workflow.

## Runtime and job limits

Each job has a 30-minute limit; installation, archive extraction, hash checks,
quantization, passive logging, fidelity calculations and artifact upload must
fit inside that limit. The workflow pins Python 3.12.14, matching the preflight
runtime, and NumPy 2.3.5. Fresh engineering measurements are archived in
`results/fyp_ideal_preflight_20261120/pipeline_timing.json`; derived estimates
are in that directory's `execution_plan.json`.

| Engineering measurement or estimate | Ring, viewed dense 7777 | Torus, viewed 5555 |
| --- | ---: | ---: |
| Measured INT7 logged trajectory, 50000 updates | 0.05498 s | 0.03705 s |
| Estimated complete generated graph, 576 trajectories and fidelity work | 34.55 s | 22.08 s |
| Estimated 12-graph shard | 414.61 s (6.91 min) | 264.94 s (4.42 min) |
| Twice the estimated shard runtime | 13.82 min | 8.83 min |

These estimates include fitting each representation once and the measured
logging/fidelity work. They use one viewed-case timing sample per candidate,
so they are not confidence bounds or completed generated-campaign timings.
The estimated serial total, including anchors, is 71.69 minutes before
separate bootstrap/figure work and CI installation/upload overhead. A twofold
engineering margin still leaves substantial room within each 30-minute job.
Actual completed-bundle timing sidecars provide the campaign measurements.

A timeout is an execution failure, not permission to add seeds or omit a
graph. The runner verifies and skips an existing complete graph bundle; a
partial or `FAILED` bundle stops execution and requires review. Preserve
completed artifacts before any resumption, and do not blindly redispatch a
finished campaign. Partial artifacts remain available on failure. They
cannot support a complete-family checkpoint.

## Deterministic merge and verification

Generated graph bundles live under
`results/fyp_ideal_20261120/generated/{ring|torus}/{index:03d}/`; anchors live
under `results/fyp_ideal_20261120/anchors/{official_name}/`. Shards publish raw
records and provenance only. Their logs report progress/counts/timing rather
than quality summaries. No quality-analysis step runs until all 18 shard jobs
succeed and their artifacts have been merged.

The aggregate job requires exactly the 12 generated and six anchor artifacts.
It merges sorted artifact paths and refuses differing files at any duplicate
path. It then verifies complete counts, unique keys, source hashes and the
fixed reference pools before running analysis:

```bash
python -m experiments.fyp_ideal_campaign \
  --freeze docs/FYP_IDEAL_FREEZE_20261120.json \
  --freeze-commit FULL_40_CHARACTER_FREEZE_COMMIT --verify-all

python -m experiments.fyp_ideal_analysis \
  --analyse results/fyp_ideal_20261120
```

The generated reference is the best feasible original cut visited in the
fixed 576-trajectory pool, with the empty cut as zero fallback. It is neither
an optimum certificate nor a reference updated by later runs. The analysis
uses the frozen 18-contrast registry, whole-graph-vector studentized
bootstrap-t with 500,000 resamples, and the existing Bonferroni tails. The
descriptive endpoints and reused first-block records retain their stated
limitations, including unavailable historical `R_last` values.

## Publication and stopping point

Every job has read-only repository permission. No matrix job commits or
pushes, so parallel shards cannot race over the research branch. The aggregate
job publishes one `fyp-ideal-checkpoint-FREEZE_SHA` artifact, containing the
verified complete bundle, analysis, figures, result report and post-freeze
official-source provenance.

A single final publisher may download that artifact, verify it against the
same freeze, and commit the completed results once. Deterministic result
archives use sorted member paths, stable JSON/CSV ordering and gzip mtime 0;
do not include incidental machine-specific absolute paths or current
timestamps in canonical result content. Do not rewrite the closed first-block
archive or its original commit. If the branch advanced while the campaign
ran, integrate the single result commit normally without force-pushing or
changing the executable freeze.

The checkpoint report must cover all 18 core contrasts with bounds/labels,
the lowest tested certified widths and selected future offset pair, the
descriptive access/selection results and tentative prediction failures,
`R_last - R`, all six official anchors relative to their generated-family
spread, and any failed or unresolved checks. Stop there. An unresolved
candidate remains unresolved at the registered cap. The workflow does not
start the offset stage or execute an additional campaign after this report.
