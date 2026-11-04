#!/usr/bin/env python3
"""E23D: FIRST FRESH independent GF Spectre mask validation of E22C suffix Q.

This is a confirmatory SCREEN only for frozen B=32,m=k=16 model, not a 256x256
PEX macro. Train EVERY decoder from the OLD E22 CAL masks; never tune or train
on OLD DEV or any NEW E23D masks. One new resistance value R=4 is intentionally
unseen in E22, with decoder coefficients and ADC fullscale interpolated from
R=3 and R=5 old CAL. All Rs are ASSUMED wiring, never measured.
Python 3.6; local license needed for 'run' only.
"""
from __future__ import print_function
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

import e22_gf_precision_regime as e22
import e22c_spatial_feature_ablation as e22c

RS=(0.,1.,2.,3.,4.,5.)
FEATURES=('raw','near','centroid','suffixQ')
BITS=(0,5,6,7)

def stop(msg):
    raise SystemExit('E23D_ERROR: '+str(msg))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def generate(old,seed,reps):
    if reps<12:stop('At least 12 fresh DEV masks per count required')
    if old.get('status')!='FINISHED' or old.get('GF_PEX') is not False:
        stop('Original E22 source must be complete and non-PEX')
    old_hashes=set(p['mask_hash'] for p in old['profiles'])
    rng=random.Random(seed)
    profiles=[]; hashes=set()
    for n in range(17):
        for i in range(reps):
            for attempt in range(30000):
                a=tuple(sorted(rng.sample(range(32),16)))
                inside=set(rng.sample(a,n))
                other=[j for j in range(32) if j not in a]
                w=tuple(sorted(inside | set(rng.sample(other,16-n))))
                h=sha(repr((a,w)).encode('ascii'))[:16]
                if h not in old_hashes and h not in hashes:
                    hashes.add(h)
                    break
            else:stop('Cannot create independent mask')
            if len(set(a)&set(w))!=n:stop('Bad generated count')
            profiles.append({'id':len(profiles),'split':'DEV','true_n':n,
                'm':16,'k':16,'active_rows_0based':list(a),
                'weight_P_rows_0based':list(w),'mask_hash':h})
    return profiles

def run(args):
    import e19_gf_nfet_mtj_nonideal_count_gate_v2 as e19
    if not shutil.which('spectre'):
        stop('GF Spectre not found; execute on NUS Singularity')
    if args.reps<12 or args.reps>200 or args.chunk_size<1 or args.chunk_size>80:
        stop('Invalid independent sample count/chunk')
    if not (0<args.vread<=.05 and 0<args.vwl<=.8):
        stop('Do not increase historical read/WL bias without qualification')
    e22file=Path(args.train).expanduser().resolve()
    if not e22file.is_file():stop('Missing E22 CAL source '+str(e22file))
    raw=e22file.read_bytes()
    old=json.loads(raw.decode('utf-8'))
    profiles=generate(old,args.seed,args.reps)
    model=Path.home()/e19.MODEL_REL
    if not model.is_file() or e19.file_hash(model)!=e19.MODEL_SHA:
        stop('Student custom MTJ SHA incorrect. Do not substitute model')
    src=e19.choose_template(args.template)
    template=e19.parse_template(src)
    private=Path(args.private).expanduser().resolve()
    private.mkdir(parents=True,exist_ok=True)
    folder=private/('E23D_FRESH_'+datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')+
                    '_'+str(os.getpid()))
    folder.mkdir(mode=0o700)
    manifest={'experiment':'E23D_FRESH_MASK_GF_NFET_Q_VALIDATION',
              'status':'INCOMPLETE','GF_PEX':False,
              'physical_ADC':False,'line_R_ASSUMED':list(RS),
              'train_E22_SHA256':sha(raw),'train_path':str(e22file),
              'seed':args.seed,'reps_per_count':args.reps,
              'template_SHA256':e19.file_hash(src),
              'student_MTJ_SHA256':e19.MODEL_SHA,
              'profiles':profiles,'results':{}}
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('E23D_WORKDIR',folder,flush=True)
    print('E23D_FRESH_MASKS',len(profiles),
          'NO_REUSE_OF_OLD_CAL_OR_DEV_MASKS',True,flush=True)
    print('E23D_TRAIN_OLD_E22_SHA256',sha(raw),flush=True)
    args.rows=32; args.m=16; args.k=16
    for r in RS:
        curr=[]
        for j in range(0,len(profiles),args.chunk_size):
            chunk=profiles[j:j+args.chunk_size]
            site=folder/('R%g_C%03d'%(r,j//args.chunk_size))
            site.mkdir()
            deck=e19.make_deck(site,chunk,r,template,model,args)
            start=time.time()
            try:
                with (site/'stdout.log').open('w') as log:
                    result=subprocess.run(['spectre',str(deck),
                        '+log',str(site/'spectre.log'),'-format','psfascii'],
                        cwd=str(site),stdout=log,stderr=subprocess.STDOUT,
                        timeout=args.timeout_sec)
                rc=result.returncode
            except subprocess.TimeoutExpired:rc=124
            if rc:
                stop('Spectre failed rc=%d in %s; check private logs, do not interpret'%(
                    rc,site))
            vals=e19.parse_sources(site/'input.raw/dcOp.dc')
            for p in chunk:
                key='VC%04d:p'%p['id']
                if key not in vals:stop('Missing DC current '+key)
                curr.append({'case_id':p['id'],'split':'DEV',
                    'true_n':p['true_n'],'mask_hash':p['mask_hash'],
                    'current_A':vals[key]})
            print('E23D_CHUNK_SUCCESS R=%g offset=%d cases=%d elapsed=%.2fs'%(
                r,j,len(chunk),time.time()-start),flush=True)
        if len(curr)!=len(profiles):stop('Incomplete R slice')
        manifest['results']['R%g'%r]={
            'R_segment_assumed_ohm':r,'per_case_currents':curr}
        (folder/'results_partial.json').write_text(json.dumps(
            manifest,indent=2)+'\n')
        print('E23D_R_COMPLETE R=%g cases=%d'%(r,len(curr)),flush=True)
    manifest['status']='FINISHED'
    dest=folder/'e23d_fresh_results.json'
    dest.write_text(json.dumps(manifest,indent=2)+'\n')
    print('E23D_RESULTS',dest,flush=True)
    print('E23D_NO_CAL_FITTED_ON_FRESH_MASKS',True)

def packtrain(data):
    if data.get('status')!='FINISHED' or data.get('GF_PEX') is not False:
        stop('Old E22 train dataset incomplete')
    source=e22.nmap(data)
    if set(source)!=set((0.,1.,2.,3.,5.)):
        stop('Old E22 does not contain required R slices')
    profiles={int(p['id']):p for p in data['profiles']}
    models={}
    for r in source:
        cal=[]
        for x in source[r]:
            if x['split']=='CAL':
                p=dict(profiles[x['id']]);p['rows']=32
                cal.append(dict(x,f=e22c.features(p)))
        if len(cal)!=102 or any(sum(x['n']==n for x in cal)!=6
                               for n in range(17)):
            stop('Expected exactly six OLD CAL masks for every count')
        vals=[x['I'] for x in cal]
        span=max(vals)-min(vals)
        win=(min(vals)-.05*span,max(vals)+.05*span)
        models[r]={'window':win,'fits':{
            name:e22c.fit(cal,name) for name in FEATURES}}
    # Never train on R4: interpolate slopes, CAL feature centering, 17 class
    # reference levels and ADC range ONLY from older R3/R5 CAL values.
    a,b=models[3.],models[5.]
    new={}
    for name in FEATURES:
        m1,m2=a['fits'][name],b['fits'][name]
        new[name]=((m1[0]+m2[0])/2.,(m1[1]+m2[1])/2.,
                   [(u+v)/2. for u,v in zip(m1[2],m2[2])])
    models[4.]={'window':tuple((u+v)/2. for u,v in zip(
        a['window'],b['window'])),'fits':new}
    return models

def analyse(args):
    oldfile=Path(args.train).expanduser().resolve()
    freshfile=Path(args.fresh).expanduser().resolve()
    dest=Path(args.out).expanduser().resolve()
    if dest.exists():stop('Refuses overwrite '+str(dest))
    if not oldfile.is_file() or not freshfile.is_file():
        stop('Missing old E22 training file or fresh E23D current file')
    raw=oldfile.read_bytes()
    old=json.loads(raw.decode('utf-8'))
    fresh=json.loads(freshfile.read_text())
    if fresh.get('status')!='FINISHED' or fresh.get('GF_PEX') is not False:
        stop('Fresh GF Spectre run incomplete')
    if fresh.get('train_E22_SHA256')!=sha(raw):
        stop('Original E22 training hash changed: no valid confirmation')
    old_hashes=set(p['mask_hash'] for p in old['profiles'])
    profiles={int(p['id']):p for p in fresh['profiles']}
    if any(p['mask_hash'] in old_hashes for p in profiles.values()):
        stop('Mask reuse from original CAL or inspected DEV found')
    if len(profiles)!=17*fresh['reps_per_count']:
        stop('Fresh mask count inconsistent')
    m=packtrain(old)
    result={'experiment':'E23D_FRESH_HOLDOUT_FROZEN_E22_CAL',
            'old_E22_SHA256':sha(raw),
            'fresh_E23D_SHA256':sha(freshfile.read_bytes()),
            'new_R4_calibration':'R3/R5 old CAL linear interpolation',
            'all_analog_line_R_assumed':True,'real_GF_NFET':True,
            'actual_ADC_or_PEX':False,'summary':{}}
    for R in RS:
        key='R%g'%R
        if key not in fresh['results']:stop('Missing R '+key)
        current=fresh['results'][key]['per_case_currents']
        if len(current)!=len(profiles):stop('Incomplete R DEV')
        rows=[]
        for x in current:
            p=profiles[int(x['case_id'])]
            if x['split']!='DEV' or (
               x['mask_hash'],x['true_n'])!=(p['mask_hash'],p['true_n']):
                stop('Fresh labels or mask hash mismatch')
            rows.append({'id':p['id'],'n':p['true_n'],
                'I':float(x['current_A']),'f':e22c.features(p)})
        window=m[R]['window']
        err={};gaps={}
        pairs={}
        flags={}
        for name in FEATURES:
            fit=m[R]['fits'][name]
            err[name]={};flags[name]={}
            for b in BITS:
                wrong=[]; mae=0
                for x in rows:
                    pred=e22c.classify(x,fit,name,b,window)
                    wrong.append(int(pred!=x['n']))
                    mae+=abs(pred-x['n'])
                label='continuous' if b==0 else 'b%d'%b
                err[name][label]={'wrong':sum(wrong),'total':len(rows),
                    'mae':mae/float(len(rows))}
                flags[name][label]=wrong
            states={n:[e22c.adjust(x['I'],x,fit,name)
                       for x in rows if x['n']==n] for n in range(17)}
            sign=1. if fit[2][-1]>fit[2][0] else -1.
            signedgap=[min(sign*v for v in states[n+1])-
                       max(sign*v for v in states[n]) for n in range(16)]
            gaps[name]=sum(v<=0 for v in signedgap)
        for baseline in ('near','centroid'):
            a,b=flags[baseline]['b7'],flags['suffixQ']['b7']
            pairs[baseline]={'baseline_wrong_Q_right':sum(x and not y for x,y in zip(a,b)),
                             'baseline_right_Q_wrong':sum(y and not x for x,y in zip(a,b))}
        result['summary'][key]={'R_assumed_ohm':R,'fresh_DEV':len(rows),
            'old_CAL_only':True,'R_interpolated_without_R4_CAL':R==4.,
            'errors':err,'nonseparable_adjacent':gaps,'paired_Q':pairs}
        print('E23D_FRESH_R=%g DEV=%d train=OLD_CAL_ONLY%s'%(
            R,len(rows),' R4_INTERPOLATED' if R==4. else ''))
        for name in FEATURES:
            v=err[name]
            print(' %-9s CONT=%d b5=%d b6=%d b7=%d ADJ_NONSEP=%d'%(
                name,v['continuous']['wrong'],v['b5']['wrong'],
                v['b6']['wrong'],v['b7']['wrong'],gaps[name]))
        print(' PAIR_Q_vs_near',pairs['near'],
              'PAIR_Q_vs_centroid',pairs['centroid'])
    result['limitations']=[
        'Fresh mask TEST data is independent but fixed m=k=16; varied m and k remain untested.',
        'R=4 is interpolated using old CAL models and known hypothetical R.',
        'No Q computation latency/energy or physical programmable ADC costs.',
        'All wire R values are assumptions, not extracted GF interconnect.',
        'GF access transistor compact model plus student static MTJ only; no variation.',
        '204 or 408 stratified spatial-mask cases per R cannot establish zero population BER.'
    ]
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('E23D_REPORT',dest)
    print('E23D_EVIDENCE: FRESH_MASKS_OLD_CAL_ONLY_GF_CURRENT_NO_PEX')

def selftest():
    old={'status':'FINISHED','GF_PEX':False,'profiles':[]}
    masks=generate(old,20261106,12)
    assert len(masks)==204 and len(set(x['mask_hash'] for x in masks))==204
    assert sorted(set(x['true_n'] for x in masks))==list(range(17))
    assert all(len(set(x['active_rows_0based']) & set(
        x['weight_P_rows_0based']))==x['true_n'] for x in masks)
    assert e22c.features(masks[0])['near']>=0
    a=(1.,3.,[1.,2.]);b=(3.,5.,[3.,4.])
    mid=((a[0]+b[0])/2.,(a[1]+b[1])/2.,
         [(x+y)/2 for x,y in zip(a[2],b[2])])
    assert mid==(2.,4.,[2.,3.])
    print('E23D_SELFTEST_PASS fresh mask uniqueness, all 17 counts,'
          ' old-mask exclusion, CAL-only R interpolation. NO SPECTRE.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('selftest','run','analyze'))
    parser.add_argument('--train',default=str(Path.home()/
        'mram_private/E02_256x256/E22/E22_GFCURRENT_20261104T162140_178/e22_results.json'))
    parser.add_argument('--fresh',help='Fresh E23D GF result file, for analyze')
    parser.add_argument('--out',help='Fresh confirmation analysis JSON, for analyze')
    parser.add_argument('--private',default=str(Path.home()/
        'mram_private/E02_256x256/E23D'))
    parser.add_argument('--template',default=None)
    parser.add_argument('--seed',type=int,default=20261106)
    parser.add_argument('--reps',type=int,default=24)
    parser.add_argument('--vread',type=float,default=.05)
    parser.add_argument('--vwl',type=float,default=.8)
    parser.add_argument('--timeout-sec',type=int,default=240)
    parser.add_argument('--chunk-size',type=int,default=16)
    args=parser.parse_args()
    if args.mode=='selftest':selftest()
    elif args.mode=='run':run(args)
    else:
        if not args.fresh or not args.out:
            parser.error('analyze needs --fresh and --out')
        analyse(args)

if __name__=='__main__':
    main()
