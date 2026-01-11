#!/usr/bin/env python3
import subprocess
import sys


def run_command(cmd, description=None):
    if description:
        print(description)
    try:
        subprocess.run(cmd, shell=True, check=True, cwd='reports-frontend')
        print()
    except subprocess.CalledProcessError as e:
        print(f'Command failed: {cmd}')
        sys.exit(e.returncode)

def main():
    run_command(
        cmd='npm install',
        description='Installing react reports dependencies...'
    )

    run_command(
        cmd='npm run build',
        description='Building react reports...'
    )

    run_command(
        cmd='npm audit --audit-level=low',
        description='Running npm audit (to fix run npm audit fix in `reports-frontend`)...'
    )

    run_command(
        cmd='npm run test-no-watch',
        description='Running npm test (once, no watch)...'
    )

if __name__ == '__main__':
    main()
