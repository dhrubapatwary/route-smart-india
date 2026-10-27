#!/usr/bin/env bash
# Two-stage, hash-verified install of requirements/dev.lock.txt.
#
# Stage 1: the interpreter's *existing* pip (whatever version the environment
#          ships, e.g. the GitHub runner's) installs ONLY the pinned pip from
#          the lock, with --require-hashes and --no-deps.
# Stage 2: the now-pinned pip installs the full lock with --require-hashes.
#
# So every package except pip itself is installed by the pinned pip, and pip
# itself is hash-verified. The bootstrap pip version is printed, not assumed.
#
# Usage: [PYTHON=/path/to/python] scripts/install-locked.sh
set -euo pipefail

cd "$(dirname "$0")/.."
lock=requirements/dev.lock.txt

requested_python="${PYTHON:-python}"
if ! python_bin="$(command -v -- "$requested_python")"; then
  echo "install-locked: Python interpreter not found: '${requested_python}' (set PYTHON=/path/to/python)" >&2
  exit 2
fi

pip_pin_file="$(mktemp)"
trap 'rm -f "$pip_pin_file"' EXIT
# The pip block is "pip==X \" followed by "--hash=... \" lines; the last hash line has no "\".
awk '/^pip==/{found=1} found{print; if ($0 !~ /\\$/) exit}' "$lock" > "$pip_pin_file"
expected_pip="$(sed -n 's/^pip==\([^ ]*\).*/\1/p' "$pip_pin_file")"
if [ -z "$expected_pip" ] || ! grep -q -- '--hash=sha256:' "$pip_pin_file"; then
  echo "install-locked: no hashed pip pin found in ${lock}" >&2
  exit 2
fi

echo "install-locked: stage 1 bootstrap pip: $("$python_bin" -m pip --version)" >&2
"$python_bin" -m pip install --require-hashes --no-deps -r "$pip_pin_file"

actual_pip="$("$python_bin" -m pip --version | awk '{print $2}')"
if [ "$actual_pip" != "$expected_pip" ]; then
  echo "install-locked: expected pip ${expected_pip} after stage 1, found ${actual_pip}" >&2
  exit 1
fi
echo "install-locked: stage 2 installing ${lock} with pinned pip ${actual_pip}" >&2
"$python_bin" -m pip install --require-hashes -r "$lock"
