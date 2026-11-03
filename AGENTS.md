# Active pathfinding workspace

- This is the public `Makise-okabe/MRAM_Path_Finding` repository. Keep the legacy
  `MRAM_FYP_Overleaf` repository and its archive unchanged during new experiments.
- The target is a physical 256x256 array. Software matrices, proposed row schedules
  and padded/packed neural weights do not validate its electrical implementation.
- Reuse audited neural weights, quantizers, dataset partitions and general software.
  Exclude retired electrical measurements, fitted current laws and ADC settings from
  new target calibration, validation and claimed improvements.
- GF access-NFET use in the authorized environment with the student-owned MTJ model
  is the current source policy. Never commit licensed PDK sources/coefficients,
  proprietary MTJ models, credentials, raw netlists or private machine artifacts.
- Read `research/00_scope.md` and the applicable experiment protocol before changing
  scientific code. Label software verification, workload structure, illustrative
  models, target simulations and task evaluation separately.
- Previously inspected validation/test inputs remain development data. Fit mapping
  on calibration parents only and retain parent-image and activation-bit identities.
- A resident mapping is shared across all activation/weight planes using its array.
  Preserve signed reconstruction and count physical bit positions explicitly.
- Use non-overwriting run directories and record source/input/output hashes. Update
  the register, dated logbook and CA2 evidence map for meaningful outcomes. A prepared
  NUS runner is not an executed MNIST or Spectre experiment.
- Keep physical quantities unavailable until validated; read counts are not energy
  or latency. No method has a novelty pass. F3 is the primary bounded investigation;
  F7 remains conditional.
- Run meaningful input-contract/arithmetic checks for code changes. If LaTeX changes,
  compile and review its PDF. GitHub and Overleaf synchronization remain separate.
