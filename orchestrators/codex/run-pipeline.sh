#!/usr/bin/env bash
# Codex entrypoint for QA pipeline
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PYTHON="${ROOT}/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi
RUNNER="${ROOT}/scripts/pipeline_runner.py"

usage() {
  cat <<'EOF'
Usage: ./orchestrators/codex/run-pipeline.sh [options]

Options:
  --auto             Automatically launch sub-agents via Codex CLI (codex exec)
  --execute          Validate artifacts only (no launch)
  --check-auth       Check codex CLI availability
  --dry-run          Print/write stage prompts only (default)
  --from-stage ID    Resume from stage (default: prd-analyze)
  --to-stage ID      Stop after stage
  --sync-skills      No-op (skills now read directly from .agents/skills/)
  -h, --help         Show help

Examples:
  ./orchestrators/codex/run-pipeline.sh
  ./orchestrators/codex/run-pipeline.sh --execute
  ./orchestrators/codex/run-pipeline.sh --from-stage case-generate --execute
EOF
}

# 无参数：默认自动拉起各阶段子 Agent
if [[ $# -eq 0 ]]; then
  set -- --auto
fi

EXTRA=()
SYNC=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --sync-skills) SYNC=true; shift ;;
  --execute) EXTRA+=(--execute); shift ;;
  --auto) EXTRA+=(--auto); shift ;;
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

exec "$PYTHON" "$RUNNER" --platform codex "${EXTRA[@]}"
