#!/usr/bin/env bash
# Cursor CLI wrapper — uses Node tsx runner when available, else Python runner only
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Auto-detect project slug from workspace/inputs/config.yaml if not passed explicitly
_project=""
_has_project=false
for _a in "$@"; do
  case "$_a" in --project) _has_project=true ;; esac
done
if ! $_has_project && [[ -f "${ROOT}/workspace/inputs/config.yaml" ]]; then
  _name=$(grep '^project_name:' "${ROOT}/workspace/inputs/config.yaml" 2>/dev/null | head -1 | sed 's/^project_name: *//' | tr -d '"' | xargs)
  if [[ -n "$_name" ]]; then
    _project="$_name"
  fi
fi

# 未显式指定模式时默认 --ide-chain（IDE 内 Task 子 Agent 可见）
# Cursor --auto 须 --allow-cli 或 QA_PIPELINE_ALLOW_CLI=1（见 pipeline_runner.py）
_has_mode=false
_want_auto=false
for _a in "$@"; do
  case "$_a" in
    --auto) _want_auto=true ;;
    --auto|--ide-chain|--execute|--dry-run|--ide|--check-auth) _has_mode=true ;;
  esac
done
if $_want_auto && [[ "${QA_PIPELINE_ALLOW_CLI:-}" != "1" ]]; then
  _has_allow=false
  for _a in "$@"; do
    case "$_a" in --allow-cli) _has_allow=true ;; esac
  done
  if ! $_has_allow; then
    echo "ERROR: run-pipeline.sh --auto 已禁用（默认 ide-chain）。" >&2
    echo "  跑流水线: $0 [--project <slug>]" >&2
    echo "  维护者无头: QA_PIPELINE_ALLOW_CLI=1 $0 --auto --allow-cli" >&2
    exit 1
  fi
fi
if ! $_has_mode; then
  set -- --ide-chain "$@"
fi

# Inject --project if auto-detected and not already passed
if [[ -n "$_project" ]] && ! $_has_project; then
  set -- --project "$_project" "$@"
fi

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
