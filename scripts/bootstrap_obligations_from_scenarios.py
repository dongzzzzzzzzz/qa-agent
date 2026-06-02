#!/usr/bin/env python3
"""One-off: derive minimal TOG from existing blueprint (until prd-analyze re-run)."""

from __future__ import annotations

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
BLUEPRINT = ARTIFACTS / "00-test-ready-blueprint.json"
OBLIGATIONS = ARTIFACTS / "00-test-obligations.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Maintainer-only migration helper: derive minimal TOG from scenarios"
    )
    parser.add_argument("--write", action="store_true", help="Actually write generated TOG")
    args = parser.parse_args()
    if not args.write:
        print("DRY-RUN: this is a maintainer-only migration helper.")
        print("It derives TOG from scenarios and weakens normal PRD-first gate semantics.")
        print("Re-run with --write only for migration fixtures, never normal pipeline runs.")
        return 0
    if not BLUEPRINT.exists():
        print(f"Missing {BLUEPRINT}", file=sys.stderr)
        return 1
    bp = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    scenarios = bp.get("scenarios") or []
    obligations = []
    for i, sc in enumerate(scenarios, start=1):
        oid = f"O-{i:03d}"
        title = sc.get("title", "未命名")
        obligations.append(
            {
                "id": oid,
                "statement": title,
                "predicate": f"场景 {sc['id']} 的步骤与预期可验证：{title}",
                "source": sc.get("source", "prd"),
                "risk": sc.get("priority", "P1"),
                "kind": "rule",
                "prd_section": sc.get("prd_section") or "",
                "figma_ref": sc.get("figma_ref") or "",
                "module_id": sc.get("module_id"),
                "covered_by_scenarios": [sc["id"]],
            }
        )
        sc["covers_obligations"] = [oid]
    ob_doc = {
        "version": "1.0",
        "project_name": bp.get("project_name", "unknown"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "synced_from": "bootstrap_obligations_from_scenarios.py",
        "obligations": obligations,
        "state_machines": [],
    }
    OBLIGATIONS.write_text(json.dumps(ob_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    bp["obligations_ref"] = "workspace/artifacts/00-test-obligations.json"
    BLUEPRINT.write_text(json.dumps(bp, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Bootstrap {len(obligations)} obligations → {OBLIGATIONS}")
    print("Re-run prd-analyze for production-quality TOG.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
