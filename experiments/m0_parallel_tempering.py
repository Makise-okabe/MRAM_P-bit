#!/usr/bin/env python3
"""Ideal-device M0 parallel tempering (PT) with cost and mixing diagnostics.

Fresh independent software gate only. Not a nonideal MTJ / floating-point result.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random

import m0_reference as base


def swap_log_ratio(beta_a, beta_b, energy_a, energy_b):
    """Log Pr(exchange) ratio for paired Boltzmann replicas.

    The same solver Hamiltonian is used by local updates and swaps.
    """
    return (beta_a - beta_b) * (energy_a - energy_b)


def target_from_exact(instance):
    """Original task target, feasible-only for constrained TSP."""
    ref = base.exact(instance['J'], instance['h'], 0.1, instance['C'])
    if instance['kind'] == 'tsp_onehot':
        valid = [base.tsp_objective(instance, s)['tour_cost']
                 for s in ref['states'] if base.tsp_objective(instance, s)['valid']]
        return min(valid)
    if instance['kind'] == 'weighted_maxcut':
        return max(base.cut_value(instance['weights'], s) for s in ref['states'])
    raise ValueError('unsupported instance')


def task_score(instance, state):
    if instance['kind'] == 'tsp_onehot':
        d = base.tsp_objective(instance, state)
        return d['valid'], d['tour_cost']
    return True, base.cut_value(instance['weights'], state)


def at_target(instance, state, target, atol=1e-8):
    valid, score = task_score(instance, state)
    if not valid:
        return False
    if instance['kind'] == 'tsp_onehot':
        return score <= target + atol
    return score >= target - atol


def pt_run(instance, betas, *, seed=20261107, burnin=2000,
           collect=3000, sweeps=1, solver_J=None, solver_h=None):
    """One PT trial. Each sweep performs N random-site single-spin updates per replica.

    Optimizer target: first cold-replica checkpoint that hits the exact *original*
    task optimum. Sampling diagnostics: cold replica after burn-in. Report all
    attempted replica updates and exchanges, including burn-in.
    """
    if len(betas) < 2 or any(not math.isfinite(b) or b <= 0 for b in betas):
        raise ValueError('need >=2 finite positive inverse temperatures')
    if any(a >= b for a, b in zip(betas, betas[1:])):
        raise ValueError('betas must be strictly increasing (hottest to coldest)')
    if burnin < 0 or collect < 1 or sweeps < 1:
        raise ValueError('bad PT budget')
    J = instance['J'] if solver_J is None else solver_J
    h = instance['h'] if solver_h is None else solver_h
    base.assert_ising(J, h)
    if len(h) != len(instance['h']):
        raise ValueError('solver and original spin counts differ')
    n, k = len(h), len(betas)
    if n > 16:
        raise ValueError('M0 exact-target PT pilot restricted to N<=16')
    target = target_from_exact(instance)
    rng = random.Random(seed)
    states = [[rng.choice((-1, 1)) for _ in range(n)] for _ in betas]
    first_hit_updates = 0 if at_target(instance, states[-1], target) else None
    first_hit_swaps = 0 if first_hit_updates == 0 else None
    total_updates = 0
    swap_attempts = swap_accepts = 0
    cold_samples = []
    total_cycles = burnin + collect
    for cycle in range(total_cycles):
        for ridx, beta in enumerate(betas):
            for _ in range(sweeps*n):
                base.update(J, h, states[ridx], beta, rng)
                total_updates += 1
        start = cycle % 2
        for a in range(start, k-1, 2):
            b = a+1
            ea = base.energy(J,h,states[a])
            eb = base.energy(J,h,states[b])
            log_ratio = swap_log_ratio(betas[a],betas[b],ea,eb)
            swap_attempts += 1
            if log_ratio >= 0 or rng.random() < math.exp(log_ratio):
                states[a], states[b] = states[b], states[a]
                swap_accepts += 1
        # COLD-only target check avoids uncounted hot-replica selection.
        if first_hit_updates is None and at_target(instance, states[-1], target):
            first_hit_updates = total_updates
            first_hit_swaps = swap_attempts
        if cycle >= burnin:
            cold_samples.append(tuple(states[-1]))
    freq = {}
    for s in cold_samples:
        freq[s] = freq.get(s,0)+1
    exact = base.exact(instance['J'],instance['h'],betas[-1],instance['C'])
    tv = 0.5*sum(abs(freq.get(s,0)/len(cold_samples)-p)
                 for s,p in zip(exact['states'],exact['probabilities'])) if solver_J is None and solver_h is None else None
    changes = sum(a != b for a,b in zip(cold_samples,cold_samples[1:]))
    valid = [task_score(instance,s)[0] for s in cold_samples]
    return dict(
        tier='E1 independent ideal-device software M0; no physical MTJ claims',
        instance_kind=instance['kind'], spin_count=n, betas=list(betas), seed=seed,
        burnin_cycles=burnin, measured_cycles=collect, sweeps_per_cycle=sweeps,
        all_replica_spin_update_attempts=total_updates, initialization_spin_draws=n*k,
        replica_swap_attempts=swap_attempts, replica_swap_accepts=swap_accepts,
        replica_swap_acceptance=swap_accepts/swap_attempts if swap_attempts else None,
        cold_checkpoint_count=total_cycles, cold_sample_count=len(cold_samples),
        cold_unique_states=len(freq), cold_state_changes=changes,
        cold_valid_fraction=sum(valid)/len(valid), cold_sample_tv_to_ideal=tv,
        original_task_target=target, target_type='original valid tour min cost' if instance['kind']=='tsp_onehot' else 'original max cut',
        cold_first_target_spin_updates=first_hit_updates,
        cold_first_target_swap_attempts=first_hit_swaps,
        target_hit=first_hit_updates is not None,
        cold_samples=cold_samples,
    )


def write_trial(instance, result, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    samples = result['cold_samples']
    manifest = dict(instance=instance,result={k:v for k,v in result.items() if k!='cold_samples'})
    (output/'pt_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True,allow_nan=False)+'\n')
    with (output/'pt_cold_samples.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['sample','state_bits','valid','original_task_objective','original_ising_energy','target_hit'])
        for i,s in enumerate(samples):
            v,score=task_score(instance,s)
            w.writerow([i,''.join('1' if x>0 else '0' for x in s),int(v),score,
                        base.energy(instance['J'],instance['h'],s,instance['C']),int(at_target(instance,s,result['original_task_target']))])
    sums={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob('pt_*')}
    (output/'SHA256SUMS.json').write_text(json.dumps(sums,indent=2,sort_keys=True)+'\n')
    return manifest['result']


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--family',choices=('tsp','maxcut'),default='tsp')
    ap.add_argument('--size',type=int,default=4)
    ap.add_argument('--instance-seed',type=int,default=20261106)
    ap.add_argument('--sample-seed',type=int,default=20261107)
    ap.add_argument('--betas',type=str,default='0.03,0.05,0.08,0.12,0.18,0.27,0.38,0.50')
    ap.add_argument('--burnin',type=int,default=1000)
    ap.add_argument('--collect',type=int,default=2000)
    ap.add_argument('--sweeps',type=int,default=1)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    try:
        betas=[float(x.strip()) for x in a.betas.split(',')]
        inst=base.tsp_instance(a.size,a.instance_seed) if a.family=='tsp' else base.maxcut_instance(a.size,a.instance_seed)
        result=pt_run(inst,betas,seed=a.sample_seed,burnin=a.burnin,collect=a.collect,sweeps=a.sweeps)
        shown=write_trial(inst,result,a.output)
    except (ValueError, FileExistsError) as exc:
        ap.error(str(exc))
    print(json.dumps(shown,indent=2))

if __name__=='__main__':
    main()
