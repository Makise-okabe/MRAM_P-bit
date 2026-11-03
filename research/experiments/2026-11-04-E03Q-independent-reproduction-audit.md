# Independent reproduction audit and evidence correction — 4 Nov 2026

The 4 November E03Q constructed-model result was challenged as possibly invented. This audit reran the `experiments/e03q_finite_adc_pilot.py` Python script in an independent container process against 65,536 calibration + 131,072 evaluation samples, with seed and options from the saved experiment. The recomputed JSON was **byte-identical** to the existing constructed output.

- Source script SHA256: `9afd60c36bb260eb7fb3914e84bf494615474c3741a04f677c2a64ccdae8410c`.
- Previous output SHA256: `0541221d31a3cff41ea78b3ab936535b993447a09d02c7ba310217048cfa758a`.
- Independently reproduced output SHA256: `0541221d31a3cff41ea78b3ab936535b993447a09d02c7ba310217048cfa758a`.
- Replicated tuned 6-bit MSE: A = `0.12227630615234375`, B = `0.0876312255859375`.
- These are **independent simulated chip draws**, not physical MRAM chips. Parameters are normalized and chosen by a constructed model; an oracle-like group-correction assumption is made.
- There was **zero Spectre execution, PEX or 256x256 physical-array measurement** behind E03Q. Presenting the improvement without foregrounding this was misleading. The experiment is not a novelty or target-hardware pass.

Reproduction command:
```sh
OPENBLAS_NUM_THREADS=1 python3 experiments/e03q_finite_adc_pilot.py \
  --out NEW_PRIVATE_OUTPUT.json --cal-samples 65536 --eval-samples 131072
sha256sum NEW_PRIVATE_OUTPUT.json
```

**Next experiment:** target physical E02-A as in `research/experiments/E02A_fresh_256x256_physical_read_screen.md`. No retired current data may be imported into the target calibration. E01 independently trained digits pilot is also workload-only, not a target-circuit result.
