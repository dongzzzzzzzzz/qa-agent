#!/usr/bin/env python3
"""Build a knowledge-base inventory for AI selection.

This script deliberately does not decide which documents are relevant. It only
indexes paths, document type, headings, and short excerpts so prd-analyze can
make the final selection after reading the PRD/Figma.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
import os as _os
ARTIFACTS = __import__("pathlib").Path(_os.environ["QA_WORKSPACE"]) if _os.environ.get("QA_WORKSPACE") else ROOT / "workspace" / "artifacts"
DEFAULT_KB = ROOT / "bundled" / "knowledge_base"
OUT_JSON = ARTIFACTS / "00-knowledge-inventory.json"
OUT_MD = ARTIFACTS / "00-knowledge-inventory.md"

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from load_project_config import load_project_config  # noqa: E402

BUSINESS_DIR_MARKERS = ("业务规则库", "业务知识图谱")
HISTORICAL_DIR_MARKERS = ("文本用例",)


def _kb_config(config: dict[str, Any]) -> dict[str, Any]:
    raw = config.get("knowledge_base") or {}
    return raw if isinstance(raw, dict) else {}


def _doc_kind(rel: str) -> str:
    if any(marker in rel for marker in HISTORICAL_DIR_MARKERS):
        return "historical_case_reference"
    if any(marker in rel for marker in BUSINESS_DIR_MARKERS):
        return "business_knowledge"
    if rel.startswith("产品全景/"):
        return "product_overview"
    return "metadata"


def _iter_docs(kb_root: Path) -> list[Path]:
    return sorted(
        p
        for p in kb_root.rglob("*.md")
        if p.is_file()
        and ".git" not in p.parts
        and ".claude" not in p.parts
        and ".cursor" not in p.parts
        and ".codex" not in p.parts
    )


def _safe_read(path: Path, max_chars: int = 8000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except OSError:
        return ""


def _headings(text: str, limit: int = 8) -> list[str]:
    rows = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,4})\s+(.+?)\s*$", line)
        if m:
            rows.append(m.group(2).strip())
        if len(rows) >= limit:
            break
    return rows


def _excerpt(text: str, limit: int = 280) -> str:
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    joined = " ".join(lines)
    return joined[:limit]


def build_inventory(config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config if config is not None else load_project_config()
    kb_cfg = _kb_config(config)
    enabled = kb_cfg.get("enabled", True)
    kb_root = ROOT / str(kb_cfg.get("path") or "bundled/knowledge_base")
    if not enabled:
        return {
            "version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "enabled": False,
            "knowledge_base_path": str(kb_root),
            "documents": [],
            "notes": ["knowledge_base.enabled=false"],
        }
    if not kb_root.exists():
        return {
            "version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "enabled": True,
            "knowledge_base_path": str(kb_root),
            "documents": [],
            "notes": [f"知识库目录不存在: {kb_root}"],
        }

    excluded = {
        str(x).strip().lower()
        for x in kb_cfg.get("exclude_modules") or []
        if str(x).strip()
    }
    docs = []
    for path in _iter_docs(kb_root):
        rel = path.relative_to(kb_root).as_posix()
        lower_rel = rel.lower()
        if any(x and x in lower_rel for x in excluded):
            continue
        text = _safe_read(path)
        parts = rel.split("/")
        docs.append(
            {
                "path": f"bundled/knowledge_base/{rel}",
                "kind": _doc_kind(rel),
                "domain": parts[0] if parts else "",
                "module_hint": parts[1] if len(parts) > 1 else "",
                "headings": _headings(text),
                "excerpt": _excerpt(text),
            }
        )

    return {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "enabled": True,
        "knowledge_base_path": "bundled/knowledge_base",
        "decision_policy": {
            "decision_owner": "prd-analyzer-subagent",
            "script_role": "inventory_only",
            "prd_figma_priority": "PRD/Figma 高于 GT 知识库；冲突时不得用知识库覆盖 PRD/Figma",
            "historical_cases_authority": "reference_only",
        },
        "documents": docs,
        "notes": [],
    }


def render_markdown(inventory: dict[str, Any]) -> str:
    lines = [
        "# GT 知识库目录清单",
        "",
        "- 脚本角色: 只建目录，不做最终选择。",
        "- 最终选择者: prd-analyze 子 Agent。",
        "- 选择原则: 先读 PRD/Figma，再从本清单挑相关业务模块；历史用例只作参考。",
        "",
        f"- 启用: {'是' if inventory.get('enabled') else '否'}",
        f"- 知识库路径: `{inventory.get('knowledge_base_path', '')}`",
        f"- 文档数: {len(inventory.get('documents') or [])}",
        f"- 生成时间: {inventory.get('generated_at', '')}",
        "",
        "## 文档清单",
        "",
    ]
    for doc in inventory.get("documents") or []:
        headings = " / ".join(doc.get("headings") or [])
        lines.append(f"### {doc.get('path')}")
        lines.append(f"- 类型: {doc.get('kind')}")
        lines.append(f"- 模块提示: {doc.get('module_hint', '')}")
        if headings:
            lines.append(f"- 标题线索: {headings}")
        if doc.get("excerpt"):
            lines.append(f"- 摘要片段: {doc['excerpt']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory()
    OUT_JSON.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    OUT_MD.write_text(render_markdown(inventory), encoding="utf-8")
    print(OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
