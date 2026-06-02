#!/usr/bin/env python3
"""Self tests for QA pipeline orchestration and validation logic.

The tests patch artifact paths to temporary directories and do not write to the
real workspace/artifacts runtime directory.
"""

from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def minimal_blueprint() -> dict:
    return {
        "version": "1.0",
        "project_name": "selftest",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "figma_url": "",
        "modules": [{"id": "mod", "name": "Module", "priority": "P0"}],
        "roles": [{"id": "user", "name": "User"}],
        "scenarios": [
            {
                "id": "SC-001",
                "module_id": "mod",
                "title": "Happy path",
                "type": "功能",
                "priority": "P0",
                "preconditions": ["ready"],
                "steps": ["do action"],
                "expected": ["see result"],
                "source": "prd",
                "covers_obligations": ["O-001"],
                "prd_section": "S1",
            }
        ],
        "assumptions": [],
        "coverage_matrix": [{"module_id": "mod", "functional": True, "boundary": True, "exception": True}],
        "blocking_gaps": [],
        "delivery_coverage": {
            "executed_by": "prd-analyzer-subagent",
            "project_scale": "small",
            "scenario_minimum_required": 1,
            "prd": {
                "read_complete": True,
                "sources": [{"path": "workspace/inputs/prd.md", "read_complete": True, "pages_total": 1, "pages_read": 1}],
                "sections_inventory": [{"section_id": f"S{i}", "title": f"S{i}", "in_scope": i == 1, "scenario_ids": ["SC-001"] if i == 1 else []} for i in range(1, 11)],
                "functional_points_count": 1,
                "functional_points_mapped": 1,
            },
            "figma": {"read_complete": False, "urls": [], "frames_inventory": [], "note": "not provided"},
        },
    }


def minimal_obligations() -> dict:
    return {
        "version": "1.0",
        "project_name": "selftest",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "obligations": [
            {
                "id": "O-001",
                "statement": "Must do action",
                "predicate": "do action and see result",
                "source": "prd",
                "risk": "P0",
                "kind": "rule",
                "module_id": "mod",
                "covered_by_scenarios": ["SC-001"],
            }
        ],
    }


def patch_artifacts(module, path: Path) -> None:
    module.ARTIFACTS = path
    if hasattr(module, "PROMPTS_DIR"):
        module.PROMPTS_DIR = path / "prompts"
    if hasattr(module, "AWAITING_SUBAGENT"):
        module.AWAITING_SUBAGENT = path / ".qa-pipeline-awaiting-subagent"
    if hasattr(module, "PRD_GATE_FINDINGS"):
        module.PRD_GATE_FINDINGS = {
            "prd-gate-product-review": path / "gate-findings-product.json",
            "prd-gate-dev-review": path / "gate-findings-dev.json",
            "prd-gate-qa-review": path / "gate-findings-qa.json",
            "prd-gate-red-team": path / "gate-findings-red-team.json",
        }


def test_pipeline_runner() -> None:
    runner = load_module("pipeline_runner_selftest", ROOT / "scripts" / "pipeline_runner.py")
    with tempfile.TemporaryDirectory() as td:
        artifacts = Path(td)
        patch_artifacts(runner, artifacts)
        write_json(artifacts / "00-prd-gate-report.json", {"verdict": "reject"})
        assert runner.artifact_ready("prd-gate"), "prd-gate reject report must be treated as ready"

        pipeline = runner.load_pipeline()
        stage = runner.stage_by_id(pipeline, "test-execute")
        prompt = runner.build_prompt("codex", stage, pipeline, {"run_id": "selftest"})
        assert "workspace/artifacts/04-execution-result.json" in prompt
        assert "workspace/artifacts/05b-bug-list.md" in prompt
        assert "optional, missing" in prompt

        stale = artifacts / "02-test-cases.md"
        stale.write_text("old", encoding="utf-8")
        runner.cleanup_outputs_for_stages(pipeline, ["case-generate"])
        assert not stale.exists(), "forced cleanup should remove stale case-generate output"


def test_validate_artifacts() -> None:
    validate = load_module("validate_artifacts_selftest", ROOT / "scripts" / "validate-artifacts.py")
    with tempfile.TemporaryDirectory() as td:
        artifacts = Path(td)
        validate.ARTIFACTS = artifacts
        write_json(artifacts / "00-test-ready-blueprint.json", minimal_blueprint())
        write_json(artifacts / "00-test-obligations.json", minimal_obligations())
        write_json(artifacts / "01-prd-analysis.json", {"version": "1.0", "project_name": "selftest", "analyzed_at": datetime.now(timezone.utc).isoformat(), "figma_url": "", "modules": [{"id": "mod", "name": "Module"}], "roles": [], "main_flows": [], "risks": []})
        write_json(artifacts / ".prd-analyze-complete.ok", {"ok": True})
        write_json(artifacts / ".test-point-coverage-precheck.json", {"ok": False, "false_coverage_count": 1})

        gate_pass = {
            "version": "1.0",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "verdict": "pass",
            "summary": "pass",
            "issues": [],
            "test_point_review": {
                "coverage_score": 1,
                "obligations_total": 1,
                "obligations_p0_uncovered": 0,
                "scenarios_total": 1,
                "false_coverage_count": 1,
                "tri_party": {
                    "product": {"verdict": "pass", "finding_count": 0},
                    "dev": {"verdict": "pass", "finding_count": 0},
                    "qa": {"verdict": "pass", "finding_count": 0},
                    "red_team": {"verdict": "pass", "finding_count": 0},
                },
            },
            "false_coverage": [{"scenario_id": "SC-001", "obligation_ids": ["O-001"], "reason": "weak"}],
        }
        errs = validate.validate_prd_gate_report(gate_pass)
        assert errs, "gate pass with false coverage must fail"

        write_json(
            artifacts / "03-review-report.json",
            {
                "version": "1.0",
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "verdict": "pass",
                "coverage_score": 1,
                "gaps": ["gap"],
                "revision_hints": [],
            },
        )
        with contextlib.redirect_stdout(io.StringIO()):
            case_review_ok = validate.validate_stage("case-review")
        assert not case_review_ok, "case-review pass with gaps must fail"

        write_json(
            artifacts / "04-execution-result.json",
            {
                "version": "1.0",
                "executed_at": datetime.now(timezone.utc).isoformat(),
                "environment": {},
                "summary": {"total": 1, "pass": 1, "fail": 0, "skip": 0, "block": 0},
                "cases": [{"case_id": "SC-001", "title": "x", "status": "fail"}],
                "has_pass": True,
                "has_fail": False,
            },
        )
        with contextlib.redirect_stdout(io.StringIO()):
            test_execute_ok = validate.validate_stage("test-execute")
        assert not test_execute_ok, "execution summary mismatch must fail"


def main() -> int:
    tests = [test_pipeline_runner, test_validate_artifacts]
    failed = []
    for test in tests:
        try:
            test()
            print(f"OK {test.__name__}")
        except Exception as exc:
            failed.append((test.__name__, exc))
            print(f"FAIL {test.__name__}: {exc}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
