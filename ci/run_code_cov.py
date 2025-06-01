#!/usr/bin/env python3
import subprocess

cmd = ['pytest', '--cov=simpleval', '--cov-report=term', '--cov-report=term-missing', '--cov-report=html', '--cov-fail-under=90']
try:
    subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print('\nCommand failed with exit code:', e.returncode)
    if e.stdout:
        print('\nSTDOUT:\n', e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout)
    if e.stderr:
        print('\nSTDERR:\n', e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr)
    raise
