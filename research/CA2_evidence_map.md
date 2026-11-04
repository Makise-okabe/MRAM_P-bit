# CA2 writing map

This is a traceable working structure. Confirm the official CA2 rubric and required
format before submission; they are not supplied in the current repository request.

| Report component | Durable source | Evidence still needed |
|---|---|---|
| Motivation / objective | `00_scope.md`, report problem section | Supervisor agreement on final contribution scope |
| Evolution of research question | Dated logbook + ADRs | Append outcomes as they occur, without backdating |
| Related work / research gap | Literature register + access log | Full closest implementations, explicit differences |
| Proposed method | Candidate card, frozen experiment protocol | One selected and fully specified contribution |
| Architecture / assumptions | Versioned target contract | Circuit interfaces, source provenance, target validation |
| Experimental method | E00-E09 protocols, run records | Frozen budgets, split IDs, chip sampling and simulator details |
| Results / analysis | Curated output hashes + uncertainty | Target circuit and task-level results; currently absent |
| Decisions / negative findings | Decision log and claim ledger | Evidence-based continue, narrow or stop decisions |
| Remaining work / timetable | Experiment register | Actual turnaround and scope after physical gate |
| Reproducibility / AI assistance | Code commit, commands, paper records | Human review of generated code, claims and final write-up |

## Current pathfinding narrative

1. The broad precision/nonideality subject did not yet identify a distinctive contribution.
2. User required a precise method, a justified physical case and a strong small comparison.
3. The physical target was clarified as 256 x 256; prior trial evidence was excluded.
4. Twenty-one ideas were consolidated into seven competing families rather than one
   prematurely chosen sector topic.
5. Close work makes ordinary co-zero grouping, activity-aware conversion, calibration and
   selective refinement serious comparators. Broad overlap does not eliminate every narrow gap.
6. This reset archives the former report and starts prospective evidence collection. E00
   verifies software identities; E01 requires real traces; E02 requires a target model.
7. The subsequent [Claude/Yanzhang survey review](reviews/2026-11-03-claude-field-survey.md)
   records the earlier revisions, additional circuit reserves and estimator audit. Its
   externally reported demonstrations remain separate from our prospective evidence.
8. On 4 November the novelty question was narrowed to [decoded-covariance grouping](novelty/2026-11-04-covariance-mapping.md).
   E03M establishes a constructed equal-marginal counterexample after scalar calibration;
   ADR-0002 records the candidate priority and remaining prior-art, physics and practical
   gates. No earlier physical discovery is claimed as its motivation.

## Per-run CA2 note template

Date; experiment/decision ID; question before the run; exact method/comparator difference;
input and code hashes; evidence class; principal outcome with uncertainty; interpretation;
what was ruled out; limitations; next decision. Link artifacts rather than transcribing
untraceable numbers into prose. A failed candidate is reported as rejected, not relabelled.

## Revision-15 consolidation and first Ising controls

The [resource audit and executable first-run protocol](experiments/2026-11-04-resource-audit-and-first-run.md)
record which legacy neural assets can be reused and which electrical evidence stays
excluded. E01R verifies runner readiness with 27 software tests and the expected local
missing-resource preflight. The later [E01 workload audit](experiments/2026-11-04-E01-frozen-MNIST-workload-audit.md)
records the user-executed frozen-MNIST run. It adds workload/ideal-arithmetic evidence,
not target circuit, noisy task or energy results. E02 target validation remains open.

The [bounded queue](04_screening_queue.md), ADR-0003 and [source review](reviews/2026-11-04-claude-revision15.md) record why Ising is retained conditionally. E09A checks exact references and the cache-drift control; E09B/C remain unrun target studies. Preserve the distinction between external toy claims, software identities and a new transferable contribution.

The subsequently attached 48-page survey is identified by the
[revision-15 source receipt](reviews/2026-11-04-claude-revision15.source.json). Its new
opening synthesis matches the previously reviewed excerpt; this improves source access
without changing the experimental evidence or candidate decision.

## Intended artifacts and parasitic-model role

The [4 November candidate outcome contracts](reviews/2026-11-04-parasitics-and-candidate-deliverables.md)
define proposed finished deliverables and rejection conditions for the existing three
screens: spatial read control, F3 static mapping and conditional F7 field maintenance.
This is a planning/research-design record, not experimental evidence. Include distributed
RC in the shared target model and distinguish static loading, settling, persistent
mismatch and temporal noise. The eventual CA2 method claim requires one distinct
implemented intervention plus a useful strong-baseline comparison; characterized
distributions alone do not satisfy the user's chosen method/design objective.

## Scope-presentation correction — ADR-0005

[ADR-0005](decisions/ADR-0005-one-mapping-study-and-supporting-tools.md) explicitly
corrects the unrecorded promotion of spatial read control into a replacement
top-level candidate. Present the three original discussion topics consistently:
mapping as the main method, failure prediction as its validated supporting tool,
and Ising as optional. A controller is a gated extension of the mapping study.
Preserve the earlier narrative as history; do not imply supervisor approval.

The [replacement WhatsApp text](communications/2026-11-04-prof-fong-mapping-focus-draft.md)
is a draft, not a sent message. The suggested 10-30% matched-failure read-saving
range is not accepted as a target-array forecast. E01 conventional CAR/sorting
counts do not establish that outcome or a new method's incremental gain.


## 2026-11-04 late-stage DIB prior-art pathfinding update (E13–E15)

**Do not overwrite older failures with the new positive candidate.** Full provenance: [E13–E15 record](experiments/2026-11-04-E13-E15-DIB-conditional-ADC-discovery.md).

- **E13 rejected:** CAL-selected output-certificate-adaptive common-WL schedule skipped only 0.03987 percentage points more logical output-count conversions on independent DEV than the static E12 joint schedule (7,162 extra skipped / 17,965,231 eligible). Additional runtime scheduling and certification overhead makes this an unconvincing standalone contribution. ReLU early termination is established prior art; zero-bias FC1 only.
- **E14 mathematical candidate:** operand-conditioned threshold tree for exact AND-popcount, based on m active input bits and k stored weight ones. Held-out DEV ideal-comparator decisions 36,558,784 versus 41,310,333 for CAL-optimal input-only threshold tree (11.502% reduction), with all 6,545 legal count leaves separately audited. Unconstrained tree can require nine comparator decisions in worst case; depth cap5 gives 36,972,994 vs 45,032,056 for same-max-depth balanced joint baseline.
- **E15 hardware-aware algorithm candidate:** a limited-bank (four k-groups) threshold-tree controller capped at six decisions per count uses 37,477,206 DEV ideal comparison decisions vs 41,310,333 trained input-only baseline (9.279% fewer; paired parent-bootstrap 95% CI 9.040–9.509%). Four-bank tree has 1,088 internal threshold nodes across all m vs 5,456 for full 33-bank version. Nodes are not physical area.
- **Prior art caveat:** DIB-CIM 2026 (user-provided LEBD/I3D Algorithm 1 adjusts WL size and the abstract describes DR-ADC), probability-based hybrid CIM ADC 2023, and entropy-coded threshold-tree ADC patent 2020. Distinctness from the DIB screenshot is not sufficient to certify external novelty. Must inspect full DIB DR-ADC algorithm and closest patents before claiming original method.
- **Hardware caveat:** each k-conditioned tree needs programmable reference selection; if physical ADC references are shared across all columns, per-column comparator savings may disappear or induce serialization. No NUS multirow GF NFET+custom MTJ ADC kernel, noise, voltage references, DAC settling, area, or total energy/latency measured. Do not compare percent ideal comparisons with DIB's published percent latency.
- **Research-choice status:** E15 is a *specific algorithm to propose* to Prof Fong for targeted hardware feasibility and novelty review, NOT an approved direction or proven physical advantage.

