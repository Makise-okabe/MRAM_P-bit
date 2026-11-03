# Bounded screening queue and elimination decisions

4 November 2026 (Singapore). Implements ADR-0003; no final core selected.

## Research question for the next stage

Which aspects of physical read organization and persistent error structure change a
useful computation decision, and can a specific mapper or controller improve that
decision beyond the strongest simple alternatives? The physical target remains 256x256.
The shared story is an organizing question, not the contribution itself.

## Consolidated dispositions

| Ideas / IDs | Current role | What earns continuation |
|---|---|---|
| D12-D14, F3 | Main development candidate: grouping using decoded error covariance under a resource budget | Target covariance effect plus an effective one-permutation mapper beyond tuned combined baselines |
| D17, F7a | Retained Ising persistence/field-organization diagnostic | A distinct design consequence after matching marginals, cache controls and existing coupling-error theory |
| D18, F7b | Reserve Ising refinement intervention | A cheap valid field bound and useful cost improvement beyond existing update schemes |
| D01-D03, F1 | Estimation tool and independent method reserve | A demonstrable accuracy/total-cost advantage; an inaccessible paper title does not eliminate it |
| D05,D10,D13; routine bit-aware allocation and incremental fields | Mandatory baselines; generic novelty claims eliminated | Narrower new implementations remain possible, but ordinary versions are not claimed |
| D04,D06,D20 / F4 | Decision-refinement reserve | New cheap implementation and total resource gain |
| D08-D11 / F2 | Encoding/polarity reserve | Target electrical benefit beyond minority inversion and known recoding |
| D15 / F5 and circuit co-design R01 | Cost/architecture reserve | Credible costs and a distinct rule or implementation |
| D07,D16,D21 / F6 | Information/sensing reserve | Relevant ambiguity and an economical new observable |
| D19, LLM/MoE; R02-R04 and special-device topics | Deferred applications / separate leads | A surviving core method and the required models/data |

The old broad claims 'build a pipeline', 'more ADC bits', 'frozen errors matter',
'complement inputs' and 'read one coupling row per spin flip' are not core contributions.
We do not eliminate every narrower method in an occupied family. We also do not
automatically rescue a failed method by adding an Ising chapter.

## Execute in this order

| Step | Experiment / concrete question | Ready state and output | Eliminate or narrow when |
|---|---|---|---|
| 0 | E00, E03M and E09A: arithmetic, covariance witness, exact Ising reference and cache controls | Completed software/constructed evidence only | Any arithmetic or identity check fails |
| 1 | E01: real-trace occupancy, skipping and mapping opportunity | Tool implemented; actual frozen trace bundle needed | Claimed savings come only from inactive-feature packing, or no useful mapping opportunity remains |
| 2 | E02: meaningful physical read operation on 256x256 storage | NUS model/port/topology/readout inputs needed | Bias/headroom/settling invalid, or a response model cannot be validated |
| 3a | E03 pair probe: matched activity/count, varied overlap, calibrated decoded covariance | Requires E02, then paired target cases | Calibration or a simple shuffle removes the effect; continuous-error reasoning already explains it |
| 3b | E09B: fixed-state marginal audit and full-versus-cached field errors | Requires E02 and temporal-noise provenance | Apparent 'fresh worse' comes from mismatched marginals, cached drift, initialization or another known operator difference |
| 4a | E03 mapper: one shared row order on real pooled bit planes | General mapper still prospective | Retuned CAR plus adaptive sensing/calibration, balancing or equal-budget random search matches the frontier |
| 4b | E09C: small, exact-target solver pilot | Conditional target adapter not implemented | Only generic coupling sensitivity is observed, a simple reset/digital baseline suffices, or hardware costs dominate |
| 5 | Scope decision with evidence and Prof Fong | Choose one main contribution and at most one backup/companion | A common story alone is the justification |

E01's absence of a skipping benefit does not alone disprove the equal-read-count
covariance mechanism. Distinguish a failed sparsity claim from a surviving arithmetic-
quality claim. Either still needs a strong practical comparison.

## First commands

On NUS, an optional separate checkout preserves the existing working tree. From the
existing repository, choose a new directory name if the example already exists:

```sh
git fetch origin main
git worktree add --detach ../MRAM_screening_20261104 origin/main
cd ../MRAM_screening_20261104
```

From the repository root, with requirements.txt installed:

```sh
python3 -m unittest discover -s tests -v
python3 -m experiments.ising_reference verify \
  --out experiments/runs/E09A_my_new_run/verification.json
python3 -m experiments.ising_reference preflight \
  --out experiments/runs/E09A_my_new_run/kernel_preflight.json
python3 -m experiments.run preflight
```

The preflights currently return exit code 2 by design. They identify missing physical
information; they do not execute Spectre or a noisy solver. Choose new output directories.

For an actual exported trace bundle (replace the input paths with real files):

```sh
python3 -m experiments.run trace-screen \
  --bundle experiments/local_inputs/layer_traces.npz \
  --metadata experiments/local_inputs/layer_metadata.json \
  --group-sizes 32 64 128 \
  --out experiments/runs/E01_my_new_run/occupancy.json
```

Those group sizes are software schedules until E02 validates them. The trace metadata
must retain source identities and calibration/evaluation parent membership. For the
covariance extension, also retain parent-input IDs and activation-bit indices; independently
pooled planes lose the information needed for cross-cycle scoring. The current E01
occupancy tool does not itself compute those cross-cycle moments or fit the new mapper.

## E09B: isolate the mechanism before a solver campaign

Freeze a target field operator, signed encoding, calibration information and error
units. Stable binary memory and stochastic p-bits are distinct; initially the spin RNG
and heat-bath update are software components. Operator A recomputes fields through an
analog sum. Operator B fetches couplings and updates cached fields. Their error laws and
hardware costs require separate justification.

Use fixed probe states selected independently of chip variation. Compare the full
post-calibration conditional error PMFs (bias, amplitude and tails), not only error rate.
Keep a chip's manufacturing variation fixed. Physical temporal noise needs its own
amplitude/correlation source. A redraw of manufacturing variation at each read is a
matched-law counterfactual control, not measured temporal noise. Match calibration
information as well; do not silently recalibrate the counterfactual every operation.

Add a spin-flip/reversal loop and report cache residual; compare full recomputation,
incremental updates, exact refresh and initialization-only errors. Test whether a fixed
effective coupling matrix explains the field response on independent states. If it does,
compare with established coupling-imprecision theory before proposing novelty. A fixed
but asymmetric matrix need not have the intended Ising energy.

## E09C: bounded pilot and decision rule

After E09B and a reviewed adapter, start with three frozen small graphs (12-16 spins),
three independent chip assignments and twenty RNG restarts per graph/chip as an effort
budget. Freeze exact Max-Cut optima by enumeration; select graph instances and schedules
before inspecting noisy outcomes. These counts are a screening budget, not a powered
population claim. Do not run fifty graphs by default.

Arms: exact full-field heat-bath reference; exact incremental reference; quantized
digital couplings; calibrated target full-field response with persistent variation;
matched-law decorrelation control; and persistent-plus-physically-justified temporal
noise. Add incremental target reads and refresh variants only if they are physically
implemented. Use one update kernel/order and paired initial states/uniform streams.
Schedule retuning on calibration graphs is a separate equally budgeted comparison.

Report target-Hamiltonian cut gaps, fixed-chip success with uncertainty, wrong-update
probability on fixed states, and cache residuals. TTS needs declared run time/cost and
target success. With no trustworthy hardware timing, report update/operation budgets,
not seconds or joules. Report initialization, coupling fetches, signed planes,
transpose/duplicate capacity, cache precision, control and refresh costs. A digital
incremental implementation may avoid repeated analog sums and is a mandatory competitor.

Continue Ising as a method only for a useful specific design/controller gap. Keep it as
a companion only if it tests a declared transferable mechanism or method beyond a
second sensitivity plot and fits the approved scope. Otherwise retain the diagnostic
as an honest negative/control result and focus the thesis on the surviving main method.
