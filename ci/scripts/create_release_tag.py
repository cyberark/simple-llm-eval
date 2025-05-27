#!/usr/bin/env python3
import argparse
import json
import sys
import subprocess


def run_cmd(cmd):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(description='Create a release tag from pyproject.toml version.')
    parser.add_argument('-y', '--yes', action='store_true', help='Automatically approve tag creation without prompting')
    args = parser.parse_args()

    print('🏷️ Create tag from pyproject.toml version.')

    try:
        run_cmd(['git', 'checkout', 'main'])
        run_cmd(['git', 'pull', 'origin', 'main'])

        result = run_cmd(['uv', 'version', '--output-format', 'json'])
        data = json.loads(result.stdout)
        py_project_version = data.get('version')
        if not py_project_version:
            raise ValueError("Could not find 'version' in uv output.")

        tag_name = f'v{py_project_version}'

        if args.yes:
            response = 'y'
        else:
            response = input(f'⚠️  Do you want to create a release tag `{tag_name}`? (y/N): ').strip().lower()

        if response != 'y':
            print('✋ Aborted by user.')
            sys.exit(0)

        print(f'🔖 Creating tag: {tag_name}')

        run_cmd(['git', 'tag', '-a', tag_name, '-m', f'Release version {py_project_version}'])
        run_cmd(['git', 'push', 'origin', tag_name])

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Failed to run command: {e}')
    except json.JSONDecodeError as e:
        raise RuntimeError(f'Failed to parse JSON output: {e}')
    except RuntimeError as e:
        print(f'❌ {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
