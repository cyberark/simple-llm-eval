#!/usr/bin/env python3

import os
import sys
import subprocess
import json
import argparse
import time
import glob
import re

from colorama import Fore

from gh_utils import get_pr_info
from run_commands import run_cmd
from update_changelog import update_changelog


# Stable release tag: vX.Y.Z (no pre-release suffix).
# Per docs, only stable releases publish docs.
STABLE_TAG_RE = re.compile(r'^v?\d+\.\d+\.\d+$')


def get_current_version():
    """Run 'uv version --output-format json' and return the current version as a string."""
    result = run_cmd(['uv', 'version', '--output-format', 'json'])
    try:
        return json.loads(result.stdout).get('version')
    except json.JSONDecodeError as e:
        raise RuntimeError(f'{Fore.RED}Failed to parse JSON output: {e}{Fore.RESET}')


def open_link(link):
    if sys.platform == 'darwin':
        run_cmd(['open', link])
    elif sys.platform == 'win32':
        run_cmd(['start', link], do_not_fail=True)
    else:
        run_cmd(['xdg-open', link], do_not_fail=True)

def wait_for_human_approval_and_merge(pr_link, pr_number):
    print(f'{Fore.GREEN}🦖 PR checks passed, merging like a peasant{Fore.RESET}')
    print(f'{Fore.YELLOW}🔄 Waiting for PR human approval and merge, approve, merge and come back here...{Fore.RESET}')

    open_link(pr_link)

    pr_state = 'OPEN'
    while pr_state == 'OPEN':
        time.sleep(10)
        pr_state = get_pr_info(pr_number, 'state')

    if pr_state != 'MERGED':
        raise RuntimeError(f'{Fore.RED}PR was not merged, please try again.{Fore.RESET}')


def build_and_release(tag_name: str, version: str, publish_docs: bool, sign: bool):
    """Mirror the release steps documented in docs/maintainers/version-release.md.

    Per docs the release does: validate version vs tag, build the package,
    create the GitHub release with binaries, and (optionally) publish the docs.
    PyPI publish is intentionally omitted (docs say it's manual).
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = run_cmd(['git', 'rev-parse', '--show-toplevel']).stdout.strip()
    dist_dir = os.path.join(repo_root, 'dist')

    print(f'{Fore.YELLOW}🔎 Validating tag value against pyproject.toml...{Fore.RESET}')
    run_cmd([sys.executable, os.path.join(script_dir, 'validate_tag.py'), tag_name])

    # Clean dist/ so stale artifacts from a previous build aren't attached to the release.
    for path in glob.glob(os.path.join(dist_dir, '*')):
        os.remove(path)

    print(f'{Fore.YELLOW}📦 Building project package...{Fore.RESET}')
    run_cmd(['uv', 'build'])

    if sign:
        artifacts = sorted(
            glob.glob(os.path.join(dist_dir, '*.whl')) + glob.glob(os.path.join(dist_dir, '*.tar.gz'))
        )
        if not artifacts:
            raise RuntimeError('No artifacts found in dist/ to sign.')
        print(f'{Fore.YELLOW}🔏 Signing the wheel(s)...{Fore.RESET}')
        for artifact in artifacts:
            run_cmd(['gpg', '--batch', '--yes', '--armor', '--detach-sign', artifact])
    else:
        print(f'{Fore.YELLOW}🔏 Skipping artifact signing (pass --sign to enable).{Fore.RESET}')

    release_files = sorted(glob.glob(os.path.join(dist_dir, '*')))
    if not release_files:
        raise RuntimeError('No artifacts found in dist/ to attach to the release.')

    print(f'{Fore.YELLOW}📝 Creating GitHub release {tag_name}...{Fore.RESET}')
    run_cmd([
        'gh', 'release', 'create', tag_name,
        '--title', tag_name,
        '--generate-notes',
        '--verify-tag',
        *release_files,
    ])

    if not publish_docs:
        print(f'{Fore.YELLOW}📚 Skipping docs publish (pass --publish-docs to enable).{Fore.RESET}')
        return

    if not STABLE_TAG_RE.match(tag_name):
        print(f'{Fore.YELLOW}📚 Skipping docs publish: {tag_name} is not a stable release ([v]X.Y.Z).{Fore.RESET}')
        return

    print(f'{Fore.YELLOW}📚 Publishing docs for {version}...{Fore.RESET}')
    run_cmd([os.path.join(script_dir, 'publish_docs.sh'), version])


def main():
    try:
        parser = argparse.ArgumentParser(description='Manual release procedure: bump version, open PR, merge, tag, build and create the GitHub release.')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--version', type=str, help='Set version to a specific value')
        group.add_argument('--bump-patch', action='store_true', help='Bump patch version')
        group.add_argument('--bump-minor', action='store_true', help='Bump minor version')
        group.add_argument('--bump-major', action='store_true', help='Bump major version')
        parser.add_argument('--publish-docs', action='store_true', default=False,
                            help='Publish docs after the GitHub release is created. Only effective for stable [v]X.Y.Z releases. Off by default.')
        parser.add_argument('--sign', action='store_true', default=False,
                            help='GPG-sign the built artifacts (requires a configured GPG key). Off by default.')
        args = parser.parse_args()

        print(f'{Fore.YELLOW}🔧 Update version in pyproject.toml.{Fore.RESET}')

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
        elif args.bump_patch:
            run_cmd(['uv', 'version', '--bump', 'patch'])
        elif args.bump_minor:
            run_cmd(['uv', 'version', '--bump', 'minor'])
        elif args.bump_major:
            run_cmd(['uv', 'version', '--bump', 'major'])
        else:
            raise ValueError('No valid version argument provided.')

        new_version = get_current_version()

        run_cmd(['uv', 'sync'])

        update_changelog(version=new_version)

        run_cmd(['git', 'add', 'pyproject.toml'])
        run_cmd(['git', 'add', 'uv.lock'])
        run_cmd(['git', 'add', 'CHANGELOG.md'])

        run_cmd(['git', 'commit', '-m', f'Bump version to {new_version}'])
        run_cmd(['git', 'push', '--set-upstream', 'origin', version_branch_name])

        pr_title = f'chore: 🤖 Bump version to {new_version}'
        pr_body = f'## Summary \n\nBump version to {new_version}'

        print(f'{Fore.YELLOW}📝 Creating PR with title: {pr_title}{Fore.RESET}')
        result = run_cmd(['gh', 'pr', 'create', '--title', pr_title, '--body', pr_body])
        pr_number = result.stdout.strip().split('/')[-1]

        pr_link = result.stdout.strip()
        print(f'{Fore.YELLOW}⏰ Waiting for PR checks for be published, check PR to see status: {pr_link}{Fore.RESET}')
        time.sleep(10)
        run_cmd(['gh', 'pr', 'checks', pr_number, '--watch'], do_not_fail=True)
        run_cmd(['gh', 'pr', 'checks', pr_number, '--watch', '--fail-fast'], error='PR checks failed, please fix the issues and try again.')

        if os.environ.get('BOSS_MODE', '0') == '1':
            print(f'🦖 PR checks passed, merging like a boss')
            run_cmd(['gh', 'pr', 'merge', pr_number, '--squash', '--admin'])
        else:
            wait_for_human_approval_and_merge(pr_link, pr_number)

        print(f'{Fore.GREEN}🎉 Version PR created and merged successfully!{Fore.RESET}')

        time.sleep(2)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        release_tag_script = os.path.join(script_dir, 'create_release_tag.py')
        run_cmd([sys.executable, release_tag_script, '--yes'])

        print(f'{Fore.GREEN}🚀 Release tag created successfully!{Fore.RESET}')

        tag_name = f'v{new_version}'
        build_and_release(tag_name=tag_name, version=new_version, publish_docs=args.publish_docs, sign=args.sign)

        print(f'{Fore.GREEN}🎉 Release {tag_name} completed successfully!{Fore.RESET}')
        print(f'{Fore.CYAN}Release URL: https://github.com/cyberark/simple-llm-eval/releases/tag/{tag_name}{Fore.RESET}')

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Failed to run command: {e}')
    except RuntimeError as e:
        print(f'{Fore.RED}❌ {e}{Fore.RESET}')
        sys.exit(1)

if __name__ == '__main__':
    main()
