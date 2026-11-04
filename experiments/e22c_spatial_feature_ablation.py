#!/usr/bin/env python3
"""E22C: CAL-only input-mask spatial-correction ablation on SAVED E22 GF currents.

Python 3.6 standard library, NO new Spectre, NO GF PEX, NO real ADC.
Each correction feature uses ONLY known input activation rows. True n labels
fit CAL class centroids and slopes; never used as DEV features or for tuning.
Assumed wire R and 17 classes at fixed m=k=16 inherited from E22.
"""
from __future__ import print_function
import argparse
import hashlib
import json
from pathlib import Path
import e22_gf_precision_regime as e22

FEATURES=('raw','near','centroid','suffixQ')
BITS=(0,4,5,6,7)

def features(p):
    active=tuple(sorted(int(j) for j in p['active_rows_0based']))
    rows=int(p.get('rows',32))
    if len(active)!=len(set(active)) or any(j<0 or j>=rows for j in active):
        raise ValueError('Invalid activation mask')
    near=sum(j<rows//2 for j in active)
    centroid=sum(j+1 for j in active)
    s=0; q=0; occupied=set(active)
    for j in range(rows-1,-1,-1):
        s+=(j in occupied)
        q+=s*s
    return {'raw':0.,'near':float(near),'centroid':float(centroid),
            'suffixQ':float(q)}

def avg(a):
    return sum(a)/float(len(a))

def fit(cal,f):
    group={n:[x for x in cal if x['n']==n] for n in range(17)}
    if any(len(group[n])<3 for n in group):
        raise ValueError('Insufficient CAL patterns/count')
    mean_i={n:avg([x['I'] for x in group[n]]) for n in group}
    mean_f={n:avg([x['f'][f] for x in group[n]]) for n in group}
    numer=sum((x['f'][f]-mean_f[x['n']])*
              (x['I']-mean_i[x['n']]) for x in cal)
    denom=sum((x['f'][f]-mean_f[x['n']])**2 for x in cal)
    slope=numer/denom if denom else 0.
    fmean=avg([x['f'][f] for x in cal])
    levels=[avg([x['I']-slope*(x['f'][f]-fmean)
                 for x in group[n]]) for n in range(17)]
    return (slope,fmean,levels)

def adjust(v,x,model,f):
    return v-model[0]*(x['f'][f]-model[1])

def classify(x,model,f,b,window):
    if b==0:
        v=x['I']
    else:
        c=e22.ADC(x['I'],b,*window)
        v=window[0]+(c+.5)*(window[1]-window[0])/(1<<b)
    return e22.predict(adjust(v,x,model,f),model[2],0,0.,1.)

def measure(dev,model,f,b,window):
    flags=[]; mae=0
    for x in dev:
        guess=classify(x,model,f,b,window)
        flags.append(int(guess!=x['n']))
        mae+=abs(guess-x['n'])
    return {'wrong':sum(flags),'total':len(dev),
            'count_MAE':mae/float(len(dev))},flags

def gaps(dev,model,f):
    states={n:[adjust(x['I'],x,model,f)
               for x in dev if x['n']==n] for n in range(17)}
    s=1. if model[2][16]>model[2][0] else -1.
    d=[min(s*v for v in states[n+1])-max(s*v for v in states[n])
       for n in range(16)]
    return {'num_nonseparable_adjacent':sum(g<=0 for g in d),
            'minimum_signed_gap_A':min(d)}

def analyze(data):
    if data.get('status')!='FINISHED' or data.get('GF_PEX') is not False:
        raise ValueError('Expected finished nominal GF E22, not full PEX')
    group=e22.nmap(data)
    profiles={int(p['id']):p for p in data['profiles']}
    if 0. not in group:raise ValueError('Missing R=0 control')
    identity={x['id']:(x['n'],x['split']) for x in group[0.]}
    report={}
    for R in sorted(group):
        if {x['id']:(x['n'],x['split']) for x in group[R]}!=identity:
            raise ValueError('Mismatched CAL/DEV mask identities across R')
        rows=[]
        for x in group[R]:
            p=dict(profiles[x['id']]);p['rows']=int(data['config']['rows'])
            if (p['true_n'],p['split'])!=(x['n'],x['split']):
                raise ValueError('Mismatched E22 mask metadata')
            rows.append(dict(x,f=features(p)))
        cal=[x for x in rows if x['split']=='CAL']
        dev=[x for x in rows if x['split']=='DEV']
        cur=[x['I'] for x in cal]
        span=max(cur)-min(cur)
        if span<=0:raise ValueError('Nonpositive CAL span')
        # Exact E22B hypothetical per-R programmable full-scale.
        window=(min(cur)-.05*span,max(cur)+.05*span)
        result={'CAL':len(cal),'DEV':len(dev),
                'R_segment_ohm_ASSUMED':R,'methods':{}}
        bits_error={}
        for f in FEATURES:
            model=fit(cal,f)
            entry={'CAL_slope_A_per_feature':model[0],
                   'DEV_adjacent_boundaries':gaps(dev,model,f),
                   'errors':{}}
            bits_error[f]={}
            for b in BITS:
                score,flags=measure(dev,model,f,b,window)
                entry['errors']['continuous' if b==0 else 'b%d'%b]=score
                bits_error[f][b]=flags
            result['methods'][f]=entry
        for f in ('centroid','suffixQ'):
            result['near_vs_'+f+'_b7_paired']={
                'near_wrong_candidate_right':sum(a and not b for a,b in
                    zip(bits_error['near'][7],bits_error[f][7])),
                'near_right_candidate_wrong':sum(b and not a for a,b in
                    zip(bits_error['near'][7],bits_error[f][7])),
                'both_wrong':sum(a and b for a,b in
                    zip(bits_error['near'][7],bits_error[f][7]))}
        report['R%g'%R]=result
        print('E22C R=%g CAL=%d DEV=%d ASSUMED R'%(R,len(cal),len(dev)))
        for f in FEATURES:
            entry=result['methods'][f]
            e=entry['errors']
            print(' %-9s continuous=%d 4bit=%d 5bit=%d 6bit=%d 7bit=%d '
                  'ADJ_NONSEP=%d slope_A=%.6g'%(f,e['continuous']['wrong'],
                    e['b4']['wrong'],e['b5']['wrong'],e['b6']['wrong'],
                    e['b7']['wrong'],entry['DEV_adjacent_boundaries']
                    ['num_nonseparable_adjacent'],entry['CAL_slope_A_per_feature']))
        for f in ('centroid','suffixQ'):
            z=result['near_vs_'+f+'_b7_paired']
            print('  b7 paired near vs %s: improves=%d worsens=%d bothwrong=%d'%(
                f,z['near_wrong_candidate_right'],
                z['near_right_candidate_wrong'],z['both_wrong']))
    return {'experiment':'E22C','results':report,
            'source':'NUS E22 existing GF hvtnfet+student static MTJ currents',
            'no_new_spectre':True,'all_line_resistances_assumed':True,
            'ADC_circuit_simulated':False,'full_PEX':False,
            'cautions':['CAL only slope/centroids/window per R; DEV scored independently',
                        'Only input spatial masks, no unknown n or weight overlap in features',
                        'Six CAL patterns per count; small validation sample',
                        'Per-R programmable ADC current range has hardware costs',
                        'Known IR-drop compensation is not a novelty claim']}

def selftest():
    x=features({'active_rows_0based':[0,2],'rows':4})
    assert x=={'raw':0.,'near':1.,'centroid':4.,'suffixQ':6.},x
    import random
    r=random.Random(17)
    rows=[]
    for split,num in (('CAL',6),('DEV',12)):
        for n in range(17):
            for _ in range(num):
                f=features({'active_rows_0based':r.sample(range(32),16),'rows':32})
                rows.append({'split':split,'n':n,'I':1e-5+n*5e-7-
                             1e-8*f['centroid'],'f':f})
    cal=[x for x in rows if x['split']=='CAL']
    dev=[x for x in rows if x['split']=='DEV']
    model=fit(cal,'centroid')
    assert measure(dev,model,'centroid',0,(0.,1.))[0]['wrong']==0
    print('E22C_SELFTEST_PASS: input position/Q, CAL-fit, held-out scoring; MOCK ONLY')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',nargs='?')
    p.add_argument('--out')
    p.add_argument('--selftest',action='store_true')
    a=p.parse_args()
    if a.selftest:selftest();return
    if not a.source or not a.out:p.error('Provide E22 raw results and --out')
    src=Path(a.source).expanduser()
    out=Path(a.out).expanduser()
    if not src.is_file():p.error('Missing input '+str(src))
    if out.exists():p.error('Refuses overwrite '+str(out))
    raw=src.read_bytes()
    result=analyze(json.loads(raw.decode('utf-8')))
    result['source_sha256']=hashlib.sha256(raw).hexdigest()
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('E22C_REPORT',out)
    print('NO_NEW_SPECTRE; NO_PEX; MATHEMATICAL_ADC; NO_NOVELTY_CERTIFICATION.')

if __name__=='__main__':main()
