#!/usr/bin/env python3
"""Render 02-test-cases.md from 00-test-ready-blueprint.json (no new scenarios)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
BLUEPRINT_PATH = ARTIFACTS / "00-test-ready-blueprint.json"
OUTPUT_PATH = ARTIFACTS / "02-test-cases.md"

def load_blueprint(path: Path = BLUEPRINT_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_markdown(blueprint: dict) -> str:
    module_names = {
        m.get("id"): m.get("name") or m.get("id")
        for m in blueprint.get("modules") or []
        if m.get("id")
    }
    lines = [
        f"# {blueprint.get('project_name', '测试用例')} - 测试用例",
        "",
        f"> 来源: 00-test-ready-blueprint.json | 场景数: {len(blueprint.get('scenarios', []))}",
        "",
        "## 测试用例表格",
        "",
        "| 编号 | 模块 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 测试类型 |",
        "|------|------|----------|----------|----------|----------|--------|----------|",
    ]
    by_module: dict[str, list[dict]] = {}
    for sc in blueprint.get("scenarios") or []:
        by_module.setdefault(sc["module_id"], []).append(sc)

    xmind_lines = ["", "---", ""]
    for module_id, scenarios in by_module.items():
        mod_name = module_names.get(module_id, module_id)
        xmind_lines.append(f"# {mod_name}")
        for sc in scenarios:
            pre = sc.get("preconditions") or []
            steps = sc.get("steps") or []
            exp = sc.get("expected") or []
            pre_cell = "; ".join(pre)
            step_cell = " ".join(f"{i + 1}. {s}" for i, s in enumerate(steps))
            exp_cell = "; ".join(exp)
            lines.append(
                f"| {sc['id']} | {mod_name} | {sc['title']} | {pre_cell} | {step_cell} | {exp_cell} | {sc['priority']} | {sc['type']} |"
            )
            xmind_lines.append(f"## {sc['type']}")
            xmind_lines.append(f"### {sc['title']}")
            xmind_lines.append(f"- 前置条件：{pre_cell}")
            xmind_lines.append(f"- 测试步骤：{step_cell}")
            xmind_lines.append(f"- 预期结果：{exp_cell}")
            xmind_lines.append(f"- 优先级：{sc['priority']}")
            xmind_lines.append(f"- 测试类型：{sc['type']}")
            xmind_lines.append(f"- 来源：{sc.get('source', '')}")
            if sc.get("assumption_id"):
                xmind_lines.append(f"- 假设：{sc['assumption_id']}")
            xmind_lines.append("")

    return "\n".join(lines + xmind_lines)


def main() -> int:
    if not BLUEPRINT_PATH.exists():
        print(f"Missing {BLUEPRINT_PATH}", file=sys.stderr)
        return 1
    blueprint = load_blueprint()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(render_markdown(blueprint), encoding="utf-8")
    print(OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
