#!/usr/bin/env python3
import sys
import subprocess
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description='Validate tag version against uv version output.')
    parser.add_argument('tag_value', help='The tag version to validate with or without the leading `v` (0.1.0/v0.1.0).')
    args = parser.parse_args()

    tag_value = args.tag_value.lstrip('v')
    print(f'🔎 Validating tag version: {tag_value} (from cli: {args.tag_value})')

    try:
        result = subprocess.run(['uv', 'version', '--output-format', 'json'], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        py_project_version = data.get('version')
        if not py_project_version:
            raise ValueError("Could not find 'version' in uv output.")

        if tag_value.count('-') > 1:
            raise ValueError(f'Tag value "{tag_value}" contains more than one hyphen.')

        tag_name_no_hyphen = tag_value.replace('-', '')

        if tag_name_no_hyphen == py_project_version:
            print(f'✅ Tag version matches: {tag_name_no_hyphen}')
            sys.exit(0)
        else:
            raise ValueError(f'Tag version mismatch: got: {tag_name_no_hyphen}, expected: {py_project_version}')
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to run 'uv version': {e}")
    except json.JSONDecodeError as e:
        raise ValueError('Failed to parse JSON output: {e}')
    except ValueError as e:
        print(f'❌ {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
