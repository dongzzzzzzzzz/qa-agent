#!/usr/bin/env python3
"""Validate that prd-analyze produced the single readable blueprint."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
BLUEPRINT = ARTIFACTS / "00-test-blueprint.json"
BLUEPRINT_MD = ARTIFACTS / "00-test-blueprint.md"
KNOWLEDGE_CONTEXT = ARTIFACTS / "00-knowledge-context.json"
MARKER = ARTIFACTS / ".prd-analyze-complete.ok"


def analyze_validation_errors() -> list[str]:
    errors: list[str] = []
    if not BLUEPRINT.exists():
        return ["missing 00-test-blueprint.json — 须先完成 prd-analyze 子 Agent"]
    if not BLUEPRINT_MD.exists():
        errors.append("missing 00-test-blueprint.md — 须输出给人看的测试蓝图")
    if not KNOWLEDGE_CONTEXT.exists():
        errors.append("missing 00-knowledge-context.json — prd-analyze 子 Agent 必须决策知识库上下文")

    try:
        blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"invalid 00-test-blueprint.json: {e}"]

    if not blueprint.get("modules"):
        errors.append("00-test-blueprint.json: modules[] empty")
    scenario_count = sum(
        len(point.get("scenarios") or [])
        for module in blueprint.get("modules") or []
        for point in module.get("test_points") or []
    )
    if scenario_count < 1:
        errors.append("00-test-blueprint.json: no scenarios")

    if KNOWLEDGE_CONTEXT.exists():
        try:
            context = json.loads(KNOWLEDGE_CONTEXT.read_text(encoding="utf-8"))
            if context.get("decision_owner") != "prd-analyzer-subagent":
                errors.append("00-knowledge-context.json: decision_owner must be prd-analyzer-subagent")
        except json.JSONDecodeError as e:
            errors.append(f"invalid 00-knowledge-context.json: {e}")
    return errors


def is_analyze_complete() -> bool:
    return len(analyze_validation_errors()) == 0


def write_analyze_complete_marker() -> None:
    if not is_analyze_complete():
        MARKER.unlink(missing_ok=True)
        return
    blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    scenario_count = sum(
        len(point.get("scenarios") or [])
        for module in blueprint.get("modules") or []
        for point in module.get("test_points") or []
    )
    MARKER.write_text(
        json.dumps(
            {
                "ok": True,
                "blueprint": str(BLUEPRINT),
                "modules": len(blueprint.get("modules") or []),
                "scenarios": scenario_count,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def require_analyze_complete(context: str = "case-review") -> list[str]:
    errs = analyze_validation_errors()
    if errs:
        return [f"{context}: prd-analyze 未完成唯一测试蓝图，禁止继续"] + errs
    if not MARKER.exists():
        return [
            f"{context}: missing {MARKER.name} — 请先运行: "
            "python3 scripts/validate-artifacts.py --stage prd-analyze"
        ]
    return []


if __name__ == "__main__":
    errs = analyze_validation_errors()
    if errs:
        print("FAIL prd-analyze prerequisites:")
        for err in errs:
            print(f"  - {err}")
        sys.exit(1)
    print("OK prd-analyze prerequisites (single blueprint)")
