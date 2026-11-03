#!/usr/bin/env python3
"""Run from the repository root: python3 -m experiments.run --help."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
import numpy as np

from .core import GROUP_SIZES, mathematical_checks, screen, sha256, validate_contract, write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    verify = sub.add_parser('verify', help='Exact arithmetic checks, not circuit experiments')
    verify.add_argument('--out', type=Path, required=True)
    preflight = sub.add_parser('preflight', help='Show unresolved physical architecture fields')
    preflight.add_argument('--contract', type=Path, default=Path('experiments/config/architecture.template.json'))
    trace = sub.add_parser('trace-screen', help='Workload-only mapping screen on real exported traces')
    trace.add_argument('--bundle', type=Path, required=True)
    trace.add_argument('--metadata', type=Path, required=True)
    trace.add_argument('--out', type=Path, required=True)
    trace.add_argument('--group-sizes', type=int, nargs='+', choices=GROUP_SIZES, default=GROUP_SIZES)
    trace.add_argument('--seed', type=int, default=20261103)
    args = parser.parse_args()
    if args.command == 'preflight':
        contract = json.loads(args.contract.read_text())
        missing = validate_contract(contract, physical=True)
        print(json.dumps({'status': 'BLOCKED_PHYSICS' if missing else 'DECLARED_READY_FOR_VALIDATION_REVIEW',
                          'missing': missing, 'contract_sha256': sha256(args.contract),
                          'note': 'A completed declaration alone is not a verified physical experiment.'}, indent=2))
        return 2 if missing else 0
    if args.out.exists():
        parser.error('Output already exists; use a new run path')
    if args.command == 'verify':
        result = mathematical_checks()
    else:
        result = screen(args.bundle, args.metadata, args.group_sizes, args.seed)
    result['created_utc'] = datetime.now(timezone.utc).isoformat()
    result['environment'] = {'python': platform.python_version(), 'numpy': np.__version__}
    result['command_argv'] = [sys.executable, '-m', 'experiments.run', *sys.argv[1:]]
    result['implementation_sha256'] = {str(p): sha256(p) for p in
                                       (Path('experiments/core.py'), Path('experiments/run.py'))}
    write_new(args.out, result)
    print(json.dumps({'saved': str(args.out), 'evidence_class': result['evidence_class'],
                      'physical_validation': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
