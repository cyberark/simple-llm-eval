#!/usr/bin/env python3

TITLE_PREFIXES_TO_LABELS = {
    'ci': 'ci',
    'feat': 'enhancement',
    'fix': 'bug',
    'docs': 'documentation',
    'refactor': 'refactoring',
    'test': 'testing',
    'chore': 'maintenance',
    'release': 'ignore-for-release',
}
BODY_TEXT_TO_LABELS = {
    '[x] Bug Fix': 'bug',
    '[x] Feature': 'enhancement',
    '[x] Documentation': 'documentation',
    '[x] Update Dependencies': 'dependencies',
    '[x] CICD / DevOps': 'ci',
}

import json
import os

def propose_labels_from_env():
    pr_title = os.environ.get('PR_TITLE', '')
    pr_body = os.environ.get('PR_BODY', '')
    labels = set()

    # Check body for labels
    for text, label in BODY_TEXT_TO_LABELS.items():
        if text in pr_body:
            labels.add(label)

    # Check title for labels
    title = pr_title.strip()
    for prefix, label in TITLE_PREFIXES_TO_LABELS.items():
        if title.lower().startswith(f'{prefix}:') or title.lower().startswith(f'{prefix}('):
            labels.add(label)

    return list(labels)

if __name__ == '__main__':
    labels = propose_labels_from_env()
    print(json.dumps(labels))
