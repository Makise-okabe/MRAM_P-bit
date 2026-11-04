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



## 2026-11-04 E16 final DIB PDF audit + E15 conditional-ADC falsification
Detailed [E16 research record](experiments/2026-11-04-E16-full-DIB-read-strong-baseline-and-physical-falsifier.md). The user-provided 14-page IEEE TCAS-I paper is NUS-licensed; **do not redistribute or publish it**.
- **Actual DIB**: adaptive B=8/16/32/64 WL sizing from LEBD and I3D input activity/imbalance plus zero-skip; DR-ADC is 2-bit coarse flash + V2T/flash TDC. Its coarse flash code DOES control a reference MUX for fine conversion. No evidence in this paper of an operand m,k-conditioned optimal threshold-search tree. Our E15 differs in decision/action, but both probability-based CIM ADC and decision-tree ADC have prior art; global novelty not certified.
- **E16-A software-survival result:** matched six-comparison worst-depth; input-only CAL-trained tree with the SAME stored-k interval pruning: **40,529,665** independent-DEV ideal comparator decisions. E15 four-k-class tree: **37,477,206**, gain **7.5314%**, 256/256 parent wins, parent bootstrap 95% CI [7.3447%,7.7055%]. Stronger control replaces previous 9.28% comparison against an unpruned input-only model. Logic/codebook/DAC/reference overhead absent.
- **E16-B physical falsifier (synthetic, NOT GF):** in constructed 32-row passive ladder with Rp=5k,Rap=10k, m=k=16, n7 and n8, r≥5Ω/segment produces overlapping sensed current distributions across different row placements. With r=25Ω assumed, CAL-trained best single threshold gives 41.86% held-out two-class error; a perfect exact-count comparison tree cannot recover overlapping scalar current values. This invalidates the blanket 'error-free ADC conversion' claim for that toy physical network; actual GF target may differ.
- **Immediate feasibility gate:** at NUS implement fresh GF NFET + custom MTJ multiro w read; measure conditional current ranges for adjacent counts and spatial masks; compute ADC error, per-column control and total energy/delay before claiming system benefit. The paper's 12–16% latency improvement and our 7.53% ideal comparator operation reduction are **incomparable**.


## 2026-11-04 E17/E18 gate: final answer to “does E15 work?”
Detailed [E17/E18 matched-metadata and actual-trace constructed-ladder audit](experiments/2026-11-04-E17-E18-E15-go-no-go-matched-metadata-and-realtrace-ladder.md).
- **Software result survives a better fair comparator.** E17 **two-bit-only k-bank metadata** (no exact k hidden shortcut) scores **37,708,650** ideal DEV comparisons. Input-only CAL-trained baseline with **exactly the same bank metadata / range pruning** scores 41,385,223: **8.8838% fewer** ideal comparisons, 256/256 DEV parents win, 95% paired-parent CI [8.6233%,9.1319%]. Both max depth6. Previous 7.53% ratio answered a different metadata comparison.
- **Real-resource risk:** two-bit static k-class metadata = 32,768 bits for the packed four-plane 128×784 FC1 weights, **6.25% storage-bit equivalent** over 524,288 original stored W bits; this excludes class computation and physical SRAM/CAM/ROM area. Saving amounts to only **0.10957 comparator decisions per possible count event**. Incremental DAC/controller overhead may erase efficiency.
- **Physical-model failure condition, not actual GF data:** 180k CAL+180k DEV real E01 bitplane patterns decoded through a constructed, variable rΩ/segment 32-shunt passive bitline. CAL-fitted monotone decoder with same legal m,k support gets 0% error at assumed r≤.5Ω; at r=1Ω all-count error .005%; r=2Ω .255%; r=5Ω **3.393%**; r=10Ω **9.177%**; r=25Ω **18.841%**. Non-deterministic-only errors at r=5Ω = 6.331%. Independently checked linear KCL against dense-matrix solve. The resistor values are **not measured GF wire RC**, access NFETs/ADC are missing; cannot claim this physically occurs in target array.
- **Explicit disposition for CA2:** Keep E15's mathematical comparison saving. Reject claims of *guaranteed physical exact-count decoding* and *better measured DIB latency/energy*. No demonstrated original hardware advantage yet. Immediate decisive real-hardware requirement = fresh GF NFET + student MTJ multirow read-current levels and per-column ADC references/cost, then strong hardware-consistent baselines.


## E19 user-executed GF access-NFET + student MTJ nominal nonideal-read results (4 Nov 2026)
The first E19 failure was a Python string/Path crash before Spectre; corrected SHA-guarded v2 script completed. Grounded evidence: [E19 actual user-run results](experiments/2026-11-04-E19-NUS-GF-NFET-MTJ-nonideal-RESULTS.md).
- **192 successful independent per-mask, per-assumed-R GF Spectre circuit cases**: 16 distinct placement masks ×3 R settings first, 48×3 second. GF `hvtnfet` model and student static `mtj_read_v0`, nominal m=k=16, n=7 or 8, historical VREAD=.05V, VWL=.8V. Segment R=0/1/5 Ω are EXPLICITLY ASSUMED, **not extracted GF PEX**.
- First run DEV calibrated-midpoint errors: R0 0/8, R1 0/8, R5 **2/8 (25%)**, R5 observed DEV overlap **0.31172µA**.
- Independent run DEV errors: R0 0/24, R1 0/24, R5 **2/24 (8.33%)**, R5 observed DEV overlap **0.20122µA**. Sample 2/24 Wilson 95% interval about 2.3–25.8%, i.e. point estimate unreliable.
- **Conditional failure finding:** under the assumed 5Ω/segment physical topology, finite placement samples of adjacent true counts overlap in sensed current; nominal single-threshold, exact-count decoding is not guaranteed. This does **not** falsify E15's ideal mathematical comparison reduction (E17 8.88%) or establish real 256x256 PEX failure/energy.
- Next no-additional-Spectre discriminator: [E19C threshold and abstention postprocessing](../experiments/e19c_nus_current_calibration_gate.py) comparing CAL-only optimized versus midpoint; deferred cases must not be counted corrected without an actual fallback operation. Then real PEX and ADC/control overhead needed.


## E19C/E20 decision update — 2026-11-04
- **E19C failed to improve the two 5Ω GF-NFET current classes by CAL-only threshold optimization**: held-out errors remained 2/8 and 2/24, separately from the ideal E15 comparator result.
- **Abstention is not correction**: zero automatic-decision errors came at unresolved deferral of 3/8 and 5/24 at assumed 5Ω, and also deferred 12/24 even at R=0 in one run. This is not an implementation of a second read nor a proven energy benefit.
- **E20 constructed-ladder exploratory positive**: fixed random 16/16 adjacent-count CAL/DEV classes, 10,000 held-out samples at assumed 5Ω, ordinary raw midpoint 1,631 wrong vs near-count 744, centroid 275, input-only suffixQ compensation 132. **Passive circuit, not new GF measurement; no novelty**.
- **E20 NUS test is pending**: new `experiments/e20_mask_suffix_gf_calibration.py` fits CAL-only current correction from public activation-mask suffix load Qx and compares raw/near-count/centroid on both E19 GF current datasets. Results must be read before claims. Full pre-registered gate: [E20 rescue-or-retire log](experiments/2026-11-04-E20-suffix-load-rescue-or-retire-E15.md). If Q fails relative to cheap controls or metadata control costs exceed E15's small ideal gain, **retire E15 as principal novelty**, preserve all failures here.

## E20 complete on user-run E19 GF currents — method succeeds, novelty test fails (2026-11-04)

Results and explicit go/no-go: [E20 completed detailed record](experiments/2026-11-04-E20-suffix-load-rescue-or-retire-E15.md).

- **NUS CAL-only positional correction works in this restricted test**. First run 8 DEV and confirmation 24 DEV, two adjacent counts n=7/8, both with m=k=16, GF hvtnfet + student static MTJ at assumed 5Ω BL segment: raw CAL current-midpoint decoder wrong **2/8 and 2/24**; near/far active-position count **0/8 and 0/24**; centroid **0/8 and 0/24**; proposed suffixQ **0/8 and 0/24**. All methods gave 0 wrong at assumed R0 and R1 for these samples.
- **E20 negative relative-novelty finding:** The complex suffixQ method offers **no measured advantage** versus substantially simpler input-position statistics in the completed GF-current test. The earlier *passive synthetic ladder* suffixQ > centroid result did not transfer as a unique advantage on the limited actual GF-NFET dataset. A 0/24 score is not zero underlying BER.
- **Decision:** RETIRE E15 + E20 as principal FYP novelty hypothesis. Do not misreport as outright physical error-correction failure: the input-position CAL compensation worked on the tested nominal circuit, and E15 still has ideal 8.88% comparison saving with two-bit metadata, but no demonstrated ADC hardware energy/accuracy improvement. Generic input imbalance detection strongly overlaps DIB's I3D and spatial IR-drop prior work.
- **Scope guard:** No fresh NUS Spectre in E20, only reanalysis of E19 measured currents; assumed R5 Ω/segment is not GF PEX, no noise/PVT or array-wide inference. E20 output remains in NUS private path.


## 2026-11-04 E21–E23: new mapping/pathfinding candidate and strict evidence boundaries
Detailed [E21–E23 experiment record](experiments/2026-11-04-E21-E23-coactivation-mapping-discovery-and-GF-gate.md).

**E21 rejected:** signing the four W4 planes to cancel reconstructed group-orientation errors improved DEV partial-block MSE by 4.41% over per-read-error orientation at one assumed-wire zero-sort setting (R5 with centroid correction), but not reliably across CAR, alternative R, other mappings. No novelty claim.

**E22B analytical positive, with negative controls:** at fixed E01 32-row group membership (therefore exactly **zero change in activation group read count**), 128 CAL/256 DEV real MNIST input parents, first 256 rows and 8 output channels only, CAL-estimated 32x32 pairwise coactivation matrix C_ij, offline within-group swaps. In constructed first-order one-ended ladder at assumed 5Ω/segment with CAL-fitted input-only centroid correction, CAMP-light DEV signed arithmetic MSE was 28,895.2 vs mean-conductance sort 32,071.6 under zero-sort grouping; CAR 28,946.0 vs 32,447.8. Same greedy optimizer but independent-activation C_ij=p_i p_j is weaker. Full cross-weight conductance covariance improves only marginally over CAMP-light and is inconsistent at R10; **do not advocate unnecessary full variant**. In original E01 grouping, CAMP can lose to simple activity sorting; note this negative.

**E22D exact Kirchhoff passive circuit positive:** at assumed R5 and with identical CAL centroid calibration, CAMP-light vs conductance sort **25,508.2 vs 28,332.5** DEV signed 256-row-block MSE (zero-sort, 9.968% decrease), **25,316.2 vs 28,105.8** (CAR, 9.925% decrease). Exploratory 256-DEV-parent paired bootstrap 95% absolute MSE improvement: [1185,4666] and [1128,4564], respectively; **DEV was inspected during research, so not prospective confirmation**.

**Critical scope:** This is **NOT actual NUS GF transistor simulation nor 256x256 PEX**, and the device conductance ratios and R=5Ω are assumed. The improvement is in reconstructed **partial-layer arithmetic MSE**, not final MNIST inference/classification. Count-decoder errors change minimally and partial sum sign flips can worsen. General hardware-aware mapping and correlated-input order dependence already have serious prior art (Dyn-A-Map 2026, hardware-aware AIMC 2023, DIB-CIM 2026), so **publication-level novelty is open**.

**E23 NUS GF microgate prepared, NOT run:** user-private ZIP `E21_E23_CAMP_candidate.zip` SHA256 a6a93bdf0f912a8b3961626c06f6452e1919b9fbda5100688534a8a6c0e43561 includes executable code and verified user-origin E01 packet. Simulates same CAL/DEV logical reads under CAMP-light versus conductance sorting with local licensed GF `hvtnfet`+student static MTJ, assumed R=0 and 5Ω/segment. R0 serves a zero-wire permutation-invariance null; R5 measures **actual matched sense-current droop**, not ADC/classification gain. First sample ~384 circuits. **If GF test doesn't replicate the advantage, reject CAMP rather than extending speculative models**.

**Research decision:** retain CAMP-light as a narrowly specified hypothesis requiring physical verification; reject E21, full-correlated extra complexity, and any claims of already-proven novelty or physical end-to-end energy saving.


## E21 physical-aware within-group mapping after E15/E20 retirement (2026-11-04)
Detailed evidence, full source and numeric results: [E21 study](experiments/2026-11-04-E21-within-group-covariance-mapping-and-nanocim-prior-art-gate.md). **E21 is software only, real frozen E01 MNIST bitplanes + assumed first-order resistive wire-load model; not PEX/Spectre or real inference.**
- **Precise proposed algorithm**: for a frozen 32-row read group, optimize the *permutation inside the group* by CAL input/weight pairwise second moments `C_ij=E[a_i a_j]` to minimize expected suffix-load `Q=sum_l(sum_(j>=l)a_j)^2`. Thus ideal MAC count and nonempty read cycles provably unchanged across competing intra-group maps.
- **Strong simple baseline**: order rows within group by CAL activation rate × average stored-state conductance, hottest near driver; compare to input-only sort, original within-group order, CAR and zero-rate starting group memberships.
- **E21A HELD-OUT DEV Q**: original-group simple joint-sort 1335.36 vs covariance optimizer **1337.63** (**fails**); zero-sort 4227.42 vs **4177.83** (optimizer wins marginally); CAR 4174.06 vs **4140.05** (marginal); activity-balanced 436.65 vs **431.23** (different much higher total read count). Within each grouping exact number of nonempty reads remains equal, verified by assertions.
- **E21B ASSUMED nonlinear ADC proxy** with alpha=.0005, reconstructed first-block DEV MSE: original-group joint-sort 73361.8 vs covariance optimizer **75707.2 worse (-3.20%)**; zero-rate 505934.9 vs **459176.1 better (+9.24%)**; CAR 508036.7 vs **472462.0 better (+7.00%)**. Advantage persists at synthetic alpha .0002/.001 for zero-sort and CAR, but optimizer *always loses* from original grouping. No GF measured count/energy/task evidence, no proof of invention.
- **CRITICAL close prior art discovered:** NanoCiM 2026 (Matsui et al., DOI 10.1109/TCASAI.2026.3661436) already weight-aware X-address row scrambling to reduce bitline IR-drop MAC current variation, with a TSP-based method. Dyn-A-Map 2026 (https://www.nature.com/articles/s44335-026-00072-6) maps SOT-MRAM weights according to spatial process-variation faults. **Do NOT claim 'physical-aware row mapping' or 'weight-aware scrambling' is novel.** A narrower contribution would require materially different decision rule, beating the existing scrambling class and producing physically validated held-out task gain.
- **Decision:** retain E21 as a *non-certified candidate pool item*, not an accepted FYP contribution. Next gate full NanoCiM methods plus independent GF/PEX readout with actual position-sensitive decoder, strong equal-read count mapping competitor and downstream task-level accuracy/energy. Record failed original-group test for CA2.


## Direction freeze 2026-11-05 — Coupled precision and hardware nonidealities (adopted)
The user chose to **retain the submitted original FYP scope** rather than pivot to Ising or the E21 mapper. Decision and evidence tiers are frozen in [ADR-0006](decisions/ADR-0006-coupled-precision-failure-boundary-primary.md). Exact working objective: a physically justified and independently tested prediction/design rule for **failure thresholds of nominal quantized MRAM reads under simultaneous ADC precision and position-dependent parasitics**, against strong conventional margin/offset/near-far models; full task relevance and measured circuit costs are future gates, not existing results.
- **Immediate E22 is PENDING**, not a completed result: [E22 preregistration](experiments/2026-11-05-E22-coupled-precision-17count-GF-PENDING.md), executable `experiments/e22_gf_precision_regime.py`. Extends E19 from n7/8 to all n=0..16 at m=k16, R0/1/2/3/5Ω *assumed* per segment; 6 CAL+12 DEV independent masks/count (1530 paired GF DC simulations), then offline uniform ADC 4/5/6/7 bits with fixed R0 CAL fullscale, continuous nearest-count comparator and CAL-only offset/near-far controls. No foundry PEX, actual ADC or task result can be inferred in advance.
- **E23** will fit a boundary-risk model from CAL circuit data and test held-out DEV compared with simple ADC margins and additive noise/current-shift models, not just draw a heatmap. **E24** will require geometrically justified/extracted RC and fixed per-chip MTJ spread, while **E25** requires the full trained network and biases for genuine MNIST classification.
- CA2 must keep the prior E15/E20 novelty rejection, Ising and mapping pilot failures as reasoning that led to this adopted direction.


## Post-E20 independence correction and stronger-baseline audit

Detailed [executed software audit](experiments/2026-11-04-post-E20-calibration-and-CAMP-independence-audit.md).
This supplements, rather than erases, E22's original positive and negative cases.

- **Mathematical correction:** independent binary second moments have C_ii=p_i;
  the previous outer(p,p) ablation used p_i^2 and did not isolate inter-row
  correlation cleanly. Complete five-row enumeration verifies the corrected law.
- **Reproduction and survival in E22's declared model:** exactly reproduced all
  six frozen E22D baseline/CAMP MSE and wrong-count outcomes. Matched seven-swap
  optimizer with corrected independent moments gives zero-rate 28,440.44 versus
  CAMP-light 25,508.23 (10.31% lower) and CAR 28,601.66 versus 25,316.25 (11.49%
  lower). Original grouping remains negative: 489.24 versus 537.80 (9.93% worse).
  These are constructed passive-ladder partial-block arithmetic outcomes only.
- **More demanding separate model:** on an assumed monolithic 256-node column,
  AP/P=100/200 microSiemens, ideal 8-bit ADC and common bounded five-coefficient
  CAL residual correction, R5 joint-sort MSE=30,184.68 and CAMP=30,021.13. The
  0.54% difference has a descriptive paired-parent interval spanning zero.
  Multiple model conditions changed; this is not a calibration-only ablation.
- **New objective rejected:** same-pool CAL decoded-W4A8-MSE selector scores
  30,376.41 at R5 versus continuous-MSE selector 30,021.13; at R1, 576.59 versus
  284.86. No incremental benefit demonstrated. All selection uses CAL only.
- **Integrity:** initial prototype failed zero-wire decoding because CAL-unexcited
  groups acquired an arbitrary zero fit, and initially omitted A8 weighting.
  It supplies no positive evidence. Corrected runs pass zero-wire invariance,
  full signed W4A8 arithmetic, group/read conservation and independent dense KCL.
- **Disposition:** retain CAMP-light for closest-method novelty review and one
  bounded GF falsifier; no selected core method, hardware gain, final-test claim
  or novelty pass. Generic mapping with calibration is occupied by Wang 2024
  and DATE 2026; NanoCiM full TSP/activation-statistics comparison remains open.
  An E23 raw-current improvement would not establish post-calibration decoded
  count or task improvement.


## 2026-11-05 NanoCiM full text read; preserve ADR-0006 primary scope

[Full method review](reviews/2026-11-05-NanoCiM-fulltext-CAMP-and-primary-scope.md),
[source receipt](reviews/2026-11-05-NanoCiM-fulltext.source.json). The complete
13-page user-provided PDF has now been read; the earlier abstract-only access
caveat is superseded. No licensed PDF, extracted article or figures are public.

- NanoCiM Eq.5 is sqrt(weight-row inner product); its TSP puts low-overlap rows
  adjacent. The stated rule does not use the CAMP input-coactivation matrix or
  all-pair shared-wire-length position kernel. This is a precise method
  difference, not publication-level novelty or evidence of useful superiority.
- Row permutation with matching input permutation, pairwise weight-aware
  spatial mapping and IR-drop mitigation are established. ReRAM-to-MRAM
  substitution and fixed-group restriction do not certify a contribution.
- Table V reports 83.1% Random versus 79.9% TSP MNIST accuracy at the stated
  condition; full-dataset outcomes and selected-digit examples are separate.
- NanoCiM fixes input/weight/output at 2/4/4 bits and studies physical
  nonidealities; the broad precision/nonideality subject is not new. It does
  not supply the proposed systematic ADC/spatial-mask failure-boundary
  experiment or held-out predictor comparison.
- **Scope:** ADR-0006 governs. CAMP and Ising stay archived; do not read the
  historical post-E20 recommendation as a reversal of the user's adopted
  primary route. Continue the current coupled-precision E22 pilot, not the
  older CAMP-E23 probe. No new physical/task result or predictor novelty pass.
