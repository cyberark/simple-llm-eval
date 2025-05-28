#!/usr/bin/env python3
import argparse
import os
import re
from typing import Dict, List
from datetime import datetime

from gh_utils import get_pr_info, get_release_view
from run_commands import run_cmd


OTHER_CATEGORY = 'Other'
CHANGE_LOG_FILE = 'CHANGELOG.md'
CHANGE_LOG_LAST_HEADER_LINE = 'and this project adheres to [Semantic Versioning](http://semver.org/)'

DEFAULT_CATEGORIES={
    'feat': '🎁 New Features',
    'fix': '🐛 Bug Fixes',
    'docs': '📚 Documentation',
    'refactor': '🚜 Refactoring',
    'test': '🧪 Tests',
    'perf': '🚀 Performance Improvements',
},

DEFAULT_EXCLUDE_PREFIXES = [
    'chore',
    'ci',
    'release'
]

def update_changelog_from_commits(version: str, commit_message_by_category: Dict[str, List[str]]):
    root_path = run_cmd(['git', 'rev-parse', '--show-toplevel'], error='Failed to get root path of the repository.').stdout.strip()
    changelog_path = os.path.join(root_path, CHANGE_LOG_FILE)
    print(f'Changelog path: {changelog_path}')

    with open(changelog_path, 'r+', encoding='utf-8') as changelog_file:
        changelog_content = changelog_file.readlines()

    new_changelog_content = []
    remaining_content = []

    header_index = next((i for i, line in enumerate(changelog_content) if CHANGE_LOG_LAST_HEADER_LINE in line), -1)
    if header_index == -1:
        raise RuntimeError(f'Could not find the header line "{CHANGE_LOG_LAST_HEADER_LINE}" in {CHANGE_LOG_FILE}.')

    new_changelog_content.extend(changelog_content[:header_index + 1])
    new_changelog_content.append('\n')
    remaining_content = changelog_content[header_index + 1:]

    today = datetime.now().strftime('%Y-%m-%d')
    new_changelog_content.append(f'## [{version}] - {today}\n')

    new_changelog_content.append('\n')

    for category in commit_message_by_category:
        if not commit_message_by_category[category]:
            continue

        new_changelog_content.append(f'### {category}\n\n')
        for commit in commit_message_by_category[category]:
            commit = commit.strip()
            pr_link, pr_number = get_pr_link(commit)
            if pr_link and pr_number:
                commit = commit.replace(pr_number, f'[{pr_number}]({pr_link})')
            new_changelog_content.append(f'- {commit}\n')

        new_changelog_content.append('\n')

    new_changelog_content.extend(remaining_content)

    with open(changelog_path, 'w', encoding='utf-8') as changelog_file:
        changelog_file.writelines(new_changelog_content)


def get_pr_link(commit_message: str) -> str:
    url = None
    pr_number = None

    try:
        match = re.search(r'#(\d+)', commit_message)
        if match:
            pr_number = match.group(0)
            print(f'Found PR number: {pr_number} in commit message: {commit_message}')
            url = get_pr_info(pr_number, 'url')
    except:
        url = None
        print(f'Failed to get PR link for commit message: {commit_message}')

    return url, pr_number


def update_changelog(version: str, categories: Dict[str, str]=None, exclude_prefixes: List[str]=None):
    categories = categories or DEFAULT_CATEGORIES
    exclude_prefixes = exclude_prefixes or DEFAULT_EXCLUDE_PREFIXES

    print('🔄 Updating changelog...')
    latest_release_tag = get_release_view('tagName')
    print(f'Latest release tag: {latest_release_tag}')

    result = run_cmd(['git', 'log', '--pretty=format:%s', f'{latest_release_tag}..HEAD', '--no-merges', '--reverse'], error='Failed to get commit messages since last release.')

    commit_messages = result.stdout.strip().split('\n')
    if not commit_messages:
        raise RuntimeError('No commit messages found since the last release.')

    commit_messages = [msg for msg in commit_messages
                       if not any(msg.strip().startswith(prefix) for prefix in exclude_prefixes)]

    commit_message_by_category = {}
    commit_message_by_category[OTHER_CATEGORY] = []
    for commit_message in commit_messages:
        # Extract prefix until colon or '('
        msg = commit_message.strip()
        prefix = None
        for sep in (':', '('):
            if sep in msg:
                prefix = msg.split(sep, 1)[0].strip()
                break
        if prefix is None:
            prefix = msg.split()[0] if msg else ''
        if prefix in categories:
            commit_message_by_category[prefix].append(commit_message)
        else:
            commit_message_by_category[OTHER_CATEGORY].append(commit_message)


    update_changelog_from_commits(version, commit_message_by_category)
    print(f'✅ Changelog updated for version {version}.')


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Update changelog from commit messages since the last release.')
        parser.add_argument('--version', required=True, type=str, help=f'New changelog version')
        args = parser.parse_args()

        update_changelog(version=args.version)
    except RuntimeError as e:
        print(f'Error: {e}')
        exit(1)
