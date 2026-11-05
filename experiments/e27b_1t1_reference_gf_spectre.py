#!/usr/bin/env python3
"""E27B: Bounded real-GF-NFET 1T1-like ideal-wire four-column reference.

Uses VERIFIED local E19 v2 deck generator + student static-MTJ model to execute
16 independent GF-transistor Spectre cases. These are FOUR SEPARATE COLUMNS,
not jointly driven 4-column CIM or actual 1T1 PEX. R per segment=0 by design.
Only nominal read bias 0.05V/0.8V from prior E22 is allowed as a screen, not
independent read-disturb certification. No PDK or model source exported.
"""
from __future__ import print_function
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

MASKS=[('N2_ROWS01',(0,1)),('F2_ROWS23',(2,3)),
       ('D2_ROWS03',(0,3)),('D2_ROWS12',(1,2))]
STATE=[[('P' if (r+c)%2==0 else 'AP') for c in range(4)] for r in range(4)]
E19_SHA='b6bec40bc234fac406d191229146354a5fe47c6969fb6db6a672e607ddf83e54'
MODEL_SHA='1d22984b7be5135c07bb5e392d73aa53e1ad42b7c4bdc6d2fc11bb3f313b9a88'

def die(s):
    raise SystemExit('E27B_BLOCKED: '+str(s))

def sha(p):
    h=hashlib.sha256()
    with open(str(p),'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def profiles():
    out=[]
    for c in range(4):
        p=[r for r in range(4) if STATE[r][c]=='P']
        for name,act in MASKS:
            n=len(set(act)&set(p))
            assert len(p)==2 and n==1
            out.append({'id':len(out),'split':'CONTROL','true_n':n,
                        'm':2,'k':2,'active_rows_0based':list(act),
                        'weight_P_rows_0based':list(p),
                        'mask_hash':hashlib.sha256(repr((c,act,p)).encode('ascii')).hexdigest()[:16],
                        'physical_column_label':c,'case_name':name})
    return out

def selftest():
    p=profiles()
    assert len(p)==16 and len(set(x['mask_hash'] for x in p))==16
    print('E27B_SELFTEST_PASS: 16 matched m2/k2/n1 cases, four INDEPENDENT column circuits')
    print('E27B_NO_PEX_NO_PARALLEL_4COL_NO_VARIATION_NO_CORRELATION')

def run(args):
    selftest()
    if not shutil.which('spectre'):
        die('Spectre unavailable in authorized NUS shell')
    if args.vread!=0.05 or args.vwl!=0.8:
        die('Only frozen historical 0.05V read, 0.8V WL allowed until topology/bias review')
    try:
        import e19_gf_nfet_mtj_nonideal_count_gate_v2 as e19
    except ImportError:
        die('verified E19 v2 source missing alongside experiments')
    source=Path(e19.__file__).resolve()
    if sha(source)!=E19_SHA:
        die('unverified E19 source SHA: '+sha(source))
    model=Path.home()/e19.MODEL_REL
    if not model.is_file() or sha(model)!=MODEL_SHA or e19.MODEL_SHA!=MODEL_SHA:
        die('student MTJ source SHA mismatch, do not substitute')
    template_source=e19.choose_template(args.template)
    template=e19.parse_template(template_source)
    base=Path(args.private).expanduser().resolve()
    base.mkdir(parents=True,exist_ok=True)
    wd=base/('E27B_GF_R0_'+datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')+'_'+str(os.getpid()))
    wd.mkdir(mode=0o700)
    cfg=argparse.Namespace(**vars(args))
    cfg.rows=4;cfg.m=2;cfg.k=2
    cases=profiles()
    record={'experiment':'E27B_GF_NFET_STATIC_MTJ_IDEALWIRE',
            'status':'INCOMPLETE','physical_1T1_PEX':False,
            'joint_columns':False,'num_independent_columns':4,
            'assumed_BL_R_per_segment_ohm':0.0,
            'source_e19_sha256':sha(source),
            'student_mtj_sha256':sha(model),
            'input_template_sha256':sha(template_source),
            'vread_V':args.vread,'vwl_V':args.vwl,
            'historical_bias_not_read_disturb_certification':True,
            'profiles':cases,'currents':[]}
    (wd/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    print('E27B_WORKDIR',wd,flush=True)
    deck=e19.make_deck(wd,cases,0.,template,model,cfg)
    print('E27B_DECK',deck,flush=True)
    st=time.time()
    with (wd/'stdout.log').open('w') as f:
        try:
            rc=subprocess.run(['spectre',str(deck),'+log',str(wd/'spectre.log'),
                              '-format','psfascii'],cwd=str(wd),
                              stdout=f,stderr=subprocess.STDOUT,
                              timeout=args.timeout_sec).returncode
        except subprocess.TimeoutExpired:
            rc=124
    if rc:
        die('Spectre failed or timed out rc={} after {:.1f}s; see private logs {}'.format(
            rc,time.time()-st,wd))
    dc=wd/'input.raw/dcOp.dc'
    if not dc.is_file():
        die('missing Spectre DC output: '+str(dc))
    readings=e19.parse_sources(dc)
    for p in cases:
        name='VC%04d:p'%p['id']
        if name not in readings:die('missing actual source '+name)
        record['currents'].append({'column':p['physical_column_label'],
            'case':p['case_name'],'ideal_count':1,
            'current_A':float(readings[name]),'mask_hash':p['mask_hash']})
    assert len(record['currents'])==16
    record['status']='FINISHED'
    record['dc_source_sha256']=sha(dc)
    out=wd/'e27b_nominal_16cases.json'
    out.write_text(json.dumps(record,indent=2)+'\n')
    print('E27B_ACTUAL_GF_NFET_NOMINAL_RESULT',out,flush=True)
    for c in range(4):
        vals=[r for r in record['currents'] if r['column']==c]
        lo=min(r['current_A'] for r in vals);hi=max(r['current_A'] for r in vals)
        print('E27B_COLUMN',c,'SPAN_nA',1e9*(hi-lo),
              'I_uA',[(r['case'],1e6*r['current_A']) for r in vals],flush=True)
    print('E27B_DONE_ACTUAL_GF_TRANSISTOR_DC_NOT_1T1_PEX_OR_JOINT',flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('mode',choices=('selftest','run'))
    ap.add_argument('--template',default=None)
    ap.add_argument('--private',default=str(Path.home()/'mram_private/E27_1T1/E27B'))
    ap.add_argument('--vread',type=float,default=0.05)
    ap.add_argument('--vwl',type=float,default=0.8)
    ap.add_argument('--timeout-sec',type=int,default=240)
    a=ap.parse_args()
    selftest() if a.mode=='selftest' else run(a)

if __name__=='__main__':
    main()
