#!/usr/bin/env python3
"""E29A: signed-W4 cancellation-aware recovery, 16-subset CAL/DEV gate.

PURE SOFTWARE. Demo is SYNTHETIC, not GF / PEX / neural accuracy.
Runtime selector reads observable feature labels, never true count errors.
Digital replay costs are abstract, not measured hardware energy/latency.
Python 3.6+ standard library only.
"""
import argparse
import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

C=(1,2,4,-8)
ORDER=(3,2,1,0)

def bits(s):
    return [j for j in range(4) if s>>j&1]

def cost(s,d):
    return sum(d[j] for j in bits(s))

def residual(e,s):
    return sum(C[j]*e[j] for j in range(4) if not(s>>j&1))

def candidates(d,b):
    return [s for s in range(16) if cost(s,d)<=b]

def risks(rows,subsets):
    return {s:sum(residual(r['e'],s)**2 for r in rows)/len(rows) for s in subsets}

def choose(r,choices,d,lmb):
    return min(choices,key=lambda s:(r[s]+lmb*cost(s,d),cost(s,d),s))

def moments(rows):
    n=len(rows)
    mu=[sum(r['e'][j] for r in rows)/n for j in range(4)]
    var=[sum((r['e'][j]-mu[j])**2 for r in rows)/n for j in range(4)]
    return mu,var

def diag_risk(s,mu,var):
    remain=[j for j in range(4) if not(s>>j&1)]
    return (sum(C[j]*mu[j] for j in remain)**2+
            sum(C[j]**2*var[j] for j in remain))

def fit(cal,d,b,min_cal,lmb):
    allowed=candidates(d,b)
    by=defaultdict(list)
    for r in cal:by[r['feature']].append(r)
    global_mse=risks(cal,allowed)
    prefixes=[0]
    s=0
    for j in ORDER:
        s|=1<<j
        if s in allowed:prefixes.append(s)
    policy={'NONE':{'*':0},
            'SIGNIFICANCE_PREFIX_GLOBAL':{'*':choose(global_mse,prefixes,d,lmb)},
            'SIGNIFICANCE_PREFIX_CONTEXT':{},
            'FIXED_ANY_GLOBAL':{'*':choose(global_mse,allowed,d,lmb)},
            'INDEPENDENT_MOMENT_CONTEXT':{},
            'INDIVIDUAL_SCORE_CONTEXT':{},
            'JOINT_MOMENT_CONTEXT':{}}
    for feature,rows in sorted(by.items()):
        if len(rows)<min_cal:
            raise ValueError('Too few CAL cases for runtime feature '+feature)
        joint=risks(rows,allowed)
        mu,var=moments(rows)
        diag={s:diag_risk(s,mu,var) for s in allowed}
        policy['SIGNIFICANCE_PREFIX_CONTEXT'][feature]=choose(joint,prefixes,d,lmb)
        policy['INDEPENDENT_MOMENT_CONTEXT'][feature]=choose(diag,allowed,d,lmb)
        score=sorted(range(4),key=lambda j:(-C[j]**2*(var[j]+mu[j]**2),j))
        greedy=0
        for j in score:
            if cost(greedy|(1<<j),d)<=b:greedy|=1<<j
        policy['INDIVIDUAL_SCORE_CONTEXT'][feature]=(greedy if diag[greedy]+
             lmb*cost(greedy,d)<diag[0] else 0)
        policy['JOINT_MOMENT_CONTEXT'][feature]=choose(joint,allowed,d,lmb)
    return policy

def evaluate(cal,dev,d,b,min_cal,lmb):
    if not cal or not dev:raise ValueError('Need CAL and held-out DEV')
    if {r['feature'] for r in dev}-{r['feature'] for r in cal}:
        raise ValueError('Unseen DEV feature: no calibrated runtime selection')
    policies=fit(cal,d,b,min_cal,lmb)
    results={}
    for name,rule in policies.items():
        errors=[]
        spent=[]
        for r in dev:
            s=rule.get(r['feature'],rule.get('*'))
            if s is None:raise ValueError('No fitted subset for a DEV feature')
            errors.append(residual(r['e'],s))
            spent.append(cost(s,d))
        n=len(dev)
        results[name]={'mse':sum(x*x for x in errors)/n,
                       'mae':sum(abs(x) for x in errors)/n,
                       'nonzero_fraction':sum(x!=0 for x in errors)/n,
                       'mean_cost_abstract':sum(spent)/n,
                       'subsets':{key:bits(val) for key,val in rule.items()}}
    allowed=candidates(d,b)
    oracles=[min(allowed,key=lambda s:(residual(r['e'],s)**2,cost(s,d),s))
             for r in dev]
    results['ORACLE_DEV_ERRORS_UNDEPLOYABLE']={
        'mse':sum(residual(r['e'],s)**2 for r,s in zip(dev,oracles))/len(dev),
        'mean_cost_abstract':sum(cost(s,d) for s in oracles)/len(dev)}
    return results

def demo(n,seed):
    rng=random.Random(seed)
    cal=[]
    dev=[]
    for split in ('CAL','DEV'):
        for feature,vec in (('A_COHERENT_CANCELLING',(-1,1,1,1)),
                            ('B_COHERENT_REINFORCING',(1,1,1,-1))):
            for i in range(n):
                sign=rng.choice((-1,1))
                r={'split':split,'feature':feature,'chip_id':split+'_'+str(i),
                   'e':tuple(sign*v for v in vec)}
                (cal if split=='CAL' else dev).append(r)
    return cal,dev

def read_csv(path):
    cal=[]
    dev=[]
    chips=defaultdict(set)
    with open(str(path),newline='') as f:
        reader=csv.DictReader(f)
        if not {'split','feature','chip_id','e0','e1','e2','e3'}.issubset(set(reader.fieldnames or [])):
            raise ValueError('CSV columns: split,feature,chip_id,e0,e1,e2,e3')
        for row in reader:
            split=row['split'].upper()
            if split not in ('CAL','DEV'):raise ValueError('CAL/DEV split required')
            if not row['feature'] or not row['chip_id']:
                raise ValueError('Unobservable feature or missing chip ID')
            e=tuple(int(row['e'+str(i)]) for i in range(4))
            if any(abs(v)>32 for v in e):raise ValueError('Decoded count error >32')
            item={'feature':row['feature'],'chip_id':row['chip_id'],'e':e}
            chips[split].add(row['chip_id'])
            (cal if split=='CAL' else dev).append(item)
    if chips['CAL'] & chips['DEV']:
        raise ValueError('CAL/DEV chip IDs overlap: not a new-chip holdout')
    return cal,dev

def digest(path):
    h=hashlib.sha256()
    with open(str(path),'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def selftest():
    cal,dev=demo(50,13)
    r=evaluate(cal,dev,(1,1,1,1),1,10,0)
    a='A_COHERENT_CANCELLING'
    b='B_COHERENT_REINFORCING'
    assert r['JOINT_MOMENT_CONTEXT']['subsets']=={a:[0],b:[3]}
    assert r['SIGNIFICANCE_PREFIX_CONTEXT']['subsets']=={a:[],b:[3]}
    assert r['JOINT_MOMENT_CONTEXT']['mse']==26.5
    assert r['SIGNIFICANCE_PREFIX_CONTEXT']['mse']==29.0
    assert r['FIXED_ANY_GLOBAL']['mse']==37.0
    rp=evaluate(cal,dev,(1,1,1,1),1,10,5.0)
    assert rp['JOINT_MOMENT_CONTEXT']['mse']==29.0
    assert rp['JOINT_MOMENT_CONTEXT']['mean_cost_abstract']==0.5
    print('E29A_SELFTEST_PASS: 16 subsets, strong contextual prefix, covariance-sensitive recovery')
    print('E29A_SELFTEST_SYNTHETIC_ONLY_NOT_GF_NOT_PEX')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('selftest','demo','evaluate'))
    p.add_argument('--csv',type=Path)
    p.add_argument('--attestation',type=Path)
    p.add_argument('--budget',type=int,default=1)
    p.add_argument('--costs',default='1,1,1,1')
    p.add_argument('--cost-penalty',type=float,default=0.0)
    p.add_argument('--min-cal',type=int,default=10)
    p.add_argument('--n-per-regime',type=int,default=1000)
    p.add_argument('--seed',type=int,default=20261105)
    p.add_argument('--out',type=Path)
    args=p.parse_args()
    selftest()
    if args.mode=='selftest':return
    d=tuple(int(v) for v in args.costs.split(','))
    if len(d)!=4 or any(v<=0 for v in d) or args.budget<0 or \
       not math.isfinite(args.cost_penalty) or args.cost_penalty<0:
        raise ValueError('Need four positive abstract costs, budget>=0, penalty>=0')
    if args.mode=='demo':
        cal,dev=demo(args.n_per_regime,args.seed)
        evidence='SYNTHETIC_COVARIANCE_COUNTEREXAMPLE_NOT_PHYSICAL'
        provenance={'generated_seed':args.seed}
    else:
        if not args.csv or not args.attestation:
            raise ValueError('evaluate needs --csv and --attestation')
        att=json.loads(args.attestation.read_text())
        if (att.get('evidence_tier')!='physically_extracted_1T1MTJ_joint' or
            not att.get('joint_planes_from_matched_reads') or
            not att.get('runtime_features_provenance') or
            not att.get('exact_recompute_path')):
            raise ValueError('Attestation must establish actual joint 1T1 PEX, runtime feature and recompute path')
        cal,dev=read_csv(args.csv)
        evidence='STUDENT_ATTESTED_PHYSICAL_NOT_INDEPENDENTLY_VERIFIED'
        provenance={'CSV_sha256':digest(args.csv),'attestation':att}
    r=evaluate(cal,dev,d,args.budget,args.min_cal,args.cost_penalty)
    print('E29A_EVIDENCE',evidence)
    for name,row in r.items():
        print('E29A_POLICY',name,'DEV_MSE',row['mse'],
              'COST',row['mean_cost_abstract'],'SUBSETS',row.get('subsets',{}))
    if args.out:
        path=args.out.expanduser()
        if path.exists():raise ValueError('Will not overwrite '+str(path))
        path.parent.mkdir(parents=True,exist_ok=True)
        obj={'evidence':evidence,'provenance':provenance,
             'costs':d,'budget':args.budget,'cost_penalty':args.cost_penalty,
             'CAL':len(cal),'DEV':len(dev),'results':r,
             'metric':'four-plane signed reconstruction residual MSE',
             'warning':'Not full MNIST inference; cost abstract; actual joint 1T1 errors unverified'}
        path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
        print('E29A_REPORT',path)
    print('E29A_NO_PHYSICAL_NOVELTY_OR_INFERENCE_CLAIM')

if __name__=='__main__':
    main()
