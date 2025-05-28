#!/usr/bin/env python3
import os
from typing import Dict, List
from datetime import datetime

from gh_utils import get_release_view
from run_commands import run_cmd


OTHER_CATEGORY = 'Other'
CHANGE_LOG_FILE = 'CHANGELOG.md'
CHANGE_LOG_LAST_HEADER_LINE = 'and this project adheres to [Semantic Versioning](http://semver.org/)'

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
    new_changelog_content.append(f'## [{version}] - {today}\n\n')

    new_changelog_content.append('\n')
    
    for category in commit_message_by_category:
        new_changelog_content.append(f'### {category}\n\n')
        for commit in commit_message_by_category[category]:
            new_changelog_content.append(f'- {commit}\n')

    new_changelog_content.append('\n')
    new_changelog_content.extend(remaining_content)

    with open(changelog_path, 'w', encoding='utf-8') as changelog_file:
        changelog_file.writelines(new_changelog_content)

    

def update_changelog(version: str, categories: Dict[str, str], exclude_prefixes: List[str]=None):
    exclude_prefixes = exclude_prefixes or []
    print('🔄 Updating changelog...'
          )
    latest_release_tag = get_release_view('tagName')
    print(f'Latest release tag: {latest_release_tag}')

    result = run_cmd(['git', 'log', '--pretty=format:%s', f'{latest_release_tag}..HEAD', '--no-merges', '--reverse'], error='Failed to get commit messages since last release.')

    commit_messages = result.stdout.strip().split('\n')
    if not commit_messages:
        raise RuntimeError('No commit messages found since the last release.')

    commit_messages = [msg for msg in commit_messages 
                       if not any(msg.strip().startswith(prefix) for prefix in exclude_prefixes)]

    commit_message_by_category = {cat: [] for cat in categories}
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


if __name__ == '__main__':
    try:

        categories={
                'feat': '🎁 New Features',
                'fix': '🐛 Bug Fixes',
                'docs': '📚 Documentation',
                'refactor': '🚜 Refactoring',
                'test': '🧪 Tests',
                'perf': '🚀 Performance Improvements',
            }

        exclude_prefixes = [
            'chore',
            'ci',
        ]

        update_changelog(categories=categories, exclude_prefixes=exclude_prefixes)

    except RuntimeError as e:
        print(f"Error: {e}")
        exit(1)
