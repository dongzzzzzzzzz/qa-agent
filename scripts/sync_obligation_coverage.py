#!/usr/bin/env python3
"""Sync scenario covers_obligations <-> obligation covered_by_scenarios."""

from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
BLUEPRINT = ARTIFACTS / "00-test-ready-blueprint.json"
OBLIGATIONS = ARTIFACTS / "00-test-obligations.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync scenario covers_obligations into TOG")
    parser.add_argument("--write", action="store_true", help="Write changes to blueprint and obligations")
    args = parser.parse_args()
    if not BLUEPRINT.exists() or not OBLIGATIONS.exists():
        print("Missing blueprint or obligations", file=sys.stderr)
        return 1
    bp = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    ob_doc = json.loads(OBLIGATIONS.read_text(encoding="utf-8"))
    cover_map: dict[str, set[str]] = {}
    for sc in bp.get("scenarios") or []:
        sid = sc.get("id")
        for oid in sc.get("covers_obligations") or []:
            cover_map.setdefault(oid, set()).add(sid)
    for o in ob_doc.get("obligations") or []:
        oid = o["id"]
        merged = set(o.get("covered_by_scenarios") or []) | cover_map.get(oid, set())
        o["covered_by_scenarios"] = sorted(merged)
    ob_doc["synced_from"] = "00-test-ready-blueprint.json"
    bp["obligations_ref"] = "workspace/artifacts/00-test-obligations.json"
    changed_refs = sum(len(v) for v in cover_map.values())
    if not args.write:
        print(f"DRY-RUN obligation coverage sync: {changed_refs} scenario refs collected")
        print("Re-run with --write to update blueprint and obligations.")
        return 0
    OBLIGATIONS.write_text(json.dumps(ob_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    BLUEPRINT.write_text(json.dumps(bp, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote obligation coverage sync: {OBLIGATIONS}, {BLUEPRINT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
