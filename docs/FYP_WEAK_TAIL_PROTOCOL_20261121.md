# Bounded weak-tail mechanism experiment

Registered 21 November 2026, after ideal checkpoint
`b8e6f28eab87b40ad97f124837c2e2bcec74a992` and before fresh solver outcomes.
The student explicitly authorized this extension and execution. It supplements
the existing coupling-representation FYP; the original ideal results, 18 core
contrasts and selected offset triples remain unchanged. Stop at this mechanism
checkpoint. No offset, gain or hardware work is authorized by this extension.

## Question and evidence boundary

Truncating weak couplings may impair the ranking of visited solutions,
contributing to FP–INT quality differences on distance-decaying coupling
matrices. The motivation is post hoc. Retained-edge ordering across six code
averages does not establish that edge count governs the loss. Within-format
graph correlations were weak, and probability distortion correlated more
strongly with selection loss. A failed test does not establish probability
error as the alternative cause. The experiment does not establish publication
priority, real MTJ device behavior, or a universally optimal encoding.

## Arms and precise factorial intervention

All source edges are encoded once and mirrored, with zero diagonal and h=0.
Fit ordinary FP6 E3M2 and symmetric INT6 using the original source-MSE global
scale rule. Do not refit a scale after modifying an arm. Let S be the original
edges for which INT6 is nonzero. Let F_S contain FP6 values on S and zero
elsewhere; I_S is ordinary INT6; T contains ordinary FP6 values outside S.

| Strong values | Tail kept | Tail removed |
|---|---|---|
| FP6 values | FP6 = F_S+T | FP6_mask = F_S |
| INT6 values | INT6_tail = I_S+T | INT6 = I_S |

Add FP64 as reference and INT6_keep as a diagnostic. INT6_keep replaces every
zeroed nonzero source coupling with its signed INT6 step, retaining the existing
INT6 values elsewhere. This can inflate weak weights; it cannot refute the
accurate-tail hypothesis. FP6_mask and INT6_tail are mechanism probes, without
an implementable-format, bit-width or area claim. Verify the exact coefficient
identity FP6-FP6_mask = INT6_tail-INT6 on every graph.

The six-arm order is FP64, FP6, INT6, FP6_mask, INT6_tail, INT6_keep. Values,
adjacency order and source beta of the three controls remain unchanged.

## Sources, streams and controller

Use 24 new 100-spin graphs per family, with no quality filtering. The ring and
Gaussian torus equations, c_N normalization, multiplier 100000, ties-to-even
integerization and PCG64DXSM implementation match the 20 November source model.
NumPy is pinned to 2.3.5. Source entropy is
SeedSequence([20261121,910,family,index]), family 0/1 and index 0..23.
Save all 48 Rudy files and SHA256 values before any fresh solver trajectory.
Source-only generator tests may inspect these source draws; no fresh quality
outcomes are used for implementation, selection or the freeze.

Solver seeds are 4000000000000 + 100000*family + 1000*index + replicate,
replicate 0..63, paired across all six arms. This is a separate namespace from
the closed ideal study. The controller remains random-scan sequential Gibbs,
linear source-beta schedule, gain 1, logit offset 0, exactly 50000 attempts.
Keep the original earliest strict represented-energy minimum as the real
returned state. Total scientific trajectories: 48*64*6 = 18432.

For each graph, B_control is max(0,V) over exactly the three control arms
FP64/FP6/INT6, 64 seeds each. It is a fixed feasible best-observed reference,
not a known optimum. This bounded extension has no additional independent
reference trajectories. Record a witness and exact original-weight rescore.
All six arms use the same denominator. Probe shortfalls may be negative if
they outperform this fixed control reference. A nonpositive denominator stops
analysis rather than triggering graph replacement.

## Search and selection measurements

V is best original cut ever visited; M is best original cut among visited
states attaining the final minimum represented energy; R is actual returned
original cut. Record R_last passively as before. For each paired seed define
A = 100*(V_FP64-V_arm)/B_control and Rz = 100*(V_arm-R_arm)/B_control.
Extra loss is 100*(R_FP64-R_arm)/B_control = A+Rz, since FP64 V=R.
Split Rz into represented-objective selection 100*(V-M)/B_control and
earliest-tie loss 100*(M-R)/B_control. Rz >= 0 is definitional.

For every arm, prove that its coefficients lie on a common binary lattice
whose energy and field sums stay inside exact binary64 integer capacity.
Use exact integer lattice keys for offline bank ranking, with no tolerance
chosen after seeing ties. All saved states are independently rescored on
original integer weights. Passive work consumes no random numbers and does
not enter the transition or actual-return decision.

## Passive K=16 buffer and common bank

Retain up to 16 distinct raw spin vectors with the lowest represented energy.
Break equal-energy ties by the earliest first visit, including the initial
state as visit 0. Global inversions remain distinct raw spin vectors. Original
cut is payload only and never selects a buffer member. Log each member's spin
vector, represented energy, first visit and original cut. Count distinct visited
vectors attaining the final minimum represented energy. Log all visited-state
counts descriptively. The buffered counterfactual return is the best original
cut among these 16 retained states; report its gain over R. M is an oracle over
all visited minimum-energy states and need not be reached by this buffer.

Per graph, pool the buffers from all six arms and 64 seeds, deduplicate exact
raw spin vectors, and rescore this same bank under every arm. The bank's own
tie rule is the smallest unsigned spin-state integer, independent of arm and
original quality. Report bank size, best original cut V_bank, best original cut
among represented-energy minimizers M_bank, chosen cut R_bank, and both loss
components. This comparison is conditional on the pooled bank; it does not
prove how a different live trajectory would behave.

Rechecking requires original J accessible to the host, spin transfer and
host work. For each candidate this is m original-edge contributions, with
sign-selected additions for +/-1 spins, not general multipliers. On a dense
100-spin undirected graph there are at most 4950 contributions per candidate,
or 79200 for K=16. No free rescoring, measured hardware saving or on-chip
original-J storage is assumed.

## Registered inference and interpretation

The independent replication unit is a generated graph, not a seed or spin.
Average paired seed contrasts within each graph and jointly resample the
24 whole graph vectors with studentized bootstrap-t, 500000 resamples,
PCG64DXSM, NumPy linear quantiles, entropy [20261121,940,0].

The only confirmatory endpoints are on the ring:

- C1: Rz(FP6_mask)-Rz(FP6) > 0.
- C2: Rz(INT6)-Rz(INT6_tail) > 0.

Each uses one-sided alpha .0125, familywise alpha at most .025 by Bonferroni.
The confirmatory 98.75% lower bound must exceed zero for SUPPORTED; otherwise
report NOT_ESTABLISHED. An upper bound is retained for orientation, without
converting non-support into a zero-effect or alternative-mechanism claim.
Zero or unstable studentization remains unresolved, with no dropped resamples.
Report effect magnitudes as well as signs.

All other bounds are ordinary descriptive 95% graph-resampled intervals, with
entropy [20261121,940,family,1]. Report the six-arm Rz/A/extra table, V-M/M-R,
buffer recovery, minimum-state counts, common-bank loss and the factorial
interaction (FP6_mask-FP6)-(INT6-INT6_tail). The torus near-null expectation is
descriptive; no practical-equivalence margin is introduced. No no-interaction
or independent device/calibration budget claim follows from this study.

Both contrasts supported means these particular accurate-tail interventions
matter for live-trajectory selection under this controller. Common-bank data
help assess ranking effects on a fixed set. If only one or neither is supported,
retain the estimates and uncertainty; neither result proves a unique cause.
This is one bounded experiment, not a search for a quantizer that makes FP win.

## Verification, execution and checkpoint

Preserve all old evidence. Before freeze, pass synthetic tests of exact
factorization, buffer tie behavior, no original-score leakage, common-bank
enumeration, alpha/sign rules and passivity. Replay the 21 FP64/FP6/INT6
controls from the committed 25-control ideal preflight plan against their
actual historical archive hashes and compare all legacy trajectory outputs.
Engineering timings use already-viewed sources only. Freeze code, analysis,
source graph files, complete seed namespaces and preflight evidence in GitHub
before running any fresh trajectory. Verify published freeze bytes and hashes.

Execution is Python software in the Codex workspace. Record Python, NumPy,
platform, worker count and elapsed time; there are no real-device, EDA or
Schrodinger measurements in this experiment. Use six workers, with progress
reporting limited to counts/timing until execution and integrity verification
complete. Never silently resume partial scientific bundles or add runs.

At the checkpoint archive all 18432 raw records, candidate buffers, shared-bank
states, original source files, hashes, summaries and analysis. Report C1/C2,
descriptive factorial effects, common-bank results, K16 recovery, torus behavior,
diagnostic INT6_keep and failures or surprises. Stop before offset/gain/hardware.
