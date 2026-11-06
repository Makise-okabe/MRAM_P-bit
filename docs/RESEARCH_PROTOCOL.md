# Evidence protocol — weighted Max-Cut / STT-MRAM p-bit coupling

**Active policy, 6 November 2026:** weighted Max-Cut using the Biq Mac Library Mac section, confirmed after supervisor discussion. The [benchmark decision](BENCHMARK_DECISION_WEIGHTED_MAXCUT_20261106.md) supersedes earlier BPSK/QAM-only policies. Low-order FP coupling and STT-MRAM p-bit nonidealities remain the core; optimized INT/BFP are controls.

Tier E0 exact theory; E1 seeded algorithmic simulation; E2 illustrative response; E3 sourced/validated device response; E4 authorized circuit; E5 bit-true/synthesis/hardware. Do not relabel synthetic response parameters or CMOS logic synthesis as measured stochastic-MTJ evidence.

Independent graph instance is the statistical unit. Pair representations on the same original graph and budgets; nest solver seeds and device populations. Predeclare calibration/held-out graphs, quality floor, target definition and observation/output policy. Save source instance identity and weights, represented J, format/scale/rounding, input normalization, seeds, attempted updates and relevant source/output hashes. Do not add infrastructure beyond what the actual experiment needs.

Use symmetric zero-diagonal J=-w and h=0 under E=-sum J_ij*s_i*s_j. The original objective is Cut_w=sum w_ij*(1-s_i*s_j)/2 and E=sum w-2*Cut_w. Verify signs and reference-value conventions independently. Report original-cut quality and gap; identify references as certified optima, best-known values or bounds. Relative gaps require a meaningful denominator. Original/represented objectives must not be silently interchanged.

Any-visit target probability, final snapshot quality and best-represented-energy returned output are distinct. Runtime selection may not consult an uncosted original-task oracle. Physical offset does not vanish just because problem h=0.

Use unchanged source weights, including signs. Weighted integer instances are legitimate: do not introduce fractional or widened weights just to favor FP. No FP advantage is assumed. Preserve metadata, encoded-scale, accumulator and memory/access costs. Update counts are not physical latency/energy; pre-placement logic area is not total accelerator area.

Unrelated earlier experiments are outside the active weighted Max-Cut evidence chain. Generic mathematical tests and component RTL evidence may be reused within their stated scope; new Biq Mac task claims require fresh instance-specific runs. Do not claim that documentation migration has implemented or executed the new benchmark.

## M0 executable source gate
A dedicated Mac/Rudy loader and exact Decimal original-cut/Ising/flip audit have been authored on a separate draft branch, alongside signed-graph unit tests. Preserve source SHA256, source node and edge counts, loop and parallel-edge handling and optimum_status=NOT_LOADED until exact/verified reference data is imported. This is E0 mathematical consistency, not measured Max-Cut solver quality. See [M0 source protocol](M0_BIQMAC_SOURCE_PROTOCOL.md).
