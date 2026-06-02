#!/usr/bin/env python3
"""Validate QA pipeline artifacts against contracts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "contracts"
ARTIFACTS = ROOT / "workspace" / "artifacts"

BLUEPRINT_FILE = "00-test-ready-blueprint.json"
BLUEPRINT_SCHEMA = "test-ready-blueprint.schema.json"

GATE_FINDINGS_FILES = {
    "gate-findings-product": ("gate-findings-product.json", "gate-review-findings.schema.json"),
    "gate-findings-dev": ("gate-findings-dev.json", "gate-review-findings.schema.json"),
    "gate-findings-qa": ("gate-findings-qa.json", "gate-review-findings.schema.json"),
    "gate-findings-red-team": ("gate-findings-red-team.json", "gate-review-findings.schema.json"),
}

# Pipeline sub-stage ids → gate-findings validation keys
STAGE_ALIASES = {
    "prd-gate-product-review": "gate-findings-product",
    "prd-gate-dev-review": "gate-findings-dev",
    "prd-gate-qa-review": "gate-findings-qa",
    "prd-gate-red-team": "gate-findings-red-team",
}

STAGE_FILES = {
    "prd-gate": ("00-prd-gate-report.json", "prd-gate-report.schema.json"),
    "test-obligations": ("00-test-obligations.json", "test-obligations.schema.json"),
    "test-ready-blueprint": (BLUEPRINT_FILE, BLUEPRINT_SCHEMA),
    "prd-analyze": ("01-prd-analysis.json", "prd-analysis.schema.json"),
    "case-review": ("03-review-report.json", "review-report.schema.json"),
    "test-execute": ("04-execution-result.json", "execution-result.schema.json"),
}

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_json_schema(data: dict, schema_path: Path) -> list[str]:
    errors: list[str] = []
    if not HAS_JSONSCHEMA:
        errors.append("jsonschema not installed; run: pip install -r requirements.txt")
        return errors
    schema = load_json(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        loc = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{loc}: {err.message}")
    return errors


def validate_test_cases_md(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing: {path}"]
    text = path.read_text(encoding="utf-8")
    if "| 编号 |" not in text and "|编号|" not in text:
        errors.append("missing markdown table with 编号 column")
    if not re.search(r"^#\s+\S+", text, re.MULTILINE):
        errors.append("missing XMind-style module heading (# Module)")
    if not re.search(r"^###\s+\S+", text, re.MULTILINE):
        errors.append("missing case heading (### title)")
    rows = [l for l in text.splitlines() if l.startswith("|") and "---" not in l]
    if len(rows) < 2:
        errors.append("table appears empty (need header + at least one case row)")
    for i, row in enumerate(rows[1:], start=1):
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) != 8:
            errors.append(f"table row {i} must have 8 columns, got {len(cells)}")
            continue
        if not cells[0]:
            errors.append(f"table row {i} missing case id")
        if not cells[4]:
            errors.append(f"table row {i} missing test steps")
        if not cells[5]:
            errors.append(f"table row {i} missing expected result")
    return errors


def validate_bug_list_md(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing: {path}"]
    text = path.read_text(encoding="utf-8")
    if "# Bug List" not in text:
        errors.append('missing "# Bug List" heading')
    if not re.search(r"^##\s+BUG-\d+", text, re.MULTILINE):
        errors.append("missing bug entries (## BUG-NNN)")
    return errors


def validate_scripts_dir(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing: {path}"]
    files = [f for f in path.iterdir() if f.is_file() and f.name != "manifest.json"]
    if not files:
        errors.append("no script files in 05a-scripts/")
    manifest = path / "manifest.json"
    if manifest.exists():
        errors.extend(validate_json_schema(load_json(manifest), CONTRACTS / "automation-script.schema.json"))
    result_path = ARTIFACTS / "04-execution-result.json"
    if result_path.exists():
        data = load_json(result_path)
        expected = [
            c.get("case_id")
            for c in data.get("cases", [])
            if c.get("status") == "pass" and c.get("automatable") is True
        ]
        if expected:
            names = {f.name for f in files}
            manifest_cases = set()
            if manifest.exists():
                try:
                    manifest_cases = {
                        s.get("case_id")
                        for s in load_json(manifest).get("scripts", [])
                        if s.get("case_id")
                    }
                except json.JSONDecodeError:
                    manifest_cases = set()
            for cid in expected:
                by_file = any(cid in name for name in names)
                if cid not in manifest_cases and not by_file:
                    errors.append(f"missing automation script for pass+automatable case {cid}")
    return errors


SUGGESTION_MIN_LEN = 10
VAGUE_SUGGESTIONS = (
    "请完善",
    "待补充",
    "请补充",
    "需要完善",
    "请修改",
)


def _classify_reject_kind(issues: list[dict]) -> str:
    audiences = {(i.get("audience") or "product") for i in issues}
    has_product = "product" in audiences
    has_internal = "internal" in audiences
    if has_product and has_internal:
        return "mixed"
    if has_internal:
        return "internal"
    return "product"


def validate_prd_gate_report(data: dict) -> list[str]:
    """Business rules for zero-defect gate and reject copy quality."""
    errors: list[str] = []
    verdict = data.get("verdict")
    issues = data.get("issues") or []
    summary = (data.get("summary") or "").strip()

    # 禁止在 prd-analyze 全文分析未完成时出具 gate 结论（含 reject 打回产品）
    import sys as _sys

    _scripts = Path(__file__).resolve().parent
    if str(_scripts) not in _sys.path:
        _sys.path.insert(0, str(_scripts))
    from analyze_gate_prerequisites import require_analyze_complete

    errors.extend(require_analyze_complete("prd-gate-report"))

    tpr = data.get("test_point_review") or {}
    if verdict == "pass":
        if issues:
            errors.append("verdict=pass requires empty issues[] (zero-defect gate)")
        if not summary:
            errors.append("verdict=pass requires non-empty summary")
        bp = ARTIFACTS / BLUEPRINT_FILE
        analysis = ARTIFACTS / "01-prd-analysis.json"
        ob = ARTIFACTS / "00-test-obligations.json"
        if not bp.exists():
            errors.append(f"verdict=pass requires {BLUEPRINT_FILE} (from prd-analyze)")
        if not analysis.exists():
            errors.append("verdict=pass requires 01-prd-analysis.json (from prd-analyze)")
        if not ob.exists():
            errors.append("verdict=pass requires 00-test-obligations.json (TOG)")
        threshold = 0.90
        meta_path = ARTIFACTS / "00-meta.json"
        if meta_path.exists():
            meta = load_json(meta_path)
            threshold = meta.get("review", {}).get("test_point_coverage_threshold", threshold)
        required_tpr = [
            "coverage_score",
            "obligations_total",
            "obligations_p0_uncovered",
            "scenarios_total",
            "false_coverage_count",
            "tri_party",
        ]
        for field in required_tpr:
            if field not in tpr:
                errors.append(f"verdict=pass requires test_point_review.{field}")
        score = tpr.get("coverage_score")
        if score is None:
            errors.append("verdict=pass requires test_point_review.coverage_score")
        elif score < threshold:
            errors.append(
                f"test_point_review.coverage_score {score} < threshold {threshold}"
            )
        if tpr.get("false_coverage_count", 0) != 0:
            errors.append("verdict=pass requires test_point_review.false_coverage_count=0")
        if data.get("false_coverage"):
            errors.append("verdict=pass requires empty false_coverage[]")
        tri = tpr.get("tri_party") or {}
        for role in ("product", "dev", "qa", "red_team"):
            r = tri.get(role)
            if not r:
                errors.append(f"verdict=pass requires test_point_review.tri_party.{role}")
            elif r.get("verdict") != "pass":
                errors.append(f"tri_party.{role}.verdict must be pass for gate pass")
        precheck = ARTIFACTS / ".test-point-coverage-precheck.json"
        if precheck.exists():
            pc = load_json(precheck)
            if pc.get("ok") is not True:
                errors.append(".test-point-coverage-precheck.json ok=false blocks gate pass")
        return errors

    if verdict == "reject":
        if not issues:
            errors.append("verdict=reject requires non-empty issues[]")
        if not summary:
            errors.append("verdict=reject requires non-empty summary (打回原因摘要)")
        rk = data.get("reject_kind") or _classify_reject_kind(issues)
        if rk != _classify_reject_kind(issues):
            errors.append(
                f"reject_kind={rk} inconsistent with issue audiences (expected {_classify_reject_kind(issues)})"
            )
        product_issues = [i for i in issues if (i.get("audience") or "product") == "product"]
        if rk in ("product", "mixed") and not product_issues:
            errors.append("reject_kind product/mixed requires at least one audience=product issue")
        for i, issue in enumerate(issues):
            prefix = f"issues[{i}]"
            desc = (issue.get("description") or "").strip()
            sugg = (issue.get("suggestion") or "").strip()
            aud = issue.get("audience") or "product"
            rc = issue.get("root_cause")
            if len(desc) < SUGGESTION_MIN_LEN:
                errors.append(f"{prefix}.description too short (min {SUGGESTION_MIN_LEN})")
            if len(sugg) < SUGGESTION_MIN_LEN:
                errors.append(f"{prefix}.suggestion too short (min {SUGGESTION_MIN_LEN})")
            if desc and sugg and desc == sugg:
                errors.append(f"{prefix}: suggestion must differ from description")
            if aud == "product" and any(v in sugg for v in VAGUE_SUGGESTIONS) and len(sugg) < 30:
                errors.append(
                    f"{prefix}.suggestion looks vague; provide actionable product steps"
                )
            if rc == "qa_undercoverage" and aud != "internal":
                errors.append(f"{prefix}: qa_undercoverage must use audience=internal")
            if rc in ("prd", "figma", "assumption_unresolved") and aud == "internal":
                errors.append(
                    f"{prefix}: root_cause={rc} should not use audience=internal for product-facing gaps"
                )
    return errors


def validate_test_ready_blueprint_data(data: dict) -> list[str]:
    errs = []
    import sys
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from validate_test_ready_blueprint import validate_test_ready_blueprint
    errs.extend(validate_test_ready_blueprint(data))
    return errs


def count_scenario_ids_in_cases_md(text: str) -> set[str]:
    found = set(re.findall(r"\b(SC-\d{3})\b", text))
    found.update(re.findall(r"\b([A-Z]+-\d{3})\b", text))
    return found


def validate_case_generate_fidelity() -> list[str]:
    errors: list[str] = []
    bp_path = ARTIFACTS / BLUEPRINT_FILE
    cases_path = ARTIFACTS / "02-test-cases.md"
    if not bp_path.exists():
        return ["missing blueprint for case-generate fidelity check"]
    if not cases_path.exists():
        return [f"missing: {cases_path}"]
    blueprint = load_json(bp_path)
    expected_ids = {s["id"] for s in blueprint.get("scenarios") or []}
    text = cases_path.read_text(encoding="utf-8")
    for phrase in ("需产品确认", "待产品确认", "待产品补充"):
        if phrase in text:
            errors.append(f"02-test-cases.md must not contain '{phrase}'")
    # Table rows: module-NNN or SC-NNN
    table_ids = set(re.findall(r"\|\s*([A-Z]+-\d{3})\s*\|", text))
    if expected_ids and not table_ids:
        errors.append("no case ids found in table (expected blueprint scenario ids)")
    missing = expected_ids - table_ids
    extra = table_ids - expected_ids
    if missing:
        errors.append(f"missing rendered scenarios: {sorted(missing)[:5]}{'...' if len(missing) > 5 else ''}")
    if extra:
        errors.append(f"extra cases not in blueprint: {sorted(extra)[:5]}{'...' if len(extra) > 5 else ''}")
    return errors


def validate_stage(stage: str, *, finalize: bool = False) -> bool:
    ok = True
    stage = STAGE_ALIASES.get(stage, stage)
    if stage == "case-generate":
        errs = validate_test_cases_md(ARTIFACTS / "02-test-cases.md")
        errs.extend(validate_case_generate_fidelity())
    elif stage == "bug-list-write":
        errs = validate_bug_list_md(ARTIFACTS / "05b-bug-list.md")
    elif stage == "script-convert":
        errs = validate_scripts_dir(ARTIFACTS / "05a-scripts")
    elif stage in GATE_FINDINGS_FILES:
        fname, schema_name = GATE_FINDINGS_FILES[stage]
        fpath = ARTIFACTS / fname
        if not fpath.exists():
            print(f"FAIL {stage}: missing {fpath}")
            return False
        data = load_json(fpath)
        errs = validate_json_schema(data, CONTRACTS / schema_name)
        expected_lens = {
            "gate-findings-product": "product",
            "gate-findings-dev": "dev",
            "gate-findings-qa": "qa",
            "gate-findings-red-team": "red_team",
        }
        if data.get("lens") != expected_lens.get(stage):
            errs.append(f"lens must be {expected_lens.get(stage)}")
        for i, finding in enumerate(data.get("findings") or []):
            if finding.get("verdict") != "fail":
                continue
            prefix = f"findings[{i}]"
            if not finding.get("root_cause_draft"):
                errs.append(f"{prefix}.root_cause_draft required when verdict=fail")
            if not finding.get("audience_draft"):
                errs.append(f"{prefix}.audience_draft required when verdict=fail")
            if not (finding.get("suggestion_draft") or "").strip():
                errs.append(f"{prefix}.suggestion_draft required when verdict=fail")
            if not (
                finding.get("obligation_ids")
                or finding.get("scenario_ids")
                or finding.get("prd_section")
            ):
                errs.append(
                    f"{prefix} requires obligation_ids, scenario_ids, or prd_section when verdict=fail"
                )
    elif stage in STAGE_FILES:
        fname, schema_name = STAGE_FILES[stage]
        fpath = ARTIFACTS / fname
        if not fpath.exists():
            print(f"FAIL {stage}: missing {fpath}")
            return False
        data = load_json(fpath)
        errs = validate_json_schema(data, CONTRACTS / schema_name)
        if stage == "prd-gate" and not errs:
            errs.extend(validate_prd_gate_report(data))
            if data.get("verdict") == "pass" and not errs:
                bp_path = ARTIFACTS / BLUEPRINT_FILE
                if bp_path.exists():
                    bp_data = load_json(bp_path)
                    errs.extend(
                        validate_json_schema(bp_data, CONTRACTS / BLUEPRINT_SCHEMA)
                    )
                    if not errs:
                        errs.extend(validate_test_ready_blueprint_data(bp_data))
                else:
                    errs.append(f"missing {BLUEPRINT_FILE} for pass verdict")
        if stage == "test-ready-blueprint" and not errs:
            errs.extend(validate_test_ready_blueprint_data(data))
        if stage == "prd-analyze" and not errs and finalize:
            from analyze_gate_prerequisites import write_analyze_complete_marker

            write_analyze_complete_marker()
            ob_path = ARTIFACTS / "00-test-obligations.json"
            if ob_path.exists():
                subprocess.run(
                    [
                        sys.executable,
                        str(Path(__file__).resolve().parent / "sync_obligation_coverage.py"),
                        "--write",
                    ],
                    cwd=str(ROOT),
                    check=False,
                )
        if stage == "prd-analyze" and not errs:
            bp_path = ARTIFACTS / BLUEPRINT_FILE
            if not bp_path.exists():
                errs.append(f"missing {BLUEPRINT_FILE} for prd-analyze")
            else:
                bp_data = load_json(bp_path)
                errs.extend(
                    validate_json_schema(bp_data, CONTRACTS / BLUEPRINT_SCHEMA)
                )
                if not errs:
                    errs.extend(validate_test_ready_blueprint_data(bp_data))
        if stage == "case-review" and not errs:
            threshold = 0.85
            meta_path = ARTIFACTS / "00-meta.json"
            if meta_path.exists():
                meta = load_json(meta_path)
                threshold = meta.get("review", {}).get("pass_threshold", threshold)
            if data.get("verdict") == "pass" and data.get("coverage_score", 0) < threshold:
                errs.append(
                    f"coverage_score {data.get('coverage_score')} < threshold {threshold}"
                )
            if data.get("verdict") == "pass":
                if data.get("gaps"):
                    errs.append("verdict=pass requires gaps=[]")
                if data.get("duplicate_cases"):
                    errs.append("verdict=pass requires duplicate_cases=[]")
        if stage == "test-execute" and not errs:
            summary = data.get("summary", {})
            cases = data.get("cases", [])
            total = summary.get("total", 0)
            if total != len(cases):
                errs.append(f"summary.total ({total}) != len(cases) ({len(cases)})")
            counts = {
                "pass": sum(1 for c in cases if c.get("status") == "pass"),
                "fail": sum(1 for c in cases if c.get("status") == "fail"),
                "skip": sum(1 for c in cases if c.get("status") == "skip"),
                "block": sum(1 for c in cases if c.get("status") == "block"),
            }
            for key, actual in counts.items():
                if summary.get(key, 0) != actual:
                    errs.append(f"summary.{key} ({summary.get(key, 0)}) != {actual} cases")
            has_fail = data.get("has_fail", any(
                c.get("status") in ("fail", "block") for c in cases
            ))
            expected_has_pass = any(c.get("status") == "pass" for c in cases)
            expected_has_fail = any(c.get("status") in ("fail", "block") for c in cases)
            if data.get("has_pass", expected_has_pass) != expected_has_pass:
                errs.append("has_pass inconsistent with cases[]")
            if data.get("has_fail", expected_has_fail) != expected_has_fail:
                errs.append("has_fail inconsistent with cases[]")
            for i, case in enumerate(cases):
                status = case.get("status")
                if status in ("fail", "block") and not (case.get("failure_reason") or "").strip():
                    errs.append(f"cases[{i}].failure_reason required for {status}")
                for ev in case.get("evidence") or []:
                    ev_path = ROOT / ev
                    if not ev_path.exists():
                        errs.append(f"cases[{i}].evidence missing: {ev}")
            if has_fail and not (ARTIFACTS / "05b-bug-list.md").exists():
                errs.append("has_fail=true but missing 05b-bug-list.md")
            elif has_fail:
                errs.extend(validate_bug_list_md(ARTIFACTS / "05b-bug-list.md"))
    else:
        print(f"Unknown stage: {stage}")
        return False

    if errs:
        print(f"FAIL {stage}:")
        for e in errs:
            print(f"  - {e}")
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


def update_meta_stage(stage: str, status: str, extra: dict | None = None) -> None:
    meta_path = ARTIFACTS / "00-meta.json"
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    if meta_path.exists():
        meta = load_json(meta_path)
    else:
        meta = init_meta()
    meta["current_stage"] = stage
    meta["stages"][stage] = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if extra:
        meta["stages"][stage].update(extra)
    if status == "done" and stage == "case-review" and extra and "verdict" in extra:
        meta["review"]["last_verdict"] = extra["verdict"]
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate QA pipeline artifacts")
    parser.add_argument("--stage", help="Validate single stage")
    parser.add_argument("--all", action="store_true", help="Validate all completed artifacts")
    parser.add_argument("--strict-all", action="store_true", help="Validate required pipeline artifacts, not just existing files")
    parser.add_argument("--finalize", action="store_true", help="Allow validation to write finalize markers/sync artifacts")
    parser.add_argument("--init-meta", action="store_true", help="Initialize 00-meta.json")
    parser.add_argument("--mark-done", metavar="STAGE", help="Mark stage done in meta")
    parser.add_argument("--extra", help="JSON extra fields for --mark-done")
    args = parser.parse_args()

    if args.init_meta:
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        meta = init_meta()
        (ARTIFACTS / "00-meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("Initialized workspace/artifacts/00-meta.json")
        return 0

    if args.mark_done:
        extra = json.loads(args.extra) if args.extra else None
        update_meta_stage(args.mark_done, "done", extra)
        print(f"Marked {args.mark_done} as done in meta")
        return 0

    stages = (
        ["prd-gate", "prd-analyze", "case-generate", "case-review", "test-execute", "script-convert"]
        if args.all or args.strict_all
        else [args.stage]
        if args.stage
        else []
    )
    if not stages:
        parser.print_help()
        return 1

    # Only validate artifacts that exist when using --all
    if args.all:
        checks = []
        if (ARTIFACTS / "00-prd-gate-report.json").exists():
            checks.append("prd-gate")
        if (ARTIFACTS / BLUEPRINT_FILE).exists():
            checks.append("test-ready-blueprint")
        if (ARTIFACTS / "01-prd-analysis.json").exists():
            checks.append("prd-analyze")
        if (ARTIFACTS / "02-test-cases.md").exists():
            checks.append("case-generate")
        if (ARTIFACTS / "03-review-report.json").exists():
            checks.append("case-review")
        if (ARTIFACTS / "04-execution-result.json").exists():
            checks.append("test-execute")
        if (ARTIFACTS / "05a-scripts").exists():
            checks.append("script-convert")
        if (ARTIFACTS / "05b-bug-list.md").exists() and (ARTIFACTS / "04-execution-result.json").exists():
            checks.append("test-execute")
        stages = checks or stages
    if args.strict_all:
        stages = [
            "test-obligations",
            "test-ready-blueprint",
            "prd-analyze",
            "prd-gate",
            "case-generate",
            "case-review",
            "test-execute",
        ]
        if (ARTIFACTS / "04-execution-result.json").exists():
            data = load_json(ARTIFACTS / "04-execution-result.json")
            if data.get("has_pass"):
                stages.append("script-convert")

    failed = [s for s in stages if not validate_stage(s, finalize=args.finalize)]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
