#!/usr/bin/env bash
# Sync skills/ to Cursor, Codex, and Claude Code skill directories.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${ROOT}/skills"

CURSOR_DEST="${ROOT}/.cursor/skills"
CODEX_DEST="${ROOT}/.codex/skills"
CLAUDE_DEST="${ROOT}/.claude/skills"
AGENTS_DEST="${ROOT}/.agents/skills"

sync_dir() {
  local dest="$1"
  mkdir -p "$dest"
  for skill in "$SRC"/*/; do
    [[ -d "$skill" ]] || continue
    name="$(basename "$skill")"
    rm -rf "${dest}/${name}"
    cp -R "$skill" "${dest}/${name}"
    echo "  synced: ${name} -> ${dest}/${name}"
  done
}

echo "Syncing skills from ${SRC}"
echo ""
echo "[Cursor] ${CURSOR_DEST}"
sync_dir "$CURSOR_DEST"
echo ""
echo "[Codex] ${CODEX_DEST}"
sync_dir "$CODEX_DEST"
echo ""
echo "[Claude Code] ${CLAUDE_DEST}"
sync_dir "$CLAUDE_DEST"
echo ""
echo "[Agents] ${AGENTS_DEST}"
sync_dir "$AGENTS_DEST"
echo ""
echo "Done. Skills are ready for sub-agents on all three platforms."
