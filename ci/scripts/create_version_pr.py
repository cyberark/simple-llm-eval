#!/usr/bin/env python3

import sys
import subprocess
import json
import argparse
import time

def run_cmd(cmd, do_not_fail=False, error=''):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print(result.stdout)
    if not do_not_fail and result.returncode != 0:
        raise RuntimeError(f'{result.stderr} | {error}')
    return result


def get_current_version():
    """Run 'uv version --output-format json' and return the current version as a string."""
    result = run_cmd(['uv', 'version', '--output-format', 'json'])
    try:
        return json.loads(result.stdout).get('version')
    except json.JSONDecodeError as e:
        raise RuntimeError(f'Failed to parse JSON output: {e}')

def main():
    try:
        parser = argparse.ArgumentParser(description='Create version PR from pyproject.toml version.')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--version', type=str, help='Set version to a specific value')
        group.add_argument('--bump-path', action='store_true', help='Bump patch version')
        group.add_argument('--bump-minor', action='store_true', help='Bump minor version')
        group.add_argument('--bump-major', action='store_true', help='Bump major version')
        args = parser.parse_args()


        print('🔧 Update version in pyproject.toml.')

        current_version = get_current_version()
        version_branch_name = f'release/bump-version-{current_version}'

        run_cmd(['git', 'diff', '--quiet'], error='There are uncommitted changes, cannot proceed.')

        run_cmd(['git', 'checkout', 'main'])
        run_cmd(['git', 'pull', 'origin', 'main'])

        # Delete the version branch if it exists
        run_cmd(['git', 'branch', '-d', version_branch_name], do_not_fail=True)
        run_cmd(['git', 'push', 'origin', '--delete', version_branch_name], do_not_fail=True)

        # Create a new version branch
        run_cmd(['git', 'checkout', '-b', version_branch_name], do_not_fail=True)

        if args.version:
            run_cmd(['uv', 'version', args.version])
        elif args.bump_path:
            run_cmd(['uv', 'version', '--bump', 'patch'])
        elif args.bump_minor:
            run_cmd(['uv', 'version', '--bump', 'minor'])
        elif args.bump_major:
            run_cmd(['uv', 'version', '--bump', 'major'])
        else:
            raise ValueError('No valid version argument provided.')

        new_version = get_current_version()

        run_cmd(['uv', 'sync'])

        run_cmd(['git', 'add', 'pyproject.toml'])
        run_cmd(['git', 'add', 'uv.lock'])

        run_cmd(['git', 'commit', '-m', f'Bump version to {new_version}'])
        run_cmd(['git', 'push'])

        pr_title = f'chore: 🤖 Bump version to {new_version}'
        pr_body = f'## Summary \n\nBump version to {new_version}'

        print(f'📝 Creating PR with title: {pr_title}')
        result = run_cmd(['gh', 'pr', 'create', '--title', pr_title, '--body', pr_body])
        pr_number = result.stdout.strip().split('/')[-1]

        print(f'⏰ Waiting for PR checks for be published, check PR to see status: {result.stdout.strip()}')
        time.sleep(10)
        run_cmd(['gh', 'pr', 'checks', pr_number, '--watch'], do_not_fail=True)
        run_cmd(['gh', 'pr', 'checks', pr_number, '--watch', '--fail-fast'], error='PR checks failed, please fix the issues and try again.')
        
        print(f'🦖 PR checks passed, merging like a boss')
        run_cmd(['gh', 'pr', 'merge', pr_number, '--admin'])
        print('🎉 Version PR created and merged successfully!')

        time.sleep(2)

        

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Failed to run command: {e}')
    except RuntimeError as e:
        print(f'❌ {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
