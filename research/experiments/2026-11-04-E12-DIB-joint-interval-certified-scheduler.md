# E12: DIB-CIM review and Joint-Interval Certified Read Scheduling
2026-11-04. **Candidate algorithm, not validated research originality, physical ADC energy or final neural classification.**

## Literature evidence
DIB-CIM, Chen et al., IEEE TCAS-I, published 31 August 2026, DOI 10.1109/TCSI.2026.3726936, is a 28nm 128x128 SOT-MRAM CIM architecture. Its publicly readable abstract describes LEBD (leading effective bits), I3D (0/1 input distribution), wordline block-size adaptation, zero-skipping, and dynamic-resolution ADC. Abstract reports 12-16% latency decrease against fixed-B=8 excluding zero-skipping. https://ieeexplore.ieee.org/abstract/document/11672681 . **Full 14-page DIB methods were not accessible; do not claim they lack an unobserved joint-operand condition.**

Other closest work: BLC-CIM with ReLU early termination (2025) https://doi.org/10.1016/j.mejo.2025.106796 ; input sparsity-aware ADC (2026) https://doi.org/10.1002/aisy.202501336 ; US11875244 early ReLU ADC skip; EP4028956B1 weight+activation threshold control; signed CIM mapping https://doi.org/10.3390/electronics14071340 . The novelty claim would have to be **tight joint input/weight intersection bounds plus expected certificate improvement for scheduling signed partial-count reads**. Early stopping, signed bitplanes, and dynamic ADC are not original inventions.

## Method
For a binary group of B=32, input popcount m and stored weight-bit popcount k, the exact integer intersection n lies in [max(0,m+k-B), min(m,k)]. Width equals min(m,k,B-m,B-k). A signed bit-serial partial read has coefficient c_t and current feasible count interval [L_t,U_t]; conservative upper bound on whole signed sum H = sum(c_t>0 ? c_t*U_t : c_t*L_t). A completed exact read n_t reduces H by c_t*(U_t-n_t) if c_t>0, or (-c_t)*(n_t-L_t) otherwise. If H<0, the final zero-bias ReLU output is provably zero: remaining reads for that output are unnecessary. Read t to maximize estimated bound reduction computed using E[n_t] = m_t*k_t/B (uniform overlap prior). No hidden true read is accessed for the scheduler.

## Executed experiments, real E01 MNIST activation and W4 weights
E01 source SHA256 400f094606615d73bfd90a0f32f7ef5d2ab0825bac67de1f3727c703c49f704a. 128 CAL and independent 256 DEV MNIST parent inputs.

E12A: on first FC1 256-row block, zero-rate-sorted mapping, joint feasible range reduces ideal *per-column programmable ADC comparison-count lower bound* by 13.121% relative to an input-only popcount bound; per-cycle maximum resolution shared by all columns improves only 4.714%. Input-only comparator model is a DIB-inspired proxy, **not a reproduction of DIB**.

E12B: optimizer that swaps physical rows to minimize joint ambiguity subject to fixed CAL group-read limit did not reliably beat sorting/CAR on DEV. Zero-sort seeded runs varied -0.396% to +0.351% held-out improvement in comparator count; some incurred more DEV reads. **Reject present mapper gain claim.**

E12C partial 256-row FC1 block, 8 output channels: joint bound-guided read order avoided 24.38% of eligible reads versus 20.07% by sign/MSB first; NOT whole layer.

E12D: concatenate all 784 real FC1 rows using four E01 256-row blocks (last 240 padded zeros), all 128 output channels, 8 input planes and signed 4-bit weights (+1,+2,+4,-8). Missing layer bias means **bias assumed ZERO**, so this is NOT the actual trained-model ReLU or final MNIST accuracy. Exact binary-count oracle only; no transistor circuit, ADC error, energy, or physical read simulation.

256 independent DEV parents / 128 channels: 17,965,231 ideal eligible binary-read events.
- Sign/MSB-first: 15,471,234 reads; 13.882% saved.
- Magnitude-first: 15,130,251 reads; 15.780% saved.
- **Joint-interval expected-bound-tightening scheduler: 14,839,921 reads; 17.396% saved.**
- Unimplementable future-outcome oracle: 14,107,579 reads; 21.473% saved.
- Zero-bias negative fraction: 45.883%. Every tested negative/zero decision preserved *exactly*.
- Joint over magnitude: **290,330** fewer reads, +1.616 percentage points of eligible reads; paired parent-bootstrap 95% [1.563, 1.673]pp.
- Joint over sign/MSB: +631,313 fewer reads, +3.514pp; 95% [3.430, 3.600]pp.
- CAL savings for joint: 17.344%; for magnitude: 15.655%. Narrow but consistent incremental benefit.

## Reproduce / source
Code + numerical results + user-originated frozen E01 packet bundled as conversation download E12_DIB_novelty_candidate_package.zip (SHA256 7382f66a1217560431c7afc2b4631e7163ad1e7ac08032de6ccc2cf5209a5845). Main Python e12d_full_fc1_interval_scheduler.py SHA256 17b817bb90823f1629846f48cc9f638433b473cc014a3a6065e536d9be68c67f. **The ZIP and code were not uploaded to GitHub in this commit.** Avoid placing the E01 user's model bitplanes on a public repository without authorization.

## Gates before academic novelty / FYP selection
1. Inspect actual full DIB 14-page method via NUS library and BLC ReLU early-termination rule; reject originality if equivalent decision exists.
2. Re-run full FC1 with actual model bias, then classification and later layers.
3. Replace exact count oracle with measured GF access-NFET + authorized student MTJ ADC error intervals: never certify an incorrect ReLU zero.
4. Implement low-overhead bucket/priority controller, account for 6-bit per-group weight-popcount ROM, additional references/control, delays, ADC energy, and signal integrity. Compare against input-only confidence bounds, optimized signed MSB order and magnitude-first, not only DIB input-distribution style.
5. Only choose method if **task-level and total energy/time** gains are meaningful under physically defensible hardware model.

Provisional summary for Prof Fong: DIB disclosed architecture allocates WL blocks and ADC precision from input significance/distribution. Here a bound-guaranteed signed read ordering uses BOTH input and weight counts to select which partial read tightens the output negativity certificate. Initial real-E01 full-FC1 zero-bias arithmetic reduces ideal eligible reads by 17.4% vs 15.8% for a simple strong competitor. Novelty and hardware savings **remain open**.
