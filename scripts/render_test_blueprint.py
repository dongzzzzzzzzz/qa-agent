#!/usr/bin/env python3
"""Render readable Markdown from the single test blueprint JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import os as _os
ARTIFACTS = __import__("pathlib").Path(_os.environ["QA_WORKSPACE"]) if _os.environ.get("QA_WORKSPACE") else ROOT / "workspace" / "artifacts"
BLUEPRINT_PATH = ARTIFACTS / "00-test-blueprint.json"
OUTPUT_PATH = ARTIFACTS / "00-test-blueprint.md"


def _join(items: list[str]) -> str:
    return "；".join(str(i).strip() for i in items if str(i).strip())


def render_markdown(blueprint: dict) -> str:
    scenarios_count = sum(
        len(point.get("scenarios") or [])
        for module in blueprint.get("modules") or []
        for point in module.get("test_points") or []
    )
    lines = [
        "# 测试蓝图",
        "",
        f"项目：{blueprint.get('project_name', '')}",
        "",
        "这份蓝图按普通测试设计思路组织：需求模块 -> 测试点 -> 测试范围 -> 场景。",
        "",
        "## 总览",
        "",
        f"- 需求模块数：{len(blueprint.get('modules') or [])}",
        f"- 测试场景数：{scenarios_count}",
    ]
    if blueprint.get("knowledge_context_ref"):
        lines.append(f"- 知识库上下文：`{blueprint['knowledge_context_ref']}`")
    lines.append("")

    for idx, module in enumerate(blueprint.get("modules") or [], 1):
        lines.extend(
            [
                f"## {idx}. 需求模块：{module.get('title', '')}",
                "",
                f"目标：{module.get('goal', '')}",
                "",
                f"依据：{_join(module.get('source_refs') or [])}",
                "",
            ]
        )
        for pidx, point in enumerate(module.get("test_points") or [], 1):
            scope = point.get("scope") or {}
            lines.extend(
                [
                    f"### 测试点 {idx}.{pidx}：{point.get('title', '')}",
                    "",
                    f"依据：{point.get('basis', '')}",
                    "",
                    f"验收规则：{point.get('acceptance_rule', '')}",
                    "",
                    "#### 测试范围",
                    "",
                    f"包含：{_join(scope.get('include') or [])}",
                    "",
                    f"不包含：{_join(scope.get('exclude') or []) or '无'}",
                    "",
                ]
            )
            if scope.get("platforms"):
                lines.extend([f"平台：{_join(scope['platforms'])}", ""])
            if scope.get("entry_points"):
                lines.extend([f"入口：{_join(scope['entry_points'])}", ""])
            if scope.get("data"):
                lines.extend([f"数据：{_join(scope['data'])}", ""])
            lines.extend(["#### 场景", ""])
            for scenario in point.get("scenarios") or []:
                ch = scenario.get("execution_channel", "")
                auto = scenario.get("automatable", "")
                suffix = f" · {ch} · 自动化{auto}" if ch or auto else ""
                lines.append(
                    f"- [{scenario.get('priority', '')}/{scenario.get('type', '')}] {scenario.get('title', '')}{suffix}"
                )
            lines.append("")

    questions = blueprint.get("open_questions") or []
    if questions:
        lines.extend(["## 待产品确认问题", ""])
        for q in questions:
            blocking = "阻塞" if q.get("blocking") else "非阻塞"
            lines.append(f"- **{q.get('id', '')}（{blocking}）** {q.get('question', '')}")
            lines.append(f"  - 影响：{q.get('impact', '')}")
            lines.append(f"  - 归属：{q.get('owner', '')}")
            lines.append(f"  - 来源：{_join(q.get('source_refs') or [])}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    if not BLUEPRINT_PATH.exists():
        print(f"Missing {BLUEPRINT_PATH}", file=sys.stderr)
        return 1
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    OUTPUT_PATH.write_text(render_markdown(blueprint), encoding="utf-8")
    print(OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
