#!/usr/bin/env python3
"""Check the Git-tracked source payload before publication.

Added 2026-10-15. GNU GPL version 3 or later; see LICENSE.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    names = [name for name in names if name]
    if not names:
        raise SystemExit('No tracked or staged files. Stage the source files before checking.')
    issues = []
    forbidden = ('dat/IMGTHLA/', 'dat/ref/', 'bin/', 'build/', 'test/fixtures/',
                 '.codex-repair-backup-', '__pycache__/', 'hla_results/')
    personal = re.compile(rb'/(?:Users|home)/[A-Za-z0-9_.-]+/')
    for name in names:
        path = ROOT / name
        if name.startswith(forbidden) or name == 'dat/info/hla_freq.tsv':
            issues.append(name + ': runtime data or binary directory')
        data = subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT)
        if len(data) > 5_000_000:
            issues.append(name + ': unexpected large file')
        if b'\0' in data:
            issues.append(name + ': unexpected binary content')
        if personal.search(data):
            issues.append(name + ': personal absolute path')
        if path.suffix in {'.bam', '.bai', '.idx', '.pyc', '.p', '.log'} or name.endswith('.fq.gz'):
            issues.append(name + ': generated or dataset file')
    if issues:
        raise SystemExit('\n'.join(issues))
    total = sum(len(subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT)) for name in names)
    print(f'Upload check passed: {len(names)} source/documentation files, {total:,} bytes.')


if __name__ == '__main__':
    main()
