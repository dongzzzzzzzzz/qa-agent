#!/usr/bin/env python3
"""
QA pipeline orchestrator — shared by Cursor / Codex / Claude Code entrypoints.

Default: dry-run (writes stage prompts under workspace/artifacts/prompts/).
Use --execute to run validation gates after you (or an agent) produce artifacts.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml
except ImportError:
    print("Install dependencies: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

ARTIFACTS = ROOT / "workspace" / "artifacts"
PROMPTS_DIR = ARTIFACTS / "prompts"
INPUTS = ROOT / "workspace" / "inputs"
VALIDATE = ROOT / "scripts" / "validate-artifacts.py"
LAUNCHER = ROOT / "scripts" / "launch_subagent.py"
PIPELINE_ACTIVE = ROOT / "scripts" / "pipeline_active.py"
AWAITING_SUBAGENT = ARTIFACTS / ".qa-pipeline-awaiting-subagent"

LINEAR_STAGES = ["prd-analyze", "prd-gate", "case-generate", "case-review", "test-execute"]


def _set_awaiting_subagent(stage_id: str) -> None:
    """Cursor Hook 仅在存在此标记且 subagentStop 时注入下一阶段 followup。"""
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    AWAITING_SUBAGENT.write_text(stage_id + "\n", encoding="utf-8")


def _clear_awaiting_subagent() -> None:
    AWAITING_SUBAGENT.unlink(missing_ok=True)

PRD_GATE_SUBSTAGES = [
    "prd-gate-product-review",
    "prd-gate-dev-review",
    "prd-gate-qa-review",
    "prd-gate-red-team",
    "prd-gate",
]

PRD_GATE_FINDINGS = {
    "prd-gate-product-review": ARTIFACTS / "gate-findings-product.json",
    "prd-gate-dev-review": ARTIFACTS / "gate-findings-dev.json",
    "prd-gate-qa-review": ARTIFACTS / "gate-findings-qa.json",
    "prd-gate-red-team": ARTIFACTS / "gate-findings-red-team.json",
}


def _pipeline_active_touch(launch_mode: str = "ide", force: bool = False) -> None:
    cmd = [sys.executable, str(PIPELINE_ACTIVE), "touch", launch_mode]
    if force:
        cmd.append("1")
    subprocess.run(cmd, cwd=str(ROOT), check=False)


def _pipeline_active_clear() -> None:
    subprocess.run(
        [sys.executable, str(PIPELINE_ACTIVE), "clear"],
        cwd=str(ROOT),
        check=False,
    )


def _pipeline_reject_mark_notified() -> None:
    subprocess.run(
        [sys.executable, str(PIPELINE_ACTIVE), "mark-reject-notified"],
        cwd=str(ROOT),
        check=False,
    )
POST_BRANCHES = ["script-convert"]


def load_pipeline() -> dict:
    with (ROOT / "pipeline.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_meta() -> dict:
    meta_path = ARTIFACTS / "00-meta.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    subprocess.run([sys.executable, str(VALIDATE), "--init-meta"], check=True)
    return json.loads(meta_path.read_text(encoding="utf-8"))


def save_meta(meta: dict) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "00-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def stage_by_id(pipeline: dict, stage_id: str) -> dict | None:
    for s in pipeline.get("stages", []):
        if s.get("id") == stage_id:
            return s
        if s.get("id") == "post-process":
            for b in s.get("branches", []):
                if b.get("id") == stage_id:
                    return b
    return None


def linear_stage_ids(pipeline: dict) -> list[str]:
    ids = [
        s.get("id")
        for s in pipeline.get("stages", [])
        if s.get("id") and s.get("id") != "post-process"
    ]
    return ids or LINEAR_STAGES.copy()


def post_branch_ids(pipeline: dict) -> list[str]:
    for stage in pipeline.get("stages", []):
        if stage.get("id") == "post-process":
            ids = [b.get("id") for b in stage.get("branches", []) if b.get("id")]
            return ids or POST_BRANCHES.copy()
    return POST_BRANCHES.copy()


def read_agent_role(agent_name: str) -> str:
    path = ROOT / "agents" / f"{agent_name}.md"
    if not path.exists():
        # agent field uses hyphenated names mapping to files
        mapping = {
            "prd-gatekeeper": "prd-gatekeeper.md",
            "gate-product-reviewer": "gate-product-reviewer.md",
            "gate-dev-reviewer": "gate-dev-reviewer.md",
            "gate-qa-reviewer": "gate-qa-reviewer.md",
            "test-point-red-team": "test-point-red-team.md",
            "prd-analyzer": "prd-analyzer.md",
            "case-generator": "case-generator.md",
            "case-reviewer": "case-reviewer.md",
            "test-executor": "test-executor.md",
            "script-converter": "script-converter.md",
            "qa-orchestrator": "qa-orchestrator.md",
        }
        path = ROOT / "agents" / mapping.get(agent_name, f"{agent_name}.md")
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_prompt(platform: str, stage: dict, pipeline: dict, meta: dict) -> str:
    stage_id = stage["id"]
    skill = stage.get("skill", stage_id)
    agent = stage.get("agent", "")
    role = read_agent_role(agent)
    inputs = stage.get("inputs", [])
    outputs = []
    if stage.get("output"):
        outputs.append(stage["output"])
    outputs.extend(stage.get("outputs") or [])
    contract = stage.get("contract", "")

    lines = [
        f"# QA Pipeline — {stage_id}",
        f"**Platform**: {platform}",
        f"**Skill**: {skill}",
        f"**Run ID**: {meta.get('run_id', 'unknown')}",
        "",
        "## Agent role",
        role,
        "",
        "## Task",
        f"运行 QA 流水线阶段: **{stage_id}**",
        f"加载并执行 Skill: **{skill}**",
        "",
        "## Inputs",
    ]
    for inp in inputs:
        p = ROOT / inp
        optional = inp.endswith("env.json")
        if p.exists():
            status = "exists"
        elif optional:
            status = "optional, missing"
        else:
            status = "MISSING — create before run"
        lines.append(f"- `{inp}` ({status})")

    lines.extend([
        "",
        "## Output",
    ])
    if outputs:
        for out in outputs:
            lines.append(f"- Write to: `{out}`")
    else:
        lines.append("- No explicit output path declared; follow the stage Skill output section.")
    if stage.get("output_notes"):
        lines.append(f"- Notes: {stage['output_notes']}")
    if contract:
        lines.append(f"- Contract: `{contract}`")
    lines.extend([
        "",
        "## Rules",
        "- 若输出不符合契约，只修复输出，不要进入下一阶段。",
        "- 完成后运行:",
        f"  python3 scripts/validate-artifacts.py --stage {stage_id}"
        + (" --finalize" if stage_id == "prd-analyze" else ""),
        f"  python3 scripts/validate-artifacts.py --mark-done {stage_id}"
        + (" --extra '{\"verdict\":\"pass\"}'" if stage_id == "case-review" else ""),
        "",
    ])
    if stage_id == "case-generate" and meta.get("review", {}).get("retry_count", 0) > 0:
        hints_path = ARTIFACTS / "03-review-report.json"
        if hints_path.exists():
            report = json.loads(hints_path.read_text(encoding="utf-8"))
            lines.append("## Revision hints (from failed review)")
            for h in report.get("revision_hints", []):
                lines.append(f"- {h}")
            lines.append("")

    return "\n".join(lines)


def write_prompt(platform: str, stage: dict, pipeline: dict, meta: dict) -> Path:
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    if stage["id"] == "prd-gate":
        gen = ROOT / "scripts" / "generate_gate_prompts.py"
        subprocess.run([sys.executable, str(gen)], cwd=str(ROOT), check=False)
        return PROMPTS_DIR / "prd-gate.md"
    content = build_prompt(platform, stage, pipeline, meta)
    out = PROMPTS_DIR / f"{stage['id']}.md"
    out.write_text(content, encoding="utf-8")
    return out


def run_prd_gate_scripts() -> bool:
    scripts = Path(__file__).resolve().parent
    steps = [
        [sys.executable, str(scripts / "analyze_gate_prerequisites.py")],
        [sys.executable, str(scripts / "validate_obligation_coverage.py")],
        [sys.executable, str(scripts / "slice_gate_review_inputs.py")],
        [sys.executable, str(scripts / "generate_gate_prompts.py")],
    ]
    for cmd in steps:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        if r.stdout:
            print(r.stdout, end="")
        if r.returncode != 0:
            if r.stderr:
                print(r.stderr, file=sys.stderr)
            return False
    return True


def prd_gate_substage_ready(sub_id: str) -> bool:
    if sub_id == "prd-gate":
        return (ARTIFACTS / "00-prd-gate-report.json").exists()
    path = PRD_GATE_FINDINGS.get(sub_id)
    return path.exists() if path else False


def next_prd_gate_substage() -> str:
    for sub_id in PRD_GATE_SUBSTAGES:
        if not prd_gate_substage_ready(sub_id):
            return sub_id
    return "prd-gate"


def run_prd_gate_compound(
    platform: str,
    pipeline: dict,
    meta: dict,
    auto: bool,
) -> bool:
    """Run gate scripts then sub-reviews (auto) or only prepare prompts (dry)."""
    if not run_prd_gate_scripts():
        return False
    if not auto:
        print("[prd-gate] Prompts generated under workspace/artifacts/prompts/")
        print("[prd-gate] IDE: run sub-prompts in order, then prd-gate.md merge")
        return True
    for sub_id in PRD_GATE_SUBSTAGES:
        prompt = PROMPTS_DIR / f"{sub_id}.md"
        if not prompt.exists():
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "generate_gate_prompts.py")],
                cwd=str(ROOT),
                check=False,
            )
        if prd_gate_substage_ready(sub_id):
            print(f"[prd-gate] Skip sub-stage {sub_id} (artifact exists)")
            if not run_validate(sub_id):
                print(f"[prd-gate] Existing artifact failed validation: {sub_id}")
                return False
            continue
        print(f"\n[prd-gate] Sub-stage: {sub_id}")
        exit_code = launch_subagent_cli(platform, sub_id, prompt, pipeline)
        if exit_code != 0:
            print(f"[prd-gate] Sub-agent {sub_id} exit {exit_code}")
        if not prd_gate_substage_ready(sub_id):
            print(f"[prd-gate] Missing artifact after {sub_id}")
            return False
        if not run_validate(sub_id):
            print(f"[prd-gate] Sub-agent artifact failed validation: {sub_id}")
            return False
    return True


def run_validate(stage_id: str) -> bool:
    r = subprocess.run(
        [sys.executable, str(VALIDATE), "--stage", stage_id],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    return r.returncode == 0


def _force_rerun() -> bool:
    r = subprocess.run(
        [sys.executable, str(PIPELINE_ACTIVE), "force"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    return (r.stdout or "").strip() == "1"


def _delete_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink(missing_ok=True)


def stage_outputs(stage: dict) -> list[Path]:
    paths: list[Path] = []
    for key in ("output",):
        rel = stage.get(key)
        if rel:
            paths.append(ROOT / rel)
    for rel in stage.get("outputs") or []:
        paths.append(ROOT / rel)
    return paths


def cleanup_outputs_for_stages(pipeline: dict, stage_ids: list[str]) -> None:
    """Remove stale artifacts before a forced rerun so readiness checks can stay honest."""
    extra_by_stage = {
        "prd-analyze": [
            ARTIFACTS / "00-test-ready-blueprint.json",
            ARTIFACTS / "00-test-obligations.json",
            ARTIFACTS / "01-prd-analysis.json",
            ARTIFACTS / "test-ready-internal.md",
            ARTIFACTS / ".prd-analyze-complete.ok",
            ARTIFACTS / "figma-snapshot.json",
        ],
        "prd-gate": [
            ARTIFACTS / "00-prd-gate-report.json",
            ARTIFACTS / "prd-reject-to-product.md",
            ARTIFACTS / "prd-gate-pass-to-product.md",
            ARTIFACTS / "test-point-rework-to-qa.md",
            ARTIFACTS / "gate-findings-product.json",
            ARTIFACTS / "gate-findings-dev.json",
            ARTIFACTS / "gate-findings-qa.json",
            ARTIFACTS / "gate-findings-red-team.json",
            ARTIFACTS / ".test-point-coverage-precheck.json",
            ARTIFACTS / ".gate-slices",
        ],
        "case-generate": [ARTIFACTS / "02-test-cases.md"],
        "case-review": [ARTIFACTS / "03-review-report.json"],
        "test-execute": [
            ARTIFACTS / "04-execution-result.json",
            ARTIFACTS / "05b-bug-list.md",
            ARTIFACTS / "evidence",
        ],
        "script-convert": [ARTIFACTS / "05a-scripts"],
    }
    seen: set[Path] = set()
    for stage_id in stage_ids:
        stage = stage_by_id(pipeline, stage_id)
        candidates = []
        if stage:
            candidates.extend(stage_outputs(stage))
        candidates.extend(extra_by_stage.get(stage_id, []))
        for path in candidates:
            if path in seen:
                continue
            seen.add(path)
            if path.is_relative_to(ARTIFACTS):
                _delete_path(path)


def artifact_ready(stage_id: str) -> bool:
    if stage_id == "prd-analyze":
        return (
            (ARTIFACTS / "00-test-ready-blueprint.json").exists()
            and (ARTIFACTS / "01-prd-analysis.json").exists()
        )
    if stage_id == "prd-gate":
        return (ARTIFACTS / "00-prd-gate-report.json").exists()
    mapping = {
        "case-generate": ARTIFACTS / "02-test-cases.md",
        "case-review": ARTIFACTS / "03-review-report.json",
        "test-execute": ARTIFACTS / "04-execution-result.json",
        "script-convert": ARTIFACTS / "05a-scripts",
    }
    p = mapping.get(stage_id)
    if p is None:
        return False
    if stage_id == "script-convert":
        return p.exists() and any(p.iterdir())
    if stage_id == "test-execute":
        if not p.exists():
            return False
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("has_fail"):
            return (ARTIFACTS / "05b-bug-list.md").exists()
        return True
    return p.exists()


def prd_gate_passed() -> bool:
    path = ARTIFACTS / "00-prd-gate-report.json"
    if not path.exists():
        return False
    return json.loads(path.read_text(encoding="utf-8")).get("verdict") == "pass"


def write_prd_reject_notice() -> Path:
    from render_prd_gate_notice import write_product_markdown

    return write_product_markdown()


def _run_prd_analyze_finalize() -> bool:
    """Sync blueprint -> analysis, validate blueprint, render internal MD."""
    scripts = Path(__file__).resolve().parent
    sync = scripts / "sync_blueprint_to_analysis.py"
    r = subprocess.run([sys.executable, str(sync)], cwd=str(ROOT), capture_output=True, text=True)
    if r.stdout:
        print(r.stdout, end="")
    if r.returncode != 0:
        if r.stderr:
            print(r.stderr, file=sys.stderr)
        return False
    if not run_validate("test-ready-blueprint"):
        return False
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from render_test_ready_internal import main as render_internal
    from analyze_gate_prerequisites import write_analyze_complete_marker

    render_internal()
    write_analyze_complete_marker()
    bp = ARTIFACTS / "00-test-ready-blueprint.json"
    if bp.exists():
        print(f"[prd-analyze] Blueprint: {bp}")
    return True


def check_inputs(stage: dict) -> list[str]:
    missing = []
    for inp in stage.get("inputs", []):
        candidate = (ROOT / inp).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            missing.append(f"{inp} (outside project root)")
            continue
        if inp.startswith("workspace/inputs/"):
            try:
                candidate.relative_to(INPUTS.resolve())
            except ValueError:
                missing.append(f"{inp} (outside workspace/inputs)")
                continue
        if not candidate.exists():
            # env.json optional
            if inp.endswith("env.json"):
                continue
            missing.append(inp)
    return missing


def review_passed() -> bool:
    path = ARTIFACTS / "03-review-report.json"
    if not path.exists():
        return False
    data = json.loads(path.read_text(encoding="utf-8"))
    pipeline = load_pipeline()
    threshold = pipeline.get("review", {}).get("pass_threshold", 0.85)
    return data.get("verdict") == "pass" and data.get("coverage_score", 0) >= threshold


def execution_flags() -> tuple[bool, bool]:
    path = ARTIFACTS / "04-execution-result.json"
    if not path.exists():
        return False, False
    data = json.loads(path.read_text(encoding="utf-8"))
    if "has_pass" in data and "has_fail" in data:
        return data["has_pass"], data["has_fail"]
    cases = data.get("cases", [])
    has_pass = any(c.get("status") == "pass" for c in cases)
    has_fail = any(c.get("status") in ("fail", "block") for c in cases)
    return has_pass, has_fail


def should_run_branch(branch: dict) -> bool:
    when = branch.get("when", "")
    has_pass, has_fail = execution_flags()
    if when == "execution.has_pass":
        return has_pass
    if when == "execution.has_fail":
        return has_fail
    return True


def launch_subagent_cli(
    platform: str,
    stage_id: str,
    prompt_path: Path,
    pipeline: dict,
) -> int:
    """Invoke platform CLI to run one sub-agent."""
    auto_cfg = pipeline.get("auto", {})
    timeout = auto_cfg.get("stage_timeout_sec", 3600)
    models = auto_cfg.get("models", {}) or {}
    model = models.get(platform) or None

    cmd = [
        sys.executable,
        str(LAUNCHER),
        "--platform",
        platform,
        "--stage",
        stage_id,
        "--prompt",
        str(prompt_path),
        "--timeout",
        str(timeout),
    ]
    if model:
        cmd.extend(["--model", str(model)])

    print(f"[auto] Launching sub-agent via {platform} CLI...")
    r = subprocess.run(cmd, cwd=str(ROOT))
    return r.returncode


def finalize_stage(
    stage_id: str,
    pipeline: dict,
    meta: dict,
) -> str:
    """Validate artifact and handle review branch. Returns continue | retry_generate | abort."""
    _clear_awaiting_subagent()
    if not run_validate(stage_id):
        mark_stage(meta, stage_id, "validation_failed")
        return "abort"

    extra = None
    if stage_id == "prd-analyze":
        if not _run_prd_analyze_finalize():
            mark_stage(meta, stage_id, "validation_failed")
            return "abort"
    if stage_id == "prd-gate":
        report = json.loads((ARTIFACTS / "00-prd-gate-report.json").read_text(encoding="utf-8"))
        extra = {
            "verdict": report.get("verdict"),
            "reject_kind": report.get("reject_kind"),
        }
        notice = write_prd_reject_notice()
        if report.get("verdict") == "reject":
            rk = report.get("reject_kind") or "product"
            issues = report.get("issues") or []
            product_count = sum(
                1 for i in issues if (i.get("audience") or "product") == "product"
            )
            mark_stage(meta, stage_id, "rejected", extra)
            if rk == "internal" or product_count == 0:
                rework = ARTIFACTS / "test-point-rework-to-qa.md"
                print(f"[prd-gate] REJECT (internal) — 回 prd-analyze 补测试点/义务映射")
                if rework.exists():
                    print(f"[prd-gate] QA 说明: {rework}")
                for stale in (
                    ARTIFACTS / "00-prd-gate-report.json",
                    ARTIFACTS / "prd-reject-to-product.md",
                ):
                    stale.unlink(missing_ok=True)
                mark_stage(meta, stage_id, "rework_analyze", extra)
                return "rework_analyze"
            _pipeline_reject_mark_notified()
            _pipeline_active_clear()
            print(f"[prd-gate] REJECT ({rk}) — 流水线停止。产品 Markdown: {notice}")
            print("[prd-gate] 请将 prd-reject-to-product.md 交产品修订。")
            print("[prd-gate] 产品修订后请从 prd-analyze 重跑: --from-stage prd-analyze")
            return "prd_rejected"
        print(f"[prd-gate] PASS — 产品 Markdown: {notice}")
    if stage_id == "case-review":
        report = json.loads((ARTIFACTS / "03-review-report.json").read_text(encoding="utf-8"))
        extra = {"verdict": report.get("verdict")}
        if report.get("verdict") == "fail":
            max_retries = pipeline.get("review", {}).get("max_regenerate_retries", 2)
            retry = meta.get("review", {}).get("retry_count", 0)
            if retry < max_retries:
                meta.setdefault("review", {})["retry_count"] = retry + 1
                save_meta(meta)
                cleanup_outputs_for_stages(pipeline, ["case-generate"])
                print(f"[case-review] FAIL — retry case-generate ({retry + 1}/{max_retries})")
                return "retry_generate"
            print("[case-review] FAIL — max retries exceeded")
            print("[orchestrator] 决策: escalate_human — 请主 Agent 介入或人工修订用例")
            meta.setdefault("orchestrator", {})["last_decision"] = "escalate_human"
            save_meta(meta)
            return "abort"

    mark_stage(meta, stage_id, "done", extra)
    subprocess.run(
        [sys.executable, str(VALIDATE), "--mark-done", stage_id]
        + (["--extra", json.dumps(extra)] if extra else []),
        cwd=str(ROOT),
        check=False,
    )
    return "continue"


def mark_stage(meta: dict, stage_id: str, status: str, extra: dict | None = None) -> None:
    meta.setdefault("stages", {})[stage_id] = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        **(extra or {}),
    }
    meta["current_stage"] = stage_id
    save_meta(meta)


def compute_overall_status(meta: dict) -> str:
    statuses = [
        (stage or {}).get("status")
        for stage in (meta.get("stages") or {}).values()
        if isinstance(stage, dict)
    ]
    if any(s in ("failed", "validation_failed") for s in statuses):
        return "failed"
    if any(s in ("waiting", "waiting_ide", "waiting_ide_task", "running", "pending") for s in statuses):
        return "running"
    if any(s in ("rejected", "rework_analyze") for s in statuses):
        return "stopped"
    if statuses and all(s in ("done", "blocked") for s in statuses):
        return "completed"
    return meta.get("status") or "running"


def run_linear_stage(
    platform: str,
    stage_id: str,
    pipeline: dict,
    meta: dict,
    dry_run: bool,
    execute: bool,
    auto: bool,
    ide: bool = False,
    ide_poll_sec: int = 10,
    stage_index: int = 1,
    stage_total: int = 6,
) -> str:
    """Returns: continue | retry_generate | abort"""
    stage = stage_by_id(pipeline, stage_id)
    if not stage:
        print(f"Unknown stage: {stage_id}")
        return "abort"

    missing = check_inputs(stage)
    if missing and stage_id != "test-execute":
        print(f"[{stage_id}] Missing inputs: {missing}")
        if stage_id in ("prd-gate", "prd-analyze") and (execute or auto):
            return "abort"

    prompt_path = write_prompt(platform, stage, pipeline, meta)
    print(f"\n{'='*60}\nStage: {stage_id}\nPrompt: {prompt_path}\n{'='*60}")

    if ide:
        print_ide_stage_guide(stage_id, prompt_path, stage_index, stage_total)
        mark_stage(meta, stage_id, "waiting_ide")
        if not wait_for_artifact(stage_id, ide_poll_sec):
            mark_stage(meta, stage_id, "failed")
            return "abort"
        return finalize_stage(stage_id, pipeline, meta)

    if dry_run and not execute and not auto:
        print("(dry-run) Open the prompt above in your agent and produce the output artifact.")
        mark_stage(meta, stage_id, "pending")
        return "continue"

    if auto:
        mark_stage(meta, stage_id, "running")
        if stage_id == "prd-gate":
            if not run_prd_gate_compound(platform, pipeline, meta, auto=True):
                mark_stage(meta, stage_id, "failed")
                return "abort"
        else:
            exit_code = launch_subagent_cli(platform, stage_id, prompt_path, pipeline)
            if exit_code != 0:
                print(f"[{stage_id}] Sub-agent CLI exited with {exit_code} (checking artifacts anyway)")
        if not artifact_ready(stage_id):
            mark_stage(meta, stage_id, "failed")
            print(f"[{stage_id}] Artifact missing after sub-agent run")
            return "abort"
        return finalize_stage(stage_id, pipeline, meta)

    if not artifact_ready(stage_id):
        print(f"[{stage_id}] Waiting for artifact. Run sub-agent, then re-run with --execute")
        mark_stage(meta, stage_id, "waiting")
        return "continue"

    if execute:
        return finalize_stage(stage_id, pipeline, meta)
    return "continue"


def cursor_cli_authenticated() -> bool:
    if os.environ.get("CURSOR_API_KEY"):
        return True
    try:
        r = subprocess.run(
            ["cursor", "agent", "status"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        out = (r.stdout or "") + (r.stderr or "")
        return "logged in" in out.lower() and "not logged" not in out.lower()
    except Exception:
        return False


def check_auth(platform: str) -> bool:
    r = subprocess.run(
        [sys.executable, str(LAUNCHER), "--platform", platform, "--stage", "prd-analyze", "--check"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    if platform == "cursor" and not cursor_cli_authenticated() and not os.environ.get("CURSOR_API_KEY"):
        return False
    return r.returncode == 0


def print_ide_stage_guide(
    stage_id: str, prompt_path: Path, index: int, total: int, platform: str = "cursor"
) -> None:
    rel = prompt_path.relative_to(ROOT)
    entry = f"./orchestrators/{platform}/run-pipeline.sh"
    print(f"\n{'#'*60}")
    print(f"# IDE 子 Agent [{index}/{total}] 阶段: {stage_id}")
    print(f"{'#'*60}")
    print(f"  Prompt 文件: {prompt_path}")
    if platform == "cursor":
        print("在 Cursor 中（无需 API Key）：")
        print("  - Hook 将在本阶段子 Agent 结束后自动注入下一阶段 Task（侧栏可见）")
        print(f"  - 或手动: 请按 @{rel} 执行本阶段 QA 子 Agent 任务")
    else:
        print(f"在 {platform} IDE 中：")
        print("  1. 主 Agent 用子 Agent 执行上述 prompt（读 agents/*.md + 对应 Skill）")
        print(f"  2. 产物就绪后再次运行: {entry}")
        print("  3. 勿使用 --auto，除非用户明确要求 CLI")
    print(f"{'#'*60}\n")


def wait_for_artifact(stage_id: str, poll_sec: int = 10, timeout_sec: int = 7200) -> bool:
    import time

    deadline = time.time() + timeout_sec
    print(f"[ide] 等待产物出现（每 {poll_sec}s 检测，超时 {timeout_sec}s）...")
    while time.time() < deadline:
        if artifact_ready(stage_id):
            print(f"[ide] 检测到产物: {stage_id}")
            return True
        time.sleep(poll_sec)
    print(f"[ide] 超时: 未检测到 {stage_id} 产物", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="QA Agent pipeline runner")
    parser.add_argument("--platform", choices=["cursor", "codex", "claude-code"], default="codex")
    parser.add_argument("--dry-run", action="store_true", help="Only generate prompts (default without --auto/--execute)")
    parser.add_argument("--execute", action="store_true", help="Validate existing artifacts and advance gates")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically launch sub-agents via platform CLI for each stage, then validate",
    )
    parser.add_argument(
        "--ide",
        action="store_true",
        help="IDE 模式：生成 prompt 并轮询产物，用 Composer/Task 执行，无需 API Key",
    )
    parser.add_argument(
        "--ide-chain",
        action="store_true",
        help="IDE 链式模式（默认）：生成 prompt，由 Hook 通过 Task followup 推进，子 Agent 在侧栏可见",
    )
    parser.add_argument("--ide-poll-sec", type=int, default=10, help="IDE 模式轮询间隔秒")
    parser.add_argument("--check-auth", action="store_true", help="Check platform CLI auth and exit")
    parser.add_argument("--from-stage", dest="from_stage", default="prd-analyze")
    parser.add_argument("--to-stage", dest="to_stage", default=None)
    parser.add_argument(
        "--force",
        action="store_true",
        help="即使产物已存在也重新跑各阶段子 Agent",
    )
    parser.add_argument(
        "--no-force",
        action="store_true",
        help="从 prd-analyze 启动时也不强制重跑（仅校验/推进已有产物）",
    )
    args = parser.parse_args()

    if args.check_auth:
        return 0 if check_auth(args.platform) else 1

    # Default mode: dry-run unless --auto / --ide-chain / --ide / --execute
    auto = args.auto
    ide_chain = getattr(args, "ide_chain", False)
    ide = args.ide
    execute = args.execute
    dry_run = not auto and not execute and not ide and not ide_chain
    if args.dry_run:
        dry_run = True
        auto = False
        ide = False
        ide_chain = False
        execute = False

    pipeline = load_pipeline()
    meta = load_meta()
    post_branches = post_branch_ids(pipeline)
    meta["platform"] = args.platform
    if auto:
        mode_label = "auto"
    elif ide_chain:
        mode_label = "ide-chain"
    elif ide:
        mode_label = "ide"
    elif execute:
        mode_label = "execute"
    else:
        mode_label = "dry_run"
    meta["mode"] = mode_label
    save_meta(meta)

    stages_to_run = linear_stage_ids(pipeline)
    if args.from_stage in stages_to_run:
        stages_to_run = stages_to_run[stages_to_run.index(args.from_stage) :]
    if args.to_stage and args.to_stage in stages_to_run:
        stages_to_run = stages_to_run[: stages_to_run.index(args.to_stage) + 1]

    explicit_from_stage = any(
        a == "--from-stage" or a.startswith("--from-stage=") for a in sys.argv[1:]
    )
    current_stage = meta.get("current_stage")
    current_status = (meta.get("stages", {}).get(current_stage, {}) or {}).get("status")
    resuming_waiting_ide = (
        mode_label == "ide-chain"
        and not explicit_from_stage
        and current_status in ("waiting_ide_task", "waiting_ide", "waiting")
    )
    force = (
        args.force
        or (args.from_stage == "prd-analyze" and not resuming_waiting_ide)
        or (explicit_from_stage and args.from_stage == "prd-analyze")
    ) and not args.no_force
    if auto:
        _pipeline_active_touch("cli", force=force)
    elif ide_chain or ide:
        _pipeline_active_touch("ide", force=force)
    if force:
        print("[pipeline] --force：清理本次范围内旧产物后重新拉起子 Agent")
        cleanup_outputs_for_stages(pipeline, stages_to_run + post_branches)

    if auto:
        print(f"=== QA Pipeline AUTO mode ({args.platform}) ===")
        if args.platform == "cursor" and not cursor_cli_authenticated():
            print("ERROR: Cursor CLI 未登录，--auto 无法使用 IDE 账号密码。", file=sys.stderr)
            print("  方案 A（推荐，无需 API Key）: cursor agent login", file=sys.stderr)
            print("  方案 B: Cursor 后台生成 API Key → export CURSOR_API_KEY=...", file=sys.stderr)
            print("  方案 C: ./orchestrators/cursor/run-pipeline.sh --ide", file=sys.stderr)
            return 1
        if args.platform != "cursor" and not check_auth(args.platform):
            print("ERROR: 平台 CLI 未就绪", file=sys.stderr)
            return 1

    if ide_chain:
        if args.platform == "cursor":
            print("=== QA Pipeline IDE-CHAIN mode（Cursor：Task 子 Agent 侧栏可见）===")
            print("Hook 将在 stop/subagentStop 时注入下一阶段 Task followup。\n")
        else:
            print(f"=== QA Pipeline IDE-CHAIN mode（{args.platform}：主 Agent 拉子 Agent）===")
            print("每阶段完成后请再次运行 run-pipeline.sh（无 --auto）。\n")
    if ide:
        print("=== QA Pipeline IDE mode（使用 IDE 登录，无需 API Key）===")
        print("请在每个阶段按提示在 Composer 中执行，编排器将轮询产物并自动推进。\n")

    # Check base inputs
    for key in ("prd", "figma"):
        rel = pipeline.get("inputs", {}).get(key, "")
        if rel and not (ROOT / rel).exists():
            print(f"WARNING: missing input {rel}")

    i = 0
    while i < len(stages_to_run):
        stage_id = stages_to_run[i]

        if stage_id == "prd-gate":
            import sys as _sys

            _scripts = Path(__file__).resolve().parent
            if str(_scripts) not in _sys.path:
                _sys.path.insert(0, str(_scripts))
            from analyze_gate_prerequisites import analyze_validation_errors

            if not artifact_ready("prd-analyze"):
                print("[prd-gate] 请先完成 prd-analyze（蓝图 + 01-prd-analysis.json）")
                return 1
            pre_errs = analyze_validation_errors()
            if pre_errs:
                print("[prd-gate] 禁止 gate：prd-analyze 未通过全文分析校验，不能出具打回/通过结论")
                for e in pre_errs[:8]:
                    print(f"  - {e}")
                if len(pre_errs) > 8:
                    print(f"  ... 共 {len(pre_errs)} 项")
                print("[prd-gate] 请自动/重跑 prd-analyzer 子 Agent，直至 validate-artifacts --stage prd-analyze 通过")
                return 1
            if dry_run and not execute and not auto:
                st = stage_by_id(pipeline, stage_id)
                if st:
                    write_prompt(args.platform, st, pipeline, meta)
                    if stage_id == "prd-gate":
                        run_prd_gate_scripts()
                i += 1
                continue

        if stage_id in ("case-generate", "case-review") and not prd_gate_passed():
            if not (ARTIFACTS / "00-prd-gate-report.json").exists():
                print(f"[{stage_id}] Gate: 请先完成 prd-gate")
            else:
                print(f"[{stage_id}] Gate: prd-gate verdict 非 pass，不可继续")
            if dry_run and not execute and not auto:
                st = stage_by_id(pipeline, stage_id)
                if st:
                    write_prompt(args.platform, st, pipeline, meta)
                i += 1
                continue
            return 1

        if stage_id == "test-execute" and not review_passed():
            if not (ARTIFACTS / "03-review-report.json").exists():
                print("[test-execute] Gate: review report missing. Complete case-review first.")
            else:
                print("[test-execute] Gate: review verdict not pass. Fix cases or re-run review.")
            if dry_run and not execute and not auto:
                st = stage_by_id(pipeline, stage_id)
                if st:
                    write_prompt(args.platform, st, pipeline, meta)
                    mark_stage(meta, stage_id, "pending")
                i += 1
                continue
            return 1

        if ide_chain:
            stage = stage_by_id(pipeline, stage_id)
            if not stage:
                return 1
            missing = check_inputs(stage)
            if missing and stage_id != "test-execute":
                print(f"[{stage_id}] Missing inputs: {missing}")
                return 1
            if stage_id == "prd-gate":
                if not run_prd_gate_scripts():
                    mark_stage(meta, stage_id, "failed")
                    return 1
                if artifact_ready(stage_id):
                    result = finalize_stage(stage_id, pipeline, meta)
                    meta = load_meta()
                    if result == "prd_rejected":
                        return 1
                    if result == "rework_analyze":
                        if "prd-analyze" in stages_to_run:
                            i = stages_to_run.index("prd-analyze")
                            continue
                        return 1
                    if result == "abort":
                        return 1
                    i += 1
                    continue
                sub_id = next_prd_gate_substage()
                prompt_path = PROMPTS_DIR / f"{sub_id}.md"
                print_ide_stage_guide(
                    sub_id, prompt_path, i + 1, len(stages_to_run), platform=args.platform
                )
                mark_stage(meta, sub_id, "waiting_ide_task")
                if args.platform == "cursor":
                    _set_awaiting_subagent(sub_id)
                    print(
                        f"[ide-chain] 等待 Task 子 Agent 完成 {sub_id}。"
                        " 子 Agent 结束后 Hook（subagentStop）自动推进。\n"
                    )
                else:
                    print(
                        f"[ide-chain] 等待子 Agent 完成 {sub_id}。"
                        f" 完成后主 Agent 请再运行: ./orchestrators/{args.platform}/run-pipeline.sh\n"
                    )
                return 0
            prompt_path = write_prompt(args.platform, stage, pipeline, meta)
            if artifact_ready(stage_id):
                result = finalize_stage(stage_id, pipeline, meta)
                meta = load_meta()
                if result == "prd_rejected":
                    return 1
                if result == "rework_analyze":
                    if "prd-analyze" in stages_to_run:
                        i = stages_to_run.index("prd-analyze")
                        continue
                    return 1
                if result == "abort":
                    return 1
                i += 1
                continue
            print_ide_stage_guide(
                stage_id, prompt_path, i + 1, len(stages_to_run), platform=args.platform
            )
            mark_stage(meta, stage_id, "waiting_ide_task")
            if args.platform == "cursor":
                _set_awaiting_subagent(stage_id)
                print(
                    f"[ide-chain] 等待 Task 子 Agent 完成 {stage_id}。"
                    " 请在本会话启动 Task；子 Agent 结束后 Hook（subagentStop）自动推进。\n"
                )
            else:
                print(
                    f"[ide-chain] 等待子 Agent 完成 {stage_id}。"
                    f" 完成后主 Agent 请再运行: ./orchestrators/{args.platform}/run-pipeline.sh\n"
                )
            return 0

        result = run_linear_stage(
            args.platform,
            stage_id,
            pipeline,
            meta,
            dry_run,
            execute,
            auto,
            ide=ide,
            ide_poll_sec=args.ide_poll_sec,
            stage_index=i + 1,
            stage_total=len(stages_to_run),
        )
        meta = load_meta()

        if result == "prd_rejected":
            return 1
        if result == "rework_analyze":
            if "prd-analyze" in stages_to_run:
                i = stages_to_run.index("prd-analyze")
                print("[pipeline] prd-gate internal reject → 重跑 prd-analyze")
                continue
            return 1
        if result == "abort":
            return 1
        if result == "retry_generate":
            if "case-generate" in stages_to_run:
                i = stages_to_run.index("case-generate")
                continue
        i += 1

    # Post-process
    if "test-execute" in stages_to_run or args.from_stage in post_branches:
        post = stage_by_id(pipeline, "post-process")
        if post:
            has_pass, has_fail = execution_flags()
            if not (ARTIFACTS / "04-execution-result.json").exists() and (execute or auto):
                print("[post-process] Skipped: no execution result")
            else:
                for branch in post.get("branches", []):
                    bid = branch["id"]
                    if args.from_stage in post_branches and bid != args.from_stage:
                        if args.to_stage is None:
                            continue
                    if not should_run_branch(branch) and not auto:
                        print(f"[{bid}] Skipped (condition {branch.get('when')} not met)")
                        continue
                    if not should_run_branch(branch):
                        print(f"[{bid}] Skipped (condition {branch.get('when')} not met)")
                        continue
                    run_linear_stage(
                        args.platform,
                        bid,
                        pipeline,
                        meta,
                        dry_run,
                        execute,
                        auto,
                        ide=ide,
                        ide_poll_sec=args.ide_poll_sec,
                    )
                    meta = load_meta()

    if dry_run and not (execute or auto or ide or ide_chain):
        meta["status"] = "dry_run"
    else:
        meta["status"] = compute_overall_status(meta)
    meta["completed_at"] = datetime.now(timezone.utc).isoformat()
    save_meta(meta)
    if auto or ide or ide_chain:
        _pipeline_active_clear()
    print("\nPipeline runner finished.")
    print(f"Meta: {ARTIFACTS / '00-meta.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
