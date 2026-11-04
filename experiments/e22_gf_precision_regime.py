#!/usr/bin/env python3
"""E22: NUS GF access-NFET + static-MTJ full-count precision x line-R gate.

Python 3.6 standard library, no PDK export. Reuses the *existing verified*
e19_gf_nfet_mtj_nonideal_count_gate_v2.py in the same experiments directory.

RUN: 17 count classes n=0..16 at fixed m=k=16, 32 physical rows; independent
CAL and DEV patterns kept IDENTICAL across explicitly ASSUMED wire R sweeps.
ANALYZE: frozen CAL-R0 current transfer; compare quantizer bit depths on
the SAME DEV Spectre currents, including offset-only and near-half correction.
This does NOT model a physical ADC, comparator noise, PEX, device variation,
trained-network output or hardware energy. It is a nominated failure-regime
diagnostic. Never infer actual GF interconnect resistance from a chosen R.
"""
from __future__ import print_function
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time

try:
    import e19_gf_nfet_mtj_nonideal_count_gate_v2 as e19
except ImportError:
    sys.stderr.write('E22_ERROR: Missing verified E19 v2 alongside script. Run E19 patch helper first.\n')
    raise

def die(msg):
    raise SystemExit('E22_ERROR: '+str(msg))

def profiles_for_counts(args):
    rng=random.Random(args.seed)
    counts=list(range(17))
    out=[]; seen=set()
    for split in ('CAL','DEV'):
        reps=args.cal_per_count if split=='CAL' else args.dev_per_count
        for n in counts:
            for _ in range(reps):
                for attempt in range(30000):
                    active=tuple(sorted(rng.sample(range(32),16)))
                    inside=set(rng.sample(active,n))
                    unused=[i for i in range(32) if i not in active]
                    weights=tuple(sorted(inside | set(rng.sample(unused,16-n))))
                    pair=(active,weights)
                    if pair not in seen:
                        seen.add(pair);break
                else:die('Could not draw independent mask')
                out.append({'id':len(out),'split':split,'true_n':n,'m':16,'k':16,
                            'active_rows_0based':list(active),
                            'weight_P_rows_0based':list(weights),
                            'mask_hash':hashlib.sha256(repr(pair).encode('ascii')).hexdigest()[:16]})
    return out

def output_path(args):
    root=Path(args.private).expanduser().resolve()
    root.mkdir(parents=True,exist_ok=True)
    stamp=datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
    wd=root/('E22_GFCURRENT_'+stamp+'_'+str(os.getpid()))
    wd.mkdir(mode=0o700)
    return wd

def execute(args):
    if not shutil.which('spectre'):
        die('Cannot execute actual GF Spectre outside licensed NUS environment')
    if args.cal_per_count<3 or args.dev_per_count<3:
        die('Need at least 3 samples/count for each CAL/DEV')
    if not(1<=args.chunk_size<=80 and 0<args.vread<=.05 and 0<args.vwl<=.8):
        die('Unsupported chunk or historic voltage; consult existing E19 contract')
    rs=[float(v) for v in args.rs.split(',')]
    if not rs or 0. not in rs or len(set(rs))!=len(rs) or any(v<0 or v>50 for v in rs):
        die('Expected unique assumed nonnegative r values <=50 including 0')
    model=Path.home()/e19.MODEL_REL
    if not model.is_file() or e19.file_hash(model)!=e19.MODEL_SHA:
        die('Student MTJ model SHA check failed; do not substitute a different model')
    source=e19.choose_template(args.template)
    template=e19.parse_template(source)
    cases=profiles_for_counts(args)
    wd=output_path(args)
    header={'experiment':'E22_GF_NFET_FULL_COUNT_ADC_QUANTIZER_DIAGNOSTIC',
            'status':'INCOMPLETE','GF_PEX':False,'device_variation':False,
            'ADC_physically_implemented':False,'MTJ_dynamic':False,
            'R_segment_ASSUMED_ohm':rs,'vread_historical_V':args.vread,
            'vwl_historical_V':args.vwl,
            'template_SHA256':e19.file_hash(source),
            'student_model_SHA256':e19.MODEL_SHA,
            'source':'GF hvtnfet compact model + student static MTJ + assumed line resistors',
            'config':vars(args),'profiles':cases,'results':{}}
    (wd/'manifest.json').write_text(json.dumps(header,indent=2,default=str)+'\n')
    print('E22_WORKDIR',wd,flush=True)
    print('E22_CASES_PER_R',len(cases),'R',rs,flush=True)
    print('E22_COUNTS',list(range(17)),'CAL_PER_COUNT',args.cal_per_count,
          'DEV_PER_COUNT',args.dev_per_count,flush=True)
    for r in rs:
        readings=[]
        for offset in range(0,len(cases),args.chunk_size):
            chunk=cases[offset:offset+args.chunk_size]
            site=wd/('R%g_C%03d'%(r,offset//args.chunk_size))
            site.mkdir()
            deck=e19.make_deck(site,chunk,r,template,model,args)
            cmd=['spectre',str(deck),'+log',str(site/'spectre.log'),'-format','psfascii']
            start=time.time()
            try:
                with (site/'stdout.log').open('w') as f:
                    proc=subprocess.run(cmd,cwd=str(site),stdout=f,
                                        stderr=subprocess.STDOUT,timeout=args.timeout_sec)
                rc=proc.returncode
            except subprocess.TimeoutExpired:
                rc=124
            if rc:
                die('Spectre failure rc=%d at %s; inspect private log, no physical conclusion'%(rc,site))
            raw=e19.parse_sources(site/'input.raw/dcOp.dc')
            for p in chunk:
                key='VC%04d:p'%p['id']
                if key not in raw:die('Missing Spectre source '+key)
                readings.append({'case_id':p['id'],'split':p['split'],
                                 'true_n':p['true_n'],'mask_hash':p['mask_hash'],
                                 'current_A':raw[key]})
            print('E22_CHUNK_SUCCESS R=%g offset=%d cases=%d elapsed_s=%.2f'%(
                r,offset,len(chunk),time.time()-start),flush=True)
        if len(readings)!=len(cases):die('Incomplete currents')
        header['results']['R%g'%r]={'R_segment_assumed_ohm':r,
                                    'per_case_currents':readings}
        (wd/'partial.json').write_text(json.dumps(header,indent=2,default=str)+'\n')
        print('E22_R_COMPLETE',r,'num',len(readings),flush=True)
    header['status']='FINISHED'
    final=wd/'e22_results.json'
    final.write_text(json.dumps(header,indent=2,default=str)+'\n')
    print('E22_GF_RESULTS',final)
    print('E22_RUN_FINISHED: nominal GF NFET; assumed R, no PEX, ADC still offline.')
    print('NEXT: python3 experiments/e22_gf_precision_regime.py analyze '+str(final))

def nmap(data):
    profiles={int(p['id']):p for p in data['profiles']}
    result={}
    for key,source in data['results'].items():
        per=[]
        for r in source['per_case_currents']:
            p=profiles[int(r['case_id'])]
            if (r['split'],r['true_n'],r['mask_hash'])!=(
                    p['split'],p['true_n'],p['mask_hash']):
                die('Source profile or mask-hash mismatch')
            f=sum(j<16 for j in p['active_rows_0based'])
            per.append({'id':int(r['case_id']),'n':int(p['true_n']),
                        'split':p['split'],'I':float(r['current_A']),
                        'near':float(f)})
        result[float(source['R_segment_assumed_ohm'])]=per
    return result

def mean(vals):
    return sum(vals)/float(len(vals))

def calibrate(all_r):
    cal0=[x for x in all_r[0.] if x['split']=='CAL']
    levels=[mean([x['I'] for x in cal0 if x['n']==n]) for n in range(17)]
    inc=levels[-1]>levels[0]
    if not all((levels[i+1]>levels[i] if inc else levels[i+1]<levels[i])
               for i in range(16)):
        die('At R0, CAL count-level means not strictly monotone. Investigate netlist.')
    step=abs(levels[-1]-levels[0])/16.
    low=min(levels)-.5*step
    high=max(levels)+.5*step
    if high<=low:die('Invalid current window')
    return levels,low,high

def fit_corr(rows,ref):
    cal=[x for x in rows if x['split']=='CAL']
    reference=[x for x in ref if x['split']=='CAL']
    byn={n:[x for x in cal if x['n']==n] for n in range(17)}
    cent={n:mean([x['near'] for x in v]) for n,v in byn.items()}
    denom=sum((x['near']-cent[x['n']])**2 for x in cal)
    numer=sum((x['near']-cent[x['n']])*
              (x['I']-mean([z['I'] for z in byn[x['n']]])) for x in cal)
    slope=numer/denom if denom else 0.
    # Fit one single per-R offset after input-position correction.
    fm=mean([x['near'] for x in cal])
    refmean=mean([x['I'] for x in reference])
    rmean=mean([x['I']-slope*(x['near']-fm) for x in cal])
    offset=rmean-refmean
    return slope,fm,offset

def ADC(I,bit,low,high):
    units=1<<bit
    return min(units-1,max(0,int(math.floor((I-low)/(high-low)*units))))

def predict(I,levels,bit,low,high):
    if bit==0:
        return min(range(17),key=lambda n:(abs(levels[n]-I),n))
    code=ADC(I,bit,low,high)
    target=[ADC(t,bit,low,high) for t in levels]
    return min(range(17),key=lambda n:(abs(target[n]-code),n))

def evaluate(data):
    if data.get('status')!='FINISHED' or data.get('GF_PEX') is not False:
        die('Need finished nominal E22 results, not an arbitrary file')
    all_r=nmap(data)
    if 0. not in all_r:die('Need R0 CAL reference')
    levels,low,high=calibrate(all_r)
    ref=all_r[0.]
    rref={x['id']:x for x in ref}
    if any(len([x for x in ref if x['n']==n and x['split']==s])<3
           for n in range(17) for s in ('CAL','DEV')):
        die('Insufficient CAL/DEV counts for every n')
    output={'reference_ADC_window_A':[low,high],
            'reference_R0_CAL_mean_by_count_A':levels,
            'ADC_bits_tested':[4,5,6,7],
            'bit0_means_ideal_continuous_nearest_nominal_current':True,
            'results':{}}
    for r in sorted(all_r):
        rows=all_r[r]
        if {x['id'] for x in rows}!={x['id'] for x in ref}:
            die('R slices do not contain exactly same mask IDs')
        if any((x['n'],x['split'])!=(rref[x['id']]['n'],rref[x['id']]['split'])
               for x in rows):
            die('Not paired across R')
        slope,fmean,offset=fit_corr(rows,ref)
        errs={}
        dev=[x for x in rows if x['split']=='DEV']
        for b in (0,4,5,6,7):
            for policy in ('raw','offset_only','offset_near'):
                wrong=0; abs_err=0
                for x in dev:
                    s=x['I']
                    if policy!='raw':s-=offset
                    if policy=='offset_near':s-=slope*(x['near']-fmean)
                    guess=predict(s,levels,b,low,high)
                    wrong+=(guess!=x['n'])
                    abs_err+=abs(guess-x['n'])
                errs['%s_b%s'%(policy,b)]={'wrong':wrong,'total':len(dev),
                    'error_rate':wrong/float(len(dev)),
                    'count_MAE':abs_err/float(len(dev))}
        # Adjacent count range overlaps; descriptive, not probability.
        spans={}
        for n in range(17):
            ix=[x['I'] for x in dev if x['n']==n]
            spans[n]=(min(ix),max(ix))
        overlaps={}
        for n in range(16):
            a,b=spans[n],spans[n+1]
            overlaps['%d-%d'%(n,n+1)]=max(0.,
                min(a[1],b[1])-max(a[0],b[0]))
        output['results']['R%g'%r]={
            'assumed_R_segment_ohm':r,'dev_count':len(dev),
            'CAL_fit_near_slope_A_per_nearcount':slope,
            'CAL_offset_A':offset,'DEV_neighbouring_count_current_overlap_A':overlaps,
            'error_by_policy_and_ADC_bits':errs}
        print('E22_REGIME R=%g DEV=%d OFF=%.4g A NEAR_SLOPE=%.4g A'%(
            r,len(dev),offset,slope))
        for pol in ('raw','offset_only','offset_near'):
            print('  ',pol,'continuous/4/5/6/7-bit ERR:',
                  ' '.join('%d/%d'%(errs['%s_b%d'%(pol,b)]['wrong'],len(dev))
                           for b in (0,4,5,6,7)))
    output['cautions']=[
       'Full-scale and nominal count levels learned on CAL at assumed R0 only.',
       'The ADC is a mathematical uniform quantizer, not Spectre ADC circuitry.',
       'R settings are assumed wiring, NOT extracted GF 256x256 interconnect.',
       'Near/offset correction fitted on CAL separately at each R, an optimistic calibration policy.',
       'One fixed m=k=16 block, nominal GF access-NFET plus static custom MTJ, no device mismatch.',
       'No full-network MNIST accuracy, timing/energy, PEX, or novelty established.'
       ]
    return output

def selftest():
    args=argparse.Namespace(seed=42,cal_per_count=4,dev_per_count=5)
    profiles=profiles_for_counts(args)
    assert len(profiles)==17*9
    assert len({p['mask_hash'] for p in profiles})==len(profiles)
    for p in profiles:
        assert len(set(p['active_rows_0based']) & set(p['weight_P_rows_0based']))==p['true_n']
    levels=[(i+1)*1e-6 for i in range(17)]
    for b in (6,7):
        lo=levels[0]-.5e-6;hi=levels[-1]+.5e-6
        assert all(predict(t,levels,b,lo,hi)==n for n,t in enumerate(levels))
    print('E22_SELFTEST_PASS: 17 count masks, CAL DEV separation, bit quantizer. NOT Spectre.')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=('selftest','run','analyze'))
    ap.add_argument('source',nargs='?',help='e22_results.json for analyze')
    ap.add_argument('--private',default=str(Path.home()/'mram_private/E02_256x256/E22'))
    ap.add_argument('--template',default=None)
    ap.add_argument('--seed',type=int,default=20261105)
    ap.add_argument('--cal-per-count',type=int,default=6)
    ap.add_argument('--dev-per-count',type=int,default=12)
    ap.add_argument('--rs',default='0,1,2,3,5')
    ap.add_argument('--chunk-size',type=int,default=16)
    ap.add_argument('--vread',type=float,default=.05)
    ap.add_argument('--vwl',type=float,default=.8)
    ap.add_argument('--timeout-sec',type=int,default=240)
    ap.add_argument('--out',default=None,help='Optional distinct E22 analysis JSON')
    args=ap.parse_args()
    if args.mode=='selftest':
        selftest()
    elif args.mode=='run':
        args.rows=32;args.m=16;args.k=16
        execute(args)
    else:
        if not args.source:die('analyze needs existing E22 output file')
        p=Path(args.source).expanduser().resolve()
        if not p.is_file():die('Missing result '+str(p))
        result=evaluate(json.loads(p.read_text()))
        target=Path(args.out).expanduser() if args.out else p.parent/'E22_ADC_REGIME.json'
        if target.exists():die('Refusing overwrite '+str(target))
        target.write_text(json.dumps(result,indent=2)+'\n')
        print('E22_ADC_ANALYSIS',target)
        print('E22_SCOPE: GF Spectre currents but mathematical ADC, assumed wire R, no PEX.')
if __name__=='__main__':
    main()
