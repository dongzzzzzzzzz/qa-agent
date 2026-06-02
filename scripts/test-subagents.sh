#!/usr/bin/env bash
# Smoke/self test wrapper. The Python selftest uses temporary artifact dirs and
# does not write to workspace/artifacts.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PYTHON="${ROOT}/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

exec "$PYTHON" "${ROOT}/scripts/selftest.py"
