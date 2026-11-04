#!/usr/bin/env python3
"""Audit Bernoulli diagonal in E22's independence ablation. Software only.

Matches E22's 32-shunt passive kernel and two global CAL-fitted features.
Uses frozen legacy maps for reproduction and matched deterministic seven-swap
optimizers for corrected independence versus measured coactivation. No GF.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,zipfile
import numpy as np
import postcal_mapping_audit_v3 as common

LEGACY_SHA='a6a93bdf0f912a8b3961626c06f6452e1919b9fbda5100688534a8a6c0e43561'
GAP=36.704e-6

def moment_check():
    p=np.array([.1,.35,.55,.8,.9]);g=np.array([1.,2.,1.,2.,2.]);K=np.minimum.outer(np.arange(1,6),np.arange(1,6))
    exact=0.
    for pattern in itertools.product([0,1],repeat=5):
        x=np.array(pattern);prob=np.prod(np.where(x,p,1-p));a=x*g
        exact+=prob*np.sum(np.cumsum(a[::-1])**2)
    old=np.outer(p,p);correct=old.copy();np.fill_diagonal(correct,p)
    formula=float(np.sum(correct*np.outer(g,g)*K))
    wrong=float(np.sum(old*np.outer(g,g)*K))
    missing=float(np.sum(np.arange(1,6)*p*(1-p)*g*g))
    np.testing.assert_allclose(exact,formula,atol=1e-12)
    np.testing.assert_allclose(exact-wrong,missing,atol=1e-12)
    return {'independent_Bernoulli_all_32_patterns':'PASS','enumerated_expected_Q':exact,'correct_formula_Q':formula,'legacy_formula_Q':wrong,'missing_diagonal_term':missing}

def make_maps(xcal,w,base):
    policies={k:base.copy() for k in ['joint_sort','matched_CAMP_light','correct_independent_light','correct_independent_full','legacy_incorrect_independent_light']}
    g=1+w.astype(float)
    for group in range(8):
        sl=slice(group*32,(group+1)*32);ix=base[sl]
        a=xcal[:,ix].astype(float);p=a.mean(0);gg=g[ix]
        mean=gg.mean(1);prod=gg@gg.T/gg.shape[1]
        C=a.T@a/len(a);ind=np.outer(p,p);np.fill_diagonal(ind,p)
        choices={'joint_sort':np.argsort(-(p*mean),kind='stable'),
                 'matched_CAMP_light':common.greedy_pair_order(C*np.outer(mean,mean)),
                 'correct_independent_light':common.greedy_pair_order(ind*np.outer(mean,mean)),
                 'correct_independent_full':common.greedy_pair_order(ind*prod),
                 'legacy_incorrect_independent_light':common.greedy_pair_order(np.outer(p*mean,p*mean))}
        for k,q in choices.items():policies[k][sl]=ix[q]
    return policies

def prepare(x,w,order,r):
    out=[]
    for group in range(8):
        ix=order[group*32:(group+1)*32]
        a=x[:,ix].astype(float);bits=w[ix].astype(float)
        m=a.sum(1);n=a@bits;k=bits.sum(0)
        shunts=a[:,:,None]*(GAP*(1+bits))[None,:,:]
        y=np.zeros(n.shape)
        for j in range(31,-1,-1):y=shunts[:,j,:]+y/(1+r*y)
        sensed=y/(1+r*y)
        droop=sensed/GAP-m[:,None]-n
        z=np.stack([m,a@np.arange(1,33)],axis=1)
        lo=np.maximum(0,m[:,None]+k[None,:]-32);hi=np.minimum(m[:,None],k[None,:])
        out.append({'n':n,'m':m,'z':z,'droop':droop,'lo':lo,'hi':hi})
    return out

def calibrate(parts):
    A=np.concatenate([np.broadcast_to(p['z'][:,None,:],p['n'].shape+(2,)).reshape(-1,2) for p in parts])
    y=np.concatenate([p['droop'].ravel() for p in parts])
    return np.linalg.lstsq(A,y,rcond=None)[0]

def score(parts,beta,d,labels):
    errs=[]
    for p in parts:
        residual=p['droop']-(p['z']@beta)[:,None]
        decoded=np.clip(np.floor(p['n']+residual+.5),p['lo'],p['hi'])
        errs.append(decoded-p['n'])
    err=np.stack(errs,axis=1)
    chans=np.unique(d['output_channels'])
    bybit=np.stack([np.sum(err[:,:,d['output_channels']==c]*d['coefficients'][d['output_channels']==c],axis=(1,2)) for c in chans],axis=1)
    pid,ab=labels
    full=np.stack([np.sum(bybit[pid==p]*(2.**ab[pid==p,None]),axis=0) for p in np.unique(pid)])
    parent=np.mean(full**2,axis=1)
    return {'block_MSE':float(parent.mean()),'wrong_integer_counts':int(np.count_nonzero(err)),
            'nonempty_vector_reads':int(sum(np.count_nonzero(p['m']) for p in parts)),
            'parent_squared_error':parent.tolist()}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--packet',type=Path,required=True);ap.add_argument('--legacy-package',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():ap.error('Non-overwriting output path required')
    if hashlib.sha256(a.legacy_package.read_bytes()).hexdigest()!=LEGACY_SHA:raise ValueError('Legacy package hash')
    with zipfile.ZipFile(a.legacy_package) as z:
        legacy=json.loads(z.read('e22b_pairwise_ablation_results.json'))
        old_exact=json.loads(z.read('e22d_exact_kcl_results.json'))
    d,splits,meta,ids=common.read_packet(a.packet)
    xc=np.concatenate([splits['fit'],splits['search']],axis=0);xd=splits['dev']
    lc=tuple(np.concatenate([d['split_labels']['fit'][i],d['split_labels']['search'][i]]) for i in range(2));ld=d['split_labels']['dev']
    checks=moment_check();records=[];comparisons=[];rng=np.random.default_rng(2026110422)
    for grouping in ['zero_rate_sorted','car_alpha_0','original']:
        def frozen(policy):
            chosen=[j for j in legacy['records'] if j['baseline']==grouping and j['policy']==policy and j['r']==5 and j['calibration']=='centroid']
            if len(chosen)!=1:raise ValueError('Legacy map not uniquely identified')
            return np.asarray(chosen[0]['order'],dtype=np.int64)
        base=frozen('original_order')
        maps={'frozen_E22_joint_sort':frozen('conductance_sort'),'frozen_E22_CAMP_light':frozen('coactivation_only')}
        maps.update(make_maps(xc,d['W'],base))
        for r in [0.,5.]:
            scored={}
            for name,order in maps.items():
                for group in range(8):np.testing.assert_array_equal(np.sort(order[group*32:(group+1)*32]),np.sort(base[group*32:(group+1)*32]))
                pc=prepare(xc,d['W'],order,r);pd=prepare(xd,d['W'],order,r)
                beta=calibrate(pc);met=score(pd,beta,d,ld);scored[name]=met
                if r==0 and met['wrong_integer_counts']!=0:raise AssertionError('R0 count null')
                if r==5 and name in ['frozen_E22_joint_sort','frozen_E22_CAMP_light']:
                    legacy_name={'frozen_E22_joint_sort':'conductance_sort','frozen_E22_CAMP_light':'coactivation_only'}[name]
                    target=[j for j in old_exact['results'] if j['baseline']==grouping and j['method']==legacy_name][0]
                    np.testing.assert_allclose(met['block_MSE'],target['dev_MSE'],atol=0,rtol=0)
                    assert met['wrong_integer_counts']==target['dev_wrong_counts']
                records.append({'grouping':grouping,'r_assumed_ohm':r,'method':name,'CAL_beta':beta.tolist(),'DEV':met,'order':order.tolist()})
                print(grouping,'R',r,name,'MSE',round(met['block_MSE'],6),'wrong',met['wrong_integer_counts'],flush=True)
            if r==5:
                for baseline in ['joint_sort','correct_independent_light','correct_independent_full']:
                    old=np.array(scored[baseline]['parent_squared_error']);new=np.array(scored['matched_CAMP_light']['parent_squared_error']);delta=old-new
                    bi=rng.integers(0,len(delta),(5000,len(delta)))
                    comparisons.append({'grouping':grouping,'baseline':baseline,'candidate':'matched_CAMP_light','baseline_MSE':float(old.mean()),'candidate_MSE':float(new.mean()),'gain_pct':float(100*delta.mean()/old.mean()),'absolute_improvement':float(delta.mean()),'paired_parent_percentile_95pct':np.percentile(delta[bi].mean(1),[2.5,97.5]).tolist()})
    checks['frozen_E22D_all_six_MSE_and_count_reproductions']='PASS'
    checks['R0_null_all_21_mapping_grouping_arms']='PASS'
    out={'evidence':'real frozen MNIST traces and constructed 32-shunt passive network; NOT GF, PEX, ADC hardware, full layer, inference or novelty','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'common_source_sha256':hashlib.sha256(Path(common.__file__).read_bytes()).hexdigest(),'packet_sha256':common.EXPECTED_PACKET,'legacy_package_sha256':LEGACY_SHA,'settings':{'CAL_parents':128,'previously_inspected_DEV_parents':256,'outputs':8,'FC1_rows_used':256,'parallel_rows_assumed':32,'gAP_S':GAP,'gP_S':2*GAP,'r_assumed_ohm':[0,5],'finite_ADC':False,'calibration':'same two global coefficients on m and activation centroid, fitted on all CAL for each map; legal count clamping','pair_swaps':7,'independence_diagonal':'p_i, not p_i^2','bootstrap':'5000 paired parent resamples; exploratory, DEV previously inspected; seed 2026110422'},'checks':checks,'comparisons':comparisons,'records':records}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print('CHECKS',json.dumps(checks),flush=True)
    print('COMPARISONS',json.dumps(comparisons),flush=True)

if __name__=='__main__':main()
