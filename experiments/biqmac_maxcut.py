#!/usr/bin/env python3
"""Biq Mac / Mac Rudy loader and exact weighted-Max-Cut identity audit.

Stage M0/E0 only: NO solver, no p-bit response, no approximation results.
All original weights are retained as exact decimal values; loops ignored
and parallel undirected edges summed, matching Biq Mac solver conventions.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import random


@dataclass(frozen=True)
class RudyGraph:
    n: int
    raw_edge_count: int
    edges: tuple[tuple[int, int, Decimal], ...]  # 0-based, u<v
    loops_ignored: int
    parallel_entries: int
    zero_sum_edges: int
    source: str
    sha256: str

    @property
    def sum_weights(self) -> Decimal:
        return sum((w for _, _, w in self.edges), Decimal(0))


def load_rudy(path: str | Path) -> RudyGraph:
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    # Biq Mac explicitly permits comment lines beginning with '#'.
    lines = [(ln, text.strip()) for ln, text in
             enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1)
             if text.strip() and not text.lstrip().startswith("#")]
    if not lines:
        raise ValueError("No Rudy header")
    line_no, header = lines[0]
    parts = header.split()
    if len(parts) != 2:
        raise ValueError(f"line {line_no}: expected 'n m' header")
    try:
        n, m = map(int, parts)
    except ValueError as exc:
        raise ValueError(f"line {line_no}: n and m must be integers") from exc
    if n < 1 or m < 0:
        raise ValueError("n must be positive and m nonnegative")
    if len(lines) != m + 1:
        raise ValueError(f"declares {m} edges, contains {len(lines)-1}")
    combined: dict[tuple[int, int], Decimal] = {}
    loops = duplicates = 0
    for line_no, line in lines[1:]:
        cols = line.split()
        if len(cols) != 3:
            raise ValueError(f"line {line_no}: expected 'u v weight'")
        try:
            u, v = int(cols[0]), int(cols[1])
            weight = Decimal(cols[2])
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"line {line_no}: invalid edge") from exc
        if not (1 <= u <= n and 1 <= v <= n) or not weight.is_finite():
            raise ValueError(f"line {line_no}: node index or weight invalid")
        if u == v:
            loops += 1
            continue
        a, b = sorted((u - 1, v - 1))
        key = (a, b)
        if key in combined:
            duplicates += 1
        combined[key] = combined.get(key, Decimal(0)) + weight
    zero_pairs = sum(1 for v in combined.values() if v == 0)
    edges = tuple((a, b, w) for (a, b), w in sorted(combined.items())
                  if w != 0)
    return RudyGraph(n=n, raw_edge_count=m, edges=edges,
                     loops_ignored=loops, parallel_entries=duplicates,
                     zero_sum_edges=zero_pairs,
                     source=str(path), sha256=digest)


def _validate_spins(graph: RudyGraph, spins: tuple[int, ...] | list[int]) -> None:
    if len(spins) != graph.n or any(s not in (-1, 1) for s in spins):
        raise ValueError("Expected one +/-1 spin per graph vertex")


def cut_weight(graph: RudyGraph, spins: tuple[int, ...] | list[int]) -> Decimal:
    """True ORIGINAL weighted cut (not a quantized Hamiltonian score)."""
    _validate_spins(graph, spins)
    return sum((w for i, j, w in graph.edges if spins[i] != spins[j]),
               Decimal(0))


def ising_energy(graph: RudyGraph, spins: tuple[int, ...] | list[int]) -> Decimal:
    """E=-sum(Jij si sj), with Jij=-wij and h=0; no constant offset."""
    _validate_spins(graph, spins)
    return sum((w * spins[i] * spins[j] for i, j, w in graph.edges),
               Decimal(0))


def local_field(graph: RudyGraph, spins: tuple[int, ...] | list[int],
                i: int) -> Decimal:
    _validate_spins(graph, spins)
    if not 0 <= i < graph.n:
        raise IndexError(i)
    return -sum((w * spins[j] if a == i else
                 w * spins[a] if j == i else Decimal(0)
                 for a, j, w in graph.edges), Decimal(0))


def audit_graph(graph: RudyGraph, n_random_states: int = 32,
                seed: int = 20261106) -> dict:
    """Check cut/energy identity and DeltaE for deterministic independent flips."""
    if n_random_states < 1:
        raise ValueError("n_random_states must be positive")
    rng = random.Random(seed)
    states = [[1] * graph.n, [-1] * graph.n,
              [(-1 if i % 2 else 1) for i in range(graph.n)]]
    states += [[rng.choice((-1, 1)) for _ in range(graph.n)]
               for _ in range(n_random_states)]
    checks = 0
    for state in states:
        score = cut_weight(graph, state)
        energy = ising_energy(graph, state)
        if energy != graph.sum_weights - 2 * score:
            raise AssertionError("E=sum(w)-2*Cut identity FAILED")
        i = rng.randrange(graph.n)
        flipped = list(state)
        flipped[i] = -flipped[i]
        delta = 2 * state[i] * local_field(graph, state, i)
        if ising_energy(graph, flipped) - energy != delta:
            raise AssertionError("DeltaE=2*s_old*H_i FAILED")
        checks += 1
    return {
        "status": "E0_PASS",
        "evidence": "Exact Rudy original-graph mapping and flip identity only; NOT a Max-Cut solver",
        "source": graph.source, "sha256": graph.sha256,
        "n": graph.n, "raw_edge_count": graph.raw_edge_count,
        "effective_nonzero_edges": len(graph.edges),
        "loops_ignored": graph.loops_ignored,
        "parallel_entries_aggregated": graph.parallel_entries,
        "zero_sum_edges": graph.zero_sum_edges,
        "original_weight_sum": str(graph.sum_weights),
        "identity_and_flip_checks": checks,
        "seed": seed,
        "optimum_status": "NOT_LOADED",
        "device_evidence": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path,
                        help="Original, unchanged Biq Mac Mac/Rudy text graph")
    parser.add_argument("--random-states", type=int, default=32)
    parser.add_argument("--seed", type=int, default=20261106)
    parser.add_argument("--output", type=Path,
                        help="Optional unique JSON audit report; never overwrite")
    args = parser.parse_args()
    result = audit_graph(load_rudy(args.file), args.random_states, args.seed)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as f:
            f.write(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
