#!/usr/bin/env python3
"""Sync 00-test-ready-blueprint.json -> 01-prd-analysis.json (no creative analysis)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
BLUEPRINT = ARTIFACTS / "00-test-ready-blueprint.json"
ANALYSIS = ARTIFACTS / "01-prd-analysis.json"


def sync(blueprint: dict) -> dict:
    boundary = []
    exception = []
    for sc in blueprint.get("scenarios") or []:
        line = f"{sc['id']}: {sc['title']} ({sc['type']})"
        if sc["type"] == "边界":
            boundary.append(line)
        elif sc["type"] in ("异常", "安全"):
            exception.append(line)

    return {
        "version": "1.0",
        "project_name": blueprint["project_name"],
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "figma_url": blueprint.get("figma_url", ""),
        "summary": blueprint.get("summary", ""),
        "modules": blueprint.get("modules", []),
        "roles": blueprint.get("roles", []),
        "main_flows": blueprint.get("main_flows", []),
        "boundary_cases": boundary or _legacy_list(blueprint, "boundary"),
        "exception_cases": exception or _legacy_list(blueprint, "exception"),
        "api_endpoints": blueprint.get("api_endpoints", []),
        "figma_mapping": blueprint.get("figma_mapping", []),
        "risks": blueprint.get("risks", []),
        "assumptions": blueprint.get("assumptions", []),
        "synced_from": "00-test-ready-blueprint.json",
    }


def _legacy_list(bp: dict, kind: str) -> list:
    return [s["title"] for s in bp.get("scenarios", []) if s.get("type") == ("边界" if kind == "boundary" else "异常")]


def main() -> int:
    if not BLUEPRINT.exists():
        print(f"Missing {BLUEPRINT}", file=sys.stderr)
        return 1
    blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    analysis = sync(blueprint)
    ANALYSIS.parent.mkdir(parents=True, exist_ok=True)
    ANALYSIS.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    print(ANALYSIS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
