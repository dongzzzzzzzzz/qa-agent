#!/usr/bin/env python3
"""Shared deterministic coverage / rework / pre-review checks for QA pipeline."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

def _artifacts_dir() -> Path:
    import os
    if os.environ.get("QA_WORKSPACE"):
        return Path(os.environ["QA_WORKSPACE"])
    return ROOT / "workspace" / "artifacts"

ARTIFACTS = _artifacts_dir()
PENDING_REWORK_FILE = ARTIFACTS / ".pending-rework-issues.json"
PRECHECK_FILE = ARTIFACTS / "case-review-precheck.json"
SNAPSHOTS_DIR = ARTIFACTS / "snapshots"


def _all_scenarios(blueprint: dict) -> list[dict]:
    out: list[dict] = []
    for module in blueprint.get("modules") or []:
        for point in module.get("test_points") or []:
            for scenario in point.get("scenarios") or []:
                out.append(
                    {
                        "module": module,
                        "point": point,
                        "scenario": scenario,
                    }
                )
    return out


def _blueprint_blob(blueprint: dict) -> str:
    return json.dumps(blueprint, ensure_ascii=False).lower()


def _scenario_blob(scenario: dict) -> str:
    parts: list[str] = []
    for key in ("title", "preconditions", "test_data", "steps", "expected_results", "postconditions"):
        val = scenario.get(key)
        if isinstance(val, list):
            parts.extend(str(x) for x in val)
        elif val:
            parts.append(str(val))
    return " ".join(parts).lower()


def required_coverage_items(config: dict) -> list[dict]:
    """兼容旧名：与 obligation_items 相同。"""
    return obligation_items(config)


def obligation_items(config: dict) -> list[dict]:
    """合并 required_coverage + prd_contract_obligations（按 id 去重）。"""
    out: list[dict] = []
    seen: set[str] = set()
    for key in ("required_coverage", "prd_contract_obligations"):
        for item in config.get(key) or []:
            if not isinstance(item, dict):
                continue
            oid = str(item.get("id") or "").strip()
            if oid:
                if oid in seen:
                    continue
                seen.add(oid)
            out.append(item)
    return out


def _scenario_matches_obligation(row: dict, item: dict) -> bool:
    """优先使用场景的 covers 字段精确匹配；无 covers 时降级到关键词匹配（兼容旧蓝图）。"""
    scenario = row["scenario"]
    obligation_id = str(item.get("id") or "").strip()

    # 优先路径：covers 字段精确匹配（AI 在生成场景时主动声明）
    covers = scenario.get("covers")
    if covers is not None:  # 字段存在（即使是空列表也说明 AI 明确填写了）
        if not obligation_id:
            return False
        # channel 约束仍然生效
        channel = str(scenario.get("execution_channel") or "").lower()
        req_channel = item.get("require_channel")
        if req_channel and channel != str(req_channel).lower():
            return False
        req_channels = item.get("require_channels") or []
        if req_channels:
            allowed = {str(c).lower() for c in req_channels}
            if channel not in allowed:
                return False
        return obligation_id in [str(c).strip() for c in covers]

    # 降级路径：旧蓝图没有 covers 字段，继续用关键词匹配
    blob = _scenario_blob(scenario)
    channel = str(scenario.get("execution_channel") or "").lower()

    require_all = [str(k).lower() for k in (item.get("require_all_in_scenario") or []) if str(k).strip()]
    if require_all:
        if not all(kw in blob for kw in require_all):
            return False
    else:
        keywords = [str(k).lower() for k in (item.get("keywords") or []) if str(k).strip()]
        if keywords and not any(kw in blob for kw in keywords):
            return False

    req_channel = item.get("require_channel")
    if req_channel and channel != str(req_channel).lower():
        return False
    req_channels = item.get("require_channels") or []
    if req_channels:
        allowed = {str(c).lower() for c in req_channels}
        if channel not in allowed:
            return False
    return True


def _obligation_hits(blueprint: dict, item: dict) -> tuple[int, list[str]]:
    scenarios = _all_scenarios(blueprint)
    matched_ids: list[str] = []
    for row in scenarios:
        if _scenario_matches_obligation(row, item):
            sid = str(row["scenario"].get("scenario_id") or "")
            if sid:
                matched_ids.append(sid)
    return len(matched_ids), matched_ids


def validate_prd_obligations(blueprint: dict, config: dict) -> list[str]:
    """② PRD 契约清单：每项至少 min_scenarios 条场景满足 keywords / require_all / channel。"""
    errors: list[str] = []
    for item in obligation_items(config):
        cid = item.get("id") or "?"
        label = item.get("label") or cid
        min_n = int(item.get("min_scenarios") or 1)
        keywords = [str(k).lower() for k in (item.get("keywords") or []) if str(k).strip()]
        require_all = item.get("require_all_in_scenario") or []
        if not keywords and not require_all:
            continue
        hits, _ = _obligation_hits(blueprint, item)
        if hits < min_n:
            detail = require_all if require_all else keywords
            ch = item.get("require_channel") or item.get("require_channels")
            ch_note = f", channel={ch}" if ch else ""
            errors.append(
                f"prd_obligation[{cid}] ({label}): need >={min_n} scenario(s) matching "
                f"{detail}{ch_note}, found {hits}"
            )
    return errors


def validate_required_coverage(blueprint: dict, config: dict) -> list[str]:
    return validate_prd_obligations(blueprint, config)


def build_prd_coverage_matrix(blueprint: dict, config: dict) -> dict:
    """供子 Agent / 评审读取：每条 PRD 契约义务是否已在蓝图中闭合。"""
    rows: list[dict] = []
    for item in obligation_items(config):
        cid = item.get("id") or "?"
        label = item.get("label") or cid
        min_n = int(item.get("min_scenarios") or 1)
        hits, matched_ids = _obligation_hits(blueprint, item)
        rows.append(
            {
                "id": cid,
                "label": label,
                "min_scenarios": min_n,
                "matched_count": hits,
                "matched_scenario_ids": matched_ids,
                "status": "pass" if hits >= min_n else "fail",
                "source": item.get("source") or "config.yaml",
            }
        )
    failed = [r for r in rows if r["status"] == "fail"]
    return {
        "version": "1.0",
        "obligation_count": len(rows),
        "failed_count": len(failed),
        "pass": len(failed) == 0,
        "obligations": rows,
    }


def write_prd_coverage_matrix(blueprint: dict, config: dict) -> Path:
    path = ARTIFACTS / "prd-coverage-matrix.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_prd_coverage_matrix(blueprint, config)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _internal_issues(report: dict) -> list[dict]:
    issues = []
    for i in report.get("issues") or []:
        aud = i.get("audience") or "product"
        root = i.get("root_cause") or ""
        retry = i.get("retry_target") or ""
        if aud == "internal" or root in ("qa_undercoverage", "case_generation"):
            issues.append(i)
        elif retry in ("prd-analyze", "case-generate"):
            issues.append(i)
    return issues


def build_pending_rework_issues(report: dict, config: dict) -> dict:
    """① 返工核销：从评审报告提取待闭合内部项 + 解析验收条件。"""
    items = obligation_items(config)
    pending = []
    for issue in _internal_issues(report):
        entry: dict[str, Any] = {
            "id": issue.get("id"),
            "description": issue.get("description"),
            "suggestion": issue.get("suggestion"),
            "scenario_ids": issue.get("scenario_ids") or [],
            "module_ids": issue.get("module_ids") or [],
        }
        checks: dict[str, Any] = {}
        desc = (issue.get("description") or "") + " " + (issue.get("suggestion") or "")
        desc_l = desc.lower()
        # 子类目漏测 → 要求 required_coverage 全部满足
        if any(
            tok in desc_l
            for tok in (
                "to share",
                "commercial",
                "parking",
                "holiday",
                "子类目",
                "in scope",
                "prd_obligation",
                "price_frequency",
                "amount=0",
                "type=free",
                "api 契约",
            )
        ):
            checks["coverage_ids"] = [it.get("id") for it in items if it.get("id")]
        # 显式 scenario 引用：返工后应新增场景（旧 id 可保留，但须有新增覆盖）
        if issue.get("scenario_ids"):
            checks["require_new_scenarios_min"] = 1
            checks["related_module_ids"] = issue.get("module_ids") or []
        entry["resolution_check"] = checks
        pending.append(entry)
    return {
        "from_reviewed_at": report.get("reviewed_at"),
        "issues": pending,
    }


def write_pending_rework(report: dict, config: dict) -> Path:
    PENDING_REWORK_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = build_pending_rework_issues(report, config)
    PENDING_REWORK_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return PENDING_REWORK_FILE


def clear_pending_rework() -> None:
    PENDING_REWORK_FILE.unlink(missing_ok=True)


def validate_rework_resolution(blueprint: dict, config: dict) -> list[str]:
    """① 返工核销：prd-analyze 后待闭合内部项须满足 resolution_check。"""
    if not PENDING_REWORK_FILE.exists():
        return []
    try:
        pending = json.loads(PENDING_REWORK_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["invalid .pending-rework-issues.json"]
    errors: list[str] = []
    scenarios = _all_scenarios(blueprint)
    scenario_count_by_module: dict[str, int] = {}
    for row in scenarios:
        mid = row["module"].get("module_id") or ""
        scenario_count_by_module[mid] = scenario_count_by_module.get(mid, 0) + 1

    for issue in pending.get("issues") or []:
        iid = issue.get("id") or "?"
        check = issue.get("resolution_check") or {}
        cov_ids = check.get("coverage_ids") or []
        if cov_ids:
            all_items = obligation_items(config)
            subset = {
                "required_coverage": [c for c in all_items if c.get("id") in cov_ids],
                "prd_contract_obligations": [],
            }
            sub_errs = validate_prd_obligations(blueprint, subset)
            for e in sub_errs:
                errors.append(f"rework {iid}: {e}")

        min_new = int(check.get("require_new_scenarios_min") or 0)
        related_modules = check.get("related_module_ids") or []
        if min_new > 0 and related_modules:
            total = sum(scenario_count_by_module.get(m, 0) for m in related_modules)
            # 返工应扩充：相关模块至少 min_new+1 场景（原为 1 条漏测时）
            if total <= min_new:
                errors.append(
                    f"rework {iid}: module(s) {related_modules} need more scenarios after rework, found {total}"
                )

    if not errors:
        clear_pending_rework()
    return errors


def _figma_is_placeholder(figma_path: Path) -> bool:
    if not figma_path.exists():
        return True
    text = figma_path.read_text(encoding="utf-8").strip().upper()
    return "PLACEHOLDER" in text or len(text) < 12


def run_case_review_precheck(
    blueprint: dict,
    cases_text: str,
    config: dict,
    *,
    figma_path: Path,
    prd_path: Path | None = None,
) -> dict:
    """③ 评审预检：确定性 GATE 项，供 case-review 合并进 issues 或阻塞 pass。"""
    findings: list[dict] = []
    seq = 1

    def gate(
        category: str,
        description: str,
        *,
        root_cause: str = "qa_undercoverage",
        audience: str = "internal",
        retry_target: str = "prd-analyze",
        severity: str = "major",
        blocking: bool = True,
    ) -> None:
        nonlocal seq
        findings.append(
            {
                "id": f"GATE-{seq:03d}",
                "severity": severity,
                "category": category,
                "root_cause": root_cause,
                "audience": audience,
                "retry_target": retry_target,
                "blocking": blocking,
                "dimension": "coverage" if audience == "internal" else "acceptance",
                "description": description,
                "evidence": {"source": "scripts/qa_coverage_checks.py"},
                "suggestion": description,
            }
        )
        seq += 1

    matrix = build_prd_coverage_matrix(blueprint, config)
    write_prd_coverage_matrix(blueprint, config)
    for row in matrix.get("obligations") or []:
        if row.get("status") == "fail":
            gate(
                "PRD 契约未闭合",
                f"{row.get('id')}: {row.get('label')} — matched {row.get('matched_count')}/"
                f"{row.get('min_scenarios')}",
                root_cause="qa_undercoverage",
                audience="internal",
            )

    if _figma_is_placeholder(figma_path):
        gate(
            "设计稿不可用",
            "figma.url 为 PLACEHOLDER 或缺失，无法验收 Requirement 3 排版/字号。",
            root_cause="figma",
            audience="product",
            retry_target="product",
            severity="blocker",
        )

    for q in blueprint.get("open_questions") or []:
        if q.get("blocking") is True:
            gate(
                "阻塞级 open_question",
                f"{q.get('id')}: {q.get('question', '')}",
                root_cause="assumption_unresolved",
                audience="product",
                retry_target="product",
                severity="blocker",
            )

    if prd_path and prd_path.exists():
        prd = prd_path.read_text(encoding="utf-8").lower()
        if "a/b testing plan (tbd)" in prd or "testing plan (tbd)" in prd:
            gate(
                "A/B 未闭合",
                "PRD A/B Testing Plan 标注 TBD，实验分桶不可验收。",
                root_cause="prd",
                audience="product",
                retry_target="product",
                severity="blocker",
            )
        if "£x pm" in prd or "£x pw" in prd:
            if "no additional spacing" in prd or "£1,200pm" in prd:
                gate(
                    "PRD 规则矛盾",
                    "Requirement 3 要求无空格，A/B Variant 示例含 £X pm/pw 空格，须产品统一。",
                    root_cause="prd",
                    audience="product",
                    retry_target="product",
                    severity="blocker",
                )

    expected = len(_all_scenarios(blueprint))
    actual = len(re.findall(r"^###\s+TC-\d{3}:", cases_text, re.MULTILINE))
    if actual != expected:
        gate(
            "用例条数不一致",
            f"blueprint scenarios={expected}, test cases={actual}",
            root_cause="case_generation",
            audience="internal",
            retry_target="prd-analyze",
        )

    return {
        "version": "1.0",
        "precheck_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "finding_count": len(findings),
        "findings": findings,
        "pass": len(findings) == 0,
    }


def write_precheck_report(payload: dict) -> Path:
    PRECHECK_FILE.parent.mkdir(parents=True, exist_ok=True)
    PRECHECK_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return PRECHECK_FILE


def validate_review_against_precheck(report: dict) -> list[str]:
    """③ pass 时不得忽略 GATE；reject 时须覆盖全部 blocking GATE。"""
    if not PRECHECK_FILE.exists():
        return []
    pre = json.loads(PRECHECK_FILE.read_text(encoding="utf-8"))
    findings = pre.get("findings") or []
    if not findings:
        return []
    errors: list[str] = []
    report_ids = {i.get("id") for i in report.get("issues") or []}
    report_text = json.dumps(report, ensure_ascii=False).lower()
    verdict = report.get("verdict")
    for g in findings:
        gid = g.get("id")
        desc = (g.get("description") or "")[:80]
        if verdict == "pass":
            errors.append(f"precheck {gid} still open but verdict=pass: {desc}")
            continue
        if g.get("blocking") and gid not in report_ids:
            # 允许 CR 描述包含相同语义而不强制 GATE id
            key = desc[:40].lower()
            if key not in report_text:
                errors.append(f"precheck {gid} not reflected in review issues[]: {desc}")
    return errors


def snapshot_save(label: str | None = None) -> Path:
    """④ 快照：保存当前蓝图副本。"""
    import shutil
    from datetime import datetime, timezone

    src = ARTIFACTS / "00-test-blueprint.json"
    if not src.exists():
        raise FileNotFoundError(src)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"{stamp}-{label}" if label else stamp
    dest_dir = SNAPSHOTS_DIR / name
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest_dir / "00-test-blueprint.json")
    meta = {"label": label or "", "saved_at": stamp, "scenario_count": len(_all_scenarios(json.loads(src.read_text())))}
    (dest_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return dest_dir


def snapshot_compare(a: str, b: str | None = None) -> str:
    """④ 对比两个快照或「当前」与最新快照。"""
    def load(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def titles(bp: dict) -> list[str]:
        return [s["scenario"].get("title", "") for s in _all_scenarios(bp)]

    if b is None:
        dirs = sorted([d for d in SNAPSHOTS_DIR.iterdir() if d.is_dir()], reverse=True)
        if not dirs:
            return "no snapshots"
        b_path = dirs[0] / "00-test-blueprint.json"
        b_label = dirs[0].name
    else:
        b_path = SNAPSHOTS_DIR / b / "00-test-blueprint.json"
        b_label = b
    a_path = SNAPSHOTS_DIR / a / "00-test-blueprint.json"
    if not a_path.exists() or not b_path.exists():
        return "snapshot path missing"
    bp_a, bp_b = load(a_path), load(b_path)
    ta, tb = set(titles(bp_a)), set(titles(bp_b))
    lines = [
        f"compare: {a} ({len(ta)} scenarios) vs {b_label} ({len(tb)} scenarios)",
        f"  only in A: {sorted(ta - tb)[:20]}",
        f"  only in B: {sorted(tb - ta)[:20]}",
    ]
    return "\n".join(lines)
