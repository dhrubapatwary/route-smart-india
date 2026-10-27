#!/usr/bin/env bash
# Regression check for .gitignore: source paths must stay visible, while
# generated root-level artefacts must stay ignored. Uses --no-index so it
# tests the rules without needing the paths to exist.
set -euo pipefail
cd "$(dirname "$0")/.."

must_not_ignore=(
  src/routesmart/reports/summary.py
  src/routesmart/build/plan.py
  src/routesmart/dist/x.py
  tests/reports/test_x.py
  docs/build/notes.md
  .env.example
)
must_ignore=(
  build/lib/x.py
  dist/pkg.whl
  reports/bandit.json
  .env
  .env.local
  route_smart_env/bin/python
  src/routesmart/__pycache__/x.pyc
  .coverage
)

status=0
for path in "${must_not_ignore[@]}"; do
  if git check-ignore --no-index -q "$path"; then
    echo "check-gitignore: source path is ignored: $path" >&2
    status=1
  fi
done
for path in "${must_ignore[@]}"; do
  if ! git check-ignore --no-index -q "$path"; then
    echo "check-gitignore: generated/secret path is NOT ignored: $path" >&2
    status=1
  fi
done
[ "$status" -eq 0 ] && echo "check-gitignore: ok (${#must_not_ignore[@]} visible, ${#must_ignore[@]} ignored)"
exit "$status"
