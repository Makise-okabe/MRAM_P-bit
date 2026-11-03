# ADR-0002: Prioritize a precise decoded-covariance grouping check

Date: 4 November 2026 (Singapore)

Status: candidate-development priority; final topic and originality unresolved.

Context: the general mapping direction sounded useful but its novelty remained vague.
Bit-significance-aware operation, co-zero grouping and fault-aware mapping all have close
prior work. A new joint objective label would not establish a contribution.

Decision: investigate whether grouping can control decoded cross-cycle error covariance
at fixed read count and marginal read quality. The candidate and completed constructed
check are specified in [the novelty note](../novelty/2026-11-04-covariance-mapping.md).
No new direction family or physical target is introduced. ADR-0001's evidence contract,
competing alternatives and target E02 gate remain in force.

Evidence: E03M is a mathematical/illustrative counterexample with calibrated scalar
observables, exact moment computation and paired sampling. It does not establish a
useful mapper, original literature priority, target physics or task/energy improvement.

Alternatives: broad yield/tail-risk constraints, generic bit-aware grouping and ordinary
polarity/offset recoding were screened as directions already having broad antecedents;
none was selected on wording alone. F1 and the other families remain available if this
precise mechanism fails.

Next decision: full closest methods plus paired overlap/covariance checks on an authorized
target model, then real-trace mapping versus tuned combined comparators. Stop the method
claim if already supplied by prior art or if practical gain disappears. The mathematical
check remains part of the path history regardless.
