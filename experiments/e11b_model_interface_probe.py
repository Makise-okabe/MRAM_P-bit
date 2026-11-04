#!/usr/bin/env python3
"""E11B local-only student-MTJ interface and testbench discovery.

Prints only file path, size/hash, public-interface token names, and relative
paths of candidate usage; no PDK or student model source code is copied.
Compatible with Python 3.6. No Spectre execution, no inferred authorization.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

MODEL_FILES = (
    'mram_fyp/cadence/CIM1_SINGLE_CELL/mtj_read.va',
    'mram_fyp/cadence/CIM1_SINGLE_CELL/models/mtj_read_v0.va',
)
SCAN_ROOTS = (
    'mram_fyp/cadence/CIM1_SINGLE_CELL',
    'mram_fyp/cadence/manual_cross5_runs',
    'mram_fyp/cadence',
)
SKIP_DIRS = set(('simulations', 'calibre', 'runs', 'logs', 'raw', 'results',
                 'input.ahdlSimDB', '.git', 'venvs', 'venv', '__pycache__',
                 'archive', 'node_modules', 'data', 'tmp', 'cache'))
EXTS = set(('.scs', '.sp', '.cir', '.spi', '.spice', '.cdl', '.va', '.vams',
            '.py', '.sh', '.md', '.txt', '.json', '.cfg'))


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def concise_head(source):
    # Strip comments only for module/declaration scanning; never print source.
    stripped = re.sub(r'/\*.*?\*/', ' ', source, flags=re.S)
    stripped = re.sub(r'//[^\n]*', '', stripped)
    mods = []
    for m in re.finditer(r'\bmodule\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*;',
                         stripped, flags=re.S):
        ports = re.findall(r'\b[A-Za-z_]\w*\b', m.group(2))
        mods.append({'name': m.group(1), 'ports': ports[:30]})
    params = []
    for m in re.finditer(r'\bparameter\s+(?:(?:real|integer|string|signed)\s+)?([A-Za-z_]\w*)\s*=', stripped):
        if m.group(1) not in params:
            params.append(m.group(1))
    semantic_tokens = ('initial_state','state','rp','rap','r_p','r_ap','read',
                       'write','mismatch','noise','white_noise','flicker_noise',
                       '$rdist_normal','$random','ddt','idt','transition')
    found_tokens = [w for w in semantic_tokens if re.search(r'(?<![A-Za-z_0-9])' + re.escape(w) + r'(?![A-Za-z_0-9])', stripped, re.I)]
    return mods, params[:60], found_tokens


def scan_references(home, needles):
    hits, nfiles = [], 0
    seen = set()
    for relroot in SCAN_ROOTS:
        root = home / relroot
        if not root.is_dir():
            continue
        for folder, dirs, names in os.walk(str(root), followlinks=False):
            p = Path(folder)
            if len(p.relative_to(root).parts) >= 6:
                dirs[:] = []
            else:
                dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith('.'))
            for name in sorted(names):
                file = p / name
                try:
                    real = str(file.resolve())
                    if real in seen:
                        continue
                    seen.add(real)
                    if file.suffix.lower() not in EXTS or not file.is_file() or file.stat().st_size > 2000000:
                        continue
                    nfiles += 1
                    if nfiles > 16000:
                        return hits, nfiles, True
                    if str(file.relative_to(home)) in MODEL_FILES:
                        continue
                    data = file.read_text(errors='replace')
                    if any(needle in data.lower() for needle in needles):
                        hits.append({'relative_to_home': str(file.relative_to(home)),
                                     'matched_model_reference': True,
                                     'is_spectre_input': name == 'input.scs'})
                    if len(hits) >= 80:
                        return hits, nfiles, True
                except (OSError, UnicodeError, ValueError):
                    continue
    return hits, nfiles, False


def run(home):
    results = []
    models = set()
    for rel in MODEL_FILES:
        path = home / rel
        row = {'relative_to_home': rel, 'exists': path.is_file()}
        if path.is_file():
            src = path.read_text(errors='replace')
            mods, params, tokens = concise_head(src)
            row.update({'bytes': path.stat().st_size, 'sha256':sha256(path),
                        'modules':mods, 'parameter_names':params,
                        'keyword_clues_NOT_validation':tokens})
            for mod in mods:
                models.add(mod['name'].lower())
        results.append(row)
    needles = set(('mtj_read.va', 'mtj_read_v0.va')) | models
    hits, nfiles, truncated = scan_references(home, needles)
    return {'experiment':'E11B_PRIVATE_MODEL_INTERFACE_DISCOVERY',
            'evidence_class':'SOURCE_INTERFACE_ONLY_NO_ELECTRICAL_RESULT',
            'custom_model_authorized':False,
            'valid_read_bias_or_P_AP_state':False,
            'ising_analog_field_implemented':False,
            'files_checked':nfiles, 'search_truncated':truncated,
            'models':results,'candidate_usage_files':hits,
            'next_gate':'Human-check model equations and legal read testbench before Spectre.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--home',type=Path,default=Path.home())
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():p.error('Refusing overwrite: ' + str(args.out))
    report=run(args.home)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('E11B_RESULT:',args.out)
    for row in report['models']:
        print('MODEL:',row['relative_to_home'],'exists=',row['exists'])
        if row['exists']:
            print('  sha256:',row['sha256'])
            print('  modules/ports:',row['modules'])
            print('  parameter names:',row['parameter_names'])
            print('  keyword clues ONLY:',row['keyword_clues_NOT_validation'])
    print('USAGE_FILES:',len(report['candidate_usage_files']))
    for hit in report['candidate_usage_files'][:35]:
        print('  REF:',hit['relative_to_home'], 'spectre_input=',hit['is_spectre_input'])
    print('FILES_SCANNED:',report['files_checked'],'TRUNCATED:',report['search_truncated'])
    print('E11B_STATUS: INTERFACE DISCOVERY ONLY; NO VALIDATED P/AP READ')

if __name__=='__main__':
    main()
