#!/usr/bin/env python3
"""H1 E2 exact random-scan p-bit Markov dynamics on 8-spin complex 16-QAM.

Reuses H2 frozen-calibrated 16-QAM representation; no new format search.
Calculates P(hit original-quality target by K), P(output state at K in target),
expected original residual gap and Gray BER. This is mathematical exact finite
state probability propagation, NOT physical/characterized MRAM results.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

RESPONSES=("ideal", "contrast090", "mismatch")
CANDIDATES=("mixed_fp", "mixed_int", "bfp6", "uniform_fp6")


def sigmoid(z):
    """Numerically stable sigmoid on arrays."""
    z=np.asarray(z, dtype=np.float64)
    return np.where(z>=0, 1/(1+np.exp(-np.maximum(z,0))),
                    np.exp(np.minimum(z,0))/(1+np.exp(np.minimum(z,0))))


def flip_lookup(states):
    """Derive neighbors from the actual state ordering, not bit-order guesses."""
    states=np.asarray(states,dtype=np.int8)
    m,n=states.shape
    if m!=(1<<n) or n>12:
        raise ValueError("exact-chain state count must be 2^N with N<=12")
    masks=1<<np.arange(n,dtype=np.int32)
    keys=np.sum((states>0).astype(np.int32)*masks,axis=1)
    if len(np.unique(keys))!=m:
        raise ValueError("states are not a complete binary enumeration")
    lookup=np.empty(m,dtype=np.int32)
    lookup[keys]=np.arange(m,dtype=np.int32)
    flipped=lookup[keys[:,None] ^ masks[None,:]]
    return flipped


class RandomScanChain:
    """Single-site random scan, one attempted update per transition."""
    def __init__(self, states, J, h, beta, response, gains=None,offsets=None):
        states=np.asarray(states,dtype=np.int8)
        self.states=states
        m,n=states.shape
        J=np.asarray(J,dtype=float)
        h=np.asarray(h,dtype=float)
        if J.shape!=(n,n) or h.shape!=(n,) or not np.allclose(J,J.T,atol=1e-12):
            raise ValueError("invalid symmetric Hamiltonian")
        if response not in RESPONSES or beta<=0:
            raise ValueError("unsupported response or beta")
        gains=np.ones(n) if gains is None else np.asarray(gains,dtype=float)
        offsets=np.zeros(n) if offsets is None else np.asarray(offsets,dtype=float)
        if gains.shape!=(n,) or offsets.shape!=(n,):
            raise ValueError("device population shape mismatch")
        field=states.astype(float)@J.T+h[None,:]
        if response=='mismatch':
            z=2*beta*(field*gains[None,:]+offsets[None,:])
        else:
            z=2*beta*field
        pplus=sigmoid(z)
        if response=='contrast090':
            pplus=0.05+0.90*pplus
        pflip=np.where(states>0,1-pplus,pplus)/n
        self.flip=flip_lookup(states)
        self.stay=1-np.sum(pflip,axis=1)
        self.incoming=pflip[self.flip,np.arange(n)[None,:]]
        if self.stay.min() < -1e-12:
            raise ValueError("negative Markov stay probability")

    def step(self,p):
        p=np.asarray(p,dtype=np.float64)
        return p*self.stay + (p[self.flip]*self.incoming).sum(axis=1)

    def stationary(self,initial=None,max_steps=15000,tol=1e-11):
        m=len(self.states)
        p=np.full(m,1/m) if initial is None else initial.copy()
        for k in range(1,max_steps+1):
            new=self.step(p)
            if np.sum(np.abs(new-p))<tol:
                return new,k,True
            p=new
        return p,max_steps,False


def exact_dynamics(chain,orig_gap,gray_ber,budgets,target_gap,stationary_steps=15000):
    """Survival distribution is NOT renormalized after target mass removal."""
    orig_gap=np.asarray(orig_gap,float)
    gray_ber=np.asarray(gray_ber,float)
    target=orig_gap<=target_gap+1e-9
    m=len(orig_gap)
    p=np.full(m,1/m)
    survival=p.copy()
    survival[target]=0
    out=[]
    wanted={0,*budgets}
    for k in range(0,max(budgets)+1):
        if k in wanted:
            out.append(dict(budget=k,
                target_state_count=int(np.sum(target)),
                p_hit_by_budget=float(1-np.sum(survival)),
                p_snapshot_in_target=float(np.sum(p[target])),
                expected_original_gap=float(np.dot(p,orig_gap)),
                expected_gray_ber=float(np.dot(p,gray_ber))))
        if k==max(budgets):
            break
        p=chain.step(p)
        survival=chain.step(survival)
        survival[target]=0
    pi,iterations,converged=chain.stationary(initial=p,max_steps=stationary_steps)
    stat=dict(stationary_converged=converged,stationary_iterations=iterations,
              stationary_p_target=float(np.sum(pi[target])) if converged else None,
              stationary_expected_gap=float(np.dot(pi,orig_gap)) if converged else None,
              stationary_expected_gray_ber=float(np.dot(pi,gray_ber)) if converged else None)
    return out,stat


def do_selftest():
    import itertools
    spins=np.asarray(list(itertools.product((-1,1),repeat=3)),dtype=np.int8)
    J=np.array([[0,0.4,-0.3],[0.4,0,0.25],[-0.3,0.25,0]],float)
    h=np.array([0.1,-0.3,0.4])
    chain=RandomScanChain(spins,J,h,0.8,'ideal')
    p=np.ones(len(spins))/len(spins)
    np.testing.assert_allclose(chain.step(p).sum(),1,atol=1e-13)
    # Ideal Gibbs conditional must preserve the Boltzmann distribution.
    energy=-0.5*np.sum((spins@J)*spins,axis=1)-spins@h
    boltz=np.exp(-0.8*(energy-energy.min()));boltz/=boltz.sum()
    np.testing.assert_allclose(chain.step(boltz),boltz,atol=1e-13,rtol=1e-13)
    pi,it,conv=chain.stationary(tol=1e-12)
    assert conv
    np.testing.assert_allclose(pi,boltz,atol=1e-11)
    gap=np.maximum(0,energy-energy.min())
    ber=np.mean(spins!=spins[energy.argmin()],axis=1)
    outcomes,stat=exact_dynamics(chain,gap,ber,[0,1,10,100],0.0)
    assert math.isclose(outcomes[0]['p_hit_by_budget'],outcomes[0]['p_snapshot_in_target'])
    assert all(x['p_hit_by_budget']<=1+1e-12 for x in outcomes)
    assert all(a['p_hit_by_budget']<=b['p_hit_by_budget']+1e-12 for a,b in zip(outcomes,outcomes[1:]))
    assert all(x['p_hit_by_budget']>=x['p_snapshot_in_target']-1e-12 for x in outcomes)
    assert stat['stationary_converged']
    print('SELFTEST PASS: exact random-scan transition, Gibbs stationary, nonnormalized first-hit, snapshot policy')


def full_run(args):
    import h2_16qam_exact as h2
    if args.tx not in (2,3):
        raise ValueError("H1 accepts 2x2 (8 spins) or 3x3 (12 spins) complex 16-QAM")
    if args.rx!=args.tx:
        raise ValueError("first H1 assumes square MIMO")
    if args.cal_frames<1 or args.heldout_frames<1 or args.device_populations<1:
        raise ValueError("positive CAL, HELDOUT and device population counts required")
    if args.target_gap<0 or args.beta<=0 or not args.budgets:
        raise ValueError("invalid quality threshold or response gain")
    if set(range(args.cal_seed,args.cal_seed+args.cal_frames)) & set(range(args.heldout_seed,args.heldout_seed+args.heldout_frames)):
        raise ValueError("calibration and heldout seed overlap")
    if args.output.exists():
        raise ValueError("output exists; do not overwrite evidence")
    # Uses the SAME external J/h calibration policy as H2, extended by the
    # predeclared uniform-FP6 reference. Not another codebook search.
    h2.CANDIDATES['uniform_fp6']=('fp6_fn','fp6_fn')
    if args.grouping not in h2.GROUPINGS:
        raise ValueError('invalid symmetric grouping')
    frozen=h2.calibrate(args.tx,args.rx,args.snr_db,args.cal_frames,args.cal_seed,args.tile)
    oracle=h2.ExactOracle(args.tx)
    grayden=4*args.tx
    records=[]
    for fidx in range(args.heldout_frames):
        f=h2.frame(args.tx,args.rx,args.snr_db,args.heldout_seed+fidx)
        original=oracle.original(f,verify=True)
        reference=float(np.min(original))
        gap=np.maximum(0,original-reference)
        truth=h2.gray_bits(f['transmitted'])
        error=np.count_nonzero(oracle.gray!=truth[None,:],axis=1)/grayden
        for pop in range(args.device_populations):
            rng=np.random.default_rng(args.device_seed+pop)
            gain=np.exp(rng.normal(0,args.gain_sigma,size=4*args.tx))
            offset=rng.normal(0,args.offset_sigma,size=4*args.tx)
            for label in CANDIDATES:
                q=h2.represent(f,args.grouping,args.tile,label,frozen[f'{label}|{args.grouping}'])
                for response in RESPONSES:
                    chain=RandomScanChain(oracle.states,q['J'],q['h'],args.beta,response,gain,offset)
                    outcomes,stat=exact_dynamics(chain,gap,error,args.budgets,args.target_gap,
                                                   stationary_steps=args.stationary_steps)
                    for r in outcomes:
                        records.append(dict(frame_index=fidx,population=pop,seed=f['seed'],
                            format=label,response=response,grouping=args.grouping,
                            nominal_bits=q['bits'],target_gap=args.target_gap,
                            **r,**stat))
    summary=[]
    for label in CANDIDATES:
        for response in RESPONSES:
            for k in [0]+sorted(set(args.budgets)):
                sub=[r for r in records if r['format']==label and r['response']==response and r['budget']==k]
                if not sub:
                    continue
                av=lambda key:float(np.mean([x[key] for x in sub]))
                ok=[r for r in sub if r['stationary_converged']]
                summary.append(dict(format=label,response=response,budget=k,
                    frame_population_pairs=len(sub),nominal_bits=sub[0]['nominal_bits'],
                    p_hit_by_budget=av('p_hit_by_budget'),p_snapshot_in_target=av('p_snapshot_in_target'),
                    expected_original_gap=av('expected_original_gap'),expected_gray_ber=av('expected_gray_ber'),
                    stationary_converged_pairs=len(ok),stationary_p_target=float(np.mean([x['stationary_p_target'] for x in ok])) if len(ok)==len(sub) else None))
    args.output.mkdir(parents=True,exist_ok=False)
    for fn,items in [('h1_per_frame.csv',records),('h1_summary.csv',summary)]:
        with (args.output/fn).open('w',newline='',encoding='utf-8') as fp:
            w=csv.DictWriter(fp,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
    meta=dict(config={k:v for k,v in vars(args).items() if k not in ('output',)},
        evidence='E2 illustrative response; mathematically exact random-scan chain under assumed conditionals, not measured MRAM',
        distinction='p_hit_by_budget is ANY visit to original quality, p_snapshot_in_target is actual fixed-time snapshot output; old best-quantized-checkpoint output policy is NOT modeled. Stationary result optional only if converged.',
        frozen_scales={f'{label}|{args.grouping}':frozen[f'{label}|{args.grouping}'] for label in CANDIDATES},
        baseline='Uniform initialization over all 2^(4tx) spin states, fixed field->sigmoid beta, equal attempted single-site update budgets.',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    meta['config']['output']=str(args.output)
    (args.output/'h1_protocol.json').write_text(json.dumps(meta,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('=== H1 exact Markov 16-QAM: E2 illustrative response, NOT device measurement ===')
    print('Format Response Budget | Hit-any  Snapshot  ExpectedBER  StationaryP   Bits')
    for s in summary:
        print(f"{s['format']:11s} {s['response']:11s} {s['budget']:5d} | "
              f"{s['p_hit_by_budget']:.4f} {s['p_snapshot_in_target']:.4f} "
              f"{s['expected_gray_ber']:.4f} "
              f"{s['stationary_p_target'] if s['stationary_p_target'] is not None else 'NA'} "
              f"{s['nominal_bits']}")
    print('Saved:',args.output)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selftest',action='store_true')
    parser.add_argument('--tx',type=int,default=2)
    parser.add_argument('--rx',type=int,default=2)
    parser.add_argument('--snr-db',type=float,default=12.)
    parser.add_argument('--cal-frames',type=int,default=40)
    parser.add_argument('--heldout-frames',type=int,default=20)
    parser.add_argument('--cal-seed',type=int,default=2026114000)
    parser.add_argument('--heldout-seed',type=int,default=2026115000)
    parser.add_argument('--device-seed',type=int,default=2026116000)
    parser.add_argument('--device-populations',type=int,default=2)
    parser.add_argument('--gain-sigma',type=float,default=0.20)
    parser.add_argument('--offset-sigma',type=float,default=0.10)
    parser.add_argument('--beta',type=float,default=1.0)
    parser.add_argument('--target-gap',type=float,default=0.05)
    parser.add_argument('--budgets',type=str,default='20,100,500')
    parser.add_argument('--stationary-steps',type=int,default=15000)
    parser.add_argument('--grouping',choices=['global','significance','tile'],default='global')
    parser.add_argument('--tile',type=int,default=4)
    parser.add_argument('--output',type=Path)
    a=parser.parse_args()
    if a.selftest:
        do_selftest();return
    if a.output is None:
        parser.error('--output required')
    a.budgets=sorted({int(x) for x in a.budgets.split(',')})
    if any(x<=0 for x in a.budgets):
        parser.error('budgets must be positive')
    try:
        full_run(a)
    except (ValueError,FileExistsError) as e:
        parser.error(str(e))


if __name__=='__main__':
    main()
