# Source-only provenance and official-anchor spread

20 November 2026. All 144 registered generated sources and six official source files were checked against their recorded SHA256 values after copying the acquisition manifest. No campaign outcome was read, no solver ran, and no graph was selected or rejected for this comparison.

Executable freeze: `d217ab54fc41a3a84d6a500f3ab0f3aa433059dd`. Both official `_6666` sources were acquired after that freeze. `post_freeze_source_manifest.json` is an exact copy of the acquisition record, including its acquisition timestamp and first-fetch hashes.

The generated-family central 95% interval means the empirical 2.5th–97.5th percentiles across its 72 fixed graph draws, using NumPy linear quantiles. It is a descriptive distribution interval, not a confidence interval or a rejection rule. Maximum absolute source weight and raw zero-entry count are evaluated separately.

## Generated source spread

| Family | Source metric | Full observed range | Empirical central 95% |
| --- | --- | ---: | ---: |
| ring | `max_abs_weight` | 137395–290819 | 146617–254961 |
| ring | `zero_count` | 59–101 | 61.325–92.8 |
| torus | `max_abs_weight` | 223512–385279 | 227377–350229 |
| torus | `zero_count` | 0–0 | 0–0 |

## Six official anchors

| Official source | Max absolute weight | Raw zeros | Max weight in central 95% | Zeros in central 95% |
| --- | ---: | ---: | --- | --- |
| `ising2.5-100_5555` | 239752 | 69 | inside | inside |
| `ising2.5-100_6666` | 212231 | 73 | inside | inside |
| `ising2.5-100_7777` | 220276 | 81 | inside | inside |
| `t2g10_5555` | 294541 | 0 | inside | inside |
| `t2g10_6666` | 239344 | 0 | inside | inside |
| `t2g10_7777` | 301004 | 0 | inside | inside |

All six official sources lie within the corresponding generated family ranges for both recorded source metrics. There are 0 source-metric observations outside the empirical central 95% intervals.

These source-scale observations do not establish that anchor solution quality or precision penalties lie within the generated-family outcome spread. That requires the complete campaign analysis.

## Original sources and hashes

Official library: https://biqmac.aau.at/biqmaclib.html. Source directory: https://biqmac.aau.at/library/mac/ising/.

| Official source URL | SHA256 |
| --- | --- |
| [ising2.5-100_5555](https://biqmac.aau.at/library/mac/ising/ising2.5-100_5555) | `c8fa3ce4df1997b89aad6199525a66e55699c259680483b62cc5fd3cfc1e316e` |
| [ising2.5-100_6666](https://biqmac.aau.at/library/mac/ising/ising2.5-100_6666) | `647447f59b79efecda903732b5d2e9cada03226daf3d08871746787496b3f647` |
| [ising2.5-100_7777](https://biqmac.aau.at/library/mac/ising/ising2.5-100_7777) | `109e1ed2edc71d5f43d623367410d9257a72662d665c7a0c71af4cdd8babaf99` |
| [t2g10_5555](https://biqmac.aau.at/library/mac/ising/t2g10_5555) | `c742b78ebdebb47ad7146bffd657d42fab814a7fa82c4a17942b37f2f7fa96cb` |
| [t2g10_6666](https://biqmac.aau.at/library/mac/ising/t2g10_6666) | `8e9f42291665df989bd5422343b3b4ddf845b5cad33e98c2d9250dc7aee8a4cc` |
| [t2g10_7777](https://biqmac.aau.at/library/mac/ising/t2g10_7777) | `8f7dc4e791eb4893f7b7114b6ac51d29f37f652645ba58a22e3cd29b709fd4ef` |

Generated-source definitions, scale and seed namespaces remain those in [the study lock](../../../docs/FYP_STUDY_LOCK_20261120.md). Individual generated source hashes are in `data/fyp_locked_20261120/source_manifest.json`.

Generated source manifest SHA256: `3950867acc9a9ab2e3687b7e15ac37546682824184f5b8410d85147ba4b2a215`.

Copied official acquisition manifest SHA256: `e9beb8a658dc79be307bb23f4ee2e3659c0e0265265a9e03b93b09a05adb9584`.

`source_spread.json` contains the full summaries and comparison definitions. `source_spread.csv` contains one row per official graph and source metric.
