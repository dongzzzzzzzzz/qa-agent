#!/usr/bin/env bash
# Cursor CLI wrapper — uses Node tsx runner when available, else Python runner only
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
# shellcheck source=../lib/qa-default-mode.sh
source "${ROOT}/orchestrators/lib/qa-default-mode.sh"

if command -v npx >/dev/null 2>&1 && [[ -f "${ROOT}/orchestrators/cursor/run-pipeline.ts" ]]; then
  cd "${ROOT}/orchestrators/cursor"
  if [[ ! -d node_modules ]]; then
    npm install --no-fund --no-audit 2>/dev/null || true
  fi
  exec npx tsx run-pipeline.ts "$@"
else
  PY="${ROOT}/.venv/bin/python"
  [[ -x "$PY" ]] || PY=python3
  exec "$PY" "${ROOT}/scripts/pipeline_runner.py" --platform cursor "$@"
fi
