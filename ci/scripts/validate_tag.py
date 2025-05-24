#!/usr/bin/env python3
import sys
import subprocess
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description='Validate tag version against uv version output.')
    parser.add_argument('tag_value', help='The tag version to validate (e.g., v0.1.0)')
    args = parser.parse_args()

    try:
        result = subprocess.run(['uv', 'version', '--output-format', 'json'], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        version = data.get('version')
        if not version:
            raise ValueError("Could not find 'version' in uv output.")

        expected_tag = f'v{version}'
        if args.tag_value == expected_tag:
            print(f'✅ Tag version matches: {args.tag_value}')
            sys.exit(0)
        else:
            raise ValueError(f'Tag version mismatch: got {args.tag_value}, expected {expected_tag}')
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to run 'uv version': {e}")
    except json.JSONDecodeError as e:
        raise ValueError('Failed to parse JSON output: {e}')
    except ValueError as e:
        print(f'❌ {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
