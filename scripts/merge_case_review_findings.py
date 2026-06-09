#!/usr/bin/env python3
"""Merge structural + four perspective case-review findings into final report."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "contracts"
PERSPECTIVES = ("product", "qa", "testability", "red_team")
PERSPECTIVE_SLUGS = {
    "structural": "structural",
    "product": "product",
    "qa": "qa",
    "testability": "testability",
    "red_team": "red-team",
    "red-team": "red-team",
}
ROUTE = {
    "prd": ("product", "product"),
    "figma": ("product", "product"),
    "assumption_unresolved": ("product", "product"),
    "qa_undercoverage": ("internal", "prd-analyze"),
    "case_generation": ("internal", "case-generate"),
}


def artifacts_dir() -> Path:
    if os.environ.get("QA_WORKSPACE"):
        return Path(os.environ["QA_WORKSPACE"])
    return ROOT / "workspace" / "artifacts"


ARTIFACTS = artifacts_dir()


try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def findings_path(perspective: str) -> Path:
    slug = PERSPECTIVE_SLUGS[perspective]
    return ARTIFACTS / f"case-review-findings-{slug}.json"


def validate_schema(data: dict, schema_name: str) -> list[str]:
    if not HAS_JSONSCHEMA:
        return ["jsonschema not installed; run: pip install -r requirements.txt"]
    schema = load_json(CONTRACTS / schema_name)
    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"{'.'.join(str(p) for p in err.path) or '(root)'}: {err.message}"
        for err in sorted(validator.iter_errors(data), key=lambda e: e.path)
    ]


def required_question_ids(brief: dict, perspective: str) -> set[str]:
    section = (brief.get("perspectives") or {}).get(perspective) or {}
    return {str(q.get("id")) for q in section.get("questions") or [] if q.get("id")}


def validate_findings(data: dict, perspective: str, brief: dict) -> list[str]:
    errors = validate_schema(data, "case-review-findings.schema.json")
    expected_perspective = perspective
    if data.get("perspective") != expected_perspective:
        errors.append(f"perspective must be {expected_perspective}, got {data.get('perspective')}")
    issues = data.get("issues") or []
    if data.get("finding_count") != len(issues):
        errors.append(f"finding_count {data.get('finding_count')} != issues.length {len(issues)}")
    expected_verdict = "fail" if issues else "pass"
    if data.get("verdict") != expected_verdict:
        errors.append(f"verdict must be {expected_verdict} from issues.length")
    if perspective != "structural":
        got = {str(n.get("question_id")) for n in data.get("perspective_notes") or []}
        missing = sorted(required_question_ids(brief, perspective) - got)
        if missing:
            errors.append(f"missing perspective_notes for question_id(s): {', '.join(missing)}")
        if not data.get("knowledge_docs_read") and (brief.get("knowledge_reading_list") or {}).get(perspective):
            errors.append("knowledge_docs_read must record at least one read doc or explicit no-history note")
    for idx, issue in enumerate(issues):
        root = issue.get("root_cause")
        if root not in ROUTE:
            errors.append(f"issues[{idx}].root_cause unknown: {root}")
            continue
        audience, retry = ROUTE[root]
        if issue.get("audience") != audience:
            errors.append(f"issues[{idx}]: root_cause={root} requires audience={audience}")
        if issue.get("retry_target") != retry:
            errors.append(f"issues[{idx}]: root_cause={root} requires retry_target={retry}")
    return errors


def normalize(text: Any) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip().lower()
    return re.sub(r"[^\w\u4e00-\u9fff]+", " ", text)


def token_set(text: Any) -> set[str]:
    return {t for t in normalize(text).split() if len(t) >= 2}


def evidence_key(issue: dict) -> tuple:
    ev = issue.get("evidence") or {}
    return (
        normalize(ev.get("blueprint_ref")),
        normalize(ev.get("case_ref")),
        tuple(issue.get("scenario_ids") or []),
    )


def dedupe_key(issue: dict) -> tuple:
    return (
        normalize(issue.get("description"))[:180],
        issue.get("root_cause"),
        issue.get("retry_target"),
        evidence_key(issue),
    )


def semantic_family_key(issue: dict) -> tuple | None:
    raw_blob = " ".join(
        [
            str(issue.get("category") or ""),
            str(issue.get("description") or ""),
            str(issue.get("suggestion") or ""),
            json.dumps(issue.get("evidence") or {}, ensure_ascii=False),
        ]
    ).lower()
    blob = normalize(raw_blob)
    root = issue.get("root_cause")
    retry = issue.get("retry_target")
    audience = issue.get("audience")
    amount_positive = bool(
        re.search(r"amount\s*(?:>|大于)\s*0", raw_blob)
        or re.search(r"amount\s*[=:：]\s*[1-9]", raw_blob)
        or "amount 0" in blob and any(word in blob for word in ("原价格", "展示金额", "无后缀"))
    )
    if ("未知 type" in blob or "unknown" in blob) and "amount" in blob and amount_positive:
        return (root, audience, retry, "unknown-type-amount-positive-fallback")
    if "price" in blob and ("null" in blob or "缺失" in blob or "缺省" in blob):
        return (root, audience, retry, "price-null-or-missing-fallback")
    return None


def should_merge_issue(existing: dict, candidate: dict) -> bool:
    if dedupe_key(existing) == dedupe_key(candidate):
        return True
    family_existing = semantic_family_key(existing)
    if family_existing and family_existing == semantic_family_key(candidate):
        return True
    if (
        existing.get("root_cause") == candidate.get("root_cause")
        and existing.get("retry_target") == candidate.get("retry_target")
        and existing.get("audience") == candidate.get("audience")
    ):
        ev_existing = evidence_key(existing)
        ev_candidate = evidence_key(candidate)
        if ev_existing != ("", "", ()) and ev_existing == ev_candidate:
            return True
        a = token_set(existing.get("description"))
        b = token_set(candidate.get("description"))
        if a and b and len(a & b) / min(len(a), len(b)) >= 0.72:
            return True
    return False


def classify_reject_kind(issues: list[dict]) -> str:
    audiences = {(i.get("audience") or "product") for i in issues}
    if "product" in audiences and "internal" in audiences:
        return "mixed"
    if "internal" in audiences:
        return "internal"
    return "product"


def issue_sort_key(issue: dict) -> tuple:
    severity = {"blocker": 0, "major": 1, "minor": 2}.get(issue.get("severity"), 9)
    source = {"structural": 0, "product": 1, "qa": 2, "red_team": 3, "testability": 4}.get(
        issue.get("_source_perspective"), 9
    )
    return severity, source, issue.get("id", "")


def renumber_issues(issues: list[dict]) -> list[dict]:
    out = []
    seq = 1
    for issue in sorted(issues, key=issue_sort_key):
        cleaned = {k: v for k, v in issue.items() if k != "_source_perspective"}
        old_id = str(cleaned.get("id") or "")
        if not old_id.startswith("GATE-"):
            cleaned["id"] = f"CR-{seq:03d}"
            seq += 1
        out.append(cleaned)
    return out


def merge_issues(findings_by_perspective: dict[str, dict]) -> tuple[list[dict], int, int]:
    raw: list[dict] = []
    for perspective in ("structural", "product", "qa", "red_team", "testability"):
        for issue in findings_by_perspective[perspective].get("issues") or []:
            raw.append({**issue, "_source_perspective": perspective})
    merged: list[dict] = []
    for issue in raw:
        existing = next((m for m in merged if should_merge_issue(m, issue)), None)
        if existing is not None:
            srcs = existing.setdefault("merged_from_perspectives", [])
            for src in (existing.get("_source_perspective"), issue.get("_source_perspective")):
                if src and src not in srcs:
                    srcs.append(src)
            aliases = existing.setdefault("merged_issue_ids", [])
            for issue_id in (existing.get("id"), issue.get("id")):
                if issue_id and issue_id not in aliases:
                    aliases.append(issue_id)
            if issue.get("severity") == "major" and existing.get("severity") == "minor":
                existing["severity"] = "major"
            continue
        issue.setdefault("merged_from_perspectives", [issue.get("_source_perspective")] if issue.get("_source_perspective") else [])
        issue.setdefault("merged_issue_ids", [issue.get("id")] if issue.get("id") else [])
        merged.append(issue)
    return renumber_issues(merged), len(raw), len(merged)


def write_confirmation(raw_count: int, merged_count: int) -> None:
    path = ARTIFACTS / "case-review-merge-needs-confirmation.md"
    path.write_text(
        "\n".join(
            [
                "# Case Review Merge Needs Confirmation",
                "",
                f"- raw findings: {raw_count}",
                f"- merged findings: {merged_count}",
                f"- deduped findings: {raw_count - merged_count}",
                "",
                "去重数量超过阈值。请 case-reviewer 逐条确认是否误合并不同问题，修正 findings 后再运行 merge。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def coverage_matrix_stub(issues: list[dict]) -> dict:
    has_coverage = any(i.get("root_cause") == "qa_undercoverage" for i in issues)
    has_acceptance = any(i.get("audience") == "product" for i in issues)
    return {
        "functional": 0.85 if has_coverage else 1.0,
        "boundary": 0.8 if has_coverage else 1.0,
        "exception": 0.8 if has_coverage else 1.0,
        "security": 1.0,
        "compatibility": 0.9 if has_acceptance else 1.0,
    }


def build_report(brief: dict, findings: dict[str, dict]) -> dict:
    issues, raw_count, merged_count = merge_issues(findings)
    dedupe_count = raw_count - merged_count
    if raw_count and (dedupe_count >= 3 or dedupe_count / raw_count >= 0.30):
        write_confirmation(raw_count, merged_count)
        raise RuntimeError(
            f"dedupe threshold exceeded: raw={raw_count}, merged={merged_count}, deduped={dedupe_count}"
        )
    tri_party = {
        p: {
            "verdict": findings[p].get("verdict", "pass"),
            "finding_count": len(findings[p].get("issues") or []),
        }
        for p in PERSPECTIVES
    }
    structural = {
        "verdict": findings["structural"].get("verdict", "pass"),
        "finding_count": len(findings["structural"].get("issues") or []),
        "source": "case-review-findings-structural.json",
    }
    verdict = "reject" if raw_count else "pass"
    product_count = sum(1 for i in issues if i.get("audience") == "product")
    internal_count = sum(1 for i in issues if i.get("audience") == "internal")
    summary = (
        "四视角与结构评审未发现阻断问题，蓝图和用例可进入执行。"
        if verdict == "pass"
        else f"四视角与结构评审共发现 {raw_count} 条原始问题，合并后 {merged_count} 条；产品问题 {product_count} 条，内部返工问题 {internal_count} 条。"
    )
    perspective_notes = {
        p: findings[p].get("perspective_notes") or [] for p in ("structural", *PERSPECTIVES)
    }
    extra_notes = {
        p: findings[p].get("extra_notes") or [] for p in ("structural", *PERSPECTIVES)
    }
    knowledge_evidence_summary = {
        p: {
            "docs_read": findings[p].get("knowledge_docs_read") or [],
            "note_count": len(findings[p].get("perspective_notes") or []),
            "extra_note_count": len(findings[p].get("extra_notes") or []),
        }
        for p in PERSPECTIVES
    }
    report = {
        "version": "1.0",
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "summary": summary,
        "coverage_score": 1.0 if verdict == "pass" else 0.8,
        "coverage_matrix": coverage_matrix_stub(issues),
        "issues": issues,
        "gaps": [i.get("description", "") for i in issues if i.get("root_cause") in {"qa_undercoverage", "case_generation"}],
        "duplicate_cases": [],
        "revision_hints": sorted({i.get("suggestion", "") for i in issues if i.get("suggestion")}),
        "approved_case_count": 0,
        "tri_party": tri_party,
        "structural": structural,
        "perspective_brief_ref": "case-review-perspective-brief.json",
        "finding_count_raw": raw_count,
        "finding_count_merged": merged_count,
        "perspective_notes": perspective_notes,
        "extra_notes": extra_notes,
        "knowledge_evidence_summary": knowledge_evidence_summary,
        "false_coverage": [],
    }
    if verdict == "reject":
        report["reject_kind"] = classify_reject_kind(issues)
    return report


def load_all_findings(brief: dict) -> dict[str, dict]:
    findings: dict[str, dict] = {}
    errors: list[str] = []
    for perspective in ("structural", *PERSPECTIVES):
        path = findings_path(perspective)
        if not path.exists():
            errors.append(f"missing {path.name}")
            continue
        data = load_json(path)
        perr = validate_findings(data, perspective, brief)
        if perr:
            errors.extend(f"{path.name}: {e}" for e in perr)
        findings[perspective] = data
    if errors:
        raise RuntimeError("\n".join(errors))
    return findings


def render_markdown() -> None:
    scripts = ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from render_case_review_notice import write_product_markdown

    write_product_markdown()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", default=None)
    args = parser.parse_args()
    global ARTIFACTS
    if args.artifacts:
        ARTIFACTS = Path(args.artifacts)
    brief_path = ARTIFACTS / "case-review-perspective-brief.json"
    if not brief_path.exists():
        print(f"missing {brief_path}", file=sys.stderr)
        return 1
    try:
        brief = load_json(brief_path)
        brief_errors = validate_schema(brief, "case-review-perspective-brief.schema.json")
        if brief_errors:
            raise RuntimeError("\n".join(f"brief: {e}" for e in brief_errors))
        findings = load_all_findings(brief)
        report = build_report(brief, findings)
        report_errors = validate_schema(report, "review-report.schema.json")
        if report_errors:
            raise RuntimeError("\n".join(f"report: {e}" for e in report_errors))
        tmp = ARTIFACTS / "03-review-report.json.tmp"
        final = ARTIFACTS / "03-review-report.json"
        tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, final)
        render_markdown()
        print(final)
        return 0
    except Exception as exc:
        print(f"FAIL merge_case_review_findings: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
