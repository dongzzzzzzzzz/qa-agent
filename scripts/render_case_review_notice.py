#!/usr/bin/env python3
"""Render case-review gate JSON report to simplified Markdown."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _artifacts_dir() -> Path:
    import os
    if os.environ.get("QA_WORKSPACE"):
        return Path(os.environ["QA_WORKSPACE"])
    return ROOT / "workspace" / "artifacts"

ARTIFACTS = _artifacts_dir()
REPORT_PATH = ARTIFACTS / "03-review-report.json"
REVIEW_MD = ARTIFACTS / "03-review-report.md"
REJECT_MD = ARTIFACTS / "prd-reject-to-product.md"
LEGACY_REJECT_MD = ARTIFACTS / "PRD-REJECTED.md"
PASS_MD = ARTIFACTS / "case-review-pass.md"
REWORK_MD = ARTIFACTS / "test-point-rework-to-qa.md"

SEVERITY_ORDER = {"blocker": 0, "major": 1, "minor": 2}


def load_report(path: Path = REPORT_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sort_issues(issues: list[dict]) -> list[dict]:
    return sorted(issues, key=lambda i: (SEVERITY_ORDER.get(i.get("severity", ""), 9), i.get("id", "")))


def _report_time(report: dict) -> str:
    return report.get("reviewed_at") or report.get("checked_at") or ""


def _team(issue: dict) -> str:
    root = issue.get("root_cause")
    if root in ("prd", "figma", "assumption_unresolved"):
        return "产品/设计"
    if root == "qa_undercoverage":
        return "QA 蓝图分析"
    if root == "case_generation":
        return "用例生成"
    return "待判断"


def _retry_label(issue: dict) -> str:
    return {
        "product": "产品修订后从 prd-analyze 重跑",
        "prd-analyze": "回 prd-analyze 更新蓝图",
        "case-generate": "回 case-generate 重生成用例",
        "human": "人工介入",
    }.get(issue.get("retry_target"), issue.get("retry_target") or "")


def _short(text: object, limit: int = 180) -> str:
    normalized = re.sub(r"\s+", " ", str(text or "")).strip()
    return normalized if len(normalized) <= limit else normalized[: limit - 1] + "..."


def _issue_location(issue: dict) -> str:
    evidence = issue.get("evidence") or {}
    for key in ("prd_section", "figma_ref", "blueprint_ref", "case_ref"):
        if evidence.get(key):
            return str(evidence[key])
    return issue.get("category", "")


def _issue_blob(issue: dict) -> str:
    return " ".join(
        [
            str(issue.get("category") or ""),
            str(issue.get("description") or ""),
            str(issue.get("suggestion") or ""),
            json.dumps(issue.get("evidence") or {}, ensure_ascii=False),
        ]
    ).lower()


def _product_group_key(issue: dict) -> str:
    blob = _issue_blob(issue)
    if "figma" in blob or "设计稿" in blob or "字号" in blob or "typography" in blob:
        return "figma_typography"
    if "空格" in blob or "spacing" in blob or "£x pm" in blob or "£1,200pm" in blob:
        return "price_spacing"
    if "a/b" in blob or "ab " in blob or "tbd" in blob or "分桶" in blob or "variant" in blob:
        return "ab_plan"
    if "price_frequency" in blob or "price.type" in blob or "映射" in blob:
        return "price_field_mapping"
    return f"issue_{issue.get('id', '')}"


def _product_group_title(key: str, issues: list[dict]) -> str:
    severity = {i.get("severity") for i in issues}
    prefix = "请确认" if "blocker" not in severity else "请补充"
    titles = {
        "figma_typography": "首页价格后缀的设计稿或排版规则",
        "ab_plan": "A/B 实验方案",
        "price_spacing": "pm/pw 展示时到底要不要空格",
        "price_field_mapping": "price_frequency 与 price.type 的映射关系",
    }
    if key in titles:
        return f"{prefix} {titles[key]}"
    return issues[0].get("category") or "请确认产品验收口径"


def _bullet_lines(items: list[str]) -> list[str]:
    out = []
    seen = set()
    for item in items:
        text = _short(item, 260)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(f"- {text}")
    return out or ["- 暂无补充说明。"]


def _plain_missing(issues: list[dict]) -> list[str]:
    return [
        issue.get("description", "")
        for issue in sort_issues(issues)
    ]


def _plain_impact(issues: list[dict]) -> list[str]:
    out = []
    for issue in sort_issues(issues):
        root = issue.get("root_cause")
        if root == "figma":
            out.append("没有设计稿或排版规则时，只能检查文字是否出现，不能判断字号、对齐和视觉样式是否正确。")
        elif root == "prd":
            out.append("PRD 自身没有闭合或存在冲突时，测试无法知道哪一种结果才算通过。")
        elif root == "assumption_unresolved":
            out.append("当前说明可以被理解成多种结果，测试写死任一结果都有误判风险。")
        else:
            out.append(issue.get("description", ""))
    return out


def _plain_request(issues: list[dict]) -> list[str]:
    return [
        issue.get("suggestion", "")
        for issue in sort_issues(issues)
    ]


def _plain_locations(issues: list[dict]) -> list[str]:
    out = []
    for issue in sort_issues(issues):
        ev = issue.get("evidence") or {}
        for key in ("prd_section", "figma_ref", "blueprint_ref", "case_ref", "quoted_problem"):
            if ev.get(key):
                out.append(str(ev[key]))
    return out


def _role_summary(report: dict) -> list[str]:
    tri = report.get("tri_party") or {}
    role_names = {
        "product": "产品可验收性",
        "qa": "QA 覆盖",
        "testability": "可测性",
        "red_team": "风险视角",
    }
    issues = report.get("issues") or []
    rows = []
    for key, name in role_names.items():
        row = tri.get(key) or {}
        verdict = row.get("verdict")
        count = row.get("finding_count")
        if verdict is None:
            if key == "product":
                count = sum(1 for i in issues if i.get("audience") == "product")
            elif key == "qa":
                count = sum(1 for i in issues if i.get("root_cause") == "qa_undercoverage")
            elif key == "testability":
                count = sum(1 for i in issues if i.get("dimension") == "testability")
            else:
                count = sum(1 for i in issues if i.get("dimension") == "red_team")
            verdict = "fail" if count else "pass"
        rows.append(f"- {name}: {'发现问题' if verdict == 'fail' else '未发现问题'}，数量 {count or 0}")
    return rows


def _issue_sections(issues: list[dict]) -> list[str]:
    if not issues:
        return ["未发现问题。"]
    lines = []
    for idx, issue in enumerate(sort_issues(issues), start=1):
        lines.extend(
            [
                f"### {idx}. {issue.get('id', '未编号')} {issue.get('severity', '')}",
                "",
                f"- 问题: {_short(issue.get('description', ''), 260)}",
                f"- 发现位置: {_short(_issue_location(issue), 120) or '未标注'}",
                f"- 归属团队: {_team(issue)}",
                f"- 回退动作: {_retry_label(issue)}",
                f"- 建议: {_short(issue.get('suggestion', ''), 220) or '暂无'}",
                "",
            ]
        )
    return lines


def _product_issues(report: dict) -> list[dict]:
    return [i for i in report.get("issues") or [] if i.get("audience") == "product"]


def _nonblocking_product_questions(report: dict) -> list[dict]:
    """Surface product-facing confirmations that were not promoted to blocker issues."""
    out: list[dict] = []
    seen: set[str] = set()
    notes = report.get("extra_notes") or {}
    for perspective in ("product", "structural"):
        for idx, note in enumerate(notes.get(perspective) or [], start=1):
            blob = " ".join(
                str(note.get(k) or "") for k in ("note", "rationale", "knowledge_ref")
            )
            blob_l = blob.lower()
            if "price_frequency" not in blob_l and "price.type" not in blob_l:
                continue
            key = _product_group_key(
                {
                    "id": f"NOTE-{perspective}-{idx}",
                    "category": "product confirmation",
                    "description": blob,
                    "suggestion": blob,
                    "evidence": {},
                }
            )
            if key != "price_field_mapping":
                continue
            if blob in seen:
                continue
            seen.add(blob)
            out.append(
                {
                    "id": f"{perspective.upper()}-NOTE-{idx:03d}",
                    "severity": "minor",
                    "root_cause": "assumption_unresolved",
                    "audience": "product",
                    "retry_target": "product",
                    "category": "非阻断确认",
                    "description": note.get("note") or blob,
                    "suggestion": note.get("rationale")
                    or "请产品或研发确认字段映射口径，便于联调前关闭。",
                    "evidence": {"quoted_problem": "extra_notes"},
                    "_nonblocking_confirmation": True,
                }
            )
    return out


def _internal_issues(report: dict) -> list[dict]:
    out = []
    for i in report.get("issues") or []:
        audience = i.get("audience") or "product"
        root = i.get("root_cause") or ""
        retry = i.get("retry_target") or ""
        if audience == "internal" or root in ("qa_undercoverage", "case_generation"):
            out.append(i)
        elif retry in ("prd-analyze", "case-generate"):
            out.append(i)
    return out


def render_review_markdown(report: dict) -> str:
    issues = report.get("issues") or []
    product_like = _product_issues(report)
    case_like = [i for i in issues if i.get("root_cause") in ("qa_undercoverage", "case_generation")]
    lines = [
        "# 用例评审报告",
        "",
        f"- 结论: **{report.get('verdict', '')}**",
        f"- 类型: **{report.get('reject_kind', 'pass')}**",
        f"- 时间: {_report_time(report)}",
        f"- 摘要: {report.get('summary', '').strip()}",
        "",
        "## 角色评审结果",
        "",
        *_role_summary(report),
        "",
        "## 蓝图 vs PRD/Figma",
        "",
        f"- 是否发现问题: **{'是' if product_like else '否'}**",
        "",
        *_issue_sections(product_like),
        "",
        "## 用例 vs 蓝图",
        "",
        f"- 是否发现问题: **{'是' if case_like else '否'}**",
        "",
        *_issue_sections(case_like),
        "",
        "## 全部问题清单",
        "",
        *_issue_sections(issues),
        "",
    ]
    return "\n".join(lines)


def _find_previous_reject(current_artifacts: Path) -> dict | None:
    """
    Find the most recent previous run's prd-reject-to-product issues for the same project.
    Returns a dict mapping issue id → issue dict, or None if no previous run found.
    """
    import os
    project = os.environ.get("QA_PROJECT")
    if not project:
        return None

    runs_dir = ROOT / "workspace" / "projects" / project / "runs"
    if not runs_dir.exists():
        return None

    # Current run dir name (e.g. 20260605T033144Z)
    try:
        current_run = current_artifacts.resolve().name
    except Exception:
        return None

    # Find all run dirs sorted descending, skip current
    all_runs = sorted(
        [d for d in runs_dir.iterdir() if d.is_dir() and d.name != current_run],
        reverse=True,
    )

    for prev_run in all_runs:
        prev_report = prev_run / "03-review-report.json"
        if prev_report.exists():
            try:
                report = json.loads(prev_report.read_text(encoding="utf-8"))
                prev_issues = {
                    i["id"]: i
                    for i in report.get("issues", [])
                    if i.get("audience") == "product"
                }
                return prev_issues
            except Exception:
                continue

    return None


def render_reject_markdown(report: dict) -> str:
    product = _product_issues(report)
    product_actions = [*product, *_nonblocking_product_questions(report)]
    grouped: dict[str, list[dict]] = {}
    for issue in sort_issues(product_actions):
        grouped.setdefault(_product_group_key(issue), []).append(issue)
    blocking_count = sum(1 for issue in product if issue.get("blocking") or issue.get("severity") == "blocker")
    action_count = len(grouped)
    lines = [
        "# 产品修订说明",
        "",
        "## 本次为什么不能进入测试",
        "",
        f"这次评审发现 {len(product)} 条需要产品或设计补充的信息，其中 {blocking_count} 条会阻塞测试继续执行。",
        "测试不是不通过功能本身，而是现在缺少可判断对错的产品口径；补齐后需要从需求分析阶段重跑一次。",
        f"为便于处理，下面按产品动作归并为 {action_count} 个问题；同一问题下的内部追踪编号表示同一个待补充点被不同检查发现。",
        "",
        f"评审时间：{_report_time(report)}",
        "",
        "## 需要产品确认或补充的问题",
        "",
    ]
    for idx, (key, issues) in enumerate(grouped.items(), start=1):
        ids = ", ".join(
            i.get("id", "")
            for i in issues
            if i.get("id") and not i.get("_nonblocking_confirmation")
        )
        lines.extend(
            [
                f"### {idx}. {_product_group_title(key, issues)}",
                "",
                "#### 现在缺什么",
                *_bullet_lines(_plain_missing(issues)),
                "",
                "#### 为什么会影响测试",
                *_bullet_lines(_plain_impact(issues)),
                "",
                "#### 请产品补充什么",
                *_bullet_lines(_plain_request(issues)),
                "",
                "#### 涉及位置",
                *_bullet_lines(_plain_locations(issues)),
                "",
                f"内部追踪：{ids or '非阻断确认项'}",
                "",
            ]
        )
    lines += [
        "## 修订后怎么重跑",
        "",
        "产品或设计补充完成后，请重新提交 PRD/Figma 信息，然后从需求分析阶段重跑：",
        "",
        "```bash",
        "./orchestrators/cursor/run-pipeline.sh --from-stage prd-analyze",
        "```",
        "",
    ]
    return "\n".join(lines)


def render_legacy_reject_markdown(report: dict) -> str:
    product = _product_issues(report)
    blocking = [i for i in product if i.get("blocking") or i.get("severity") == "blocker"]
    lines = [
        "# PRD/Figma 修订后重跑",
        "",
        f"- 产品问题: {len(product)} 条",
        f"- 阻塞测试执行: {len(blocking)} 条",
        f"- 面向产品阅读文档: `prd-reject-to-product.md`",
        "",
        "请优先阅读 `prd-reject-to-product.md`，该文档已按产品动作归并问题；本文件仅作为兼容标记。",
        "",
    ]
    return "\n".join(lines)


def render_rework_markdown(report: dict) -> str:
    internal = _internal_issues(report)
    lines = [
        "# QA 内部返工说明",
        "",
        f"**摘要**: {report.get('summary', '').strip()}",
        "",
        f"**时间**: {_report_time(report)}",
        "",
        "## 用例 vs 蓝图 / 蓝图内部问题",
        "",
        *_issue_sections(internal),
        "",
        "建议重跑阶段：按每个问题中的「回退动作」执行。",
        "",
    ]
    return "\n".join(lines)


def render_pass_markdown(report: dict) -> str:
    lines = [
        "# 用例评审门禁通过说明",
        "",
        "**裁决**: pass（可进入测试执行）",
        "",
        f"**说明**: {report.get('summary', '').strip()}",
        "",
        f"**评审时间**: {_report_time(report)}",
        "",
        "测试蓝图与测试用例已通过门禁；后续测试执行、Bug 记录、自动化转换默认不再就需求细节联系产品。",
        "",
    ]
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
    from analyze_prerequisites import require_analyze_complete

    pre = require_analyze_complete("render_case_review_notice")
    if pre:
        raise SystemExit(
            "Cannot render case-review notice: prd-analyze not validated.\n"
            + "\n".join(f"  - {e}" for e in pre)
        )

    report = load_report(report_path)
    REVIEW_MD.write_text(render_review_markdown(report), encoding="utf-8")
    verdict = report.get("verdict")
    if verdict == "reject":
        product = _product_issues(report)
        internal = _internal_issues(report)
        if internal:
            rework_path.write_text(render_rework_markdown(report), encoding="utf-8")
        else:
            if rework_path.exists():
                rework_path.unlink()
        if product:
            reject_path.write_text(render_reject_markdown(report), encoding="utf-8")
            LEGACY_REJECT_MD.write_text(render_legacy_reject_markdown(report), encoding="utf-8")
        else:
            if reject_path.exists():
                reject_path.unlink()
            if LEGACY_REJECT_MD.exists():
                LEGACY_REJECT_MD.unlink()
        if pass_path.exists():
            pass_path.unlink()
        if internal:
            return rework_path
        if product:
            return reject_path
        rework_path.write_text(render_rework_markdown(report), encoding="utf-8")
        if reject_path.exists():
            reject_path.unlink()
        if LEGACY_REJECT_MD.exists():
            LEGACY_REJECT_MD.unlink()
        if pass_path.exists():
            pass_path.unlink()
        return rework_path
    if verdict == "pass":
        pass_path.write_text(render_pass_markdown(report), encoding="utf-8")
        if reject_path.exists():
            reject_path.unlink()
        if LEGACY_REJECT_MD.exists():
            LEGACY_REJECT_MD.unlink()
        if rework_path.exists():
            rework_path.unlink()
        return pass_path
    raise ValueError(f"unknown verdict: {verdict}")


def main() -> int:
    path = write_product_markdown()
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
