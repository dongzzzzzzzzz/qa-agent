#!/usr/bin/env bash
# Print preferred Python interpreter (venv if present)
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  echo "${ROOT}/.venv/bin/python"
else
  echo "${PYTHON:-python3}"
fi
