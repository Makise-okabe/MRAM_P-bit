#!/usr/bin/env python3
"""P01: exact small-N Ising reference and seeded asynchronous Gibbs.
This is software-only research scaffolding, not a physical MTJ model.
"""
import argparse
import itertools
import json
import math
import random

def generate_instance(n, rng):
    J = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            w = 10.0 ** rng.uniform(-1.0, 1.0) * rng.choice((-1.0, 1.0))
            J[i][j] = J[j][i] = w
    return J

def energy(J, s):
    return -sum(J[i][j] * s[i] * s[j] for i in range(len(s))
                for j in range(i + 1, len(s)))

def exact_ground_state(J):
    assert 2 <= len(J) <= 16
    best, multiplicity = math.inf, 0
    for s in itertools.product((-1, 1), repeat=len(J)):
        e = energy(J, s)
        if e < best - 1e-10:
            best, multiplicity = e, 1
        elif abs(e - best) <= 1e-10:
            multiplicity += 1
    return best, multiplicity

def sigmoid(x):
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)

def field(J, s, i):
    return sum(J[i][j] * s[j] for j in range(len(s)) if j != i)

def gibbs_best(solver_J, score_J, *, beta, updates, rng):
    n = len(solver_J)
    s = [rng.choice((-1, 1)) for _ in range(n)]
    best = energy(score_J, s)
    for _ in range(updates):
        i = rng.randrange(n)
        s[i] = 1 if rng.random() < sigmoid(2 * beta * field(solver_J, s, i)) else -1
        best = min(best, energy(score_J, s))
    return best

def fixed_point(J, bits, scale):
    assert bits >= 2 and scale > 0
    limit = 2 ** (bits - 1) - 1
    n = len(J)
    Q = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            code = max(-limit, min(limit, round(J[i][j] / scale)))
            Q[i][j] = Q[j][i] = code * scale
    return Q

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--cases", type=int, default=8)
    p.add_argument("--seed", type=int, default=20261105)
    p.add_argument("--updates", type=int, default=5000)
    p.add_argument("--beta", type=float, default=0.8)
    a = p.parse_args()
    if not 2 <= a.n <= 16 or a.cases < 1 or a.updates < 1 or a.beta <= 0:
        p.error("Need 2<=n<=16; cases, updates, beta must be positive")
    rng = random.Random(a.seed)
    out = []
    for k in range(a.cases):
        J = generate_instance(a.n, rng)
        e_star, degeneracy = exact_ground_state(J)
        max_abs = max(abs(J[i][j]) for i in range(a.n) for j in range(i + 1, a.n))
        seed = a.seed + k + 1000000
        best = gibbs_best(J, J, beta=a.beta, updates=a.updates, rng=random.Random(seed))
        qout = {}
        for bits in (4, 8):
            # Diagnostic max-range scale, not optimized fixed-point baseline.
            scale = max_abs / (2 ** (bits - 1) - 1)
            quant = fixed_point(J, bits, scale)
            qbest = gibbs_best(quant, J, beta=a.beta, updates=a.updates, rng=random.Random(seed))
            qout["INT%d_maxrange" % bits] = {"scale": scale, "original_energy_gap": max(0., qbest - e_star)}
        out.append({"case": k, "ground_energy": e_star, "degeneracy": degeneracy,
                    "reference_gap": max(0., best - e_star), "quantized": qout})
    print(json.dumps({"evidence": "seeded software-only exploratory",
                      "limitations": "no tuned scales, low-bit FP, device or hardware model yet",
                      "parameters": vars(a), "cases": out}, indent=2))

if __name__ == "__main__":
    main()
