#!/usr/bin/env bash
# Claude Code entrypoint for QA pipeline
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
# shellcheck source=../lib/qa-default-mode.sh
source "${ROOT}/orchestrators/lib/qa-default-mode.sh"

if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PYTHON="${ROOT}/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi
RUNNER="${ROOT}/scripts/pipeline_runner.py"

usage() {
  cat <<'EOF'
Usage: ./orchestrators/claude-code/run-pipeline.sh [options]

Options:
  (default)          --ide-chain — IDE 内子 Agent
  --auto, --cli      CLI 无头（仅用户明确要求）
  --ide-chain        显式 IDE 链（默认）
  --execute          Validate artifacts only (no launch)
  --check-auth       Check claude CLI availability
  --from-stage ID    Resume from stage
  --to-stage ID      Stop after stage
  --sync-skills      Sync skills to .claude/skills before run
  -h, --help         Show help
EOF
}

EXTRA=()
SYNC=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --sync-skills) SYNC=true; shift ;;
  --execute) EXTRA+=(--execute); shift ;;
  --auto|--cli) EXTRA+=(--auto); shift ;;
  --ide-chain) EXTRA+=(--ide-chain); shift ;;
  --ide) EXTRA+=(--ide); shift ;;
  --check-auth) EXTRA+=(--check-auth); shift ;;
  --dry-run) EXTRA+=(--dry-run); shift ;;
    --from-stage) EXTRA+=(--from-stage "$2"); shift 2 ;;
    --to-stage) EXTRA+=(--to-stage "$2"); shift 2 ;;
    *) EXTRA+=("$1"); shift ;;
  esac
done

if $SYNC; then
  bash "${ROOT}/scripts/sync-skills.sh"
fi

exec "$PYTHON" "$RUNNER" --platform claude-code "${EXTRA[@]}"
