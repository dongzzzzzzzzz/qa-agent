#!/usr/bin/env python3
"""Hard gate: prd-gate / product MD only after prd-analyze passes full-read validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
BLUEPRINT = ARTIFACTS / "00-test-ready-blueprint.json"
OBLIGATIONS = ARTIFACTS / "00-test-obligations.json"
ANALYSIS = ARTIFACTS / "01-prd-analysis.json"
MARKER = ARTIFACTS / ".prd-analyze-complete.ok"

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_test_ready_blueprint import validate_test_ready_blueprint  # noqa: E402


def analyze_validation_errors() -> list[str]:
    """Return errors if prd-analyze did not complete per full-read rules."""
    errors: list[str] = []
    if not BLUEPRINT.exists():
        return ["missing 00-test-ready-blueprint.json — 须先完成 prd-analyze 子 Agent"]
    if not ANALYSIS.exists():
        return ["missing 01-prd-analysis.json — 须先 sync 蓝图"]
    if not OBLIGATIONS.exists():
        return ["missing 00-test-obligations.json — prd-analyze 须产出测试义务图谱 (TOG)"]

    try:
        blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"invalid blueprint JSON: {e}"]

    errors.extend(validate_test_ready_blueprint(blueprint))

    try:
        ob = json.loads(OBLIGATIONS.read_text(encoding="utf-8"))
        if len(ob.get("obligations") or []) < 1:
            errors.append("00-test-obligations.json: obligations[] empty")
    except json.JSONDecodeError as e:
        errors.append(f"invalid 00-test-obligations.json: {e}")

    dc = blueprint.get("delivery_coverage") or {}
    prd = dc.get("prd") or {}
    if prd.get("read_complete") is not True:
        errors.append("delivery_coverage.prd.read_complete must be true (全文未读完禁止 gate)")
    inv = prd.get("sections_inventory") or []
    if len(inv) < 10:
        errors.append(
            f"sections_inventory too small ({len(inv)}); full PRD analyze requires per-section inventory"
        )

    return errors


def is_analyze_complete() -> bool:
    return len(analyze_validation_errors()) == 0


def write_analyze_complete_marker() -> None:
    if is_analyze_complete():
        MARKER.write_text(
            json.dumps(
                {
                    "ok": True,
                    "blueprint": str(BLUEPRINT),
                    "scenarios": len(
                        json.loads(BLUEPRINT.read_text(encoding="utf-8")).get("scenarios") or []
                    ),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


def require_analyze_complete(context: str = "prd-gate") -> list[str]:
    errs = analyze_validation_errors()
    if errs:
        return [f"{context}: prd-analyze 未完成全文分析，禁止产出 gate/打回产品文档"] + errs
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
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    print("OK prd-analyze prerequisites (full read + delivery_coverage)")
    sys.exit(0)
