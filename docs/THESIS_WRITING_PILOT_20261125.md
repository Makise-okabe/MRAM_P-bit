# Thesis writing pilot — 25 November 2026

Baseline: dc667b9d60213d3f551cb7b47e99b48627080a9a.
Upstream: [Best-Paper-Writing-Skill v1.2](https://github.com/gulucaptain/Best-Paper-Writing-Skill/tree/b9eff99a2130bea960ef1050eacf9f40cb792dd4).

## Scope and route
Manual application of the upstream intake, L5 mechanism/L3 empirical-sweep route, claim calibration, and abstract rules to the existing manuscript. The existing LaTeX class, title, introduction, results and figures are untouched. This is an abstract-only pilot, not execution of the full upstream skill.

| Intake field | Manuscript-supported content |
| --- | --- |
| Task | Choose low-bit stored coupling codes for finite-budget weighted Max-Cut |
| Tension | Nominal storage reduction versus search access and returned-state quality |
| Closest work | Hizzani et al. on precision-induced traps; Yao et al. on integer versus floating-point Ising behaviour. Existing citations only; not independently verified in this pilot |
| Insight | Output selection and stochastic access are distinct mechanisms; precision requirements depend on policy and graph family |
| Method | Family-level non-inferiority; registered weak-tail intervention; passive top-16 buffer; synthetic persistent offsets |
| Open requirement | Full-system cost, physical device calibration and thesis rubric alignment |

## Claim evidence and changes
All evidence below is traced to the baseline manuscript sections, not independently rerun or audited against raw data in this pilot.

| Claim | Source section in baseline main.tex | Wording guardrail |
| --- | --- | --- |
| FP5/INT6 ring; FP5/INT5 torus | Ideal width certification and family dependence | Lowest certified tested codes; family mean, +0.5 pp tolerance |
| Masking/restoring weak values changes selection loss | Registered weak-tail mechanism | Registered directional effect on fresh rings; not a universal causal explanation |
| Top-16 eliminates ideal ring width difference | Stage A: registered buffer-policy certification | Host-side source-objective rescoring; not free hardware, not generalised to offset ring INT5 |
| All six offset contrasts pass | Registered persistent logit-offset validation | Synthetic offset model; not measured device data or FP superiority |
| Individual-instance counterexample | Counterexamples and heterogeneity | Descriptive official anchor; not ensemble inference |
| Cost not established | Implementation implications | Nominal storage only; component synthesis is not full-system cost |

The revised abstract opens with the engineering trade-off rather than a method description, separates mechanism from format ranking, moves the detailed intervention effect sizes and trajectory counts to the unchanged results chapter, and ends with the engineering decision boundary. The original title is retained.

## Overrides and verification
- Retain decisive negative/mixed results and essential physical/hardware scope even though upstream prefers moving limitations out of abstracts. This is a thesis, not an ML award-paper submission.
- No new references, experiments, numbers, results or figures.
- Upstream Python checkers, exemplar retrieval, LaTeX compilation and Overleaf synchronization were not executed. This is a manual pilot only.
- Before merging: run the checkers locally, compile, compare the PDF, inspect source evidence and verify course AI-use requirements.
- Keep pilot and backup branches separate; do not merge without student review.

## Reproducible local trial
In a local clone on the pilot branch, use a separate temporary directory to clone the upstream repository and check out the pinned commit above. From the thesis repository directory run the upstream install.sh with arguments `codex --project` using the absolute path to that temporary clone. Review the install script before execution: it replaces an existing skill directory of the same name. Restart Codex, invoke `$bestpaper-writing`, and constrain edits to the pilot branch.
