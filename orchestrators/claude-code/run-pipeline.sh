#!/usr/bin/env bash
# Claude Code entrypoint for QA pipeline
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
Usage: ./orchestrators/claude-code/run-pipeline.sh [options]

Options:
  --project SLUG     Project slug for run isolation (auto-detected from config.yaml)
  --auto             Automatically launch sub-agents via Claude CLI (claude -p)
  --execute          Validate artifacts only (no launch)
  --check-auth       Check claude CLI availability
  --from-stage ID    Resume from stage
  --to-stage ID      Stop after stage
  --sync-skills      No-op (skills now read directly from .agents/skills/)
  -h, --help         Show help
EOF
}

if [[ $# -eq 0 ]]; then
  set -- --auto
fi

EXTRA=()
SYNC=false
_has_project=false

# Auto-detect project slug
_project=""
if [[ -f "${ROOT}/workspace/inputs/config.yaml" ]]; then
  _name=$(grep '^project_name:' "${ROOT}/workspace/inputs/config.yaml" 2>/dev/null | head -1 | sed 's/^project_name: *//' | tr -d '"' | xargs)
  [[ -n "$_name" ]] && _project="$_name"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --sync-skills) SYNC=true; shift ;;
    --project) EXTRA+=(--project "$2"); _has_project=true; shift 2 ;;
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

if ! $_has_project && [[ -n "$_project" ]]; then
  EXTRA=(--project "$_project" "${EXTRA[@]}")
fi

if $SYNC; then
  bash "${ROOT}/scripts/sync-skills.sh"
fi

exec "$PYTHON" "$RUNNER" --platform claude-code "${EXTRA[@]}"
