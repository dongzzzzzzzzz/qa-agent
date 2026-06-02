#!/usr/bin/env python3
"""
Parse workspace/inputs/figma.url and emit figma-snapshot.json for prd-analyzer.

Does not call Figma API directly — sub-agent still uses Figma MCP per
skills/prd-analyze/reference-figma-analysis.md. This script records URLs,
file keys, node ids, and a checklist for MCP follow-up.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
FIGMA_URL_FILE = ROOT / "workspace" / "inputs" / "figma.url"
OUT = ROOT / "workspace" / "artifacts" / "figma-snapshot.json"

FIGMA_DESIGN_RE = re.compile(
    r"figma\.com/(?:design|file|board)/([A-Za-z0-9]+)",
    re.I,
)


def parse_figma_line(line: str) -> dict | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if "figma.com" not in line.lower():
        return {"raw": line, "valid": False, "reason": "not a figma.com URL"}

    parsed = urlparse(line)
    qs = parse_qs(parsed.query)
    node_raw = (qs.get("node-id") or [""])[0]
    node_id = node_raw.replace("-", ":") if node_raw else ""

    file_key = ""
    m = FIGMA_DESIGN_RE.search(line)
    if m:
        file_key = m.group(1)

    return {
        "url": line,
        "file_key": file_key,
        "node_id": node_id,
        "valid": bool(file_key),
        "mcp_checklist": [
            "get_metadata(fileKey, nodeId)",
            "get_design_context(fileKey, nodeId)",
            "get_screenshot(fileKey, nodeId) for empty/error/disabled frames",
        ],
        "frames_pending": [],
    }


def load_urls() -> list[str]:
    if not FIGMA_URL_FILE.exists():
        return []
    lines = FIGMA_URL_FILE.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def main() -> int:
    urls = load_urls()
    entries = []
    for u in urls:
        entry = parse_figma_line(u)
        if entry:
            entries.append(entry)

    snapshot = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(FIGMA_URL_FILE),
        "note": "Run Figma MCP per skills/prd-analyze/reference-figma-analysis.md; fill frames_pending from get_metadata.",
        "entries": entries,
        "placeholder_detected": any(
            "placeholder" in (e.get("url") or "").lower()
            or "not-provided" in (e.get("url") or "").lower()
            for e in entries
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT)
    if snapshot["placeholder_detected"]:
        print(
            "WARN: placeholder figma URL — set delivery_coverage.figma.read_complete=false in blueprint",
            file=sys.stderr,
        )
        return 0
    if not entries:
        print("WARN: no figma URLs in figma.url", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
