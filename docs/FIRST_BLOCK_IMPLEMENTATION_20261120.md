# Locked first-block implementation (20 November 2026)

Source branch: `research/m4-gain-fusion-20261107`. This document is implementation guidance; the authoritative design remains `docs/FYP_STUDY_LOCK_20261120.md`.

Files: `experiments/fyp_first_block_20261120.py`, `experiments/fyp_first_block_stats.py`, `tests/test_fyp_first_block.py` and the `fyp-first-block.yml` workflow.

The runner requires the unchanged, SHA256-checked original official Biq Mac files `data/biqmac/raw/ising/ising2.5-100_5555` and `ising2.5-100_7777`. Use Python 3.11 and NumPy 2.3.5. Commands (run from repo root after `python -m unittest discover -s tests -p 'test_fyp_first_block.py' -v`):

```bash
python -m experiments.fyp_first_block_20261120 --freeze
python -m experiments.fyp_first_block_20261120 --run --analyse
```

`--freeze` verifies source hashes, exact graph SHA256, INT7, solver parity on three representations and three deterministic archived M5/E0/EX1 replays. It persists a seed list, source commit, versions, data identifiers, analysis rules and 1,280-key expectation **before** new observations.

`--run` uses append-only sealed JSONL, permits exact verified resume and rejects corrupt/duplicate observations. It records all final states and checkpoint states, V/M/R, best represented energy and same-reference-state error measurements; `--analyse` refuses fewer than 1,280 unique records plus 2,048 fidelity checkpoints. Analysis uses 500,000 studentized bootstrap-t resamples and the separate fixed-graph 95% descriptive thresholds; the 18-core/six-device Bonferroni registry is included but **not** used to claim family-level inference from two viewed graphs.

The official _6666 graphs are deliberately not opened. No STT-MRAM physical device response is tested in this block. If CI cannot reach the official file server, preserve its failure log and run the same frozen commands on the NUS host; do not substitute graphs or fabricate outcomes. Original completed archives are unchanged.
