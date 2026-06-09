#!/usr/bin/env python3
"""Validate QA pipeline artifacts against the single-blueprint flow."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "contracts"

def _artifacts_dir() -> Path:
    import os
    if os.environ.get("QA_WORKSPACE"):
        return Path(os.environ["QA_WORKSPACE"])
    return ROOT / "workspace" / "artifacts"

ARTIFACTS = _artifacts_dir()
_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from load_project_config import load_project_config  # noqa: E402
from qa_coverage_checks import (  # noqa: E402
    run_case_review_precheck,
    validate_required_coverage,
    write_prd_coverage_matrix,
    validate_review_against_precheck,
    validate_rework_resolution,
    write_precheck_report,
)

BLUEPRINT_FILE = "00-test-blueprint.json"
BLUEPRINT_MD = "00-test-blueprint.md"
KNOWLEDGE_CONTEXT_FILE = "00-knowledge-context.json"

STAGE_FILES = {
    "test-blueprint": (BLUEPRINT_FILE, "test-blueprint.schema.json"),
    "prd-analyze": (BLUEPRINT_FILE, "test-blueprint.schema.json"),
    "case-review": ("03-review-report.json", "review-report.schema.json"),
    "test-execute": ("04-execution-result.json", "execution-result.schema.json"),
}
PERSPECTIVE_SLUGS = {
    "product": "product",
    "qa": "qa",
    "testability": "testability",
    "red_team": "red-team",
    "red-team": "red-team",
}
PERSPECTIVES = ("product", "qa", "testability", "red_team")
TRACE_FILE = "case-review-orchestration-trace.jsonl"
TRACE_REQUIRED_GLOBAL_EVENTS = (
    "brief_built",
    "precheck_done",
    "structural_findings_written",
    "merge_done",
    "final_validate_passed",
)
TRACE_REQUIRED_PERSPECTIVE_EVENTS = (
    "perspective_task_started",
    "perspective_task_completed",
    "perspective_validate_passed",
)
TRACE_TERMINAL_PERSPECTIVE_EVENTS = (
    "perspective_task_completed",
    "perspective_task_failed",
    "perspective_task_cancelled",
)
MIN_PERSPECTIVE_SECONDS = 5.0
ROLE_KEYWORDS = {
    "product": ("验收", "产品", "PRD", "Figma", "裁定", "需求"),
    "qa": ("主链路", "边界", "异常", "状态", "覆盖", "漏测"),
    "testability": ("执行通道", "测试数据", "断言", "可观察", "自动化", "环境"),
    "red_team": ("历史", "未知", "枚举", "空值", "amount", "金额", "状态", "降级", "线上", "回归"),
}
RISK_NOTE_RE = re.compile(r"(未覆盖|缺少|未单独覆盖|风险)")
EXPLICIT_SOURCE_RE = re.compile(r"(PRD|prd|原文|明确|要求|契约|BFF|API|Requirement)")
HISTORY_CLAIM_RE = re.compile(r"(历史|惯例|知识库|同类|回归|线上常见|homepage|测试用例)")
SOURCE_ALLOW_RE = re.compile(
    r"(PRD|prd|blueprint|Blueprint|00-test-blueprint|config|配置|00-test-data|test-data|open_questions|prd-coverage-matrix)"
)

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

_OLD_READY = "00-test-" + "ready-blueprint"
_OLD_OBLIG = "00-test-" + "ob" + "ligations"
_OLD_COVER = "covers_" + "ob" + "ligations"
_OLD_LEGACY = "legacy_" + "ob" + "ligation"
_OLD_ID = "O-" + r"\d{3}"
FORBIDDEN_INTERNAL_RE = re.compile(
    "|".join(
        re.escape(term)
        for term in (_OLD_READY, _OLD_OBLIG, _OLD_COVER, _OLD_LEGACY, "内部追踪")
    )
    + "|"
    + _OLD_ID
    + "|测试" + "义" + "务"
)

VAGUE_CASE_PHRASES = (
    "满足对应" + "义" + "务" + "断言",
    "满足 PRD 范围/非功能声明",
    "构造或筛选目标 Feed 数据",
    "执行验证",
    "验证是否正常",
    "检查是否正确",
    "功能正常",
    "页面正常",
    "显示正确",
    "展示正确",
    "按预期",
    "无异常",
    "行为符合 PRD",
    "记录实际展示",
    "按 PRD 裁定",
)
FIXED_WAIT_PATTERNS = (
    re.compile(r"\b(?:sleep|time\.sleep|setTimeout)\b", re.IGNORECASE),
    re.compile(r"等待\s*\d+\s*(?:秒|s|ms|毫秒|分钟|min)", re.IGNORECASE),
    re.compile(r"固定等待"),
)
MAX_CASE_STEPS = 10


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_json_schema(data: dict, schema_path: Path) -> list[str]:
    if not HAS_JSONSCHEMA:
        return ["jsonschema not installed; run: pip install -r requirements.txt"]
    schema = load_json(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        loc = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{loc}: {err.message}")
    return errors


def _all_scenarios(blueprint: dict) -> list[dict]:
    scenarios: list[dict] = []
    for module in blueprint.get("modules") or []:
        for point in module.get("test_points") or []:
            for scenario in point.get("scenarios") or []:
                scenarios.append(
                    {
                        **scenario,
                        "_module_title": module.get("title", ""),
                        "_point_title": point.get("title", ""),
                    }
                )
    return scenarios


def validate_knowledge_context(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing {KNOWLEDGE_CONTEXT_FILE} for prd-analyze"]
    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        return [f"{KNOWLEDGE_CONTEXT_FILE}: invalid JSON: {exc}"]
    errors: list[str] = []
    if data.get("decision_owner") != "prd-analyzer-subagent":
        errors.append(f"{KNOWLEDGE_CONTEXT_FILE}: decision_owner must be prd-analyzer-subagent")
    selected = data.get("selected_documents")
    if not isinstance(selected, list):
        errors.append(f"{KNOWLEDGE_CONTEXT_FILE}: selected_documents must be an array")
    else:
        for idx, doc in enumerate(selected):
            if not isinstance(doc, dict):
                errors.append(f"{KNOWLEDGE_CONTEXT_FILE}.selected_documents[{idx}] must be object")
                continue
            if not doc.get("path"):
                errors.append(f"{KNOWLEDGE_CONTEXT_FILE}.selected_documents[{idx}].path is required")
            if not doc.get("reason"):
                errors.append(f"{KNOWLEDGE_CONTEXT_FILE}.selected_documents[{idx}].reason is required")
            if doc.get("usage") == "requirement_source":
                errors.append(
                    f"{KNOWLEDGE_CONTEXT_FILE}.selected_documents[{idx}]: "
                    "knowledge base cannot be requirement_source; use business_context/reference_only"
                )
    return errors


def validate_blueprint_data(data: dict) -> list[str]:
    errors: list[str] = []
    text = json.dumps(data, ensure_ascii=False)
    if FORBIDDEN_INTERNAL_RE.search(text):
        errors.append("00-test-blueprint.json must not expose old internal trace terms")
    scenario_ids = [s.get("scenario_id") for s in _all_scenarios(data)]
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("scenario_id values must be unique")
    if data.get("open_questions"):
        for q in data["open_questions"]:
            if q.get("blocking") is True and not q.get("impact"):
                errors.append(f"{q.get('id')}: blocking open question requires impact")
    cfg = load_project_config()
    yes_channels = set(
        (cfg.get("execution") or {}).get("automatable_yes_channels")
        or ["browser", "api_intercept"]
    )
    no_channels = set(
        (cfg.get("execution") or {}).get("automatable_no_channels") or ["native_app", "manual"]
    )
    for scenario in _all_scenarios(data):
        prefix = scenario.get("scenario_id", "scenario")
        channel = scenario.get("execution_channel")
        auto = scenario.get("automatable")
        if not channel:
            errors.append(f"{prefix}: missing execution_channel")
        elif auto == "是" and channel not in yes_channels:
            errors.append(
                f"{prefix}: automatable=是 requires execution_channel in {sorted(yes_channels)}, got {channel}"
            )
        elif channel in no_channels and auto == "是":
            errors.append(f"{prefix}: {channel} must have automatable=否 for web execution stack")
        if channel == "browser" and auto == "是":
            blob_steps = " ".join(scenario.get("steps") or [])
            if not (
                "http://" in blob_steps
                or "https://" in blob_steps
                or "base_url" in blob_steps
                or "{base_url}" in blob_steps
                or "打开" in blob_steps
                or "navigate" in blob_steps.lower()
                or "访问" in blob_steps
            ):
                errors.append(
                    f"{prefix}: browser+automatable=是 steps must open a URL (base_url/https/打开/访问/navigate)"
                )
        if len(scenario.get("steps") or []) > MAX_CASE_STEPS:
            errors.append(f"{prefix}: steps exceed {MAX_CASE_STEPS}")
        blob = " ".join(
            (scenario.get("preconditions") or [])
            + (scenario.get("steps") or [])
            + (scenario.get("expected_results") or [])
        )
        for phrase in VAGUE_CASE_PHRASES:
            if phrase in blob:
                errors.append(f"{prefix}: contains vague/non-executable phrase: {phrase}")
        for pat in FIXED_WAIT_PATTERNS:
            if pat.search(blob):
                errors.append(f"{prefix}: contains fixed wait/sleep")
    cfg = load_project_config()
    write_prd_coverage_matrix(data, cfg)
    errors.extend(validate_required_coverage(data, cfg))
    errors.extend(validate_rework_resolution(data, cfg))
    return errors


def validate_blueprint_markdown(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing {BLUEPRINT_MD}"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for header in ("# 测试蓝图", "需求模块", "测试点", "测试范围", "场景"):
        if header not in text:
            errors.append(f"{BLUEPRINT_MD}: missing readable section {header}")
    if FORBIDDEN_INTERNAL_RE.search(text):
        errors.append(f"{BLUEPRINT_MD}: must not expose old internal trace terms")
    return errors


def validate_test_cases_md(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing: {path}"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    case_headers = re.findall(r"^###\s+(TC-\d{3}):", text, re.MULTILINE)
    if not case_headers:
        errors.append("missing XMind-style case headings (### TC-NNN: title)")
    required_in_each_case = ("是否可自动化", "执行步骤", "预期结果", "执行通道")
    for case_id in case_headers:
        pattern = rf"^###\s+{re.escape(case_id)}:.*?(?=^###\s+TC-|\Z)"
        block = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        if not block:
            errors.append(f"{case_id}: cannot parse case block")
            continue
        chunk = block.group(0)
        for label in required_in_each_case:
            if f"- {label}" not in chunk and f"- {label}：" not in chunk:
                errors.append(f"{case_id}: missing field {label}")
    if FORBIDDEN_INTERNAL_RE.search(text):
        errors.append("02-test-cases.md must not expose old internal trace terms")
    for phrase in VAGUE_CASE_PHRASES:
        if phrase in text:
            errors.append(f"02-test-cases.md contains vague/non-executable phrase: {phrase}")
    for pat in FIXED_WAIT_PATTERNS:
        if pat.search(text):
            errors.append("02-test-cases.md contains fixed wait/sleep")
            break
    return errors


def validate_case_generate_fidelity() -> list[str]:
    bp_path = ARTIFACTS / BLUEPRINT_FILE
    cases_path = ARTIFACTS / "02-test-cases.md"
    if not bp_path.exists() or not cases_path.exists():
        return []
    blueprint = load_json(bp_path)
    expected = len(_all_scenarios(blueprint))
    text = cases_path.read_text(encoding="utf-8")
    actual = len(re.findall(r"^###\s+TC-\d{3}:", text, re.MULTILINE))
    if actual != expected:
        return [f"case count mismatch: blueprint scenarios={expected}, test cases={actual}"]
    return []


def validate_bug_list_md(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing: {path}"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if "# Bug List" not in text:
        errors.append('missing "# Bug List" heading')
    if not re.search(r"^##\s+BUG-\d+", text, re.MULTILINE):
        errors.append("missing bug entries (## BUG-NNN)")
    return errors


def validate_scripts_dir(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing: {path}"]
    files = [f for f in path.iterdir() if f.is_file() and f.name != "manifest.json"]
    return [] if files else ["no script files in 05a-scripts/"]


def _classify_reject_kind(issues: list[dict]) -> str:
    audiences = {(i.get("audience") or "product") for i in issues}
    has_product = "product" in audiences
    has_internal = "internal" in audiences
    if has_product and has_internal:
        return "mixed"
    if has_internal:
        return "internal"
    return "product"


def validate_blocking_open_questions_for_review() -> list[str]:
    """pass 时蓝图不得存在 blocking open_questions（门禁须打回产品）。"""
    bp_path = ARTIFACTS / "00-test-blueprint.json"
    if not bp_path.exists():
        return []
    blueprint = load_json(bp_path)
    blocking = [
        q for q in (blueprint.get("open_questions") or []) if q.get("blocking") is True
    ]
    if not blocking:
        return []
    ids = ", ".join(q.get("id", "?") for q in blocking)
    return [
        f"blueprint has blocking open_questions ({ids}); case-review must reject with product issues, not pass"
    ]


def validate_case_review_report(data: dict) -> list[str]:
    errors: list[str] = []
    verdict = data.get("verdict")
    issues = data.get("issues") or []
    summary = (data.get("summary") or "").strip()
    if verdict == "pass":
        if issues:
            errors.append("verdict=pass requires empty issues[]")
        if data.get("gaps"):
            errors.append("verdict=pass requires empty gaps[]")
        if not summary:
            errors.append("verdict=pass requires non-empty summary")
        errors.extend(validate_blocking_open_questions_for_review())
        return errors
    if verdict != "reject":
        return ["verdict must be pass or reject"]
    if not issues:
        errors.append("verdict=reject requires non-empty issues[]")
    if not summary:
        errors.append("verdict=reject requires non-empty summary")
    rk = data.get("reject_kind") or _classify_reject_kind(issues)
    expected_rk = _classify_reject_kind(issues)
    if rk != expected_rk:
        errors.append(f"reject_kind={rk} inconsistent with issue audiences (expected {expected_rk})")
    for idx, issue in enumerate(issues):
        prefix = f"issues[{idx}]"
        root = issue.get("root_cause")
        audience = issue.get("audience")
        retry = issue.get("retry_target")
        if not (issue.get("description") or "").strip():
            errors.append(f"{prefix}.description is required")
        if not (issue.get("suggestion") or "").strip():
            errors.append(f"{prefix}.suggestion is required")
        if not issue.get("evidence"):
            errors.append(f"{prefix}.evidence is required")
        if root in {"prd", "figma", "assumption_unresolved"}:
            if audience != "product":
                errors.append(f"{prefix}: product root cause must use audience=product")
            if retry != "product":
                errors.append(f"{prefix}: product root cause must use retry_target=product")
        elif root == "qa_undercoverage":
            if audience != "internal" or retry != "prd-analyze":
                errors.append(f"{prefix}: qa_undercoverage must route to prd-analyze/internal")
        elif root == "case_generation":
            if audience != "internal" or retry != "case-generate":
                errors.append(f"{prefix}: case_generation must route to case-generate/internal")
        else:
            errors.append(f"{prefix}.root_cause unknown: {root}")
    return errors


def _case_review_input_paths() -> tuple[Path, Path, Path, Path]:
    import os

    inputs = Path(os.environ.get("QA_INPUTS", str(ROOT / "workspace" / "inputs")))
    return (
        ARTIFACTS / BLUEPRINT_FILE,
        ARTIFACTS / "02-test-cases.md",
        inputs / "figma.url",
        inputs / "prd.md",
    )


def validate_case_review_precheck_stage() -> list[str]:
    bp_path, cases_path, figma_path, prd_path = _case_review_input_paths()
    errors: list[str] = []
    if not bp_path.exists():
        errors.append(f"missing {bp_path}")
    if not cases_path.exists():
        errors.append(f"missing {cases_path}")
    if errors:
        return errors
    cfg = load_project_config()
    blueprint = load_json(bp_path)
    pre = run_case_review_precheck(
        blueprint,
        cases_path.read_text(encoding="utf-8"),
        cfg,
        figma_path=figma_path,
        prd_path=prd_path,
    )
    write_precheck_report(pre)
    write_prd_coverage_matrix(blueprint, cfg)
    return []


def _findings_file_for_perspective(perspective: str) -> Path:
    slug = PERSPECTIVE_SLUGS[perspective]
    return ARTIFACTS / f"case-review-findings-{slug}.json"


def validate_case_review_findings_file(path: Path, perspective: str) -> list[str]:
    if not path.exists():
        return [f"missing {path.name}"]
    data = load_json(path)
    errors = validate_json_schema(data, CONTRACTS / "case-review-findings.schema.json")
    if data.get("perspective") != perspective:
        errors.append(f"{path.name}: perspective must be {perspective}, got {data.get('perspective')}")
    if data.get("brief_ref") != "case-review-perspective-brief.json":
        errors.append(
            f"{path.name}: brief_ref must be case-review-perspective-brief.json, got {data.get('brief_ref')}"
        )
    issues = data.get("issues") or []
    if data.get("finding_count") != len(issues):
        errors.append(f"{path.name}: finding_count {data.get('finding_count')} != issues.length {len(issues)}")
    expected_verdict = "fail" if issues else "pass"
    if data.get("verdict") != expected_verdict:
        errors.append(f"{path.name}: verdict must be {expected_verdict} from issues.length")
    return errors


def _normalize_ref(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def _doc_tokens(path: str) -> set[str]:
    p = Path(str(path))
    return {
        _normalize_ref(str(path)),
        _normalize_ref(p.name),
        _normalize_ref(p.stem),
    }


def _knowledge_ref_allowed(ref: str, docs_read: list[str]) -> bool:
    if not ref:
        return True
    if SOURCE_ALLOW_RE.search(ref):
        return True
    ref_norm = _normalize_ref(ref)
    if "no relevant history" in ref_norm or "无同类历史" in ref_norm:
        return True
    for doc in docs_read:
        for token in _doc_tokens(doc):
            if token and (token in ref_norm or ref_norm in token):
                return True
    return False


def validate_perspective_knowledge_and_role(data: dict, perspective: str, brief: dict) -> list[str]:
    errors: list[str] = []
    if perspective == "structural":
        return errors
    docs_read = [str(d) for d in data.get("knowledge_docs_read") or []]
    recommended = (brief.get("knowledge_reading_list") or {}).get(perspective) or []
    if recommended and not docs_read:
        errors.append(f"{perspective}: knowledge_docs_read must include at least one actual read doc")

    notes = data.get("perspective_notes") or []
    role_blob = " ".join(
        str(note.get("rationale") or "") + " " + str(note.get("knowledge_ref") or "")
        for note in notes
    )
    if not any(kw.lower() in role_blob.lower() for kw in ROLE_KEYWORDS[perspective]):
        errors.append(f"{perspective}: perspective_notes do not demonstrate this role's review focus")

    for idx, note in enumerate(notes):
        ref = str(note.get("knowledge_ref") or "")
        if ref and not _knowledge_ref_allowed(ref, docs_read):
            errors.append(f"{perspective}.perspective_notes[{idx}].knowledge_ref not backed by docs_read: {ref}")

    issues_text = re.sub(r"\s+", "", json.dumps(data.get("issues") or [], ensure_ascii=False))
    for idx, extra in enumerate(data.get("extra_notes") or []):
        ref = str(extra.get("knowledge_ref") or "")
        if ref and not _knowledge_ref_allowed(ref, docs_read):
            errors.append(f"{perspective}.extra_notes[{idx}].knowledge_ref not backed by docs_read: {ref}")
        blob = " ".join(str(extra.get(k) or "") for k in ("note", "rationale", "knowledge_ref"))
        if HISTORY_CLAIM_RE.search(blob) and not ref:
            errors.append(f"{perspective}.extra_notes[{idx}] cites history/practice/knowledge but lacks knowledge_ref")
        if RISK_NOTE_RE.search(blob) and EXPLICIT_SOURCE_RE.search(blob):
            compact = re.sub(r"\s+", "", blob)
            tokens = [t for t in re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}", compact) if len(t) >= 3]
            has_issue_evidence = any(t in issues_text for t in tokens[:8])
            if not has_issue_evidence:
                errors.append(
                    f"{perspective}.extra_notes[{idx}] describes an explicit uncovered/risk item; "
                    "write a routed issue instead of only an extra_note"
                )

    if perspective == "red_team":
        red_blob = " ".join(
            docs_read
            + [
                str(note.get("rationale") or "") + " " + str(note.get("knowledge_ref") or "")
                for note in notes
            ]
        )
        if not re.search(r"(历史|测试用例|规则|回归|homepage|knowledge|no relevant history|无同类历史)", red_blob, re.I):
            errors.append("red_team: must cite historical knowledge/rules or explicitly declare no relevant history")
    if data.get("issues"):
        failing_notes = [
            note for note in notes if note.get("verdict") in {"fail", "blocked"}
        ]
        if not failing_notes:
            errors.append(f"{perspective}: findings has issues but no perspective_note verdict is fail/blocked")
    return errors


def _read_trace_events() -> tuple[list[dict], list[str]]:
    path = ARTIFACTS / TRACE_FILE
    if not path.exists():
        return [], [f"missing {TRACE_FILE}; case-review requires auditable perspective Task trace"]
    events: list[dict] = []
    errors: list[str] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{TRACE_FILE}:{lineno}: invalid JSON: {exc}")
            continue
        if not event.get("event"):
            errors.append(f"{TRACE_FILE}:{lineno}: missing event")
        if not event.get("at"):
            errors.append(f"{TRACE_FILE}:{lineno}: missing at")
        events.append(event)
    return events, errors


def _current_case_review_round_id() -> str | None:
    meta_path = ARTIFACTS / "00-meta.json"
    if not meta_path.exists():
        return None
    try:
        meta = load_json(meta_path)
    except Exception:
        return None
    return (meta.get("review") or {}).get("case_review_round_id")


def validate_case_review_trace(brief: dict) -> list[str]:
    events, errors = _read_trace_events()
    if errors:
        return errors
    round_id = _current_case_review_round_id()
    if round_id:
        events = [e for e in events if e.get("round_id") == round_id]
        if not events:
            return [f"{TRACE_FILE}: missing events for current round_id={round_id}"]
    by_event: dict[str, list[dict]] = {}
    for event in events:
        by_event.setdefault(str(event.get("event")), []).append(event)
    for event_name in TRACE_REQUIRED_GLOBAL_EVENTS:
        if event_name == "final_validate_passed" and os.environ.get("QA_SKIP_FINAL_VALIDATE_TRACE") == "1":
            continue
        if not by_event.get(event_name):
            errors.append(f"{TRACE_FILE}: missing global event {event_name}")

    expected_question_counts = {
        p: len(((brief.get("perspectives") or {}).get(p) or {}).get("questions") or [])
        for p in PERSPECTIVES
    }
    for perspective in PERSPECTIVES:
        starts = [
            e
            for e in by_event.get("perspective_task_started", [])
            if e.get("perspective") == perspective
        ]
        terminals = [
            e
            for name in TRACE_TERMINAL_PERSPECTIVE_EVENTS
            for e in by_event.get(name, [])
            if e.get("perspective") == perspective
        ]
        if len(terminals) < len(starts):
            errors.append(
                f"{TRACE_FILE}: {perspective} has {len(starts)} started event(s) but only "
                f"{len(terminals)} terminal event(s); record failed/cancelled retries"
            )
        latest_started = starts[-1] if starts else {}
        for event_name in TRACE_REQUIRED_PERSPECTIVE_EVENTS:
            matches = [
                e
                for e in by_event.get(event_name, [])
                if e.get("perspective") == perspective
            ]
            if not matches:
                errors.append(f"{TRACE_FILE}: missing {event_name} for {perspective}")
                continue
            latest = matches[-1]
            prompt = latest.get("prompt_path")
            findings = latest.get("findings_path")
            expected_prompt = f"prompts/case-review-{PERSPECTIVE_SLUGS[perspective]}.md"
            expected_findings = f"case-review-findings-{PERSPECTIVE_SLUGS[perspective]}.json"
            if not prompt or expected_prompt not in str(prompt):
                errors.append(f"{TRACE_FILE}: {event_name} for {perspective} has wrong prompt_path")
            if not findings or expected_findings not in str(findings):
                errors.append(f"{TRACE_FILE}: {event_name} for {perspective} has wrong findings_path")
            if latest_started and event_name in {"perspective_task_completed", "perspective_validate_passed"}:
                if latest.get("launch_id") != latest_started.get("launch_id"):
                    errors.append(
                        f"{TRACE_FILE}: {event_name} for {perspective} launch_id does not match latest started event"
                    )
            if event_name == "perspective_task_started":
                if latest.get("stage_name") != f"case-review-{PERSPECTIVE_SLUGS[perspective]}":
                    errors.append(
                        f"{TRACE_FILE}: perspective_task_started for {perspective} must include "
                        f"stage_name=case-review-{PERSPECTIVE_SLUGS[perspective]}"
                    )
                if not latest.get("launch_id"):
                    errors.append(f"{TRACE_FILE}: perspective_task_started for {perspective} needs launch_id")
                launch_lock = latest.get("launch_lock_path")
                if not launch_lock:
                    errors.append(f"{TRACE_FILE}: perspective_task_started for {perspective} needs launch_lock_path")
                else:
                    lock_path = ROOT / str(launch_lock) if not Path(str(launch_lock)).is_absolute() else Path(str(launch_lock))
                    if not lock_path.exists():
                        errors.append(
                            f"{TRACE_FILE}: started launch_lock_path for {perspective} does not exist: {launch_lock}"
                        )
                    else:
                        try:
                            lock_data = load_json(lock_path)
                        except Exception as exc:
                            errors.append(f"{TRACE_FILE}: started launch lock for {perspective} is invalid JSON: {exc}")
                        else:
                            if lock_data.get("launcher") != "pipeline_runner":
                                errors.append(
                                    f"{TRACE_FILE}: started launch lock for {perspective} must be written by pipeline_runner"
                                )
                            if lock_data.get("launch_id") != latest.get("launch_id"):
                                errors.append(f"{TRACE_FILE}: started launch_id mismatch for {perspective}")
                            if round_id and lock_data.get("round_id") != round_id:
                                errors.append(f"{TRACE_FILE}: started launch lock round_id mismatch for {perspective}")
                            findings_path_actual = _findings_file_for_perspective(perspective)
                            try:
                                elapsed = findings_path_actual.stat().st_mtime - lock_path.stat().st_mtime
                                if elapsed < MIN_PERSPECTIVE_SECONDS:
                                    errors.append(
                                        f"{TRACE_FILE}: {perspective} findings produced {elapsed:.3f}s after launch; "
                                        f"independent perspective stage must take at least {MIN_PERSPECTIVE_SECONDS:.0f}s"
                                    )
                            except OSError as exc:
                                errors.append(f"{TRACE_FILE}: could not compare launch/findings time for {perspective}: {exc}")
            if event_name == "perspective_task_completed":
                if latest.get("stage_name") != f"case-review-{PERSPECTIVE_SLUGS[perspective]}":
                    errors.append(
                        f"{TRACE_FILE}: perspective_task_completed for {perspective} must include "
                        f"stage_name=case-review-{PERSPECTIVE_SLUGS[perspective]}"
                    )
                if not latest.get("launch_id"):
                    errors.append(
                        f"{TRACE_FILE}: perspective_task_completed for {perspective} needs launch_id "
                        "from the independent Hook/runner launch lock"
                    )
                launch_lock = latest.get("launch_lock_path")
                if not launch_lock:
                    errors.append(
                        f"{TRACE_FILE}: perspective_task_completed for {perspective} needs launch_lock_path"
                    )
                else:
                    lock_path = ROOT / str(launch_lock) if not Path(str(launch_lock)).is_absolute() else Path(str(launch_lock))
                    if not lock_path.exists():
                        errors.append(
                            f"{TRACE_FILE}: launch_lock_path for {perspective} does not exist: {launch_lock}"
                        )
                    else:
                        try:
                            lock_data = load_json(lock_path)
                        except Exception as exc:
                            errors.append(f"{TRACE_FILE}: launch lock for {perspective} is invalid JSON: {exc}")
                        else:
                            if lock_data.get("launcher") != "pipeline_runner":
                                errors.append(
                                    f"{TRACE_FILE}: launch lock for {perspective} must be written by pipeline_runner"
                                )
                            if lock_data.get("stage_name") != f"case-review-{PERSPECTIVE_SLUGS[perspective]}":
                                errors.append(
                                    f"{TRACE_FILE}: launch lock stage mismatch for {perspective}: "
                                    f"{lock_data.get('stage_name')}"
                                )
                            if lock_data.get("launch_id") != latest.get("launch_id"):
                                errors.append(f"{TRACE_FILE}: launch_id mismatch for {perspective}")
                            if round_id and lock_data.get("round_id") != round_id:
                                errors.append(f"{TRACE_FILE}: launch lock round_id mismatch for {perspective}")
                if not latest.get("agent_id") and not latest.get("agent_id_unavailable_reason"):
                    errors.append(
                        f"{TRACE_FILE}: perspective_task_completed for {perspective} needs agent_id "
                        "or agent_id_unavailable_reason"
                    )
                if not latest.get("summary"):
                    errors.append(f"{TRACE_FILE}: perspective_task_completed for {perspective} needs summary")
            if event_name == "perspective_validate_passed":
                if latest.get("stage_name") != f"case-review-{PERSPECTIVE_SLUGS[perspective]}":
                    errors.append(
                        f"{TRACE_FILE}: perspective_validate_passed for {perspective} must include "
                        f"stage_name=case-review-{PERSPECTIVE_SLUGS[perspective]}"
                    )
                if not latest.get("launch_id"):
                    errors.append(f"{TRACE_FILE}: perspective_validate_passed for {perspective} needs launch_id")
                if latest.get("validate_result") != "pass":
                    errors.append(f"{TRACE_FILE}: validate result for {perspective} must be pass")
                if "--stage case-review-perspective" not in str(latest.get("validate_command") or ""):
                    errors.append(f"{TRACE_FILE}: validate command missing perspective stage for {perspective}")

        findings = load_json(_findings_file_for_perspective(perspective))
        if len(findings.get("perspective_notes") or []) < expected_question_counts[perspective]:
            errors.append(f"{perspective}: findings do not cover all brief questions")
    return errors


def validate_case_review_perspective_stage(perspective: str | None) -> list[str]:
    if not perspective:
        return ["--perspective is required for case-review-perspective"]
    if perspective not in PERSPECTIVE_SLUGS:
        return [f"unknown perspective: {perspective}"]
    normalized = "red_team" if perspective == "red-team" else perspective
    errors: list[str] = []
    brief_path = ARTIFACTS / "case-review-perspective-brief.json"
    if not brief_path.exists():
        errors.append("missing case-review-perspective-brief.json")
        return errors
    brief = load_json(brief_path)
    errors.extend(validate_json_schema(brief, CONTRACTS / "case-review-perspective-brief.schema.json"))
    path = _findings_file_for_perspective(normalized)
    errors.extend(validate_case_review_findings_file(path, normalized))
    if errors:
        return errors
    data = load_json(path)
    section = (brief.get("perspectives") or {}).get(normalized) or {}
    required = {q.get("id") for q in section.get("questions") or [] if q.get("id")}
    got = {n.get("question_id") for n in data.get("perspective_notes") or []}
    missing = sorted(required - got)
    if missing:
        errors.append(f"{path.name}: missing perspective_notes for {', '.join(missing)}")
    docs = (brief.get("knowledge_reading_list") or {}).get(normalized) or []
    if docs and not data.get("knowledge_docs_read"):
        errors.append(f"{path.name}: knowledge_docs_read must record docs read or explicit no-history note")
    errors.extend(validate_perspective_knowledge_and_role(data, normalized, brief))
    return errors


def validate_case_review_final_files(report: dict) -> list[str]:
    errors: list[str] = []
    round_id = _current_case_review_round_id()
    brief_path = ARTIFACTS / "case-review-perspective-brief.json"
    if not brief_path.exists():
        errors.append("missing case-review-perspective-brief.json")
    else:
        brief = load_json(brief_path)
        errors.extend(validate_json_schema(brief, CONTRACTS / "case-review-perspective-brief.schema.json"))
    structural_path = ARTIFACTS / "case-review-findings-structural.json"
    errors.extend(validate_case_review_findings_file(structural_path, "structural"))
    for p in PERSPECTIVES:
        errors.extend(validate_case_review_findings_file(_findings_file_for_perspective(p), p))
        marker = ARTIFACTS / f".stage-done-case-review-{PERSPECTIVE_SLUGS[p]}.json"
        if not marker.exists():
            errors.append(f"missing stage done marker for case-review-{PERSPECTIVE_SLUGS[p]}")
        else:
            try:
                marker_data = load_json(marker)
            except Exception as exc:
                errors.append(f"{marker.name}: invalid JSON: {exc}")
            else:
                if marker_data.get("status") != "done":
                    errors.append(f"{marker.name}: status must be done")
                if round_id and marker_data.get("round_id") != round_id:
                    errors.append(f"{marker.name}: round_id mismatch")
    merge_marker = ARTIFACTS / ".stage-done-case-review-merge.json"
    if not merge_marker.exists():
        errors.append("missing stage done marker for case-review-merge")
    else:
        try:
            merge_data = load_json(merge_marker)
        except Exception as exc:
            errors.append(f"{merge_marker.name}: invalid JSON: {exc}")
        else:
            if merge_data.get("status") != "done":
                errors.append(f"{merge_marker.name}: status must be done")
            if round_id and merge_data.get("round_id") != round_id:
                errors.append(f"{merge_marker.name}: round_id mismatch")
    if errors:
        return errors
    brief = load_json(brief_path)
    structural = load_json(structural_path)
    finding_count_raw = len(structural.get("issues") or [])
    for p in PERSPECTIVES:
        finding_count_raw += len(load_json(_findings_file_for_perspective(p)).get("issues") or [])
    if report.get("finding_count_raw") != finding_count_raw:
        errors.append(f"finding_count_raw {report.get('finding_count_raw')} != five findings total {finding_count_raw}")
    if report.get("finding_count_merged") != len(report.get("issues") or []):
        errors.append("finding_count_merged must equal final issues.length")
    has_product = any((i.get("audience") or "product") == "product" for i in report.get("issues") or [])
    if report.get("verdict") == "reject" and has_product:
        if not (ARTIFACTS / "prd-reject-to-product.md").exists():
            errors.append("product reject requires prd-reject-to-product.md")
        if not (ARTIFACTS / "PRD-REJECTED.md").exists():
            errors.append("product reject requires PRD-REJECTED.md compatibility marker")
    tri = report.get("tri_party") or {}
    for p in PERSPECTIVES:
        src = load_json(_findings_file_for_perspective(p))
        row = tri.get(p) or {}
        if row.get("finding_count") != len(src.get("issues") or []):
            errors.append(f"tri_party.{p}.finding_count inconsistent with findings")
        if row.get("verdict") != src.get("verdict"):
            errors.append(f"tri_party.{p}.verdict inconsistent with findings")
        errors.extend(validate_perspective_knowledge_and_role(src, p, brief))
    structural_row = report.get("structural") or {}
    if structural_row.get("finding_count") != len(structural.get("issues") or []):
        errors.append("structural.finding_count inconsistent with findings")
    if report.get("verdict") == "pass" and finding_count_raw != 0:
        errors.append("verdict=pass requires finding_count_raw == 0")
    if report.get("verdict") == "reject" and finding_count_raw <= 0:
        errors.append("verdict=reject requires finding_count_raw > 0")
    errors.extend(validate_case_review_trace(brief))
    return errors


def validate_stage(stage: str, perspective: str | None = None) -> bool:
    ok = True
    if stage == "case-generate":
        errs = validate_test_cases_md(ARTIFACTS / "02-test-cases.md")
        errs.extend(validate_case_generate_fidelity())
    elif stage == "case-review-precheck":
        errs = validate_case_review_precheck_stage()
    elif stage == "case-review-perspective":
        errs = validate_case_review_perspective_stage(perspective)
    elif stage == "bug-list-write":
        errs = validate_bug_list_md(ARTIFACTS / "05b-bug-list.md")
    elif stage == "script-convert":
        errs = validate_scripts_dir(ARTIFACTS / "05a-scripts")
    elif stage in STAGE_FILES:
        fname, schema_name = STAGE_FILES[stage]
        fpath = ARTIFACTS / fname
        if not fpath.exists():
            print(f"FAIL {stage}: missing {fpath}")
            return False
        data = load_json(fpath)
        errs = validate_json_schema(data, CONTRACTS / schema_name)
        if stage in {"test-blueprint", "prd-analyze"} and not errs:
            errs.extend(validate_blueprint_data(data))
            errs.extend(validate_blueprint_markdown(ARTIFACTS / BLUEPRINT_MD))
        if stage == "prd-analyze" and not errs:
            errs.extend(validate_knowledge_context(ARTIFACTS / KNOWLEDGE_CONTEXT_FILE))
            if not errs:
                write_analyze_complete_marker()
        if stage == "case-review" and not errs:
            errs.extend(validate_case_review_report(data))
            errs.extend(validate_case_review_final_files(data))
            errs.extend(validate_review_against_precheck(data))
            if data.get("verdict") == "reject":
                blocking = validate_blocking_open_questions_for_review()
                if blocking and not (data.get("issues") or []):
                    errs.append(
                        "verdict=reject but issues[] empty while blueprint has blocking open_questions"
                    )
            threshold = 0.85
            meta_path = ARTIFACTS / "00-meta.json"
            if meta_path.exists():
                meta = load_json(meta_path)
                threshold = meta.get("review", {}).get("pass_threshold", threshold)
            if data.get("verdict") == "pass" and data.get("coverage_score", 0) < threshold:
                errs.append(f"coverage_score {data.get('coverage_score')} < threshold {threshold}")
        if stage == "test-execute" and not errs:
            summary = data.get("summary", {})
            cases = data.get("cases", [])
            total = summary.get("total", 0)
            if total != len(cases):
                errs.append(f"summary.total ({total}) != len(cases) ({len(cases)})")
            derived_has_pass = any(c.get("status") == "pass" for c in cases)
            derived_has_fail = any(c.get("status") in ("fail", "block") for c in cases)
            if "has_pass" in data and data.get("has_pass") != derived_has_pass:
                errs.append(f"has_pass ({data.get('has_pass')}) inconsistent with cases ({derived_has_pass})")
            if "has_fail" in data and data.get("has_fail") != derived_has_fail:
                errs.append(f"has_fail ({data.get('has_fail')}) inconsistent with cases ({derived_has_fail})")
            if data.get("has_fail", derived_has_fail):
                errs.extend(validate_bug_list_md(ARTIFACTS / "05b-bug-list.md"))
    else:
        print(f"Unknown stage: {stage}")
        return False

    if errs:
        if stage == "prd-analyze":
            (ARTIFACTS / ".prd-analyze-complete.ok").unlink(missing_ok=True)
        print(f"FAIL {stage}:")
        for err in errs:
            print(f"  - {err}")
        ok = False
    else:
        print(f"OK {stage}")
    return ok


def init_meta() -> dict:
    return {
        "version": "1.0",
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "current_stage": None,
        "status": "running",
        "review": {"pass_threshold": 0.85, "retry_count": 0},
        "stages": {},
        "post_process": {},
    }


def _stage_result_for_mark_done(stage: str, extra: dict | None = None) -> dict:
    payload = {"stage": stage, "stage_result": "STAGE_DONE"}
    if stage == "case-review":
        report_path = ARTIFACTS / "03-review-report.json"
        report = load_json(report_path) if report_path.exists() else {}
        verdict = report.get("verdict")
        issues = report.get("issues") or []
        product = [i for i in issues if (i.get("audience") or "product") == "product"]
        internal = [
            i
            for i in issues
            if (i.get("audience") or "") == "internal"
            or i.get("root_cause") in {"qa_undercoverage", "case_generation"}
            or i.get("retry_target") in {"prd-analyze", "case-generate"}
        ]
        if verdict == "pass":
            payload.update(
                {
                    "stage_result": "STAGE_DONE",
                    "has_product_issues": False,
                    "has_internal_issues": False,
                }
            )
        elif product:
            payload.update(
                {
                    "stage_result": "PRODUCT_REJECT",
                    "has_product_issues": True,
                    "has_internal_issues": bool(internal),
                    "product_issue_count": len(product),
                    "internal_issue_count": len(internal),
                }
            )
        elif internal:
            payload.update(
                {
                    "stage_result": "INTERNAL_REWORK",
                    "has_product_issues": False,
                    "has_internal_issues": True,
                    "internal_issue_count": len(internal),
                }
            )
        else:
            payload.update({"stage_result": "PIPELINE_BLOCKED"})
    payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    if extra:
        payload.update(extra)
    return payload


def update_meta_stage(stage: str, status: str, extra: dict | None = None) -> None:
    meta_path = ARTIFACTS / "00-meta.json"
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    if meta_path.exists():
        meta = load_json(meta_path)
    else:
        meta = init_meta()
    meta["current_stage"] = stage
    meta["status"] = status
    stage_result_payload = _stage_result_for_mark_done(stage, extra) if status == "done" else {}
    meta.update(stage_result_payload)
    if stage == "case-review" and status == "done":
        result = stage_result_payload.get("stage_result")
        if result == "PRODUCT_REJECT":
            meta.setdefault("orchestrator", {})["last_decision"] = "product_reject"
        elif result == "INTERNAL_REWORK":
            meta.setdefault("orchestrator", {})["last_decision"] = "internal_retry"
        elif result == "STAGE_DONE":
            meta.setdefault("orchestrator", {})["last_decision"] = "continue"
    meta.setdefault("stages", {})[stage] = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        **stage_result_payload,
        **(extra or {}),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    if stage == "case-review" and status == "done":
        active = ARTIFACTS / ".qa-pipeline-active"
        result = stage_result_payload.get("stage_result")
        if result in {"PRODUCT_REJECT", "PIPELINE_BLOCKED", "STAGE_DONE"}:
            active.unlink(missing_ok=True)


def maybe_resolve_case_review_gate(stage: str) -> None:
    if stage != "case-review":
        return
    report_path = ARTIFACTS / "03-review-report.json"
    if not report_path.exists():
        return
    report = load_json(report_path)
    verdict = report.get("verdict")
    issues = report.get("issues") or []
    internal = [
        i
        for i in issues
        if (i.get("audience") or "") == "internal"
        or i.get("root_cause") in {"qa_undercoverage", "case_generation"}
        or i.get("retry_target") in {"prd-analyze", "case-generate"}
    ]
    if verdict != "reject":
        return
    try:
        import pipeline_runner

        pipeline_runner.ARTIFACTS = ARTIFACTS
        pipeline_runner.PROMPTS_DIR = ARTIFACTS / "prompts"
        pipeline_runner.INPUTS = Path(os.environ.get("QA_INPUTS", str(ROOT / "workspace" / "inputs")))
        pipeline = pipeline_runner.load_pipeline()
        meta = pipeline_runner.load_meta()
        gate = pipeline_runner.resolve_case_review_gate(pipeline, meta)
        print(f"case-review gate: {gate}")
    except Exception as exc:
        print(f"warn: case-review gate resolution skipped: {exc}", file=sys.stderr)


def write_analyze_complete_marker() -> None:
    marker = ARTIFACTS / ".prd-analyze-complete.ok"
    blueprint = load_json(ARTIFACTS / BLUEPRINT_FILE)
    marker.write_text(
        json.dumps(
            {
                "ok": True,
                "blueprint": str(ARTIFACTS / BLUEPRINT_FILE),
                "modules": len(blueprint.get("modules") or []),
                "scenarios": len(_all_scenarios(blueprint)),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--init-meta", action="store_true")
    parser.add_argument("--mark-done")
    parser.add_argument("--extra")
    parser.add_argument("--perspective", choices=["product", "qa", "testability", "red_team", "red-team"])
    args = parser.parse_args()

    if args.init_meta:
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        (ARTIFACTS / "00-meta.json").write_text(
            json.dumps(init_meta(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(ARTIFACTS / "00-meta.json")
        return 0

    if args.mark_done:
        extra = json.loads(args.extra) if args.extra else None
        update_meta_stage(args.mark_done, "done", extra)
        maybe_resolve_case_review_gate(args.mark_done)
        print(f"marked done: {args.mark_done}")
        return 0

    if args.all:
        checks = []
        if (ARTIFACTS / BLUEPRINT_FILE).exists():
            checks.append("prd-analyze")
        checks.extend(["case-generate", "case-review", "test-execute", "script-convert"])
        ok = True
        for stage in checks:
            if stage in {"case-generate", "case-review", "test-execute", "script-convert"}:
                target = {
                    "case-generate": "02-test-cases.md",
                    "case-review": "03-review-report.json",
                    "test-execute": "04-execution-result.json",
                    "script-convert": "05a-scripts",
                }[stage]
                if not (ARTIFACTS / target).exists():
                    continue
            ok = validate_stage(stage) and ok
        return 0 if ok else 1

    if not args.stage:
        print("Provide --stage or --all", file=sys.stderr)
        return 2
    return 0 if validate_stage(args.stage, args.perspective) else 1


if __name__ == "__main__":
    raise SystemExit(main())
