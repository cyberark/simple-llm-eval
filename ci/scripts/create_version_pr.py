#!/usr/bin/env python3

import sys
import subprocess
import json
import argparse

def run_cmd(cmd, do_not_fail=False):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print(result.stdout)
    if not do_not_fail and result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result

def main():

    parser = argparse.ArgumentParser(description='Create version PR from pyproject.toml version.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--version', type=str, help='Set version to a specific value')
    group.add_argument('--bump-path', action='store_true', help='Bump patch version')
    group.add_argument('--bump-minor', action='store_true', help='Bump minor version')
    group.add_argument('--bump-major', action='store_true', help='Bump major version')
    args = parser.parse_args()


    print('🔧 Update version in pyproject.toml.')

    run_cmd(['git', 'checkout', 'main'])
    run_cmd(['git', 'pull', 'origin', 'main'])

    # Delete the version branch if it exists
    run_cmd(['git', 'branch', '-d', version_branch_name], do_not_fail=True)
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

    result = run_cmd(['uv', 'version', '--output-format', 'json'])
    new_version = json.loads(result.stdout).get('version')

    version_branch_name = f'release/bump-version-{new_version}'

    result = run_cmd(['uv', 'sync'])

    run_cmd(['git', 'add', 'pyproject.toml'])
    run_cmd(['git', 'add', 'uv.lock'])

    run_cmd(['git', 'commit', '-m', f'Bump version to {new_version}'])
    run_cmd(['git', 'push'])

    try:
        # Placeholder for logic using args
        pass
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Failed to run command: {e}')
    except json.JSONDecodeError as e:
        raise RuntimeError(f'Failed to parse JSON output: {e}')
    except RuntimeError as e:
        print(f'❌ {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
