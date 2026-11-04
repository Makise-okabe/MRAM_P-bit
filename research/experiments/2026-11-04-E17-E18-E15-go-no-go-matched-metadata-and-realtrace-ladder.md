# E17–E18: decisive E15 ideal-algorithm validation and physical-model falsification (4 Nov 2026)

**Evidence class:** assistant-executed Python on the user’s hash-verified private E01 MNIST packet, supplemented by independently verified nodal-KCL simulations of a *constructed* passive network. **No fresh NUS Spectre, licensed GF transistor/PEX, real ADC, energy, timing, or neural classification experiment. No novelty certification.**

## Question and verdict
Does the proposed four-bank joint-(m,k) ADC comparison tree improve over strong input-only trees when only its advertised two-bit weight-popcount bank class is actually accessible? **YES in a noiseless scalar-count comparator model.** Does it guarantee correct decoded counts or physical energy savings in a real MRAM CIM? **NO such result has been established; an assumed resistor network invalidates the claimed universal exact-read property.** Decision: keep as a *provisional software algorithm candidate*, not an experimentally proven MRAM thesis contribution.

## E17 – matched metadata (EXECUTED)
Same 128 CAL / independent 256 DEV MNIST input parents as E16, 784 FC1 rows padded into 32 groups, 128 channels, 8 activation bitplanes, 4 W4 planes; 33,554,432 possible count events, 6-comparison maximum for all adaptive-tree arms. CAL alone trains trees. A four-codebook tree grouped by k=0..32 was reevaluated with **ONLY its 2-bit weight-popcount-bank class**. Previously E15 had access to exact k to bypass deterministic n; that was an implementation shortcut.

| Policy | DEV comparison decisions | Stored weight-group metadata |
|---|---:|---:|
| CAL-trained input-only, depth6 | 41,390,328 | 0 bits |
| CAL-trained input-only exact-k support pruning | 40,529,665 | 6 bits |
| Four-bank E15 with exact-k shortcuts | 37,477,206 | 6 bits |
| **Four-bank E17 using bank ID only** | **37,708,650** | **2 bits** |
| **Input-only CAL-trained + same 2-bit bank-range pruning** | **41,385,223** | **2 bits** |

**Matched metadata result:** (41,385,223-37,708,650)/41,385,223 = **8.8838% fewer ideal comparator operations**, 3,676,573 total fewer, 0.10957 fewer comparisons per possible count event. All **256/256 independent held-out input parents** gained; paired parent-bootstrap 95% CI **[8.6233%, 9.1319%]**. This is the relevant new comparator, replacing less precise previously quoted 7.53% (which gave exact k support to both competitors). With 4 weight bitplanes × 128 outputs × 32 groups = 16,384 static weight groups, storing 2-bit class requires 32,768 metadata bits, **6.25% relative to the 524,288 stored weight bits**, excluding activity popcounts, LUT, per-column DAC/reference routing and control overhead. 6-bit exact k instead requires 98,304 metadata bits (18.75%). Codebook count is NOT number of physical reference voltages.

## E18 – analog sensitivity on REAL bitplane masks but a CONSTRUCTED circuit (EXECUTED)
Sample 180,000 CAL and independent 180,000 DEV binary count events directly from real E01 activation-and-weight bitplanes (not random synthetic activation masks), retaining original physical 32-row placement in each group. Build one-ended 32-segment passive resistor ladder with nominal Rp=5kΩ / Rap=10kΩ, ideal OFF for inactive input rows, mathematical 1mV source. Assume each segment r∈{0,.25,.5,1,2,5,10,25} Ω; **these are NOT measured GF parasitics**. Fit a monotone (m,n)-conditioned count-to-current decoder on CAL only and clamp inferred n to legal input-and-weight support [max(0,m+k−32),min(m,k)]. Independently verify vectorized Thomas KCL against dense matrix solve on random 32-node circuits for every r (max differences < numerical tolerance).

| Assumed r (Ω/segment) | DEV wrong n, all events | DEV wrong n, non-deterministic events |
|---|---:|---:|
| 0 | 0% | 0% |
| 0.25 | 0% | 0% |
| 0.5 | 0% | 0% |
| 1 | 0.005% | 0.0093% |
| 2 | 0.255% | 0.4758% |
| 5 | 3.3933% | 6.3309% |
| 10 | 9.1772% | 17.1219% |
| 25 | 18.8406% | 35.1507% |

These error rates are for one calibrated decoder with assumed r, **not an information-theoretic lower bound for all possible scalar decoders**. However, E16 had already demonstrated overlapping current ranges across adjacent count states for the constructed passive ladder at r≥5Ω: an ordered exact-count scalar threshold ADC cannot certify zero error for every possible spatial mask. E17's reordering of such thresholds changes comparison cost, not information encoded in one current.

## Hardware economics / comparison with DIB-CIM
- E17B saves **0.10957 ideal comparisons per potential count event**, so incremental controller/metadata/reference-routing/settling cost larger than that (in matched comparator-energy equivalents) removes any net advantage over the already reconfigurable input-only ADC. This is a conditional break-even, not measured energy.
- DIB-CIM's **actual DR-ADC is a 2-bit flash stage plus dynamic V2T/flash TDC**, not a serial binary threshold tree. E17/E18 do not establish any latency/energy gain relative to DIB’s architecture or its 12–16% latency improvement against fixed-B=8.
- Probability-based ADC and entropy-coded threshold search already have prior art; even the now demonstrated **8.88%** mathematical improvement cannot certify originality. Source NUS-licensed 14-page IEEE DIB PDF was consulted but not redistributed.

## Decision for CA2 and Prof Fong
- **Keep**: two-bit metadata joint-popcount banked, depth6 conditional reference search **as an analytical ADC selection idea** with fair controls.
- **Reject**: “only four codebook banks gives a guaranteed lossless physical MRAM count conversion” — the constructed wire-loaded channel furnishes a counterexample and actual circuit remains untested.
- **Reject**: “E15 beat DIB energy/latency” — no matched hardware, no DAC/control costs or actual time.
- **Topic gate**: physically characterize a fresh licensed GF `hvtnfet` + student-owned MTJ nominal multirow sensing operator (near/far positions and adjacent count states), then compare DAC references and control overhead against a strong input-only and DIB-like implementation. Only after actual PEX/sense currents and relative end-to-end energy/accuracy can E15 become a thesis contribution. If no reliable scalar count channel or cheap per-column reference routing exists, **retire E15 as the main FYP novelty** and retain mapping/predictor as alternative.

## Reproducibility
User-visible conversation archive: `E17_E18_decisive_algo_validation.zip` SHA256 `dda68b3591859624588ecae0120475dc74fd914e7ca48719fe84474aa4e23d61`, with Python scripts, exact numerical output JSON and README; no proprietary PDK or user E01 packet included. Required private `review_packet.zip` is in the earlier E12 package, SHA256 `400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a`. Sources `e17_bank_metadata_gate.py` SHA256 `e684c3df9499f6dbc92d3361756d3fa8cbbedaed37f77104fceb0909c5226977`; `e17b_same_metadata_control.py` SHA256 `acae5e1b9db600148ae179b5b9f7de1f3768ae1e30c2598d63a8d7ad2b35bc9c`; `e18_real_trace_ladder_adc_gate.py` SHA256 `238bd1d4fd5a1d9eb6443070c295af892b2dfea8d801e1dd0cce13b47157504c`. Scripts currently in conversation archive, **not committed as executable files to this GitHub repository**.
