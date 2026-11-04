#!/usr/bin/env python3
"""E11: source provenance and nine-mask analog-read audit; NO automatic PDK run.

This tool never exports model text, vendor decks, or a simulator testbench. It
never assumes safe read bias or chooses an MTJ model. The optional CSV analyser
uses user-generated, independently verified current measurements only.
"""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path

CASES = ('Z0','NP','NAP','FP','FAP','NN','FF','NF','FN')
TEMPLATE_FIELDS = ('case_id','sense_current_A','sample_time_ns',
                   'state_retained','read_bias_V','source_model_id',
                   'array_model_id')

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):
            h.update(part)
    return h.hexdigest()

def candidates():
    home=Path.home()
    roots=(home/'mram_fyp/cadence/CIM1_SINGLE_CELL',
           home/'mram_fyp/cadence', home/'MRAM_FYP_Overleaf')
    blocked={'simulations','manual_cross5_runs','calibre','results','raw',
             'runs','logs','.git','input.ahdlSimDB','venv','.venv',
             '__pycache__','archive','node_modules','data'}
    visited=set()
    found=[]
    count=0
    for root in roots:
        if not root.is_dir():
            continue
        for folder,dirs,files in os.walk(root):
            folder=Path(folder)
            depth=len(folder.relative_to(root).parts)
            if depth>=5:
                dirs[:]=[]
            else:
                dirs[:]=[d for d in dirs if d not in blocked and
                         not d.startswith('.')]
            for name in files:
                count+=1
                if count>40000 or len(found)>=32:
                    break
                f=folder/name
                if f in visited:
                    continue
                visited.add(f)
                if f.suffix.lower() not in {'.va','.vams','.scs','.sp','.cir','.cdl'}:
                    continue
                if not any(k in f.name.lower() for k in ('mtj','mram','spin','model')):
                    continue
                try:
                    if f.stat().st_size>2_000_000:
                        continue
                    found.append({'relative_to_home':str(f.relative_to(home)),
                                  'size_bytes':f.stat().st_size,
                                  'sha256':digest(f)})
                except (PermissionError, ValueError, OSError):
                    continue
            if count>40000 or len(found)>=32:
                break
    return found

def audit(out):
    home=Path.home()
    pex=home/('mram_fyp/cadence/calibre/xact/M047_GF_4x4_TILE_TEST_PEX/'
              'M047_GF_4x4_TILE_TEST.pex.dspf')
    prior=home/'mram_private/E02_256x256/raw'
    cases=sorted(prior.glob('E02_256x256_zero_bias_*')) if prior.is_dir() else []
    result={
        'kind':'E11_LOCAL_READ_OPERATOR_SOURCE_AUDIT',
        'status':'SOURCE_CONTRACT_NOT_VERIFIED',
        'custom_mtj_authorization_verified':False,
        'read_bias_and_retention_validated':False,
        'analog_Ising_field_physically_validated':False,
        'old_gf_native_4x4_pex_present':pex.is_file(),
        'old_gf_native_4x4_pex_sha256':digest(pex) if pex.is_file() else None,
        'old_gf_native_256x256_hierarchy_only':bool(cases),
        'local_source_filename_candidates_unverified':candidates(),
        'required_for_next_run':[
            'Approved student-owned MTJ source file/interface and permitted use',
            'GF access-NFET plus MTJ two-terminal/2T1MTJ connections',
            'Validated nondisturbing P/AP read bias and state initialization',
            'Declared SL floating/termination rule and sense current sign',
            'A legal one-cell/two-cell Spectre P/AP comparison before nine masks',
        ],
        'no_spectre_executed':True,
        'note':'This audits files. It NEVER certifies a model or fabricates read data.'
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise SystemExit('Refusing to overwrite '+str(out))
    out.write_text(json.dumps(result,indent=2)+'\n')
    print('E11_AUDIT:',out)
    print('OLD_GF_NATIVE_PEX:',result['old_gf_native_4x4_pex_present'])
    print('CUSTOM_MODEL_CANDIDATE_FILES:',len(result['local_source_filename_candidates_unverified']))
    for item in result['local_source_filename_candidates_unverified'][:18]:
        print('CANDIDATE_UNVERIFIED:',item['relative_to_home'])
    print('E11_STATUS: SOURCE_CONTRACT_NOT_VERIFIED; NO NEW SPECTRE READ')

def template(out):
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=TEMPLATE_FIELDS)
        writer.writeheader()
        for case in CASES:
            writer.writerow({'case_id':case})
    print('E11_MEASUREMENT_TEMPLATE:',out)
    print('NO_CURRENT_VALUES_GENERATED')

def analyze(path,out):
    if not path.is_file():raise SystemExit('No measurement CSV: '+str(path))
    with path.open(newline='') as f:
        reader=csv.DictReader(f)
        missing=set(TEMPLATE_FIELDS)-set(reader.fieldnames or ())
        if missing:raise SystemExit('Missing columns: '+repr(sorted(missing)))
        raw=list(reader)
    if len(raw)!=len(CASES) or {r['case_id'] for r in raw}!=set(CASES):
        raise SystemExit('Need precisely one row for every case: '+','.join(CASES))
    rows={r['case_id']:r for r in raw}
    for k,row in rows.items():
        if row['state_retained'].strip().upper() not in ('PASS','TRUE','YES'):
            raise SystemExit('Retention not verified for '+k)
    for col in ('sample_time_ns','read_bias_V','source_model_id','array_model_id'):
        vals={r[col].strip() for r in rows.values()}
        if len(vals)!=1 or '' in vals:
            raise SystemExit('Inconsistent or missing '+col)
    data={}
    for k,row in rows.items():
        try:v=float(row['sense_current_A'])
        except ValueError:raise SystemExit('Invalid current for '+k)
        if not math.isfinite(v):raise SystemExit('Nonfinite current for '+k)
        data[k]=v
    z=data['Z0']
    residuals={
        'NN':data['NN']-data['NP']-data['NAP']+z,
        'FF':data['FF']-data['FP']-data['FAP']+z,
        'NF':data['NF']-data['NP']-data['FAP']+z,
        'FN':data['FN']-data['FP']-data['NAP']+z
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise SystemExit('Refusing overwrite '+str(out))
    result={'experiment':'E11_9MASK_USER_SUPPLIED_DATA',
            'evidence_class':'USER_EXPORTED_ANALOG_CURRENTS_REQUIRE_PROVENANCE_REVIEW',
            'read_op_validated':False,'full_array_pex':False,
            'source_model_id':raw[0]['source_model_id'],
            'array_model_id':raw[0]['array_model_id'],
            'sample_time_ns':raw[0]['sample_time_ns'],
            'read_bias_V':raw[0]['read_bias_V'],
            'input_csv_sha256':digest(path),
            'P_minus_AP_sensitivity_near_A':data['NP']-data['NAP'],
            'P_minus_AP_sensitivity_far_A':data['FP']-data['FAP'],
            'interaction_residuals_A':residuals,
            'pair_residual_spread_A':max(residuals.values())-min(residuals.values()),
            'interpretation':'Residuals measure nonadditivity only; no noise, hardware novelty, or optimizer improvement inferred.'}
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='mode')  # Python 3.6: required= introduced in 3.7
    a=sub.add_parser('audit');a.add_argument('--out',type=Path,required=True)
    t=sub.add_parser('template');t.add_argument('--out',type=Path,required=True)
    e=sub.add_parser('analyze');e.add_argument('--csv',type=Path,required=True);e.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.mode is None:
        ap.error('Choose one of: audit, template, analyze')
    if args.mode=='audit':audit(args.out)
    elif args.mode=='template':template(args.out)
    else:analyze(args.csv,args.out)

if __name__=='__main__':
    main()
