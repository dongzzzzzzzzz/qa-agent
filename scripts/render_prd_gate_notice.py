#!/usr/bin/env python3
"""Render PRD gate JSON report to product-facing Markdown."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
REPORT_PATH = ARTIFACTS / "00-prd-gate-report.json"
REJECT_MD = ARTIFACTS / "prd-reject-to-product.md"
PASS_MD = ARTIFACTS / "prd-gate-pass-to-product.md"
REWORK_MD = ARTIFACTS / "test-point-rework-to-qa.md"

SEVERITY_ORDER = {"blocker": 0, "major": 1, "minor": 2}

SEVERITY_TAG = {
    "blocker": "必须修订",
    "major": "建议补充",
    "minor": "可选补充",
}


def load_report(path: Path = REPORT_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sort_issues(issues: list[dict]) -> list[dict]:
    return sorted(
        issues,
        key=lambda i: (SEVERITY_ORDER.get(i.get("severity", ""), 9), i.get("id", "")),
    )


def _product_issues(report: dict) -> list[dict]:
    return [
        i
        for i in report.get("issues") or []
        if (i.get("audience") or "product") == "product"
    ]


def _internal_issues(report: dict) -> list[dict]:
    return [i for i in report.get("issues") or [] if i.get("audience") == "internal"]


def _load_product_copy_module():
    scripts = Path(__file__).resolve().parent
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import gate_product_copy

    return gate_product_copy


def _analyze_context_footer() -> list[str]:
    bp_path = ARTIFACTS / "00-test-ready-blueprint.json"
    if not bp_path.exists():
        return [
            "",
            "> 尚未完成完整 PRD 分析，本清单可能不全。请先运行 prd-analyze。",
            "",
        ]
    try:
        bp = json.loads(bp_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["", "> 测试蓝图文件无效。", ""]
    dc = bp.get("delivery_coverage") or {}
    prd = dc.get("prd") or {}
    src = (prd.get("sources") or [{}])[0]
    read_ok = prd.get("read_complete", False)
    return [
        "",
        "## 评审说明",
        "",
        "本次结论基于：**PRD 全文阅读** + **产品 / 开发 / 测试三方评审** + **专项挑刺（红队）**。",
        "",
        f"- PRD 全文已读：**{'是' if read_ok else '否'}**（{src.get('pages_read', '?')} / {src.get('pages_total', '?')} 页）",
        f"- 来源：`{src.get('path', '未知')}`",
        "",
    ]


def _rerun_command() -> str:
    meta_path = ARTIFACTS / "00-meta.json"
    platform = "<platform>"
    if meta_path.exists():
        try:
            platform = (json.loads(meta_path.read_text(encoding="utf-8")).get("platform") or platform)
        except json.JSONDecodeError:
            platform = "<platform>"
    return f"./orchestrators/{platform}/run-pipeline.sh --from-stage prd-analyze"


def _render_product_issue_block(issue: dict, copy_mod) -> list[str]:
    copy = copy_mod.get_product_copy(issue)
    issue_id = issue.get("id", "ISSUE")
    tag = SEVERITY_TAG.get(issue.get("severity", ""), "")
    lines = [
        f"### {issue_id} · {copy['title']}",
        "",
    ]
    if tag:
        lines.append(f"**优先级**：{tag}")
        lines.append("")
    if issue.get("prd_section"):
        lines.append(f"**对应 PRD 章节**：{issue['prd_section']}")
        lines.append("")
    lines.append(copy["problem"])
    lines.append("")
    lines.append("**建议修改**")
    lines.append("")
    lines.append(copy["action"])
    lines.append("")
    if issue.get("figma_ref"):
        lines.append(f"**设计稿**：{issue['figma_ref']}")
        lines.append("")
    return lines


def _reject_intro(report: dict, product: list[dict], copy_mod) -> list[str]:
    summary = (report.get("summary_for_product") or "").strip()
    if not summary:
        summary = copy_mod.product_summary(product)
    lines = [
        "# PRD 评审未通过",
        "",
        "本次 PRD **尚未达到可开发 / 可测试标准**，请按下方清单修订后重新提测。",
        "",
        summary,
        "",
        f"**评审时间**：{report.get('checked_at', '')}",
        "",
    ]
    formal = (report.get("summary") or "").strip()
    if formal and formal != summary:
        lines.extend(
            [
                "<details>",
                "<summary>完整评审记录（技术向）</summary>",
                "",
                formal,
                "",
                "</details>",
                "",
            ]
        )
    return lines


def render_reject_markdown(report: dict) -> str:
    copy_mod = _load_product_copy_module()
    product = _product_issues(report)
    delivery = [i for i in product if i.get("dimension") == "delivery" or not i.get("dimension")]
    tog = [i for i in product if i.get("dimension") in ("test_point_coverage", "obligation_coverage")]

    lines = _reject_intro(report, product, copy_mod)
    lines.extend(_analyze_context_footer())

    issue_groups = [
        ("## 待修订问题", "按优先级排序。", delivery or product),
    ]
    if tog and delivery:
        issue_groups.append(
            (
                "## 测试就绪相关补充",
                "以下项不补清楚，后续测试执行时仍会反复确认需求，建议一并写入 PRD。",
                tog,
            )
        )

    for heading, hint, items in issue_groups:
        if not items:
            continue
        lines.extend([heading, "", hint, ""])
        for issue in sort_issues(items):
            lines.extend(_render_product_issue_block(issue, copy_mod))

    lines.extend(
        [
            "## 修订完成后",
            "",
                "- [ ] 已按上方「建议修改」更新 PRD 对应章节",
                "- [ ] 已更新 Figma 链接 / 稿面（如涉及 UI）",
                f"- [ ] 重新提测：`{_rerun_command()}`",
                "",
            ]
        )
    if report.get("notes"):
        lines.extend(["## 附注", "", report["notes"], ""])
    return "\n".join(lines)


def _render_internal_issue_block(issue: dict) -> list[str]:
    lines = [
        f"### {issue.get('id', 'ISSUE')}",
        "",
        issue.get("description", ""),
        "",
        f"**建议**：{issue.get('suggestion', '')}",
        "",
    ]
    if issue.get("obligation_ids"):
        lines.append(f"*关联义务：{', '.join(issue['obligation_ids'])}*")
        lines.append("")
    return lines


def render_rework_markdown(report: dict) -> str:
    internal = _internal_issues(report)
    fc = report.get("false_coverage") or []
    lines = [
        "# 测试蓝图返工说明（QA 内部）",
        "",
        f"**摘要**：{report.get('summary', '').strip()}",
        "",
        f"**时间**：{report.get('checked_at', '')}",
        "",
        "PRD 可能无需改动；需从 **prd-analyze** 重跑，补实测试义务与场景的对应关系。",
        "",
        "```bash",
        _rerun_command(),
        "```",
        "",
    ]
    if fc:
        lines.extend(["## 用例未真正覆盖所声称的义务", ""])
        for row in fc[:30]:
            lines.append(
                f"- 场景 **{row.get('scenario_id')}** 声称覆盖 {', '.join(row.get('obligation_ids') or [])}，"
                f"但步骤与预期对不上：{row.get('reason')}"
            )
        lines.append("")
    lines.extend(["## 内部问题清单", ""])
    for issue in sort_issues(internal):
        lines.extend(_render_internal_issue_block(issue))
    return "\n".join(lines)


def load_blueprint() -> dict | None:
    path = ARTIFACTS / "00-test-ready-blueprint.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def render_pass_markdown(report: dict) -> str:
    tpr = report.get("test_point_review") or {}
    tri = tpr.get("tri_party") or {}
    lines = [
        "# PRD 测试就绪 — 已通过",
        "",
        f"**说明**：{report.get('summary', '').strip()}",
        "",
        f"**评审时间**：{report.get('checked_at', '')}",
        "",
        "交付物与测试义务图谱已通过门禁；后续用例生成不再就需求细节联系产品。",
        "",
        "## 覆盖结论",
        "",
        f"- 义务覆盖分：**{tpr.get('coverage_score', '—')}**",
        f"- 义务总数：**{tpr.get('obligations_total', '—')}**",
        f"- 场景总数：**{tpr.get('scenarios_total', '—')}**",
    ]
    for role in ("product", "dev", "qa", "red_team"):
        r = tri.get(role) or {}
        if r:
            lines.append(
                f"- {role} 评审：**{r.get('verdict', '—')}**（{r.get('finding_count', 0)} 项发现）"
            )
    lines.extend(["", "## 请产品确认", ""])
    bp = load_blueprint()
    if bp:
        assumptions = bp.get("assumptions") or []
        if assumptions:
            for a in assumptions:
                lines.append(f"### {a.get('id', 'ASM')}")
                lines.append(f"- {a.get('statement', '')}")
                lines.append(f"- 测试将按：{a.get('test_rule', '')}")
                lines.append("")
        lines.extend(
            [
                "- [ ] 同意上述假设与覆盖范围作为本次迭代测试基线",
                "- [ ] 有异议 → 修订 PRD/Figma 后 `--from-stage prd-analyze`",
                "",
            ]
        )
    lines.extend(["## 后续", "", "需求变更请重新从 prd-analyze 提测。", ""])
    return "\n".join(lines)


def write_product_markdown(
    report_path: Path = REPORT_PATH,
    reject_path: Path = REJECT_MD,
    pass_path: Path = PASS_MD,
    rework_path: Path = REWORK_MD,
) -> Path:
    _scripts = Path(__file__).resolve().parent
    if str(_scripts) not in sys.path:
        sys.path.insert(0, str(_scripts))
    from analyze_gate_prerequisites import require_analyze_complete

    pre = require_analyze_complete("render_prd_gate_notice")
    if pre:
        raise SystemExit(
            "Cannot render product MD: prd-analyze full read not validated.\n"
            + "\n".join(f"  - {e}" for e in pre)
        )

    report = load_report(report_path)
    verdict = report.get("verdict")
    if verdict == "reject":
        rk = report.get("reject_kind") or "product"
        product = _product_issues(report)
        if rk == "internal" or not product:
            content = render_rework_markdown(report)
            rework_path.write_text(content, encoding="utf-8")
            if reject_path.exists():
                reject_path.unlink()
            return rework_path
        content = render_reject_markdown(report)
        reject_path.write_text(content, encoding="utf-8")
        if pass_path.exists():
            pass_path.unlink()
        if rework_path.exists():
            rework_path.unlink()
        return reject_path
    if verdict == "pass":
        content = render_pass_markdown(report)
        pass_path.write_text(content, encoding="utf-8")
        if reject_path.exists():
            reject_path.unlink()
        if rework_path.exists():
            rework_path.unlink()
        return pass_path
    raise ValueError(f"unknown verdict: {verdict}")


def main() -> int:
    path = write_product_markdown()
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
