#!/usr/bin/env bash

set -euo pipefail

VERSION=${1:-}
if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version>"
  exit 1
fi

# Only set the bot identity when nothing is configured (e.g. CI). Preserve any
# existing local/global user.name and user.email (e.g. when run by a maintainer).
existing_name=$(git config user.name 2>/dev/null || true)
if [[ -z "$existing_name" ]]; then
  git config user.name "github-actions[bot]"
fi

existing_email=$(git config user.email 2>/dev/null || true)
if [[ -z "$existing_email" ]]; then
  git config user.email "github-actions[bot]@users.noreply.github.com"
fi

uv run mike deploy --push --branch gh-pages "$VERSION"
uv run mike deploy --push --update-aliases "$VERSION" latest
uv run mike set-default --push latest
