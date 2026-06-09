#!/usr/bin/env python3
"""Render readable test cases from the single test blueprint (XMind-importable Markdown)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import os as _os
ARTIFACTS = __import__("pathlib").Path(_os.environ["QA_WORKSPACE"]) if _os.environ.get("QA_WORKSPACE") else ROOT / "workspace" / "artifacts"
BLUEPRINT_PATH = ARTIFACTS / "00-test-blueprint.json"
OUTPUT_PATH = ARTIFACTS / "02-test-cases.md"

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from load_project_config import load_project_config  # noqa: E402


def _bullet_lines(items: list[str], indent: str = "  ") -> list[str]:
    out: list[str] = []
    for item in items:
        text = str(item or "").strip()
        if text:
            out.append(f"{indent}- {text}")
    return out


def _numbered_bullets(items: list[str], indent: str = "  ") -> list[str]:
    out: list[str] = []
    for idx, item in enumerate(items, 1):
        text = str(item or "").strip()
        if text:
            out.append(f"{indent}- {idx}. {text}")
    return out


def _iter_cases(blueprint: dict):
    for module in blueprint.get("modules") or []:
        for point in module.get("test_points") or []:
            for scenario in point.get("scenarios") or []:
                yield module, point, scenario


def render_markdown(blueprint: dict, config: dict | None = None) -> str:
    cfg = config if config is not None else load_project_config()
    scope_note = (cfg.get("test_scope_notes") or "").strip()
    project = blueprint.get("project_name", cfg.get("project_name", "测试用例"))

    lines = [
        f"# {project} - 测试用例",
        "",
        "> 本文件由 `00-test-blueprint.json` 生成，**XMind 可导入层级 Markdown**（`#` 模块 → `###` 用例 → `-` 属性）。",
        "> 用例采用 Given / When / Then：前置条件、执行步骤、预期结果、后置动作。",
        "",
    ]
    if scope_note:
        lines.extend(["> **项目范围**：", ">", *[f"> {ln}" for ln in scope_note.splitlines() if ln.strip()], ""])

    lines.extend(["## 用例清单", ""])

    current_module = ""
    current_point = ""

    for idx, (module, point, scenario) in enumerate(_iter_cases(blueprint), 1):
        case_id = f"TC-{idx:03d}"
        module_title = (module.get("title") or "未命名模块").strip()
        point_title = (point.get("title") or "").strip()
        title = (scenario.get("title") or "").strip()
        source_refs = scenario.get("source_refs") or module.get("source_refs") or []

        if module_title != current_module:
            current_module = module_title
            current_point = ""
            lines.extend([f"## {module_title}", ""])

        if point_title and point_title != current_point:
            current_point = point_title
            lines.extend([f"### {point_title}", ""])

        lines.append(f"### {case_id}: {title}")
        lines.append("")
        meta = [
            ("用例编号", case_id),
            ("需求模块", module_title),
            ("测试点", point_title or "—"),
            ("优先级", scenario.get("priority") or point.get("priority") or "—"),
            ("执行通道", scenario.get("execution_channel") or "—"),
            ("是否可自动化", scenario.get("automatable") or "—"),
        ]
        for key, val in meta:
            lines.append(f"- {key}：{val}")
        lines.append("")

        lines.append("- 前置条件")
        lines.extend(_bullet_lines(scenario.get("preconditions") or ["无"]))
        lines.append("")

        lines.append("- 测试数据")
        lines.extend(_bullet_lines(scenario.get("test_data") or ["无"]))
        lines.append("")

        lines.append("- 执行步骤")
        lines.extend(_numbered_bullets(scenario.get("steps") or []))
        lines.append("")

        lines.append("- 预期结果")
        lines.extend(_bullet_lines(scenario.get("expected_results") or []))
        lines.append("")

        lines.append("- 后置动作")
        lines.extend(_bullet_lines(scenario.get("postconditions") or ["无"]))
        lines.append("")

        refs = "; ".join(str(r) for r in source_refs if str(r).strip())
        lines.append(f"- 需求依据：{refs or '—'}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    if not BLUEPRINT_PATH.exists():
        print(f"Missing {BLUEPRINT_PATH}", file=sys.stderr)
        return 1
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(render_markdown(blueprint), encoding="utf-8")
    print(OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
