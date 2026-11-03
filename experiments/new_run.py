#!/usr/bin/env python3
"""Create a non-overwriting provenance record before an experiment."""
import argparse
from datetime import datetime, timezone
import platform
import subprocess
from pathlib import Path
from .core import sha256, write_new


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--id', required=True, help='Experiment ID from the register, e.g. E02')
    p.add_argument('--hypothesis', required=True)
    p.add_argument('--command', required=True, help='Record text only; this tool never executes it')
    p.add_argument('--input', type=Path, action='append', default=[])
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    git = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
    record = {'schema_version': 1, 'experiment_id': args.id, 'hypothesis': args.hypothesis,
              'status': 'planned', 'command': args.command,
              'created_utc': datetime.now(timezone.utc).isoformat(),
              'code_commit': git.stdout.strip() if git.returncode == 0 else None,
              'python': platform.python_version(),
              'inputs': [{'path': str(x), 'sha256': sha256(x)} for x in args.input],
              'evidence_class': None, 'results': None, 'decision': None,
              'comparators': [], 'uncertainty': None, 'limitations': [], 'follow_up': []}
    write_new(args.out, record)
    print(args.out)


if __name__ == '__main__':
    main()
