#!/usr/bin/env python3
"""Build seed questions and reading suggestions for case-review perspectives."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def artifacts_dir() -> Path:
    if os.environ.get("QA_WORKSPACE"):
        return Path(os.environ["QA_WORKSPACE"])
    return ROOT / "workspace" / "artifacts"


ARTIFACTS = artifacts_dir()
INPUTS = Path(os.environ.get("QA_INPUTS", str(ROOT / "workspace" / "inputs")))


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def all_scenarios(blueprint: dict) -> list[dict]:
    rows: list[dict] = []
    for module in blueprint.get("modules") or []:
        for point in module.get("test_points") or []:
            for scenario in point.get("scenarios") or []:
                rows.append(
                    {
                        "module_id": module.get("module_id", ""),
                        "module_title": module.get("title", ""),
                        "point_id": point.get("point_id", ""),
                        "point_title": point.get("title", ""),
                        "scenario_id": scenario.get("scenario_id", ""),
                        "scenario_title": scenario.get("title", ""),
                        "type": scenario.get("type", ""),
                        "execution_channel": scenario.get("execution_channel", ""),
                        "automatable": scenario.get("automatable", ""),
                        "text": json.dumps(scenario, ensure_ascii=False).lower(),
                    }
                )
    return rows


def selected_docs(knowledge: dict) -> list[dict]:
    return [d for d in knowledge.get("selected_documents") or [] if isinstance(d, dict)]


def docs_for_perspective(docs: list[dict], perspective: str) -> list[dict]:
    scored: list[tuple[int, dict]] = []
    path_terms = {
        "product": ("产品全景", "业务规则库", "业务知识图谱", "规则"),
        "qa": ("文本用例", "测试用例", "业务流程", "业务知识图谱"),
        "testability": ("文本用例", "测试用例", "业务流程"),
        "red_team": ("文本用例", "规则", "业务规则库", "历史", "bug"),
    }[perspective]
    for doc in docs:
        path = str(doc.get("path") or "")
        reason = str(doc.get("reason") or "")
        blob = f"{path} {reason}".lower()
        score = sum(1 for term in path_terms if term.lower() in blob)
        if score:
            scored.append((score, doc))
    if not scored:
        scored = [(0, d) for d in docs[:2]]
    return [d for _, d in sorted(scored, key=lambda x: -x[0])[:3]]


def qid(prefix: str, idx: int) -> str:
    return f"P-{prefix}-{idx:02d}"


def question(
    prefix: str,
    idx: int,
    text: str,
    *,
    row: dict | None = None,
    obligation_id: str | None = None,
    knowledge_refs: list[str] | None = None,
    rationale: str = "",
) -> dict:
    payload = {
        "id": qid(prefix, idx),
        "question": text,
        "rationale": rationale,
        "knowledge_refs": knowledge_refs or [],
    }
    if row:
        payload.update(
            {
                "module_id": row.get("module_id", ""),
                "point_id": row.get("point_id", ""),
                "scenario_id": row.get("scenario_id", ""),
            }
        )
    if obligation_id:
        payload["obligation_id"] = obligation_id
    return payload


def obligation_questions(config: dict) -> list[dict]:
    out: list[dict] = []
    for key in ("required_coverage", "prd_contract_obligations"):
        for item in config.get(key) or []:
            if isinstance(item, dict):
                out.append(item)
    return out


def build_brief(blueprint: dict, knowledge: dict, config: dict) -> dict:
    rows = all_scenarios(blueprint)
    docs = selected_docs(knowledge)
    doc_paths = {
        p: [str(d.get("path") or "") for d in docs_for_perspective(docs, p)]
        for p in ("product", "qa", "testability", "red_team")
    }
    obligations = obligation_questions(config)
    first_row = rows[0] if rows else {}
    high_risk = next(
        (
            r
            for r in rows
            if any(term in r.get("text", "") for term in ("null", "unknown", "amount", "price", "status", "enum"))
        ),
        first_row,
    )
    boundary = next(
        (
            r
            for r in rows
            if any(term in r.get("text", "") for term in ("0", "empty", "边界", "max", "min", "null"))
        ),
        first_row,
    )
    browser_row = next((r for r in rows if r.get("execution_channel") == "browser"), first_row)
    auto_yes = (config.get("execution") or {}).get("automatable_yes_channels") or ["browser", "api_intercept"]
    auto_no = (config.get("execution") or {}).get("automatable_no_channels") or ["native_app", "manual"]
    platform = config.get("target_platform") or config.get("platform") or "未声明"

    product_qs = [
        question(
            "PD",
            1,
            "PRD/Figma 中可验收的义务是否都能被当前蓝图和用例证明，是否存在产品验收无法裁定的点？",
            row=first_row,
            obligation_id=str((obligations[0] or {}).get("id") or "") if obligations else None,
            knowledge_refs=doc_paths["product"],
            rationale="产品视角优先判断需求本身是否可验收。",
        ),
        question(
            "PD",
            2,
            "蓝图 open_questions、Figma/PRD 冲突或 TBD 是否仍阻塞最终验收，是否必须打回产品？",
            row=first_row,
            knowledge_refs=doc_paths["product"],
            rationale="blocking open question 不能被覆盖率抵消。",
        ),
    ]
    if obligations[1:2]:
        product_qs.append(
            question(
                "PD",
                3,
                f"契约义务 {obligations[1].get('id')}（{obligations[1].get('label', '')}）是否被可读用例覆盖且验收口径清晰？",
                obligation_id=str(obligations[1].get("id") or ""),
                knowledge_refs=doc_paths["product"],
            )
        )

    qa_qs = [
        question(
            "QA",
            1,
            "主链路、反向链路、状态组合是否存在显而易见漏测，尤其是蓝图场景和 Markdown 用例是否 1:1？",
            row=first_row,
            knowledge_refs=doc_paths["qa"],
        ),
        question(
            "QA",
            2,
            "边界值、空值、零值、最大/最小值或多条件组合是否有对应场景和可执行步骤？",
            row=boundary,
            knowledge_refs=doc_paths["qa"],
        ),
    ]

    testability_qs = [
        question(
            "TB",
            1,
            f"当前 target_platform={platform}，automatable_yes_channels={auto_yes}，automatable_no_channels={auto_no}；用例执行通道是否与配置一致？",
            row=browser_row,
            knowledge_refs=doc_paths["testability"],
            rationale="可测性问题必须从项目配置和目标平台派生。",
        ),
        question(
            "TB",
            2,
            "测试数据、环境状态、断言观察点是否足够稳定，是否存在依赖随机线上数据或不可准备状态的用例？",
            row=browser_row,
            knowledge_refs=doc_paths["testability"],
        ),
    ]

    red_team_qs = [
        question(
            "RT",
            1,
            "如果 API 返回未知枚举、空值、amount=0、状态缺失或降级响应，当前用例是否能在上线前暴露问题？",
            row=high_risk,
            knowledge_refs=doc_paths["red_team"],
            rationale="red_team 至少覆盖一个字段、枚举、空值、金额或状态类风险。",
        ),
        question(
            "RT",
            2,
            "参考知识库历史同类用例，最常见的线上表现是否都有对应断言，若无历史请明确声明无同类历史。",
            row=high_risk,
            knowledge_refs=doc_paths["red_team"],
        ),
    ]

    perspectives = {
        "product": {"perspective": "product", "focus": "产品验收与需求闭合", "questions": product_qs},
        "qa": {"perspective": "qa", "focus": "覆盖完整性与漏测", "questions": qa_qs},
        "testability": {"perspective": "testability", "focus": "执行通道、数据和可观察性", "questions": testability_qs},
        "red_team": {"perspective": "red_team", "focus": "历史回归、异常和线上高风险", "questions": red_team_qs},
    }
    total = sum(len(p["questions"]) for p in perspectives.values())
    anchored = sum(
        1
        for p in perspectives.values()
        for q in p["questions"]
        if q.get("scenario_id") or q.get("point_id") or q.get("obligation_id")
    )
    return {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": [
            "00-test-blueprint.json",
            "00-knowledge-context.json",
            "config.yaml",
            "00-test-data.json",
        ],
        "perspectives": perspectives,
        "knowledge_reading_list": {
            p: docs_for_perspective(docs, p) for p in ("product", "qa", "testability", "red_team")
        },
        "stats": {
            "question_count": total,
            "anchored_question_count": anchored,
            "anchored_question_ratio": round(anchored / total, 4) if total else 0,
        },
    }


def render_markdown(brief: dict) -> str:
    lines = ["# Case Review Perspective Brief", ""]
    for perspective, section in brief.get("perspectives", {}).items():
        lines.extend([f"## {perspective}", "", section.get("focus", ""), ""])
        for q in section.get("questions") or []:
            anchors = ", ".join(
                str(q.get(k))
                for k in ("module_id", "point_id", "scenario_id", "obligation_id")
                if q.get(k)
            )
            suffix = f" ({anchors})" if anchors else ""
            lines.append(f"- **{q.get('id')}** {q.get('question')}{suffix}")
        lines.append("")
        docs = brief.get("knowledge_reading_list", {}).get(perspective) or []
        lines.append("### Recommended Knowledge")
        if docs:
            for doc in docs:
                lines.append(f"- `{doc.get('path')}` — {doc.get('reason', '')}")
        else:
            lines.append("- 无推荐知识库文档；子 Agent 需在 findings 中说明原因。")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", default=None)
    args = parser.parse_args()
    global ARTIFACTS
    if args.artifacts:
        ARTIFACTS = Path(args.artifacts)

    blueprint = load_json(ARTIFACTS / "00-test-blueprint.json", {})
    knowledge = load_json(ARTIFACTS / "00-knowledge-context.json", {})
    config = load_yaml(INPUTS / "config.yaml")
    brief = build_brief(blueprint, knowledge, config)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "case-review-perspective-brief.json").write_text(
        json.dumps(brief, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ARTIFACTS / "case-review-perspective-brief.md").write_text(
        render_markdown(brief),
        encoding="utf-8",
    )
    print(ARTIFACTS / "case-review-perspective-brief.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
