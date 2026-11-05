# M0 BPSK MIMO benchmark — independent, no legacy data

Complex signal model: y=Hx+n, H in C^(Nr x Nt), x in {-1,+1}^Nt. Channels sampled from properly normalized complex Rayleigh fading; n complex AWGN with declared variance and SNR convention. Each instance is an independently generated channel/noise frame; the true x is recorded.

ML objective: minimize R(s)=||y-Hs||². Ising with E=C−Σ_(i<j) Jij si sj−Σ_i hi si, J_ij=−2 Re((HᴴH)_ij) off-diagonal, h_i=2 Re((Hᴴy)_i), C=||y||²+Σ_i (HᴴH)_ii. Exact equality must be checked exhaustively for Nt<=4.

**Task measures:** ML-hit (versus exact small-N oracle), residual gap to the original ML minimum, bit-error rate versus transmitted BPSK bits, time-to-target counting replicas and swap work. ML-hit does not mean zero BER: noise may make the transmitted word non-ML.

**Core FYP engineering target:** actual low-order FP4/FP6/FP8 J-coupling + scaling/accumulation macro, benchmarked against strong scaled INT4/6/8 and shared-exponent formats with full metadata costs, under relevant nonideal p-bit response models. MIMO is a workload, not the contribution. No TSP results, older graph benchmarks or parasitic model transfers.

Existing Ising-based MIMO work includes finite-precision couplings (A. K. Singh et al., IEEE TWC 2022, DOI: 10.1109/TWC.2022.3189604). Independent device-aware low-order FP scale/architecture and verified synthesis must carry novelty.
