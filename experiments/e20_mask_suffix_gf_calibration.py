#!/usr/bin/env python3
"""E20: Evaluate mask-only spatial current correction on existing NUS E19 files.

Features use ONLY the input activation mask (never hidden weight intersections).
True n labels are used to fit on CAL; held-out DEV labels are scored only.
This tests a standard IR-drop compensation mechanism, NOT novel hardware.
Python 3.6; no simulator or proprietary models accessed.
"""
from __future__ import print_function
import argparse
import hashlib
import json
from pathlib import Path

POLICIES=('raw','near_count','centroid','suffixQ')

def features(profile):
    m=int(profile['m'])
    active=[int(z) for z in profile['active_rows_0based']]
    size=int(profile.get('rows',32))
    if len(active)!=m or len(set(active))!=m or any(z<0 or z>=size for z in active):
        raise ValueError('Invalid activation mask')
    active_set=set(active)
    q=0; suffix=0
    for j in range(size-1,-1,-1):
        if j in active_set:
            suffix+=1
        q+=suffix*suffix
    return {'raw':0.,'near_count':float(sum(j<size//2 for j in active)),
            'centroid':float(sum(j+1 for j in active)), 'suffixQ':float(q)}

def fit(cal,policy):
    ns=sorted(set(r['n'] for r in cal))
    if len(ns)!=2:
        raise ValueError('Require exactly two count classes')
    groups={n:[r for r in cal if r['n']==n] for n in ns}
    if any(len(v)<2 for v in groups.values()):
        raise ValueError('Need at least two CAL readings per class')
    numer=0.; denom=0.
    for n,group in groups.items():
        mx=sum(r['feat'][policy] for r in group)/float(len(group))
        my=sum(r['current_A'] for r in group)/float(len(group))
        for r in group:
            dx=r['feat'][policy]-mx
            numer+=dx*(r['current_A']-my)
            denom+=dx*dx
    slope=(numer/(1.1*denom)) if denom>0 and policy!='raw' else 0.
    # The spatial load causes a downward, not upward, current effect.
    if policy in ('centroid','suffixQ'):
        slope=min(0.,slope)
    means={n:sum(r['current_A']-slope*r['feat'][policy] for r in group)/len(group)
           for n,group in groups.items()}
    positive=1 if means[ns[1]]>means[ns[0]] else -1
    return {'slope_A_per_feature':slope,'threshold_A':(means[ns[0]]+means[ns[1]])/2.,
            'polarity':positive,'labels':ns}

def evaluate(dev,params,policy):
    lo,hi=params['labels']; t=params['threshold_A']; sign=params['polarity']
    xs={lo:[],hi:[]}; errors=0
    for r in dev:
        adj=r['current_A']-params['slope_A_per_feature']*r['feat'][policy]
        xs[r['n']].append(adj)
        pred=hi if sign*(adj-t)>0 else lo
        errors+=(pred!=r['n'])
    overlap=max(0.,min(max(xs[lo]),max(xs[hi]))-
                   max(min(xs[lo]),min(xs[hi])))
    return {'dev_errors':errors,'dev_n':len(dev),
            'dev_error_pct':100.*errors/len(dev),'dev_adjusted_overlap_A':overlap}

def audit(path):
    d=json.loads(path.read_text())
    if d.get('run_state')!='FINISHED':
        raise ValueError('Cannot use unfinished E19 results')
    profiles={int(p['id']):p for p in d['profiles']}
    size=int(d['config']['rows'])
    out={}
    for key,part in sorted(d['results'].items(),key=lambda a:a[1]['R_segment_assumed_ohm']):
        allcases=[]
        for row in part['per_case_currents']:
            p=profiles[int(row['case_id'])]
            if row['mask_hash']!=p['mask_hash'] or row['true_n']!=p['true_n'] or row['split']!=p['split']:
                raise ValueError('E19 metadata and current mismatch')
            p=dict(p);p['rows']=size
            allcases.append({'n':p['true_n'],'split':p['split'],'current_A':float(row['current_A']),
                             'feat':features(p)})
        cal=[r for r in allcases if r['split']=='CAL']
        dev=[r for r in allcases if r['split']=='DEV']
        results={}
        for method in POLICIES:
            model=fit(cal,method)
            results[method]=dict(model,**evaluate(dev,model,method))
        out[key]={'R_segment_ASSUMED_ohm':part['R_segment_assumed_ohm'],
                  'CAL':len(cal),'DEV':len(dev),'methods':results}
    return out

def selftest():
    p={'m':2,'rows':4,'active_rows_0based':[0,2]}
    x=features(p)
    assert x['near_count']==1 and x['centroid']==4 and x['suffixQ']==6,x
    cases=[]
    for j in range(12):
        n=7+(j%2)
        cases.append({'n':n,'current_A':n*1e-6-2e-9*j,
                      'feat':{'raw':0.,'near_count':j%5,'centroid':float(2*j),'suffixQ':float(j)},
                      'split':'CAL' if j<8 else 'DEV'})
    for method in POLICIES:
        model=fit(cases[:8],method)
        assert evaluate(cases[8:],model,method)['dev_n']==4
    print('E20_SELFTEST_PASS: known-mask Q, CAL-only fit, independent DEV scoring; NOT Spectre')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('files',nargs='*',type=Path)
    ap.add_argument('--out',type=Path)
    ap.add_argument('--selftest',action='store_true')
    args=ap.parse_args()
    if args.selftest:
        selftest();return
    if not args.files or args.out is None:
        ap.error('Supply one or more E19 results.json and --out')
    if args.out.exists():
        ap.error('Refusing overwrite '+str(args.out))
    output={'evidence':'CAL_ONLY_POSITION_CALIBRATION_ON_E19_GF_NFET_USER_CURRENTS',
            'no_new_spectre':True,'wire_R_is_assumed':True,'results':{}}
    for path in args.files:
        if not path.is_file():
            ap.error('Missing '+str(path))
        report=audit(path)
        output['results'][path.parent.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                                             'per_R':report}
        print('E20_RUN',path.parent.name)
        for _,r in report.items():
            print(' R',r['R_segment_ASSUMED_ohm'],'CAL',r['CAL'],'DEV',r['DEV'])
            for m in POLICIES:
                z=r['methods'][m]
                print('   %-11s %d/%d (%.2f%%) overlap=%.6g uA slope=%.4g A/feature'%(
                    m,z['dev_errors'],z['dev_n'],z['dev_error_pct'],
                    z['dev_adjusted_overlap_A']*1e6,z['slope_A_per_feature']))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+'\n')
    print('E20_OUTPUT',args.out)
    print('WARNING: Any improvement is basic IR-drop correction, NOT new E15 ADC benefit.')
    print('GO/NO-GO: compare suffixQ to raw and centroid on both independently held-out E19 datasets.')

if __name__=='__main__':
    main()
