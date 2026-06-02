#!/usr/bin/env python3
"""Render test-ready-internal.md from blueprint for QA/dev."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
BLUEPRINT = ARTIFACTS / "00-test-ready-blueprint.json"
OUT = ARTIFACTS / "test-ready-internal.md"


def render(bp: dict) -> str:
    lines = [
        "# 测试就绪蓝图（内部）",
        "",
        f"**项目**: {bp.get('project_name', '')}",
        f"**场景数**: {len(bp.get('scenarios', []))}",
        f"**假设数**: {len(bp.get('assumptions', []))}",
        "",
        "## 模块",
        "",
    ]
    for m in bp.get("modules") or []:
        lines.append(f"- {m['id']}: {m['name']} ({m.get('priority', '')})")
    lines.extend(["", "## 假设（已冻结，下游勿再找产品）", ""])
    for a in bp.get("assumptions") or []:
        lines.append(f"### {a['id']} ({a.get('risk', '')})")
        lines.append(f"- {a.get('statement', '')}")
        lines.append(f"- **测试规则**: {a.get('test_rule', '')}")
        lines.append("")
    lines.extend(["", "## 场景索引", ""])
    for s in bp.get("scenarios") or []:
        src = s.get("source", "")
        extra = f" / {s['assumption_id']}" if s.get("assumption_id") else ""
        lines.append(f"- {s['id']}: [{s['priority']}] {s['title']} ({s['type']}, {src}{extra})")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if not BLUEPRINT.exists():
        print(f"Missing {BLUEPRINT}", file=sys.stderr)
        return 1
    bp = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    OUT.write_text(render(bp), encoding="utf-8")
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
