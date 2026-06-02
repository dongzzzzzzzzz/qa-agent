#!/usr/bin/env bash
# Create venv and install Python dependencies
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  echo "Created .venv"
fi

.venv/bin/pip install -r requirements.txt
bash scripts/sync-skills.sh
.venv/bin/python scripts/validate-artifacts.py --init-meta

echo ""
echo "Setup complete. Use:"
echo "  .venv/bin/python scripts/pipeline_runner.py --platform codex"
echo "  ./orchestrators/codex/run-pipeline.sh"
