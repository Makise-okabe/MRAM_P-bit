#!/usr/bin/env python3
"""E27C: read-only NUS 1T1-model and future physical-layout feasibility audit.
No Spectre, PDK copying, GF model export, DRC, LVS, PEX, or claim of correlation.
Reports model/module port NAMES and metadata; original private sources stay NUS.
"""
from __future__ import print_function
import argparse, collections, datetime, hashlib, json, os, re
from pathlib import Path

HOME=Path.home()
BASE=HOME/'mram_fyp/cadence/CIM1_SINGLE_CELL'
MODEL=BASE/'models/mtj_read_v0.va'
DECK=BASE/'simulations/MC_CURRENT_REAL_rp_m8_N10_seed20261029/cases/R01/m8/a00000/input.scs'
E19=HOME/'MRAM_Path_Finding/experiments/e19_gf_nfet_mtj_nonideal_count_gate_v2.py'
MANIFEST=HOME/'mram_private/E27_1T1/E27A_1T1_4x4_preflight_manifest.json'
MODEL_SHA='1d22984b7be5135c07bb5e392d73aa53e1ad42b7c4bdc6d2fc11bb3f313b9a88'
DECK_SHA='e3841c4954a300e213a0d3d924d5ae40b2a0a799b57a32d54daf3fb43cf47c45'
E19_SHA='b6bec40bc234fac406d191229146354a5fe47c6969fb6db6a672e607ddf83e54'

def sha(p):
    h=hashlib.sha256()
    with open(str(p),'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def file_info(path,expected=None):
    p=Path(path)
    if not p.is_file():return {'present':False}
    a={'present':True,'bytes':p.stat().st_size,'sha256':sha(p)}
    if expected:a['expected_sha_match']=(a['sha256']==expected)
    return a

def va_interface(p):
    if not p.is_file() or p.stat().st_size>200000:return {'error':'not found or too large'}
    t=p.read_text(encoding='utf-8',errors='replace')
    mods=[{'module':x,'ports':[v.strip() for v in y.split(',')]}
          for x,y in re.findall(r'\bmodule\s+(\w+)\s*\(([^)]*)\)',t,re.I)]
    params=re.findall(r'\bparameter\s+(?:real|integer|int|string)?\s*(\w+)\s*=',t,re.I)
    return {'modules':mods,'parameter_names':params,
            'dynamic_mtj_behavior_NOT_verified':True,
            'model_polarity_and_terminal_order_NOT_verified':True}

def deck_counts(p):
    if not p.is_file() or p.stat().st_size>10000000:return {'error':'missing or too large'}
    counter=collections.Counter()
    models=collections.Counter()
    for s in p.read_text(encoding='utf-8',errors='replace').splitlines():
        s=s.strip()
        if not s or s.startswith(('*','//')):continue
        if re.match(r'^(include|ahdl_include|library|section)\b',s,re.I):
            counter['includes_REDACTED']+=1;continue
        if re.match(r'^V\w+\s*\(',s,re.I):counter['voltage_sources']+=1
        if re.match(r'^I\w+\s*\(',s,re.I):counter['current_sources']+=1
        if re.match(r'^R\w+\s*\(',s,re.I):counter['resistor_instances']+=1
        if re.search(r'\bhvtnfet\b',s,re.I):counter['GF_hvtnfet_mentions']+=1
        if re.search(r'\bmtj_read_v0\b',s,re.I):counter['student_static_MTJ_mentions']+=1
        if re.search(r'\b(?:dc|dcOp|tran)\b',s,re.I):counter['analysis_mentions']+=1
        m=re.match(r'^\w+\s*\([^)]*\)\s*(\w+)',s)
        if m:models[m.group(1)[:60]]+=1
    return {'counts':dict(counter),'instance_type_counts':dict(models.most_common(15)),
            'note':'Only syntax counts; no verified single-device cell, mixed-state functionality or PEX.'}

def layout_leads(root):
    skip={'simulations','manual_cross5_runs','calibre','psf','input.raw','results','.git'}
    found=[]
    for current,subdirs,files in os.walk(str(root)):
        rel=os.path.relpath(current,str(root))
        depth=0 if rel=='.' else len(Path(rel).parts)
        subdirs[:]=[x for x in subdirs if x not in skip] if depth<6 else []
        if re.search(r'(?:^|[/_-])(?:1t1|cim1)(?:$|[/_-])',rel,re.I):
            found.append(rel)
        if len(found)>=30:break
    return found

def selftest():
    x='module mtj_read_v0(p,n); parameter real rp=1; endmodule'
    assert re.findall(r'\bmodule\s+(\w+)\s*\(([^)]*)\)',x)==[('mtj_read_v0','p,n')]
    print('E27C_SELFTEST_PASS: read-only module parser; mock source only')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--selftest',action='store_true')
    ap.add_argument('--out',default=str(HOME/'mram_private/E27_1T1/E27C'))
    a=ap.parse_args()
    selftest()
    if a.selftest:return
    report={'experiment':'E27C_1T1_READONLY_MODEL_LAYOUT_AUDIT',
            'timestamp_UTC':datetime.datetime.utcnow().isoformat()+'Z',
            'student_MTJ':file_info(MODEL,MODEL_SHA),
            'old_singlecolumn_deck':file_info(DECK,DECK_SHA),
            'local_E19_generator':file_info(E19,E19_SHA),
            'previous_E27A_manifest':file_info(MANIFEST),
            'student_MTJ_interface':va_interface(MODEL),
            'old_singlecolumn_structure':deck_counts(DECK),
            'possible_layout_directories':layout_leads(HOME/'mram_fyp/cadence'),
            'NEW_GF_1T1MTJ_PEX':'NOT_ESTABLISHED',
            'legal_simultaneous_multirow_read':'NOT_YET_VERIFIED',
            'next_action':'verify 1T1 pin connections and read biases, layout DRC/LVS/xACT then actual 4column PEX comparison'}
    out=Path(a.out).expanduser().resolve()
    out.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(str(out),0o700)
    dst=out/'E27C_1T1_model_layout_audit.json'
    dst.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    os.chmod(str(dst),0o600)
    print('E27C_MODEL_SHA_MATCH',report['student_MTJ'].get('expected_sha_match'))
    print('E27C_OLD_DECK_SHA_MATCH',report['old_singlecolumn_deck'].get('expected_sha_match'))
    print('E27C_E19_GENERATOR_MATCH',report['local_E19_generator'].get('expected_sha_match'))
    print('E27C_MTJ_MODULES',report['student_MTJ_interface'].get('modules'))
    print('E27C_MTJ_PARAMETERS',report['student_MTJ_interface'].get('parameter_names'))
    print('E27C_SINGLECOLUMN_INSTANCE_COUNTS',report['old_singlecolumn_structure'].get('counts'))
    print('E27C_SINGLECOLUMN_MODEL_INSTANCES',report['old_singlecolumn_structure'].get('instance_type_counts'))
    print('E27C_LOCAL_1T1_LAYOUT_LEADS',report['possible_layout_directories'])
    print('E27C_PRIVATE_JSON',dst)
    print('E27C_NO_SPECTRE_NO_PEX_NO_CORRELATION_MEASURED')
if __name__=='__main__':
    main()
