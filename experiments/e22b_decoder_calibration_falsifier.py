#!/usr/bin/env python3
"""E22B: strong CAL-only ADC-calibration controls on saved NUS E22 currents.
Python 3.6; NO new Spectre; NO PEX; mathematical ADC only.
"""
from __future__ import print_function
import argparse
import collections
import hashlib
import json
from pathlib import Path
import e22_gf_precision_regime as e22

BITS=(4,5,6,7)
NS=range(17)

def mean(a):
    return sum(a)/float(len(a))

def centroid(cal):
    return [mean([x['I'] for x in cal if x['n']==n]) for n in NS]

def best(I,levels):
    return min(NS,key=lambda n:(abs(I-levels[n]),n))

def nearfit(cal):
    mu=centroid(cal)
    xmean=[mean([x['near'] for x in cal if x['n']==n]) for n in NS]
    denom=sum((x['near']-xmean[x['n']])**2 for x in cal)
    numer=sum((x['near']-xmean[x['n']])*(x['I']-mu[x['n']]) for x in cal)
    slope=numer/denom if denom else 0.
    xm=mean([x['near'] for x in cal])
    corrected=[mean([x['I']-slope*(x['near']-xm)
                     for x in cal if x['n']==n]) for n in NS]
    return slope,xm,corrected

def codebook(cal,b,win):
    hist=collections.defaultdict(collections.Counter)
    for x in cal:
        hist[e22.ADC(x['I'],b,*win)][x['n']]+=1
    keys=sorted(hist)
    mapping={c:min(NS,key=lambda n:(-hist[c][n],n)) for c in keys}
    # No DEV labels are used. Unobserved codes use nearest CAL-populated code.
    return keys,mapping

def read_code(code,book):
    keys,mapping=book
    k=min(keys,key=lambda j:(abs(code-j),j))
    return mapping[k]

def score(dev,decode):
    wrong=0
    mae=0
    for x in dev:
        y=decode(x)
        wrong+=(y!=x['n'])
        mae+=abs(y-x['n'])
    return {'errors':wrong,'total':len(dev),'MAE':mae/float(len(dev))}

def check_adjacent(dev,pol):
    y={n:[pol(x) for x in dev if x['n']==n] for n in NS}
    orient=1 if mean(y[16])>mean(y[0]) else -1
    # True current-level ordering if a single monotone ADC threshold is used.
    gaps=[min(orient*v for v in y[n+1])-max(orient*v for v in y[n])
          for n in range(16)]
    return {'nonseparable_sampled_count_boundaries':sum(g<=0 for g in gaps),
            'min_adjacent_gap_A':min(gaps),'all_signed_gaps_A':gaps}

def analysis(data):
    if data.get('status')!='FINISHED' or data.get('GF_PEX') is not False:
        raise ValueError('Expected completed nominal GF E22 output')
    rows=e22.nmap(data)
    ref,low,high=e22.calibrate(rows)
    zero={x['id']:(x['n'],x['split']) for x in rows[0.]}
    report={'evidence':'REANALYSIS_OF_ACTUAL_E22_USER_GF_CURRENTS',
            'wire_r_assumed':True,'adc_simulated_with_real_transistors':False,
            'no_new_spectre':True,'nominal_ADC_window_A':[low,high],'results':{}}
    for R in sorted(rows):
        items=rows[R]
        if {x['id']:(x['n'],x['split']) for x in items}!=zero:
            raise ValueError('Unpaired masks or split across R')
        cal=[x for x in items if x['split']=='CAL']
        dev=[x for x in items if x['split']=='DEV']
        if any(sum(x['n']==n for x in cal)<3 for n in NS):
            raise ValueError('Insufficient CAL per count')
        mu=centroid(cal)
        slope,xm,mu_corr=nearfit(cal)
        # Frozen nominal window uses the identical range at every R.
        frozen=(low,high)
        v=[x['I'] for x in cal]
        vlow=min(v);vhigh=max(v)
        if not vhigh>vlow: raise ValueError('Flat CAL range')
        window=(vlow-.05*(vhigh-vlow),vhigh+.05*(vhigh-vlow))
        pol={'cal_perR_continuous':score(dev,lambda x:best(x['I'],mu)),
             'cal_perR_continuous_near':score(dev,lambda x:best(
                 x['I']-slope*(x['near']-xm),mu_corr)),
             'nominal_continuous':score(dev,lambda x:best(x['I'],ref))}
        for b in BITS:
            # Exact original E22 decoder. This MUST reproduce its raw error.
            pol['frozen_r0_b%d'%b]=score(dev,lambda x: e22.predict(
                x['I'],ref,b,low,high))
            for name,w in [('fixed',frozen),('reprogrammed',window)]:
                book=codebook(cal,b,w)
                pol[name+'_CAL_lookup_b%d'%b]=score(dev,lambda x:
                    read_code(e22.ADC(x['I'],b,*w),book))
                # Correction is DIGITAL after ADC; only ADC code center is used,
                # never the hidden pre-ADC DEV current.
                pol[name+'_CAL_near_b%d'%b]=score(dev,lambda x:best(
                    w[0]+(e22.ADC(x['I'],b,*w)+.5)*(w[1]-w[0])/(1<<b)
                    -slope*(x['near']-xm),mu_corr))
        r={'cal_n':len(cal),'dev_n':len(dev),'perR_CAL_ADC_window_A':window,
           'CAL_near_slope_A':slope,
           'fixed_window_DEV_outside':sum(x['I']<low or x['I']>=high for x in dev),
           'reprogrammed_window_DEV_outside':sum(x['I']<window[0] or x['I']>=window[1] for x in dev),
           'dev_raw_adjacent':check_adjacent(dev,lambda x:x['I']),
           'dev_near_adjacent':check_adjacent(dev,lambda x:
               x['I']-slope*(x['near']-xm)),
           'policies':pol}
        report['results']['R%g'%R]=r
        print('E22B R=%g CAL=%d DEV=%d ADC_OUTSIDE fixed=%d adaptive=%d'%(
              R,len(cal),len(dev),r['fixed_window_DEV_outside'],
              r['reprogrammed_window_DEV_outside']))
        print('  ADJACENT_NONSEPARABLE raw=%d near=%d'%(
              r['dev_raw_adjacent']['nonseparable_sampled_count_boundaries'],
              r['dev_near_adjacent']['nonseparable_sampled_count_boundaries']))
        print('  CONTINUOUS nominal=%d CAL_perR=%d CAL_near=%d'%(
              pol['nominal_continuous']['errors'],pol['cal_perR_continuous']['errors'],
              pol['cal_perR_continuous_near']['errors']))
        for name in ('frozen_r0','fixed_CAL_lookup','reprogrammed_CAL_lookup',
                     'fixed_CAL_near','reprogrammed_CAL_near'):
            print('  %-25s '%name+' '.join('b%d=%d/%d'%(b,pol[name+'_b%d'%b]['errors'],len(dev))
                    for b in BITS))
    report['limitations']=[
        'A calibrated CODE->COUNT LUT has 17 class labels and only 6 CAL patterns per class.',
        'Reprogramming the ADC range requires extra reference circuitry and cost, not included.',
        'Digital near correction applies after ADC; it cannot recover a saturated raw ADC code.',
        'Observed DEV class interval overlap prevents a perfect single ordered threshold but is not a population BER.',
        'All R values are assumptions, not extracted GF parasitics.',
        'No process/mismatch, ADC energy, full-network inference or publication novelty established.']
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',nargs='?')
    p.add_argument('--out')
    p.add_argument('--selftest',action='store_true')
    a=p.parse_args()
    if a.selftest:
        assert e22.ADC(0.25,2,0,1)==1
        assert read_code(8,([1,5,10],{1:0,5:7,10:16}))==16
        assert best(2.1,[float(n) for n in NS])==2
        print('E22B_SELFTEST_PASS: ADC, CAL lookup, count classifier; mock only')
        return
    if not a.source or not a.out:p.error('Provide e22_results.json and --out')
    path=Path(a.source).expanduser()
    target=Path(a.out).expanduser()
    if target.exists():p.error('Refuses overwrite existing '+str(target))
    if not path.is_file():p.error('No input '+str(path))
    raw=path.read_bytes()
    report=analysis(json.loads(raw.decode('utf-8')))
    report['input_SHA256']=hashlib.sha256(raw).hexdigest()
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('E22B_REPORT',target)
    print('NO_SPECTRE. ASSUMED_WIRE_R. MATHEMATICAL_ADC. CAL_ONLY_FIT.')

if __name__=='__main__':main()
