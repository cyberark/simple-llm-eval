#!/usr/bin/env bash

set -euo pipefail

VERSION=${1:-}
if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version>"
  exit 1
fi

git config user.name "github-actions"
git config user.email "github-actions@github.com"

uv run mike deploy --push --branch gh-pages "$VERSION"
uv run mike deploy --push --update-aliases "$VERSION" latest
uv run mike set-default --push latest
