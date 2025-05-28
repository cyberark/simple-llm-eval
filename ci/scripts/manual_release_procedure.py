#!/usr/bin/env python3

import os
import sys
import subprocess
import json
import argparse
import time

from colorama import Fore

from gh_utils import get_pr_info
from run_commands import run_cmd
from update_changelog import update_changelog


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



def main():
    try:
        parser = argparse.ArgumentParser(description='Create version PR from pyproject.toml version.')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--version', type=str, help='Set version to a specific value')
        group.add_argument('--bump-patch', action='store_true', help='Bump patch version')
        group.add_argument('--bump-minor', action='store_true', help='Bump minor version')
        group.add_argument('--bump-major', action='store_true', help='Bump major version')
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

        run_cmd(['git', 'add', 'pyproject.toml'])
        run_cmd(['git', 'add', 'uv.lock'])

        run_cmd(['git', 'commit', '-m', f'Bump version to {new_version}'])
        run_cmd(['git', 'push'])

        pr_title = f'chore: 🤖 Bump version to {new_version}'
        pr_body = f'## Summary \n\nBump version to {new_version}'

        update_changelog(version=new_version)

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
        print(f'{Fore.CYAN}Check out the release workflow: https://github.com/cyberark/simple-llm-eval/actions/workflows/release.yml{Fore.RESET}')

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Failed to run command: {e}')
    except RuntimeError as e:
        print(f'{Fore.RED}❌ {e}{Fore.RESET}')
        sys.exit(1)

if __name__ == '__main__':
    update_changelog()
    # main()
