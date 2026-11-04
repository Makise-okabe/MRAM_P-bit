#!/usr/bin/env python3
"""E11C: *model-only* fresh two-state MTJ small-signal Spectre DC diagnostic.

DOES NOT demonstrate safe operating bias, access-transistor functionality,
transient switching, realistic P/AP statistics, multirow CIM, or 256x256 PEX.
No PDK model / data copied. Both student VA models kept in their NUS paths.
Python 3.6 compatible. Requires installed Spectre on NUS.
"""
from __future__ import print_function
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

MODELS = (
    ('mtj_read', 'mram_fyp/cadence/CIM1_SINGLE_CELL/mtj_read.va'),
    ('mtj_read_v0', 'mram_fyp/cadence/CIM1_SINGLE_CELL/models/mtj_read_v0.va'),
)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):
            h.update(part)
    return h.hexdigest()

def snippets(folder):
    """Return diagnostic current-source lines without dumping model source."""
    snippets=[]
    files=sorted(folder.rglob('*.dc'))
    files+=sorted(folder.rglob('*.dcOp'))
    for f in files[:8]:
        if not f.is_file() or f.stat().st_size>10000000:
            continue
        try:
            lines=f.read_text(errors='replace').splitlines()
        except (OSError,UnicodeError):
            continue
        for index,line in enumerate(lines):
            if re.search(r'\bVREAD\b',line,re.I):
                lo=max(0,index-1); hi=min(len(lines),index+3)
                snippets.append({'file':str(f.relative_to(folder)),
                                 'lines':[x.strip()[:200] for x in lines[lo:hi]]})
                if len(snippets)>=8:return snippets
    return snippets

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private',type=Path,default=Path.home()/'mram_private/E02_256x256/E11')
    parser.add_argument('--bias-mv',type=float,default=1.0,
                        help='Diagnostic millivolts, NOT a validated operating point')
    parser.add_argument('--timeout-sec',type=int,default=90)
    parser.add_argument('--run',action='store_true')
    args=parser.parse_args()
    if not (0<args.bias_mv<=2.0):
        parser.error('This exploratory direct-model probe only permits 0 < |V| <= 2 mV')
    if not (10<=args.timeout_sec<=300):
        parser.error('timeout-sec should be 10..300')
    if args.run and not shutil.which('spectre'):
        parser.error('No spectre available')
    root=args.private.resolve()
    root.mkdir(parents=True,exist_ok=True)
    stamp=datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
    work=root/('E11C_model_only_'+stamp+'_'+str(os.getpid()))
    work.mkdir(mode=0o700)
    results=[]
    for model,rel in MODELS:
        modelpath=Path.home()/rel
        if not modelpath.is_file():
            results.append({'module':model,'found':False})
            continue
        for state in (0,1):
            case=work/('%s_state%d'%(model,state))
            case.mkdir()
            deck=case/'input.scs'
            deck.write_text('\n'.join([
                'simulator lang=spectre',
                '// E11C DIRECT TWO-TERMINAL VERILOG-A CHECK ONLY',
                '// p_state=0/1 are INPUT LABELS; mapping to P/AP is not yet verified.',
                '// 1mV-level source is an exploratory numerical perturbation, NOT certified read bias.',
                'ahdl_include "%s"'%str(modelpath),
                'VREAD (probe 0) vsource type=dc dc=%0.12g'%(args.bias_mv*1e-3),
                'XMTJ (probe 0) %s p_state=%d'%(model,state),
                'saveOptions options save=allpub currents=all',
                'dcOp dc',
                ''
            ]))
            row={'model':model,'p_state_setting':state,'found':True,
                 'relative_case':str(case.relative_to(work)),
                 'model_sha256':sha(modelpath),
                 'deck_sha256':sha(deck),
                 'biased_direct_model_V':args.bias_mv*1e-3,
                 'contains_access_NFET':False,'read_or_retention_validated':False}
            if args.run:
                cmd=['spectre',str(deck),'+log',str(case/'spectre.log'),'-format','psfascii']
                try:
                    with (case/'stdout.log').open('w') as log:
                        proc=subprocess.run(cmd,cwd=str(case),stdout=log,
                            stderr=subprocess.STDOUT,timeout=args.timeout_sec)
                    row['spectre_exit_code']=proc.returncode
                except subprocess.TimeoutExpired:
                    row['spectre_exit_code']=124
                    row['timeout']=True
                row['psf_files']=[str(f.relative_to(case)) for f in case.rglob('*.dc')][:12]
                row['dc_current_locator_snippets']=snippets(case)
                if (case/'spectre.log').exists():
                    logs=(case/'spectre.log').read_text(errors='replace')
                    row['spectre_log_last_diagnostics']=[
                        l.strip()[:180] for l in logs.splitlines()
                        if re.search(r'\b(error|fatal|warning|completed|spectre)\b',l,re.I)][-7:]
            else:
                row['spectre_exit_code']=None
            results.append(row)
    summary={
      'experiment':'E11C_STUDENT_MODEL_ONLY_SMALL_SIGNAL',
      'evidence_class':'UNVALIDATED_DIRECT_VERILOGA_DC_DIAGNOSTIC',
      'user_selected_exploratory_bias_mV':args.bias_mv,
      'not_a_safe_read_bias_claim':True,
      'not_a_2T1MTJ_cell_simulation':True,
      'not_an_analog_Ising_field_validation':True,
      'no_proprietary_model_content_exported':True,
      'executed':args.run,'cases':results
    }
    (work/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('E11C_OUTPUT:',str(work/'results.json'))
    for row in results:
        if not row.get('found'):
            print('MODEL_NOT_FOUND',row['module'])
            continue
        print('CASE',row['model'],'p_state='+str(row['p_state_setting']),
              'spectre_exit='+str(row['spectre_exit_code']),
              'dc_files='+str(row.get('psf_files',[])))
        for item in row.get('dc_current_locator_snippets',[])[:2]:
            print('  DC_CONTEXT:',item['file'],' | '.join(item['lines']))
        for line in row.get('spectre_log_last_diagnostics',[])[-3:]:
            print('  LOG:',line)
    print('INTERPRETATION: model-only P/AP check pending numerical extraction;')
    print('NO NFET, NO WIRE RC, NO REAL READ DISTURB, NO CIM/ISING CLAIM')

if __name__=='__main__':
    main()
