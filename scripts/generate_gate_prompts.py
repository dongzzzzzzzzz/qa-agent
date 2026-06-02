#!/usr/bin/env python3
"""Generate prd-gate compound prompts (orchestrator + role slices)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
PROMPTS = ARTIFACTS / "prompts"
AGENTS = ROOT / "agents"
SKILLS = ROOT / "skills" / "prd-gate"


def read_agent(name: str) -> str:
    p = AGENTS / f"{name}.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _base_meta(stage_id: str) -> list[str]:
    return [
        f"# QA Pipeline — {stage_id}",
        f"**Run at**: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]


def write_product_review() -> Path:
    role = read_agent("gate-product-reviewer")
    lines = _base_meta("prd-gate-product-review") + [
        "## Agent role",
        role,
        "",
        "## Inputs（仅读以下，禁止读完整蓝图 steps）",
        "- `workspace/inputs/prd.md`",
        "- `workspace/artifacts/.gate-slices/product.json`",
        "- `workspace/artifacts/00-test-obligations.json`（义务摘要）",
        "",
        "## Output",
        "- `workspace/artifacts/gate-findings-product.json`",
        "- Contract: `contracts/gate-review-findings.schema.json`（`lens`: `product`）",
        "",
        "## Rules",
        "- 只评义务是否来自 PRD、PRD 矛盾/不可测/范围问题",
        "- `root_cause_draft=prd` → `audience_draft=product`",
        "- 任一 `verdict=fail` finding 必填 `root_cause_draft`、`audience_draft`、`suggestion_draft`",
        "- 完成后: `python3 scripts/validate-artifacts.py --stage gate-findings-product`",
        "",
    ]
    out = PROMPTS / "prd-gate-product-review.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_dev_review() -> Path:
    role = read_agent("gate-dev-reviewer")
    lines = _base_meta("prd-gate-dev-review") + [
        "## Agent role",
        role,
        "",
        "## Inputs",
        "- `workspace/artifacts/.gate-slices/dev.json`",
        "- 不要读完整 `prd.md`（节选已在 slice）",
        "",
        "## Output",
        "- `workspace/artifacts/gate-findings-dev.json`",
        "",
        "## Rules",
        "- 评 P0 义务在实现层是否可验证（API/字段/错误路径）",
        "- PRD 未定义 → product；PRD 有、场景未证 → qa_undercoverage/internal",
        "- 任一 `verdict=fail` finding 必填 `root_cause_draft`、`audience_draft`、`suggestion_draft`",
        "- 完成后: `python3 scripts/validate-artifacts.py --stage gate-findings-dev`",
        "",
    ]
    out = PROMPTS / "prd-gate-dev-review.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_qa_review() -> Path:
    role = read_agent("gate-qa-reviewer")
    lines = _base_meta("prd-gate-qa-review") + [
        "## Agent role",
        role,
        "",
        "## Inputs",
        "- `workspace/artifacts/00-test-ready-blueprint.json`",
        "- `workspace/artifacts/00-test-obligations.json`",
        "- `workspace/artifacts/.test-point-coverage-precheck.json`",
        "- `workspace/artifacts/gate-findings-product.json`",
        "- `workspace/artifacts/gate-findings-dev.json`",
        "- `workspace/inputs/prd.md`",
        "",
        "## Output",
        "- `workspace/artifacts/gate-findings-qa.json`",
        "",
        "## Rules",
        "- 专查假覆盖、矩阵、组合/边界；QA 漏设计 → internal",
        "- 任一 `verdict=fail` finding 必填 `root_cause_draft`、`audience_draft`、`suggestion_draft`",
        "- 完成后: `python3 scripts/validate-artifacts.py --stage gate-findings-qa`",
        "",
    ]
    out = PROMPTS / "prd-gate-qa-review.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_red_team() -> Path:
    role = read_agent("test-point-red-team")
    lines = _base_meta("prd-gate-red-team") + [
        "## Agent role",
        role,
        "",
        "## Inputs",
        "- 三份 `gate-findings-*.json`",
        "- `00-test-obligations.json` + `00-test-ready-blueprint.json`",
        "- `workspace/inputs/prd.md`（节选即可）",
        "",
        "## Output",
        "- `workspace/artifacts/gate-findings-red-team.json`（`lens`: `red_team`）",
        "",
        "## Rules",
        "- 禁止重复已闭合项；专找漏网、反例、需求不合理",
        "- 任一 `verdict=fail` finding 必填 `root_cause_draft`、`audience_draft`、`suggestion_draft`",
        "- 完成后: `python3 scripts/validate-artifacts.py --stage gate-findings-red-team`",
        "",
    ]
    out = PROMPTS / "prd-gate-red-team.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_merge_gatekeeper() -> Path:
    role = read_agent("prd-gatekeeper")
    skill_ref = SKILLS / "SKILL.md"
    lines = _base_meta("prd-gate") + [
        "## Agent role",
        role,
        "",
        "## 前置（必须先过）",
        "```bash",
        "python3 scripts/analyze_gate_prerequisites.py",
        "python3 scripts/validate_obligation_coverage.py",
        "python3 scripts/slice_gate_review_inputs.py",
        "```",
        "",
        "## 子评审（若对应 findings 不存在则先执行）",
        "1. `prompts/prd-gate-product-review.md` → `gate-findings-product.json`",
        "2. `prompts/prd-gate-dev-review.md` → `gate-findings-dev.json`",
        "3. `prompts/prd-gate-qa-review.md` → `gate-findings-qa.json`",
        "4. `prompts/prd-gate-red-team.md` → `gate-findings-red-team.json`",
        "",
        "（全自动流水线可已由编排器顺序执行；合并阶段须读取四份 findings。）",
        "",
        "## 本阶段输出",
        "- `workspace/artifacts/00-prd-gate-report.json`",
        "- 然后: `python3 scripts/validate-artifacts.py --stage prd-gate`",
        "- 然后: `python3 scripts/render_prd_gate_notice.py`",
        "",
        "## Skill",
        f"Load: `{skill_ref.relative_to(ROOT)}`",
        "",
    ]
    if skill_ref.exists():
        lines.append(skill_ref.read_text(encoding="utf-8"))
    out = PROMPTS / "prd-gate.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def generate_all() -> list[Path]:
    PROMPTS.mkdir(parents=True, exist_ok=True)
    return [
        write_product_review(),
        write_dev_review(),
        write_qa_review(),
        write_red_team(),
        write_merge_gatekeeper(),
    ]


def main() -> int:
    paths = generate_all()
    for p in paths:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
