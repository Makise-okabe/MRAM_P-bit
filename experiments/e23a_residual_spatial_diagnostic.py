#!/usr/bin/env python3
"""E23A: CAL-only residual spatial diagnostic on saved E22 NUS GF currents.

Not novel as implemented. Assumed wire R, GF NFET + student MTJ DC currents,
no ADC hardware/PEX/energy. Seven-bit ideal ADC + CAL-derived per-R window.
17 count centroids plus parsimonious position features. All fitted on CAL.
Existing DEV was previously inspected: exploratory development evidence.
Python 3.6 stdlib; imports e22_gf_precision_regime.py from same directory.
"""
from __future__ import print_function
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import e22_gf_precision_regime as e22

BITS=7
MODELS=(
 ('perR_centroids',()),
 ('near',('near',)),
 ('centroid',('centroid',)),
 ('suffixQ',('q',)),
 ('near_centroid',('near','centroid')),
 ('near_suffixQ',('near','q')),
 ('near_suffixQ_ninteraction',('near','q','nq')),
)

def spatial_features(p):
    active=sorted(int(i) for i in p['active_rows_0based'])
    if len(active)!=16 or len(set(active))!=16 or any(i<0 or i>=32 for i in active):
        raise ValueError('Unexpected E22 input mask')
    active_set=set(active)
    suffix=0; q=0
    for j in range(31,-1,-1):
        if j in active_set: suffix+=1
        q+=suffix*suffix
    return {'near':float(sum(i<16 for i in active)),
            'centroid':float(sum(i+1 for i in active)),
            'q':float(q)}

def feature(row,name,hypothesis_n):
    # IMPORTANT: the n-dependent interaction is evaluated for EACH hypothesis,
    # never computed using the unknown true DEV count.
    if name=='nq':
        return (hypothesis_n-8.)/8. * row['feat']['q']
    return row['feat'][name]

def validated(data):
    if data.get('status')!='FINISHED' or data.get('GF_PEX') is not False:
        raise ValueError('Need finished non-PEX E22 source')
    rows=e22.nmap(data)
    profiles={int(p['id']):p for p in data['profiles']}
    if len(profiles)!=len(data['profiles']): raise ValueError('Duplicate profile IDs')
    features={i:spatial_features(p) for i,p in profiles.items()}
    if 0. not in rows: raise ValueError('Missing R0')
    reference={x['id']:(x['n'],x['split']) for x in rows[0.]}
    for r,part in rows.items():
        if {x['id']:(x['n'],x['split']) for x in part}!=reference:
            raise ValueError('Unpaired source masks at R='+str(r))
        for x in part: x['feat']=features[x['id']]
        for split,mincount in (('CAL',6),('DEV',12)):
            for n in range(17):
                if sum(x['split']==split and x['n']==n for x in part)<mincount:
                    raise ValueError('Not enough %s for count %d'%(split,n))
    return rows

def linear_solve(a,b):
    n=len(b)
    m=[list(row)+[b[i]] for i,row in enumerate(a)]
    for j in range(n):
        k=max(range(j,n),key=lambda t:abs(m[t][j]))
        if abs(m[k][j])<1e-13: raise ValueError('Rank-deficient normal equations')
        m[j],m[k]=m[k],m[j]
        d=m[j][j]
        for t in range(j,n+1):m[j][t]/=d
        for i in range(n):
            if i==j:continue
            d=m[i][j]
            for t in range(j,n+1):m[i][t]-=d*m[j][t]
    return [m[i][n] for i in range(n)]

def fit(cal,names):
    classes=sorted(set(x['n'] for x in cal))
    if classes!=list(range(17)):raise ValueError('Incomplete CAL count classes')
    mu={}; fmean={}
    for n in classes:
        group=[x for x in cal if x['n']==n]
        if len(group)<3: raise ValueError('Need at least 3 CAL/count')
        mu[n]=sum(x['I'] for x in group)/len(group)
        fmean[n]={name:sum(feature(x,name,n) for x in group)/len(group)
                  for name in names}
    scale=[]; coef=[]
    if names:
        for name in names:
            var=sum((feature(x,name,x['n'])-fmean[x['n']][name])**2
                    for x in cal)/len(cal)
            scale.append(math.sqrt(var))
        if any(s<1e-12 for s in scale):raise ValueError('CAL feature variance zero')
        xx=[[(feature(x,name,x['n'])-fmean[x['n']][name])/s
             for name,s in zip(names,scale)] for x in cal]
        yy=[(x['I']-mu[x['n']])*1e6 for x in cal]
        k=len(names)
        gram=[[sum(row[i]*row[j] for row in xx) for j in range(k)]
              for i in range(k)]
        rhs=[sum(row[i]*y for row,y in zip(xx,yy)) for i in range(k)]
        ridge=0. if k==1 else .05*len(cal)
        for i in range(k): gram[i][i]+=ridge
        coef=linear_solve(gram,rhs)
    current=[x['I'] for x in cal];span=max(current)-min(current)
    if span<=0:raise ValueError('Invalid CAL ADC range')
    return {'mu':mu,'fmean':fmean,'scale':scale,'coef_uA':coef,
            'names':names,'window':(min(current)-.05*span,
                                    max(current)+.05*span)}

def predict(row,model,bits):
    low,high=model['window']
    code=e22.ADC(row['I'],bits,low,high)
    sensed=low+(code+.5)*(high-low)/float(1<<bits)
    def distance(n):
        pred=model['mu'][n]*1e6
        for name,s,beta in zip(model['names'],model['scale'],model['coef_uA']):
            pred+=beta*(feature(row,name,n)-model['fmean'][n][name])/s
        return abs(pred-sensed*1e6)
    return min(range(17),key=lambda n:(distance(n),n))

def score(test,model,bits):
    lo,hi=model['window'];err_ids=[];mae=0.
    low_sat=high_sat=0
    by_count={n:0 for n in range(17)}
    for row in test:
        low_sat+=row['I']<lo;high_sat+=row['I']>=hi
        pred=predict(row,model,bits)
        mae+=abs(pred-row['n'])
        if pred!=row['n']:
            err_ids.append(row['id'])
            by_count[row['n']]+=1
    return {'wrong':len(err_ids),'total':len(test),'MAE':mae/len(test),
            'saturated_low':low_sat,'saturated_high':high_sat,
            'wrong_mask_ids':err_ids,'wrong_by_count':by_count}

def cv_splits(cal):
    by=collections.defaultdict(list)
    for row in sorted(cal,key=lambda x:x['id']):by[row['n']].append(row)
    # 3 folds: each 6-pattern count has 4 train / 2 validation.
    for k in range(3):
        train=[];validation=[]
        for n in range(17):
            for j,row in enumerate(by[n]):
                (validation if j%3==k else train).append(row)
        yield train,validation

def audit(path):
    raw=path.read_bytes()
    sets=validated(json.loads(raw.decode('utf-8')))
    report={'input_sha256':hashlib.sha256(raw).hexdigest(),'bit_width':BITS,
            'evidence':'REANALYSIS_OF_USER_NUS_GF_CURRENTS_ASSUMED_R_NON_PEX',
            'results':{},
            'limitations':['DEV is already development-inspected, not independent final holdout',
                           'Input-only feature moments; no true n used at inference',
                           'Only 6 CAL masks/count, ridge candidate may overfit',
                           'Programmable ADC range and 17 count references cost unmeasured',
                           'No new Spectre, no measured wire R, no PEX/ADC hardware or task accuracy']}
    for r,rows in sorted(sets.items()):
        cal=[x for x in rows if x['split']=='CAL']
        dev=[x for x in rows if x['split']=='DEV']
        summary={}
        for name,names in MODELS:
            cvs=[score(validation,fit(train,names),BITS)
                 for train,validation in cv_splits(cal)]
            cv_n=sum(s['total'] for s in cvs)
            cv_wrong=sum(s['wrong'] for s in cvs)
            cv_mae=sum(s['MAE']*s['total'] for s in cvs)/cv_n
            model=fit(cal,names)
            d=score(dev,model,BITS)
            summary[name]={'CAL_CV_wrong':cv_wrong,'CAL_CV_n':cv_n,
                           'CAL_CV_MAE':cv_mae,'DEV_development':d,
                           'CAL_coefs_uA_by_standardized_feature':
                               dict(zip(names,model['coef_uA'])),
                           'CAL_window_uA':[v*1e6 for v in model['window']]}
            print('E23A R=%g %-26s CAL_CV=%d/%d DEV=%d/%d MAE=%.4f SAT=%d'%(
                r,name,cv_wrong,cv_n,d['wrong'],d['total'],d['MAE'],
                d['saturated_low']+d['saturated_high']))
        base=summary['near'];candidate=summary['near_suffixQ_ninteraction']
        b=base['DEV_development'];c=candidate['DEV_development']
        summary['_preregistered_comparison']={
            'baseline_near_DEV_errors':b['wrong'],
            'candidate_near_Q_countinteraction_DEV_errors':c['wrong'],
            'near_wrong_candidate_right':
               len(set(b['wrong_mask_ids'])-set(c['wrong_mask_ids'])),
            'near_right_candidate_wrong':
               len(set(c['wrong_mask_ids'])-set(b['wrong_mask_ids'])),
            'candidate_CAL_CV_better':candidate['CAL_CV_wrong']<base['CAL_CV_wrong'],
            'candidate_DEV_relative_reduction_at_least_25pct':
               c['wrong']<=.75*b['wrong'] if b['wrong'] else False}
        report['results']['R%g'%r]=summary
    return report

def selftest():
    assert spatial_features({'active_rows_0based':list(range(16))})['near']==16
    assert spatial_features({'active_rows_0based':list(range(16,32))})['near']==0
    vals=linear_solve([[4.,1.],[1.,3.]],[9.,8.])
    assert all(abs(a-b)<1e-10 for a,b in zip(vals,[19./11.,23./11.]))
    assert e22.ADC(.25,2,0,1)==1
    t={'feat':{'q':500},'n':0}
    # Regression: count-interaction uses HYPOTHESIS n, not DEV true n.
    assert feature(t,'nq',0)==-500
    assert feature(t,'nq',16)==500
    print('E23A_SELFTEST_PASS: geometry, solver, count-hypothesis feature, ADC.')
    print('SELFTEST IS CONSTRUCTED DATA, NOT SPECTRE.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',nargs='?',type=Path)
    p.add_argument('--out',type=Path)
    p.add_argument('--selftest',action='store_true')
    args=p.parse_args()
    if args.selftest:selftest();return
    if not args.source or not args.out:p.error('Provide E22 JSON and unique --out')
    if not args.source.is_file():p.error('E22 input missing')
    if args.out.exists():p.error('Refusing overwrite')
    result=audit(args.source)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('E23A_OUTPUT',args.out)
    print('No novel algorithm claimed; no new Spectre; DEV is retrospective.')
if __name__=='__main__':
    main()
