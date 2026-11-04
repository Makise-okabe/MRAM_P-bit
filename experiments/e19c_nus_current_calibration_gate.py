#!/usr/bin/env python3
"""E19C: Postprocess NUS E19 per-mask DC currents; no simulator and no PDK access.
Compatible with Python 3.6.  No result is asserted until run on NUS E19 JSON.
Compares CAL mean-midpoint threshold, CAL-optimized threshold, and a CAL-only
ambiguity gate (defer undecided cases; does NOT magically correct them).
"""
from __future__ import print_function
import argparse
import json
import math
from pathlib import Path

def choose_best(cal, lo, hi):
    ordered=sorted(set(float(x['current_A']) for x in cal))
    if len(ordered)<2:
        raise ValueError('Need two distinct CAL current values')
    scale=max(abs(ordered[0]),abs(ordered[-1]),1e-12)
    eps=1e-7*scale
    cand=[ordered[0]-eps]+[(a+b)/2 for a,b in zip(ordered,ordered[1:])]+[ordered[-1]+eps]
    positive=1 if sum(x['current_A'] for x in cal if x['true_n']==hi) / sum(x['true_n']==hi for x in cal) > sum(x['current_A'] for x in cal if x['true_n']==lo) / sum(x['true_n']==lo for x in cal) else -1
    means=[sum(x['current_A'] for x in cal if x['true_n']==n)/sum(x['true_n']==n for x in cal) for n in (lo,hi)]
    mid=sum(means)/2
    def err(t):
        return sum((hi if positive*(x['current_A']-t)>0 else lo)!=x['true_n'] for x in cal)
    best=min(cand,key=lambda t:(err(t),abs(t-mid)))
    return best,positive,mid,err(best),err(mid)

def evaluate(rows, threshold,polarity,lo,hi,gate):
    out=[x for x in rows if x['split']=='DEV']
    decisions=[]
    for x in out:
        ambiguous=abs(x['current_A']-threshold)<=gate
        pred=hi if polarity*(x['current_A']-threshold)>0 else lo
        decisions.append({'correct':pred==x['true_n'],'defer':ambiguous})
    decided=[x for x in decisions if not x['defer']]
    return {'total':len(out),
            'deferred_count':len(decisions)-len(decided),
            'deferred_rate':(len(decisions)-len(decided))/float(len(decisions)),
            'automatically_decided':len(decided),
            'errors_among_auto_decisions':sum(not x['correct'] for x in decided),
            'errors_if_all_forced':sum(not x['correct'] for x in decisions),
            'no_rescue_modelled':True}

def audit(path):
    with path.open() as f: data=json.load(f)
    if data.get('run_state')!='FINISHED':
        raise ValueError('Reject incomplete run')
    out={}
    for r,entry in sorted(data['results'].items(),key=lambda v:float(v[1]['R_segment_assumed_ohm'])):
        rows=entry['per_case_currents']
        cal=[x for x in rows if x['split']=='CAL']
        dev=[x for x in rows if x['split']=='DEV']
        counts=sorted(set(x['true_n'] for x in rows))
        if len(counts)!=2 or counts[1]!=counts[0]+1:
            raise ValueError('Need adjacent count classes')
        lo,hi=counts
        if any(sum(x['split']==s and x['true_n']==n for x in rows)==0
               for s in ('CAL','DEV') for n in counts):
            raise ValueError('Missing a class in CAL or DEV')
        if len({x['mask_hash'] for x in rows})!=len(rows):
            raise ValueError('Duplicate mask hashes within this R')
        opt,pol,mid,cal_opt_err,cal_mid_err=choose_best(cal,lo,hi)
        baseline=evaluate(rows,mid,pol,lo,hi,0.)
        optimized=evaluate(rows,opt,pol,lo,hi,0.)
        distances=sorted(abs(x['current_A']-opt) for x in cal)
        # Require a quarter of CAL cases to be flagged, then use that fixed
        # gate on DEV. This is not a second measurement or a corrected count.
        target=int(math.ceil(.25*len(distances)))
        gate=distances[target-1] if target else 0.
        gated=evaluate(rows,opt,pol,lo,hi,gate)
        # Strict sampled range overlap: no ordered single threshold can
        # classify every sampled current correctly if low and high range overlap.
        dlow=[x['current_A'] for x in dev if x['true_n']==lo]
        dhigh=[x['current_A'] for x in dev if x['true_n']==hi]
        overlap=max(0.,min(max(dlow),max(dhigh))-max(min(dlow),min(dhigh)))
        out[r]={'assumed_R_ohm_per_segment':entry['R_segment_assumed_ohm'],
                'cal_samples':len(cal),'dev_samples':len(dev),
                'cal_midpoint_A':mid,'cal_optimized_threshold_A':opt,
                'cal_midpoint_errors':cal_mid_err,'cal_optimized_errors':cal_opt_err,
                'midpoint_dev':baseline,'cal_optimal_dev':optimized,
                'cal_gated_25pct_dev':gated,
                'dev_observed_current_range_overlap_A':overlap,
                'warning':'Optimized CAL threshold may overfit small CAL sample. Deferrals are UNRESOLVED, not corrected.'}
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('json_paths',nargs='+',type=Path)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():p.error('Refusing overwrite existing '+str(a.out))
    report={}
    for path in a.json_paths:
        if not path.is_file():
            p.error('Missing E19 results '+str(path))
        report[path.parent.name]=audit(path)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps({'evidence_class':'POSTPROCESSING_USER_NUS_CURRENTS_NO_NEW_SPECTRE', 'results':report},indent=2)+'\n')
    for name,by_r in report.items():
        print('RUN',name)
        for r,v in by_r.items():
            x=v['midpoint_dev']; y=v['cal_optimal_dev'];z=v['cal_gated_25pct_dev']
            print(' ',r,'DEV',x['total'],'MID_ERRORS',x['errors_if_all_forced'],
                  'CAL_OPT_ERRORS',y['errors_if_all_forced'],
                  'GATED_DEFER',z['deferred_count'],
                  'GATED_AUTO_ERRORS',z['errors_among_auto_decisions'],
                  'DEV_OVERLAP_A',format(v['dev_observed_current_range_overlap_A'],'.6g'))
    print('E19C_REPORT:',a.out)
    print('NO SECOND READ IMPLEMENTED. NO ACTUAL PEX OR ADC ENERGY MEASURED.')

if __name__=='__main__':main()
