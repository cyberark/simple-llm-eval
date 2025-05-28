#!/usr/bin/env python3
import re
import sys
import subprocess
import json
import argparse

from colorama import Fore

from run_commands import run_cmd


ALLOWED_VERSION_BUMPS = ['bump-patch', 'bump-minor', 'bump-major', 'provide-version']


def validate_version(version):

    if not version:
        raise ValueError(f'Version is required when using --version-bump="provide-version"')

    if len(version) > 30:
        raise ValueError(f'Version is too long, must be less than 30 characters.')

    if not re.match(r'^\d+\.\d+\.\d+.*$', version):
        raise ValueError(f'Invalid version: allowed format: x.y.z or x.y.z<pre-release-name>')


def get_current_version():
    """Run 'uv version --output-format json' and return the current version as a string."""
    result = run_cmd(['uv', 'version', '--output-format', 'json'])
    try:
        return json.loads(result.stdout).get('version')
    except json.JSONDecodeError as e:
        raise RuntimeError(f'{Fore.RED}Failed to parse JSON output: {e}{Fore.RESET}')


def main():
    try:
        parser = argparse.ArgumentParser(description='Bump or set version in pyproject.toml')
        parser.add_argument('--version-bump', type=str, choices=ALLOWED_VERSION_BUMPS, help=f'One of {ALLOWED_VERSION_BUMPS}')
        parser.add_argument('--version', required=False, default='', type=str, help=f'Specific version to set (requires version-bump="provide-version"')
        parser.add_argument('--commit-changes', action='store_true', default=False, help='Commit and push changes after bumping version')
        args = parser.parse_args()

        if args.version_bump == 'provide-version':
            validate_version(args.version)

        print(f'{Fore.YELLOW}🔧 Update version in pyproject.toml.{Fore.RESET}')

        if args.version_bump == 'bump-patch':
            run_cmd(['uv', 'version', '--bump', 'patch'])
        elif args.version_bump == 'bump-minor':
            run_cmd(['uv', 'version', '--bump', 'minor'])
        elif args.version_bump == 'bump-major':
            run_cmd(['uv', 'version', '--bump', 'major'])
        elif args.version_bump == 'provide-version':
            run_cmd(['uv', 'version', args.version])
        else:
            raise ValueError(f'Invalid version bump type: {args.version_bump}. Allowed values are: {ALLOWED_VERSION_BUMPS}')

        print(f'{Fore.GREEN}✅ Version updated successfully.{Fore.RESET}')

        new_version = get_current_version()

        run_cmd(['uv', 'sync'])

        if args.commit_changes:
            run_cmd(['git', 'add', 'pyproject.toml'])
            run_cmd(['git', 'add', 'uv.lock'])

            run_cmd(['git', 'commit', '-m', f'Bump version to {new_version}'])
            run_cmd(['git', 'push'])

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Failed to run command: {e}')
    except RuntimeError as e:
        print(f'{Fore.RED}❌ {e}{Fore.RESET}')
        sys.exit(1)

if __name__ == '__main__':
    main()
