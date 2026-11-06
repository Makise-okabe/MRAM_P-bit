# Proposed architecture — FP coupling array, stochastic p-bits, and CIM boundary

**Status:** architecture proposal, NOT a fabricated stochastic-MTJ array or a verified MRAM-CIM chip.

## What array are we still building?
The locked FYP is an N-spin probabilistic Ising machine. In BPSK MIMO, N equals the number of transmit BPSK symbols, Nt. A logical N-by-N matrix of symmetric couplings J (with zero diagonal), a length-N bias vector h, and an N-state stochastic p-bit network implement spin updates. A practical coupling tile can store just the unique undirected J edges or duplicate mirrored entries to increase bandwidth. The choice affects real storage/read circuitry.

Dataflow: BPSK MIMO frame (H,y) -> J,h coefficients -> **low-order FP4/FP6/FP8 coupling storage** -> sign/scale/exponent selection and bounded local-field accumulation -> p-bit control input -> stochastic spin update -> state feedback.

The selected p-bit input is H_i = h_i + sum_(j != i) J_ij s_j. It is NOT the neural-network MAC/ADC previously studied. The ideal software Gibbs sigmoid is not a measured physical p-bit transfer curve.

## What M2/M3 will implement
Keep the **64–128-spin coupling tile** milestone, initially a bit-true RTL/synthesizable digital coupling/accumulation tile with an explicit p-bit interface. This does NOT mean fabricating 64 or 128 stochastic MTJs, nor rebuilding the previous 256x256 conventional 2T1MTJ MRAM-CIM array. The previous stable MTJ model, read currents, ADC tests and extraction do not validate stochastic MRAM p-bit behavior.

Candidate implementations, to be compared and justified:
1. **Digital p-bit accelerator:** coupling values in SRAM/registers, arithmetic in peripheral CMOS, p-bits as separate circuits (or behavioral interface). Not automatically CIM.
2. **MRAM-backed near-memory coupling:** nonvolatile MRAM coefficient storage feeding adjacent local-field arithmetic; whether this counts as CIM depends on actual memory-compute integration.
3. **True in-array CIM:** array cells/interconnect execute the weighted sum within or immediately adjacent to storage. Sign, FP exponent, scaling, bias and analog/digital accumulation must be physically realized; ordinary 4-bit floating point cannot simply be assumed to map directly into MTJ conductance.

## Scientific originality and required evidence
The central novelty hypothesis is the **interaction of low-order floating-point coupling architecture (FP4/FP6/FP8, scale granularity, alignment and accumulation) with nonideal stochastic MRAM p-bit behavior**. The BPSK MIMO detector is solely the independent quality benchmark.

At M2, quantify unique/mirrored J storage, h and scale metadata, number format control, exponent alignment, accumulator width, routing/bandwidth, p-bit driving and timing, scheduling and replicas. At M3 implement bit-exact tile RTL and perform synthesis. A realistic physical p-bit input transfer (voltage/current, gain, mismatch, contrast, dynamics) needs physical provenance; E2 illustrative gain/offset sigmoid parameters are not measured MRAM parameters.

## Prior architectures, not validation of our implementation
- Camsari et al., Stochastic p-Bits for Invertible Logic, Physical Review X 7 (2017), DOI 10.1103/PhysRevX.7.031014.
- Intrinsic annealing in a hybrid memristor-magnetic tunnel junction Ising machine, Nature Communications (2026), DOI 10.1038/s41467-026-71844-8: HfO2 memristor crossbar performs weighted sums while SMTJ supplies stochastic spins. This does not demonstrate our low-order FP macro.
- In-Memory Neural Stochastic Differential Equations with Probabilistic Differential Pair Achieved by In-Situ P-Bit Using CMOS Integrated Voltage-Controlled Magnetic Tunnel Junctions, IEDM 2024, DOI 10.1109/IEDM50854.2024.10873318: related in-situ p-bit/CIM concept.
- A Scalable and Resource-Efficient Pipelined p-Computer for Probabilistic Ising Machines, Advanced Intelligent Systems (2026), DOI 10.1002/aisy.70521: digital memory/coupling bandwidth implementation comparison.

**Decision:** We retain an array and RTL/synthesis, but do not yet claim MRAM-CIM. The architecture name is *low-order FP coupling-array MRAM p-bit Ising machine* pending implementation evidence.