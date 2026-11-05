#!/usr/bin/env python3
"""M0 clean-room ideal Ising mathematical baseline. No legacy device/results used."""
import itertools
import math
import random

def assert_ising(J,h):
    n=len(h)
    if n < 2 or len(J)!=n or any(len(r)!=n for r in J):
        raise ValueError("invalid Ising matrix dimensions")
    if not all(math.isfinite(x) for x in h) or not all(math.isfinite(v) for r in J for v in r):
        raise ValueError("nonfinite coefficients")
    for i in range(n):
        if abs(J[i][i]) > 1e-12:
            raise ValueError("nonzero diagonal")
        for j in range(i+1,n):
            if abs(J[i][j]-J[j][i]) > 1e-12:
                raise ValueError("non-symmetric coupling")

def energy(J,h,s,C=0.0):
    return C-sum(h[i]*s[i] for i in range(len(h)))-sum(
        J[i][j]*s[i]*s[j] for i in range(len(h)) for j in range(i+1,len(h)))

def exact(J,h,beta,C=0.0):
    assert_ising(J,h)
    if len(h)>16 or beta<=0:
        raise ValueError("exact requires N<=16 and beta>0")
    states=list(itertools.product((-1,1),repeat=len(h)))
    energies=[energy(J,h,s,C) for s in states]
    best=min(energies)
    logs=[-beta*(v-best) for v in energies]
    z=sum(math.exp(x) for x in logs)
    return dict(states=states,energies=energies,
                probabilities=[math.exp(x)/z for x in logs],
                ground_energy=best,ground_degeneracy=sum(abs(v-best)<1e-9 for v in energies))

def sigmoid(x):
    if x>=0:
        z=math.exp(-x)
        return 1/(1+z)
    z=math.exp(x)
    return z/(1+z)

def update(J,h,s,beta,rng):
    i=rng.randrange(len(h))
    field=h[i]+sum(J[i][j]*s[j] for j in range(len(h)) if i!=j)
    s[i]=1 if rng.random()<sigmoid(2*beta*field) else -1

def sample(J,h,beta,seed,burnin,records,thin):
    assert_ising(J,h)
    if beta<=0 or burnin<0 or records<1 or thin<1:
        raise ValueError("invalid sample budget")
    rng=random.Random(seed)
    s=[rng.choice((-1,1)) for _ in h]
    for _ in range(burnin):
        update(J,h,s,beta,rng)
    draws=[]
    for _ in range(records):
        for _ in range(thin):
            update(J,h,s,beta,rng)
        draws.append(tuple(s))
    return draws

