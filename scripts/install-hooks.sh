#!/usr/bin/env bash
# Point this clone's git hooks at the tracked .githooks/ directory.
# Run once after cloning:  ./scripts/install-hooks.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

git config core.hooksPath .githooks
chmod +x .githooks/* 2>/dev/null || true

echo "Hooks enabled: core.hooksPath -> .githooks"
echo "Active: pre-commit (README-coverage guard for skills/ and automations/)"
