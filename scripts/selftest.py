#!/usr/bin/env python3
"""Self tests for the single-blueprint QA pipeline."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import uuid
from datetime import timedelta
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
    now = datetime.now(timezone.utc).isoformat()
    return {
        "version": "2.0",
        "project_name": "selftest",
        "created_at": now,
        "modules": [
            {
                "module_id": "M-01",
                "title": "示例需求模块",
                "goal": "用户完成一个明确动作后能看到明确结果。",
                "source_refs": ["PRD §1"],
                "test_points": [
                    {
                        "point_id": "TP-01.01",
                        "title": "成功结果展示",
                        "basis": "PRD §1 描述用户动作完成后展示成功结果。",
                        "acceptance_rule": "用户完成动作后，页面展示成功提示和结果内容。",
                        "priority": "P0",
                        "scope": {
                            "include": ["Web 示例入口"],
                            "exclude": ["性能、接口、日志、数据库"],
                            "platforms": ["Web"],
                            "entry_points": ["首页入口"],
                            "data": ["已登录账号", "可操作测试数据"],
                        },
                        "scenarios": [
                            {
                                "scenario_id": "S-01.01.01",
                                "title": "已登录用户完成动作后看到成功结果",
                                "priority": "P0",
                                "type": "功能",
                                "preconditions": ["测试账号已登录", "页面存在可操作数据"],
                                "test_data": [
                                    "Property To Rent To Share Commercial Parking Holiday Rentals"
                                ],
                                "steps": [
                                    "打开 https://www.example.test/",
                                    "点击首页入口 Property to rent to share commercial parking holiday",
                                    "点击目标动作按钮",
                                ],
                                "expected_results": ["页面展示成功提示", "结果区域展示测试数据 A 的处理结果"],
                                "postconditions": ["删除测试数据 A 的处理结果"],
                                "execution_channel": "browser",
                                "automatable": "是",
                                "automation_note": "可通过 UI 文案和结果区域断言。",
                                "source_refs": ["PRD §1"],
                            }
                        ],
                    }
                ],
            }
        ],
        "open_questions": [],
    }


def minimal_knowledge_context() -> dict:
    return {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision_owner": "prd-analyzer-subagent",
        "knowledge_base_path": "bundled/knowledge_base",
        "selected_documents": [
            {
                "path": "bundled/knowledge_base/产品全景/功能模块清单.md",
                "usage": "business_context",
                "reason": "提供模块背景，帮助判断测试范围。",
            }
        ],
        "excluded_candidates": [],
        "notes": [],
    }


def minimal_cases_md() -> str:
    return "\n".join(
        [
            "# 测试用例",
            "",
            "## 示例需求模块",
            "",
            "### TC-001: 已登录用户完成动作后看到成功结果",
            "",
            "- 用例编号：TC-001",
            "- 需求模块：示例需求模块",
            "- 测试点：—",
            "- 优先级：P0",
            "- 执行通道：browser",
            "- 是否可自动化：是",
            "",
            "- 前置条件",
            "  - Given 测试账号已登录",
            "  - Given 页面存在可操作数据",
            "",
            "- 测试数据",
            "  - 测试数据 A",
            "",
            "- 执行步骤",
            "  - 1. When 打开首页入口",
            "  - 2. When 点击目标动作按钮",
            "",
            "- 预期结果",
            "  - Then 页面展示成功提示",
            "",
            "- 后置动作",
            "  - 删除测试数据 A 的处理结果",
            "",
            "- 需求依据：PRD §1",
            "",
        ]
    )


def patch_artifacts(module, path: Path) -> None:
    module.ARTIFACTS = path
    if hasattr(module, "PROMPTS_DIR"):
        module.PROMPTS_DIR = path / "prompts"
    if hasattr(module, "AWAITING_SUBAGENT"):
        module.AWAITING_SUBAGENT = path / ".qa-pipeline-awaiting-subagent"


def test_pipeline_runner() -> None:
    runner = load_module("pipeline_runner_selftest", ROOT / "scripts" / "pipeline_runner.py")
    with tempfile.TemporaryDirectory() as td:
        artifacts = Path(td)
        patch_artifacts(runner, artifacts)
        old_workspace = os.environ.get("QA_WORKSPACE")
        os.environ["QA_WORKSPACE"] = str(artifacts)
        write_json(
            artifacts / "00-meta.json",
            {
                "version": "1.0",
                "run_id": "selftest",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "current_stage": "case-review",
                "status": "running",
                "review": {"pass_threshold": 0.85, "retry_count": 0},
                "stages": {},
                "post_process": {},
            },
        )
        write_json(
            artifacts / "03-review-report.json",
            {
                "version": "1.0",
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "verdict": "reject",
                "reject_kind": "product",
                "summary": "PRD 缺少验收标准。",
                "coverage_score": 0.8,
                "issues": [{"audience": "product", "retry_target": "product"}],
                "revision_hints": [],
            },
        )
        assert runner.artifact_ready("case-review"), "case-review report must be treated as ready"
        runner._force_rerun = lambda: True
        assert not runner.artifact_ready("case-review"), "force mode must not skip an existing stage"
        assert runner.artifact_ready("case-review", respect_force=False), "post-run artifact checks must ignore force mode"
        runner._force_rerun = lambda: False

        pipeline = runner.load_pipeline()
        stage = runner.stage_by_id(pipeline, "test-execute")
        prompt = runner.build_prompt("codex", stage, pipeline, {"run_id": "selftest"})
        assert "04-execution-result.json" in prompt
        assert "05b-bug-list.md" in prompt
        assert "workspace/inputs/env.json" in prompt

        assert runner.expand_stage_ids(["case-review"]) == runner.CASE_REVIEW_INTERNAL_STAGES
        product_stage = runner.stage_by_id(pipeline, "case-review-product")
        prompt_path = runner.write_prompt("cursor", product_stage, pipeline, runner.load_meta())
        assert prompt_path.name == "case-review-product.md"
        assert not (artifacts / ".subagent-launch-case-review-product.json").exists(), "prompt generation must not fake launch evidence"
        assert not (artifacts / "case-review-orchestration-trace.jsonl").exists(), "dry prompt generation must not write started trace"
        runner.write_prompt("cursor", product_stage, pipeline, runner.load_meta(), record_launch=True)
        assert (artifacts / ".subagent-launch-case-review-product.json").exists(), "real launch should create JSON launch lock"
        trace_text = (artifacts / "case-review-orchestration-trace.jsonl").read_text(encoding="utf-8")
        assert "perspective_task_started" in trace_text, "real launch should append started trace"
        write_json(
            artifacts / "case-review-findings-product.json",
            {
                "version": "1.0",
                "perspective": "product",
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "brief_ref": "case-review-perspective-brief.json",
                "knowledge_docs_read": [],
                "perspective_notes": [],
                "issues": [],
                "extra_notes": [],
                "verdict": "pass",
                "finding_count": 0,
            },
        )
        assert not runner.artifact_ready("case-review-product"), "findings alone must not mark perspective stage ready"

        meta_before = runner.load_meta()
        meta_before["mode"] = "ide-chain"
        runner.save_meta(meta_before)
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "pipeline_runner.py"),
                "--platform",
                "cursor",
                "--dry-run",
                "--from-stage",
                "case-review-product",
                "--to-stage",
                "case-review-product",
            ],
            cwd=str(ROOT),
            env={**__import__("os").environ, "QA_WORKSPACE": str(artifacts)},
            capture_output=True,
            text=True,
            check=False,
        )
        meta_after_dry = runner.load_meta()
        assert meta_after_dry.get("mode") == "ide-chain", "explicit dry-run must not overwrite meta.mode"
        assert meta_after_dry.get("last_prompt_generation_mode") == "dry_run"

        stale = artifacts / "02-test-cases.md"
        stale.write_text("old", encoding="utf-8")
        runner.cleanup_outputs_for_stages(pipeline, ["case-generate"])
        assert not stale.exists(), "forced cleanup should remove stale case-generate output"

        rework_md = artifacts / "test-point-rework-to-qa.md"
        rework_md.write_text("keep rework notes", encoding="utf-8")
        for rel in (
            "00-test-blueprint.json",
            "00-test-blueprint.md",
            "00-knowledge-inventory.json",
            "00-knowledge-inventory.md",
            "00-knowledge-context.json",
            "00-knowledge-context.md",
            "02-test-cases.md",
            "03-review-report.json",
            "04-execution-result.json",
            ".orchestrator-prd-reject-notified",
        ):
            (artifacts / rel).write_text("old", encoding="utf-8")
        runner.cleanup_outputs_for_stages(
            pipeline,
            ["prd-analyze", "case-generate", "case-review", "test-execute"],
        )
        assert not (artifacts / "00-test-blueprint.json").exists(), "force from prd-analyze must remove stale blueprint"
        assert not (artifacts / "03-review-report.json").exists(), "force from prd-analyze must remove stale review report"
        assert not (artifacts / ".orchestrator-prd-reject-notified").exists(), "force from prd-analyze must clear stale reject marker"
        assert rework_md.exists(), "internal rework notes must survive cleanup for the next prd-analyze prompt"

        write_json(
            artifacts / "03-review-report.json",
            {
                "version": "1.0",
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "verdict": "reject",
                "reject_kind": "mixed",
                "summary": "mixed selftest",
                "coverage_score": 0.8,
                "issues": [
                    {
                        "id": "GATE-001",
                        "severity": "blocker",
                        "category": "product",
                        "root_cause": "prd",
                        "audience": "product",
                        "retry_target": "product",
                        "description": "PRD A/B Testing Plan 标注 TBD。",
                        "evidence": {"prd_section": "PRD §A/B"},
                        "suggestion": "补充 A/B 方案。",
                    },
                    {
                        "id": "CR-001",
                        "severity": "minor",
                        "category": "coverage",
                        "root_cause": "qa_undercoverage",
                        "audience": "internal",
                        "retry_target": "prd-analyze",
                        "description": "未知 type 且 amount>0 回退场景未覆盖。",
                        "evidence": {"prd_section": "PRD §BFF"},
                        "suggestion": "补充 amount>0 回退场景。",
                    },
                ],
                "revision_hints": [],
            },
        )
        gate = runner.resolve_case_review_gate(pipeline, runner.load_meta())
        assert gate == "retry_analyze", "mixed reject with internal issues must trigger analyze retry"
        meta_after = runner.load_meta()
        assert meta_after.get("stage_result") == "INTERNAL_REWORK", "mixed retry must update meta away from PRODUCT_REJECT"
        assert not (artifacts / "03-review-report.json").exists(), "retry must clear stale review report"
        assert (artifacts / "test-point-rework-to-qa.md").exists(), "retry must keep internal rework markdown"
        assert (artifacts / ".pending-rework-issues.json").exists(), "retry must write pending rework checks"

        runner.cleanup_outputs_for_stages(pipeline, ["prd-analyze", "case-generate", "case-review"])

        class _Args:
            auto = True
            platform = "cursor"
            allow_cli = False

        with contextlib.redirect_stderr(io.StringIO()):
            assert runner.refuse_cursor_auto_without_allow(_Args()) == 1
        _Args.allow_cli = True
        assert runner.refuse_cursor_auto_without_allow(_Args()) is None
        if old_workspace is None:
            os.environ.pop("QA_WORKSPACE", None)
        else:
            os.environ["QA_WORKSPACE"] = old_workspace


def test_validate_artifacts() -> None:
    validate = load_module("validate_artifacts_selftest", ROOT / "scripts" / "validate-artifacts.py")
    qc = load_module("qa_coverage_checks_selftest", ROOT / "scripts" / "qa_coverage_checks.py")
    brief_mod = load_module("brief_selftest", ROOT / "scripts" / "build_case_review_perspective_brief.py")
    merge_mod = load_module("merge_selftest", ROOT / "scripts" / "merge_case_review_findings.py")
    with tempfile.TemporaryDirectory() as td:
        workspace = Path(td) / "workspace"
        artifacts = workspace / "artifacts"
        inputs = workspace / "inputs"
        artifacts.mkdir(parents=True)
        inputs.mkdir(parents=True)
        validate.ARTIFACTS = artifacts
        validate.ROOT = Path(td)
        qc.ARTIFACTS = artifacts
        qc.ROOT = Path(td)
        import qa_coverage_checks as qc_runtime

        qc_runtime.ARTIFACTS = artifacts
        qc_runtime.PRECHECK_FILE = artifacts / "case-review-precheck.json"
        qc_runtime.PENDING_REWORK_FILE = artifacts / ".pending-rework-issues.json"
        qc_runtime.SNAPSHOTS_DIR = artifacts / "snapshots"
        brief_mod.ARTIFACTS = artifacts
        brief_mod.INPUTS = inputs
        merge_mod.ARTIFACTS = artifacts
        mini_cfg = {
            "required_coverage": [
                {"id": "stub", "label": "selftest", "keywords": ["成功"], "min_scenarios": 1}
            ],
            "prd_contract_obligations": [],
        }
        (inputs / "config.yaml").write_text(
            "required_coverage:\n  - id: stub\n    label: selftest\n    keywords: ['成功']\n    min_scenarios: 1\n",
            encoding="utf-8",
        )

        def _selftest_config(_path=None):
            return mini_cfg

        import load_project_config as lpc_mod

        lpc_mod.load_project_config = _selftest_config
        validate.load_project_config = _selftest_config  # type: ignore[attr-defined]
        (inputs / "figma.url").write_text("https://www.figma.com/file/selftest-design\n", encoding="utf-8")
        (inputs / "prd.md").write_text(
            "# selftest PRD\n\nScope in scope.\n\nRequirement 3: £1,200pm no extra spacing.\n",
            encoding="utf-8",
        )
        write_json(artifacts / "00-test-blueprint.json", minimal_blueprint())
        write_json(artifacts / "00-knowledge-context.json", minimal_knowledge_context())
        (artifacts / "00-test-blueprint.md").write_text(
            "# 测试蓝图\n\n## 1. 需求模块：示例需求模块\n\n### 测试点 1.1：成功结果展示\n\n#### 测试范围\n\n#### 场景\n- 已登录用户完成动作后看到成功结果\n",
            encoding="utf-8",
        )
        (artifacts / "02-test-cases.md").write_text(minimal_cases_md(), encoding="utf-8")

        with contextlib.redirect_stdout(io.StringIO()):
            assert validate.validate_stage("prd-analyze"), "new blueprint should pass prd-analyze validation"
        with contextlib.redirect_stdout(io.StringIO()):
            assert validate.validate_stage("case-generate"), "cases should pass case-generate validation"

        review_reject = {
            "version": "1.0",
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "verdict": "reject",
            "reject_kind": "internal",
            "summary": "蓝图漏了主流程场景。",
            "coverage_score": 0.7,
            "issues": [
                {
                    "id": "CR-001",
                    "severity": "major",
                    "category": "coverage",
                    "root_cause": "qa_undercoverage",
                    "audience": "product",
                    "retry_target": "case-generate",
                    "description": "PRD 已说明成功提示，但蓝图没有覆盖。",
                    "evidence": {"scenario_ids": ["S-01.01.01"]},
                    "suggestion": "应回到 prd-analyze 补充蓝图。",
                }
            ],
            "revision_hints": [],
        }
        errs = validate.validate_case_review_report(review_reject)
        assert errs, "wrong review routing must fail"

        brief = brief_mod.build_brief(minimal_blueprint(), minimal_knowledge_context(), mini_cfg)
        write_json(artifacts / "case-review-perspective-brief.json", brief)
        (artifacts / "case-review-perspective-brief.md").write_text(
            brief_mod.render_markdown(brief), encoding="utf-8"
        )

        def _notes(perspective: str) -> list[dict]:
            role_text = {
                "product": "产品验收可裁定，PRD 与 Figma 无阻塞歧义。",
                "qa": "主链路、边界、异常、状态组合覆盖完整，无漏测。",
                "testability": "执行通道、测试数据、断言可观察性和自动化环境满足配置。",
                "red_team": "历史测试用例、未知枚举、空值、amount 金额、状态和降级风险已审查。",
            }[perspective]
            return [
                {
                    "question_id": q["id"],
                    "verdict": "pass",
                    "rationale": f"selftest mock perspective answer: {role_text}",
                    "knowledge_ref": "功能模块清单.md",
                }
                for q in brief["perspectives"][perspective]["questions"]
            ]

        def _findings(perspective: str, slug: str | None = None) -> None:
            write_json(
                artifacts / f"case-review-findings-{slug or perspective}.json",
                {
                    "version": "1.0",
                    "perspective": perspective,
                    "reviewed_at": datetime.now(timezone.utc).isoformat(),
                    "brief_ref": "case-review-perspective-brief.json",
                    "knowledge_docs_read": ["bundled/knowledge_base/产品全景/功能模块清单.md"],
                    "perspective_notes": [] if perspective == "structural" else _notes(perspective),
                    "issues": [],
                    "extra_notes": [],
                    "verdict": "pass",
                    "finding_count": 0,
                },
            )

        def _write_trace(
            skip_red_team_validate: bool = False,
            dangling_red_team_start: bool = False,
            fast_perspectives: bool = False,
            skip_product_lock: bool = False,
            include_final_validate: bool = True,
            mismatch_product_start_launch: bool = False,
            inline_launcher: bool = False,
            write_markers: bool = True,
        ) -> None:
            trace = artifacts / "case-review-orchestration-trace.jsonl"
            events = [
                {"event": "brief_built", "round_id": "selftest-round", "at": datetime.now(timezone.utc).isoformat()},
                {"event": "precheck_done", "round_id": "selftest-round", "at": datetime.now(timezone.utc).isoformat()},
                {"event": "structural_findings_written", "round_id": "selftest-round", "at": datetime.now(timezone.utc).isoformat()},
            ]
            for perspective in ("product", "qa", "testability", "red_team"):
                slug = "red-team" if perspective == "red_team" else perspective
                stage_name = f"case-review-{slug}"
                launch_id = str(uuid.uuid4())
                lock_path = artifacts / f".subagent-launch-{stage_name}.json"
                lock = {
                    "stage_name": stage_name,
                    "launch_id": launch_id,
                    "prompt_path": f"workspace/artifacts/prompts/case-review-{slug}.md",
                    "round_id": "selftest-round",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "launcher": "inline_subagent" if inline_launcher else "pipeline_runner",
                }
                if not (skip_product_lock and perspective == "product"):
                    write_json(lock_path, lock)
                findings_file = artifacts / f"case-review-findings-{slug}.json"
                if findings_file.exists():
                    base = lock_path.stat().st_mtime
                    delta = 0.03 if fast_perspectives else 6.0
                    os.utime(findings_file, (base + delta, base + delta))
                started_at = datetime.now(timezone.utc)
                completed_at = started_at + (timedelta(milliseconds=30) if fast_perspectives else timedelta(seconds=6))
                common = {
                    "perspective": perspective,
                    "prompt_path": f"workspace/artifacts/prompts/case-review-{slug}.md",
                    "findings_path": f"workspace/artifacts/case-review-findings-{slug}.json",
                    "stage_name": stage_name,
                    "launch_id": launch_id,
                    "round_id": "selftest-round",
                    "launch_lock_path": str(lock_path),
                }
                started_common = dict(common)
                if mismatch_product_start_launch and perspective == "product":
                    started_common["launch_id"] = str(uuid.uuid4())
                events.append({"event": "perspective_task_started", "at": started_at.isoformat(), **started_common})
                if dangling_red_team_start and perspective == "red_team":
                    events.append({"event": "perspective_task_started", "at": datetime.now(timezone.utc).isoformat(), **common})
                events.append(
                    {
                        "event": "perspective_task_completed",
                        "at": completed_at.isoformat(),
                        "agent_id_unavailable_reason": "selftest",
                        "summary": "selftest perspective completed",
                        **common,
                    }
                )
                if not (skip_red_team_validate and perspective == "red_team"):
                    events.append(
                        {
                            "event": "perspective_validate_passed",
                            "at": (completed_at + timedelta(milliseconds=100)).isoformat(),
                            "validate_command": (
                                "python3 scripts/validate-artifacts.py --stage "
                                f"case-review-perspective --perspective {perspective}"
                            ),
                            "validate_result": "pass",
                            **common,
                        }
                    )
            events.append({"event": "merge_done", "round_id": "selftest-round", "at": datetime.now(timezone.utc).isoformat()})
            if include_final_validate:
                events.append({"event": "final_validate_passed", "round_id": "selftest-round", "at": datetime.now(timezone.utc).isoformat()})
            trace.write_text(
                "\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\n",
                encoding="utf-8",
            )
            meta = {
                "version": "1.0",
                "review": {"case_review_round_id": "selftest-round"},
                "stages": {},
            }
            write_json(artifacts / "00-meta.json", meta)
            for marker in artifacts.glob(".stage-done-case-review*.json"):
                marker.unlink(missing_ok=True)
            if write_markers:
                for perspective in ("product", "qa", "testability", "red_team"):
                    slug = "red-team" if perspective == "red_team" else perspective
                    write_json(
                        artifacts / f".stage-done-case-review-{slug}.json",
                        {"stage": f"case-review-{slug}", "status": "done", "round_id": "selftest-round"},
                    )
                write_json(
                    artifacts / ".stage-done-case-review-merge.json",
                    {"stage": "case-review-merge", "status": "done", "round_id": "selftest-round"},
                )

        for perspective, slug in (
            ("structural", None),
            ("product", None),
            ("qa", None),
            ("testability", None),
            ("red_team", "red-team"),
        ):
            _findings(perspective, slug)

        with contextlib.redirect_stdout(io.StringIO()):
            assert validate.validate_stage("case-review-perspective", "red_team"), "red_team mapping must validate"
        report = merge_mod.build_report(
            brief,
            {
                "structural": json.loads((artifacts / "case-review-findings-structural.json").read_text(encoding="utf-8")),
                "product": json.loads((artifacts / "case-review-findings-product.json").read_text(encoding="utf-8")),
                "qa": json.loads((artifacts / "case-review-findings-qa.json").read_text(encoding="utf-8")),
                "testability": json.loads((artifacts / "case-review-findings-testability.json").read_text(encoding="utf-8")),
                "red_team": json.loads((artifacts / "case-review-findings-red-team.json").read_text(encoding="utf-8")),
            },
        )
        write_json(artifacts / "03-review-report.json", report)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review"), "missing trace must fail final case-review"
        _write_trace(skip_red_team_validate=True)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review"), "partial trace must fail final case-review"
        _write_trace(dangling_red_team_start=True)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review"), "dangling trace retry must fail final case-review"
        _write_trace(fast_perspectives=True)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review"), "too-fast perspective trace must fail final case-review"
        _write_trace(skip_product_lock=True)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review"), "missing launch lock must fail final case-review"
        _write_trace(mismatch_product_start_launch=True)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review"), "launch_id mismatch between started/completed must fail"
        _write_trace(include_final_validate=False)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review"), "missing final validate trace must fail final case-review"
        _write_trace(inline_launcher=True)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review"), "inline launch locks must fail final case-review"
        _write_trace(write_markers=False)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review"), "missing stage done markers must fail final case-review"
        _write_trace()
        with contextlib.redirect_stdout(io.StringIO()):
            assert validate.validate_stage("case-review"), "clean pass review should pass"

        bad = json.loads((artifacts / "case-review-findings-product.json").read_text(encoding="utf-8"))
        bad["brief_ref"] = "case-review-perspective-berspective-brief.json"
        write_json(artifacts / "case-review-findings-product.json", bad)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review-perspective", "product"), "brief_ref typo must fail"
        bad["brief_ref"] = "case-review-perspective-brief.json"
        bad["perspective_notes"][0]["knowledge_ref"] = "unknown-history.md"
        write_json(artifacts / "case-review-findings-product.json", bad)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review-perspective", "product"), "unknown knowledge_ref must fail"
        _findings("product")

        bad_red = json.loads((artifacts / "case-review-findings-red-team.json").read_text(encoding="utf-8"))
        bad_red["extra_notes"] = [
            {
                "note": "PRD 明确要求未知 type 且 amount>0 展示原价格，但当前未覆盖。",
                "rationale": "PRD BFF 原文要求",
            }
        ]
        write_json(artifacts / "case-review-findings-red-team.json", bad_red)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review-perspective", "red_team"), "explicit uncovered PRD branch must be an issue"
        _findings("red_team", "red-team")

        bad_red = json.loads((artifacts / "case-review-findings-red-team.json").read_text(encoding="utf-8"))
        bad_red["issues"] = [
            {
                "id": "CR-001",
                "severity": "minor",
                "category": "coverage",
                "root_cause": "qa_undercoverage",
                "audience": "internal",
                "retry_target": "prd-analyze",
                "description": "PRD 明确分支未覆盖。",
                "evidence": {"prd_section": "PRD §1"},
                "suggestion": "补充场景。",
            }
        ]
        bad_red["verdict"] = "fail"
        bad_red["finding_count"] = 1
        write_json(artifacts / "case-review-findings-red-team.json", bad_red)
        with contextlib.redirect_stdout(io.StringIO()):
            assert not validate.validate_stage("case-review-perspective", "red_team"), "issues require a failing perspective note"
        _findings("red_team", "red-team")

        write_json(
            artifacts / "04-execution-result.json",
            {
                "version": "1.0",
                "executed_at": datetime.now(timezone.utc).isoformat(),
                "environment": {},
                "summary": {"total": 1, "pass": 1, "fail": 0, "skip": 0, "block": 0},
                "cases": [{"case_id": "TC-001", "title": "x", "status": "fail"}],
                "has_pass": True,
                "has_fail": False,
            },
        )
        with contextlib.redirect_stdout(io.StringIO()):
            test_execute_ok = validate.validate_stage("test-execute")
        assert not test_execute_ok, "execution summary mismatch must fail"


def main() -> int:
    # 避免真实流水线 --force 残留导致 artifact_ready 恒为 False
    active_py = ROOT / "scripts" / "pipeline_active.py"
    if active_py.exists():
        subprocess.run(
            [sys.executable, str(active_py), "clear"],
            cwd=str(ROOT),
            capture_output=True,
            check=False,
        )
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
