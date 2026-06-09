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
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from load_project_config import load_project_config  # noqa: E402

try:
    import yaml
except ImportError:
    print("Install dependencies: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

ARTIFACTS = Path(os.environ.get("QA_WORKSPACE", str(ROOT / "workspace" / "artifacts")))
PROMPTS_DIR = ARTIFACTS / "prompts"
INPUTS = Path(os.environ.get("QA_INPUTS", str(ROOT / "workspace" / "inputs")))
VALIDATE = ROOT / "scripts" / "validate-artifacts.py"
LAUNCHER = ROOT / "scripts" / "launch_subagent.py"
PIPELINE_ACTIVE = ROOT / "scripts" / "pipeline_active.py"
CASE_REVIEW_PERSPECTIVES = ("product", "qa", "testability", "red_team")

# ---------------------------------------------------------------------------
# Workspace path helpers — updated at startup by _init_workspace()
# ---------------------------------------------------------------------------

def _compute_workspace(project: str | None) -> tuple[Path, Path]:
    """Return (artifacts_dir, inputs_dir) for the given project slug."""
    if os.environ.get("QA_WORKSPACE"):
        arts = Path(os.environ["QA_WORKSPACE"])
        ins = Path(os.environ.get("QA_INPUTS", str(ROOT / "workspace" / "inputs")))
        return arts, ins

    if project:
        project_dir = ROOT / "workspace" / "projects" / project
        ins = project_dir / "inputs"
        current = project_dir / "current"
        if current.exists() or current.is_symlink():
            return current, ins
        # No run yet — caller will bootstrap
        return current, ins

    return ROOT / "workspace" / "artifacts", ROOT / "workspace" / "inputs"


def _create_run(project: str) -> tuple[Path, str]:
    """
    Create a new timestamped run directory under workspace/projects/<project>/runs/
    and update the `current` symlink.  Returns (artifacts_dir, run_id).
    """
    import time as _time
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    project_dir = ROOT / "workspace" / "projects" / project
    run_dir = project_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Copy inputs from legacy workspace/inputs if project inputs don't exist yet
    project_inputs = project_dir / "inputs"
    if not project_inputs.exists():
        legacy_inputs = ROOT / "workspace" / "inputs"
        if legacy_inputs.exists():
            shutil.copytree(str(legacy_inputs), str(project_inputs))
        else:
            project_inputs.mkdir(parents=True, exist_ok=True)

    # Update current symlink
    current_link = project_dir / "current"
    if current_link.is_symlink():
        current_link.unlink()
    elif current_link.exists():
        shutil.rmtree(str(current_link))

    # Use relative symlink: current -> runs/<run_id>
    current_link.symlink_to(Path("runs") / run_id)

    return run_dir, run_id

CASE_REVIEW_STAGE_TO_PERSPECTIVE = {
    "case-review-product": "product",
    "case-review-qa": "qa",
    "case-review-testability": "testability",
    "case-review-red-team": "red_team",
}
CASE_REVIEW_INTERNAL_STAGES = [
    "case-review-prepare",
    "case-review-product",
    "case-review-qa",
    "case-review-testability",
    "case-review-red-team",
    "case-review-merge",
]
LINEAR_STAGES = ["prd-analyze", "case-generate", "case-review", "test-execute"]

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
    if stage_id == "case-review-prepare":
        return {
            "id": stage_id,
            "agent": "case-reviewer",
            "skill": "case-review",
            "output": "workspace/artifacts/.case-review-prepare.done",
            "inputs": [
                "workspace/inputs/config.yaml",
                "workspace/inputs/prd.md",
                "workspace/inputs/figma.url",
                "workspace/artifacts/00-test-blueprint.json",
                "workspace/artifacts/02-test-cases.md",
                "workspace/artifacts/00-knowledge-context.json",
            ],
        }
    if stage_id in CASE_REVIEW_STAGE_TO_PERSPECTIVE:
        perspective = CASE_REVIEW_STAGE_TO_PERSPECTIVE[stage_id]
        slug = "red-team" if perspective == "red_team" else perspective
        return {
            "id": stage_id,
            "agent": f"case-review-{slug}",
            "skill": "case-review-perspective",
            "output": f"workspace/artifacts/case-review-findings-{slug}.json",
            "inputs": [
                "workspace/artifacts/case-review-perspective-brief.json",
                "workspace/artifacts/00-test-blueprint.json",
                "workspace/artifacts/02-test-cases.md",
                "workspace/artifacts/00-knowledge-context.json",
            ],
        }
    if stage_id == "case-review-merge":
        return {
            "id": stage_id,
            "agent": "case-reviewer",
            "skill": "case-review",
            "contract": "contracts/review-report.schema.json",
            "output": "workspace/artifacts/03-review-report.json",
            "inputs": [
                "workspace/artifacts/case-review-findings-structural.json",
                "workspace/artifacts/case-review-findings-product.json",
                "workspace/artifacts/case-review-findings-qa.json",
                "workspace/artifacts/case-review-findings-testability.json",
                "workspace/artifacts/case-review-findings-red-team.json",
            ],
        }
    for s in pipeline.get("stages", []):
        if s.get("id") == stage_id:
            return s
        if s.get("id") == "post-process":
            for b in s.get("branches", []):
                if b.get("id") == stage_id:
                    return b
    return None


def expand_stage_ids(stage_ids: list[str]) -> list[str]:
    out: list[str] = []
    for stage_id in stage_ids:
        if stage_id == "case-review":
            out.extend(CASE_REVIEW_INTERNAL_STAGES)
        else:
            out.append(stage_id)
    return out


def visible_stage_id(stage_id: str) -> str:
    return "case-review" if stage_id in CASE_REVIEW_INTERNAL_STAGES else stage_id


def perspective_slug(perspective: str) -> str:
    return "red-team" if perspective == "red_team" else perspective


def stage_done_marker(stage_id: str) -> Path:
    return ARTIFACTS / f".stage-done-{stage_id}.json"


def _current_round_id(meta: dict | None = None) -> str:
    meta = meta or load_meta()
    review = meta.setdefault("review", {})
    round_id = review.get("case_review_round_id")
    if not round_id:
        round_id = f"cr-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        review["case_review_round_id"] = round_id
        save_meta(meta)
    return str(round_id)


def _reset_case_review_round(meta: dict, reason: str) -> str:
    review = meta.setdefault("review", {})
    round_id = f"cr-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    review["case_review_round_id"] = round_id
    review["case_review_round_started_at"] = datetime.now(timezone.utc).isoformat()
    review["case_review_round_reason"] = reason
    save_meta(meta)
    return round_id


def _remap_artifacts_path(path_str: str) -> str:
    """Remap a legacy workspace/artifacts/* path to the current ARTIFACTS dir."""
    if path_str.startswith("workspace/artifacts/"):
        rel = path_str[len("workspace/artifacts/"):]
        try:
            return str((ARTIFACTS / rel).relative_to(ROOT))
        except ValueError:
            return str(ARTIFACTS / rel)
    return path_str


def _resolve_workspace_path(path_str: str) -> Path:
    """Resolve legacy workspace paths against the active project/run directories."""
    if path_str.startswith("workspace/artifacts/"):
        return ARTIFACTS / path_str[len("workspace/artifacts/"):]
    if path_str.startswith("workspace/inputs/"):
        return INPUTS / path_str[len("workspace/inputs/"):]
    return ROOT / path_str


def read_agent_role(agent_name: str) -> str:
    path = ROOT / "agents" / f"{agent_name}.md"
    if not path.exists():
        # agent field uses hyphenated names mapping to files
        mapping = {
            "prd-analyzer": "prd-analyzer.md",
            "case-generator": "case-generator.md",
            "case-reviewer": "case-reviewer.md",
            "test-executor": "test-executor.md",
            "script-converter": "script-converter.md",
            "qa-orchestrator": "qa-orchestrator.md",
        }
        path = ROOT / "agents" / mapping.get(agent_name, f"{agent_name}.md")
    return path.read_text(encoding="utf-8") if path.exists() else ""


def stage_lock_path(stage_id: str) -> Path:
    return ARTIFACTS / f".subagent-launch-{stage_id}.json"


def legacy_stage_lock_path(stage_id: str) -> Path:
    return ARTIFACTS / f".subagent-launch-{stage_id}.lock"


def write_launch_lock(stage_id: str, prompt_path: Path, meta: dict) -> dict:
    import uuid

    round_id = _current_round_id(meta)
    payload = {
        "stage_name": stage_id,
        "launch_id": str(uuid.uuid4()),
        "prompt_path": str(prompt_path.relative_to(ROOT)) if prompt_path.is_relative_to(ROOT) else str(prompt_path),
        "run_id": meta.get("run_id"),
        "round_id": round_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "launcher": "pipeline_runner",
    }
    path = stage_lock_path(stage_id)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    legacy_stage_lock_path(stage_id).write_text(payload["created_at"], encoding="utf-8")
    return payload


def load_launch_lock(stage_id: str) -> dict:
    path = stage_lock_path(stage_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_prompt(platform: str, stage: dict, pipeline: dict, meta: dict) -> str:
    stage_id = stage["id"]
    skill = stage.get("skill", stage_id)
    agent = stage.get("agent", "")
    role = read_agent_role(agent)
    inputs = stage.get("inputs", [])
    output = stage.get("output", "")
    outputs = stage.get("outputs", [])
    contract = stage.get("contract", "")

    if stage_id == "case-review-prepare":
        return build_case_review_prepare_prompt(meta)
    if stage_id in CASE_REVIEW_STAGE_TO_PERSPECTIVE:
        return build_case_review_perspective_prompt(CASE_REVIEW_STAGE_TO_PERSPECTIVE[stage_id], meta, stage_id=stage_id)
    if stage_id == "case-review-merge":
        return build_case_review_merge_prompt(meta)

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
        # Remap legacy workspace/inputs/* paths to actual inputs dir when using --project
        actual_inp = inp
        if inp.startswith("workspace/inputs/") and str(INPUTS) != str(ROOT / "workspace" / "inputs"):
            rel = inp[len("workspace/inputs/"):]
            actual_inp = str(INPUTS.relative_to(ROOT)) + "/" + rel
        p = ROOT / actual_inp
        if p.exists():
            status = " (exists)"
        elif inp.endswith("env.json"):
            status = " (optional, missing)"
        else:
            status = " (MISSING — create before run)"
        lines.append(f"- `{actual_inp}`" + status)
    if stage_id == "prd-analyze":
        arts_rel = str(ARTIFACTS.relative_to(ROOT)) if ARTIFACTS.is_relative_to(ROOT) else str(ARTIFACTS)
        lines.extend(
            [
                f"- `{arts_rel}/00-knowledge-inventory.json` (exists; script-built inventory, not final selection)",
                f"- `{arts_rel}/00-knowledge-context.json` (write this yourself; decision_owner=prd-analyzer-subagent)",
            ]
        )

    lines.extend([
        "",
        "## Output",
    ])
    if output:
        # Remap output paths to actual run artifacts dir
        actual_out = _remap_artifacts_path(output)
        lines.append(f"- Write to: `{actual_out}`")
    for out in outputs:
        actual_out = _remap_artifacts_path(out)
        lines.append(f"- Write to: `{actual_out}`")
    if stage.get("output_notes"):
        lines.append(f"- Notes: {stage['output_notes']}")
    if contract:
        lines.append(f"- Contract: `{contract}`")
    lines.extend([
        "",
        "## Rules",
        "- 所有面向用户、产品、QA 或研发阅读的产物内容必须使用中文；保留文件名、字段名、枚举值、命令和代码标识的原文。",
        "- 若输出不符合契约，只修复输出，不要进入下一阶段。",
        "- 完成后运行:",
        f"  python3 scripts/validate-artifacts.py --stage {stage_id}",
        f"  python3 scripts/validate-artifacts.py --mark-done {stage_id}",
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

    if stage_id == "prd-analyze":
        rework_md = ARTIFACTS / "test-point-rework-to-qa.md"
        report_path = ARTIFACTS / "03-review-report.json"
        if rework_md.exists():
            lines.extend(
                [
                    "",
                    "## 上一轮 case-review 内部返工（必读，修正后再写蓝图）",
                    "",
                    rework_md.read_text(encoding="utf-8").strip(),
                    "",
                ]
            )
        elif report_path.exists():
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                report = {}
            internal = _internal_issues(report)
            if internal:
                lines.extend(
                    [
                        "",
                        "## 上一轮 case-review 内部问题（必读）",
                        "",
                    ]
                )
                for issue in internal:
                    lines.append(
                        f"- **{issue.get('id', '')}** [{issue.get('severity', '')}] "
                        f"{issue.get('description', '').strip()}"
                    )
                    if issue.get("suggestion"):
                        lines.append(f"  - 建议: {issue['suggestion'].strip()}")
                hints = report.get("revision_hints") or []
                if hints:
                    lines.append("")
                    lines.append("### revision_hints")
                    for h in hints:
                        lines.append(f"- {h}")
                lines.append("")

    return "\n".join(lines)


def build_case_review_prepare_prompt(meta: dict) -> str:
    arts_rel = str(ARTIFACTS.relative_to(ROOT)) if ARTIFACTS.is_relative_to(ROOT) else str(ARTIFACTS)
    round_id = _current_round_id(meta)
    return "\n".join(
        [
            "# QA Pipeline — case-review prepare",
            f"**Run ID**: {meta.get('run_id', 'unknown')}",
            f"**Case Review Round**: {round_id}",
            "**Skill**: case-review",
            "",
            "## Task",
            "准备 case-review 输入，只做 brief、precheck、structural findings 和四份 perspective prompt。",
            "",
            "## Steps",
            f"- 运行 `python3 scripts/build_case_review_perspective_brief.py`，然后追加 `brief_built` trace: `python3 scripts/case_review_trace.py brief_built --round-id {round_id} --summary \"case-review perspective brief generated\"`。",
            f"- 运行 `python3 scripts/validate-artifacts.py --stage case-review-precheck`，然后追加 `precheck_done` trace: `python3 scripts/case_review_trace.py precheck_done --round-id {round_id} --summary \"case-review precheck generated and validated\"`。",
            "- 只写 `case-review-findings-structural.json`；结构评审不代替四视角语义评审。",
            f"- 追加 `structural_findings_written` trace: `python3 scripts/case_review_trace.py structural_findings_written --round-id {round_id} --summary \"structural findings written\"`。",
            "- 后续 Hook/runner 会分别生成并拉起四份 perspective prompt；本阶段只准备共享输入。",
            "- 写入 `.case-review-prepare.done`，内容为当前 UTC 时间。",
            "",
            "## Boundary",
            "不要写四份 perspective findings，也不要 merge。四视角现在是流水线独立阶段，独立 launch lock 会进入最终审计。",
            "",
        ]
    )


def build_case_review_perspective_prompt(perspective: str, meta: dict, stage_id: str | None = None) -> str:
    slug = perspective_slug(perspective)
    stage_id = stage_id or f"case-review-{slug}"
    arts_rel = str(ARTIFACTS.relative_to(ROOT)) if ARTIFACTS.is_relative_to(ROOT) else str(ARTIFACTS)
    lock_rel = str(stage_lock_path(stage_id).relative_to(ROOT)) if stage_lock_path(stage_id).is_relative_to(ROOT) else str(stage_lock_path(stage_id))
    return "\n".join(
        [
            f"# QA Pipeline — case-review perspective: {perspective}",
            f"**Run ID**: {meta.get('run_id', 'unknown')}",
            f"**Stage**: {stage_id}",
            "**Skill**: case-review-perspective",
            "",
            "## Task",
            f"你是 case-review 的 `{perspective}` 独立视角子 Agent。只产出本视角 findings，不写最终报告。",
            "本 prompt 由流水线作为独立 stage 拉起；最终 validate 会检查本 stage 的 launch lock，因此不要复用其他视角产物。",
            "",
            "## Required Reading",
            f"- `{arts_rel}/case-review-perspective-brief.json` 中 `perspectives.{perspective}` 与 `knowledge_reading_list.{perspective}`",
            f"- `{arts_rel}/00-test-blueprint.json`",
            f"- `{arts_rel}/02-test-cases.md`",
            f"- `{arts_rel}/00-knowledge-context.json` 以及 brief 推荐的知识库原文",
            f"- `{lock_rel}`（独立 stage launch 证据）",
            "",
            "## Output",
            f"- 写入 `{arts_rel}/case-review-findings-{slug}.json`",
            "- JSON 字段 `perspective` 必须使用原值；red team 使用 `red_team`，文件名使用 `red-team`。",
            "- 必须逐条回答 brief 本视角 questions，写入 `perspective_notes[]`；questions 是最低必答清单，不限制额外发现。",
            "- 可把本视角新增风险写入 `issues[]` 或 `extra_notes[]`，但必须给出 rationale 和 evidence。",
            "- 如果 `issues[]` 非空，至少一条相关 `perspective_notes[].verdict` 必须是 `fail` 或 `blocked`。",
            "- `extra_notes[]` 提到历史、惯例、同类问题、回归或知识库时，必须填写 `knowledge_ref`。",
            "- 本视角只写自己的 findings；蓝图、用例和 `03-review-report.json` 由对应阶段或 merge 脚本负责，避免单个视角覆盖其他证据。",
            "",
            "## Validate",
            f"- 可自检: `python3 scripts/validate-artifacts.py --stage case-review-perspective --perspective {perspective}`",
            "- 不要写 completed/validate trace，也不要写 stage done marker；runner/Hook 会在阶段边界统一补齐审计账本。",
            "",
        ]
    )


def build_case_review_merge_prompt(meta: dict) -> str:
    arts_rel = str(ARTIFACTS.relative_to(ROOT)) if ARTIFACTS.is_relative_to(ROOT) else str(ARTIFACTS)
    return "\n".join(
        [
            "# QA Pipeline — case-review merge",
            f"**Run ID**: {meta.get('run_id', 'unknown')}",
            "**Skill**: case-review",
            "",
            "## Task",
            "合并 structural + 四个独立 perspective findings，生成最终 case-review 报告。",
            "",
            "## Required inputs",
            f"- `{arts_rel}/case-review-findings-structural.json`",
            f"- `{arts_rel}/case-review-findings-product.json`",
            f"- `{arts_rel}/case-review-findings-qa.json`",
            f"- `{arts_rel}/case-review-findings-testability.json`",
            f"- `{arts_rel}/case-review-findings-red-team.json`",
            f"- `{arts_rel}/case-review-orchestration-trace.jsonl`",
            "",
            "## Steps",
            "- 运行 `python3 scripts/merge_case_review_findings.py`。",
            "- 追加 `merge_done` trace。",
            "- 运行 `python3 scripts/validate-artifacts.py --stage case-review`。",
            "- 追加 `final_validate_passed` trace。",
            "- 运行 `python3 scripts/validate-artifacts.py --mark-done case-review`。",
            "",
        ]
    )


def build_case_review_perspective_prompts(meta: dict) -> dict[str, Path]:
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    out: dict[str, Path] = {}
    for perspective in CASE_REVIEW_PERSPECTIVES:
        slug = "red-team" if perspective == "red_team" else perspective
        path = PROMPTS_DIR / f"case-review-{slug}.md"
        path.write_text(build_case_review_perspective_prompt(perspective, meta), encoding="utf-8")
        out[perspective] = path
    return out


def write_prompt(
    platform: str,
    stage: dict,
    pipeline: dict,
    meta: dict,
    *,
    record_launch: bool = False,
) -> Path:
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    if stage["id"] == "prd-analyze":
        inventory = ROOT / "scripts" / "build_knowledge_inventory.py"
        subprocess.run([sys.executable, str(inventory)], cwd=str(ROOT), check=False)
    content = build_prompt(platform, stage, pipeline, meta)
    out = PROMPTS_DIR / f"{stage['id']}.md"
    out.write_text(content, encoding="utf-8")
    if record_launch and stage["id"] in CASE_REVIEW_STAGE_TO_PERSPECTIVE:
        lock = write_launch_lock(stage["id"], out, meta)
        perspective = CASE_REVIEW_STAGE_TO_PERSPECTIVE[stage["id"]]
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "case_review_trace.py"),
                "perspective_task_started",
                "--perspective",
                perspective,
                "--from-launch-lock",
                str(stage_lock_path(stage["id"])),
                "--round-id",
                str(lock.get("round_id") or _current_round_id(meta)),
                "--summary",
                f"Hook/runner launched independent stage {stage['id']}",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    return out


def run_validate(stage_id: str, *, env_extra: dict[str, str] | None = None) -> bool:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [sys.executable, str(VALIDATE), "--stage", stage_id],
        cwd=str(ROOT),
        env=env,
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


def prd_analyze_outputs_exist() -> bool:
    return (
        (ARTIFACTS / "00-test-blueprint.json").exists()
        and (ARTIFACTS / "00-test-blueprint.md").exists()
        and knowledge_context_ready()
    )


def knowledge_context_ready() -> bool:
    path = ARTIFACTS / "00-knowledge-context.json"
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return data.get("decision_owner") == "prd-analyzer-subagent"


def artifact_ready(stage_id: str, *, respect_force: bool = True) -> bool:
    if respect_force and _force_rerun():
        return False
    if stage_id == "prd-analyze":
        return prd_analyze_outputs_exist()
    if stage_id == "case-review-prepare":
        return (ARTIFACTS / ".case-review-prepare.done").exists()
    if stage_id in CASE_REVIEW_STAGE_TO_PERSPECTIVE:
        return stage_done_marker(stage_id).exists()
    if stage_id == "case-review-merge":
        return stage_done_marker(stage_id).exists()
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


def write_case_review_notice() -> Path:
    from render_case_review_notice import write_product_markdown

    return write_product_markdown()


def _product_issues(report: dict) -> list[dict]:
    return [
        i
        for i in report.get("issues") or []
        if (i.get("audience") or "product") == "product"
    ]


def _internal_issues(report: dict) -> list[dict]:
    """QA/用例/蓝图内部问题（须先返工，再才允许仅产品打回）。"""
    internal = []
    for i in report.get("issues") or []:
        audience = i.get("audience") or "product"
        root = i.get("root_cause") or ""
        retry = i.get("retry_target") or ""
        if audience == "internal" or root in ("qa_undercoverage", "case_generation"):
            internal.append(i)
        elif retry in ("prd-analyze", "case-generate"):
            internal.append(i)
    return internal


def _issues_target(report: dict, target: str) -> list[dict]:
    return [
        i
        for i in report.get("issues") or []
        if (i.get("retry_target") or "") == target
    ]


def _max_analyze_retries(pipeline: dict) -> int:
    stage = stage_by_id(pipeline, "case-review") or {}
    on_fail = stage.get("on_fail") or {}
    try:
        return max(1, int(on_fail.get("max_retries", 3)))
    except (TypeError, ValueError):
        return 3


def _analyze_retry_count(meta: dict) -> int:
    try:
        return int(meta.get("review", {}).get("analyze_retry_count", 0))
    except (TypeError, ValueError):
        return 0


def _can_analyze_retry(meta: dict, pipeline: dict) -> bool:
    return _analyze_retry_count(meta) < _max_analyze_retries(pipeline)


def apply_analyze_retry(pipeline: dict, meta: dict, report: dict) -> bool:
    """内部评审返工：递增计数、清理蓝图/用例产物，保留返工说明供 prd-analyze 读取。"""
    fp = str(report.get("reviewed_at") or report.get("version") or "")
    review = meta.setdefault("review", {})
    if review.get("last_retry_report_at") == fp:
        return not prd_analyze_outputs_exist()
    if not _can_analyze_retry(meta, pipeline):
        return False
    review["last_retry_report_at"] = fp
    review["analyze_retry_count"] = _analyze_retry_count(meta) + 1
    _reset_case_review_round(meta, "internal_rework")
    save_meta(meta)
    try:
        import qa_coverage_checks

        qa_coverage_checks.ARTIFACTS = ARTIFACTS
        qa_coverage_checks.PENDING_REWORK_FILE = ARTIFACTS / ".pending-rework-issues.json"
        qa_coverage_checks.PRECHECK_FILE = ARTIFACTS / "case-review-precheck.json"
        qa_coverage_checks.SNAPSHOTS_DIR = ARTIFACTS / "snapshots"
        qa_coverage_checks.write_pending_rework(report, load_project_config())
    except Exception as exc:
        print(f"[orchestrator] warn: could not write pending rework issues: {exc}")
    cleanup_outputs_for_stages(
        pipeline,
        ["prd-analyze", "case-generate", "case-review"],
        preserve_case_review_trace=True,
    )
    return True


def resolve_case_review_gate(pipeline: dict, meta: dict) -> str:
    """
    评审门禁结果（case-review 完成后调用）:
    - continue: pass，可进 test-execute
    - retry_analyze: 有内部问题且未达重试上限，已 apply 清理
    - prd_rejected: 仅剩产品问题
    - await_orchestrator: 内部问题达上限或需主 Agent 裁定
    - abort: human 升级
    """
    report_path = ARTIFACTS / "03-review-report.json"
    if not report_path.exists():
        return "continue"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    verdict = report.get("verdict")
    if verdict == "pass":
        meta.setdefault("review", {})["analyze_retry_count"] = 0
        meta["review"].pop("last_retry_report_at", None)
        save_meta(meta)
        return "continue"
    if verdict not in ("reject", "fail"):
        return "continue"

    product = _product_issues(report)
    internal = _internal_issues(report)
    write_case_review_notice()
    _print_orchestrator_case_review_decision(
        report, product=product, internal=internal
    )

    if _issues_target(report, "human"):
        meta.setdefault("orchestrator", {})["last_decision"] = "escalate_human"
        save_meta(meta)
        return "abort"

    if internal:
        if apply_analyze_retry(pipeline, meta, report):
            n = _analyze_retry_count(meta)
            mx = _max_analyze_retries(pipeline)
            print(
                f"[orchestrator] 内部问题 {len(internal)} 条 → Hook 将自动链式拉起 "
                f"prd-analyze → case-generate → case-review（返工 {n}/{mx}）"
            )
            now = datetime.now(timezone.utc).isoformat()
            meta["stage"] = "case-review"
            meta["stage_result"] = "INTERNAL_REWORK"
            meta["has_product_issues"] = bool(product)
            meta["has_internal_issues"] = True
            meta["product_issue_count"] = len(product)
            meta["internal_issue_count"] = len(internal)
            meta["completed_at"] = now
            meta.setdefault("stages", {}).setdefault("case-review", {})
            meta["stages"]["case-review"].update(
                {
                    "status": "done",
                    "stage": "case-review",
                    "stage_result": "INTERNAL_REWORK",
                    "has_product_issues": bool(product),
                    "has_internal_issues": True,
                    "product_issue_count": len(product),
                    "internal_issue_count": len(internal),
                    "updated_at": now,
                    "completed_at": now,
                }
            )
            meta.setdefault("orchestrator", {})["last_decision"] = "internal_retry"
            save_meta(meta)
            return "retry_analyze"
        meta.setdefault("orchestrator", {})["last_decision"] = "escalate_internal_max_retries"
        save_meta(meta)
        print(
            "[orchestrator] 内部返工已达上限 → 请主 Agent 阅读 test-point-rework-to-qa.md 并决定人工介入或 --force 重跑"
        )
        return "await_orchestrator"

    if product:
        _pipeline_reject_mark_notified()
        meta.setdefault("orchestrator", {})["last_decision"] = "product_reject"
        save_meta(meta)
        return "prd_rejected"

    meta.setdefault("orchestrator", {})["last_decision"] = "await_orchestrator"
    save_meta(meta)
    return "await_orchestrator"


def _print_orchestrator_case_review_decision(
    report: dict, *, product: list[dict], internal: list[dict]
) -> None:
    """打印评审摘要；内部问题由 Hook 自动返工，主 Agent 在达上限或 pass/仅产品 时介入。"""
    print("\n[orchestrator] === case-review 已完成 ===")
    print(f"  评审报告: {ARTIFACTS / '03-review-report.json'}")
    print(f"  摘要 Markdown: {ARTIFACTS / '03-review-report.md'}")
    if internal:
        print(f"  内部问题: {len(internal)} 条 → {ARTIFACTS / 'test-point-rework-to-qa.md'}")
    if product:
        print(f"  产品问题: {len(product)} 条 → {ARTIFACTS / 'prd-reject-to-product.md'}")
    print("")
    if internal and _can_analyze_retry(load_meta(), load_pipeline()):
        print(
            "[orchestrator] 内部返工 — Hook 将自动拉起 prd-analyze（注入返工说明），"
            "再 case-generate → case-review，直至内部项清零或达 max_retries。"
        )
    elif internal:
        print(
            "[orchestrator] 内部返工已达 max_retries — 请主 Agent 检查蓝图/用例是否仍缺项，"
            "或 --force --from-stage prd-analyze 人工重跑。"
        )
    if product and not internal:
        print(
            "[orchestrator] 仅剩产品问题 — 流水线停止；主 Agent 将 prd-reject-to-product.md 交产品。"
        )
    elif product and internal:
        print(
            "[orchestrator] mixed — 先自动返工清内部问题；内部清零后若仍 reject 再交产品打回。"
        )
    if report.get("verdict") == "pass":
        print("[orchestrator] pass — Hook 可继续 test-execute。")
    if _issues_target(report, "human"):
        print("[orchestrator] 含 retry_target=human，须主 Agent 升级人工。")
    print("")


def _run_prd_analyze_finalize() -> bool:
    """Render readable blueprint Markdown, then validate the single-blueprint stage."""
    scripts = Path(__file__).resolve().parent
    inventory = scripts / "build_knowledge_inventory.py"
    if not (ARTIFACTS / "00-knowledge-inventory.json").exists():
        subprocess.run([sys.executable, str(inventory)], cwd=str(ROOT), check=False)
    if not knowledge_context_ready():
        print(
            "[prd-analyze] missing AI-owned 00-knowledge-context.json "
            "(decision_owner must be prd-analyzer-subagent)",
            file=sys.stderr,
        )
        return False
    renderer = scripts / "render_test_blueprint.py"
    r = subprocess.run([sys.executable, str(renderer)], cwd=str(ROOT), capture_output=True, text=True)
    if r.stdout:
        print(r.stdout, end="")
    if r.returncode != 0:
        if r.stderr:
            print(r.stderr, file=sys.stderr)
        return False
    if not run_validate("prd-analyze"):
        return False
    bp = ARTIFACTS / "00-test-blueprint.json"
    if bp.exists():
        print(f"[prd-analyze] Blueprint: {bp}")
    return True


def _run_case_review_prepare_finalize() -> bool:
    """Deterministically validate prepare outputs and publish prepare completion."""
    trace = ROOT / "scripts" / "case_review_trace.py"
    round_id = _current_round_id()
    for check_stage in ("case-review-precheck",):
        if not run_validate(check_stage):
            return False
    if not (ARTIFACTS / "case-review-findings-structural.json").exists():
        print("[case-review-prepare] missing case-review-findings-structural.json", file=sys.stderr)
        return False
    subprocess.run(
        [
            sys.executable,
            str(trace),
            "structural_findings_written",
            "--round-id",
            round_id,
            "--summary",
            "structural findings written and prepare stage finalized",
        ],
        cwd=str(ROOT),
        check=False,
    )
    (ARTIFACTS / ".case-review-prepare.done").write_text(
        datetime.now(timezone.utc).isoformat() + "\n", encoding="utf-8"
    )
    _write_stage_done_marker("case-review-prepare", {"round_id": round_id})
    return True


def _run_case_review_merge_finalize() -> bool:
    """Merge findings with scripts, then run final case-review validation and mark done."""
    trace = ROOT / "scripts" / "case_review_trace.py"
    merge = ROOT / "scripts" / "merge_case_review_findings.py"
    r = subprocess.run([sys.executable, str(merge)], cwd=str(ROOT), capture_output=True, text=True)
    if r.stdout:
        print(r.stdout, end="")
    if r.returncode != 0:
        if r.stderr:
            print(r.stderr, file=sys.stderr)
        return False
    subprocess.run(
        [
            sys.executable,
            str(trace),
            "merge_done",
            "--round-id",
            _current_round_id(),
            "--summary",
            "structural and four independent perspective findings merged",
        ],
        cwd=str(ROOT),
        check=False,
    )
    _write_stage_done_marker("case-review-merge", {"round_id": _current_round_id()})
    if not run_validate("case-review", env_extra={"QA_SKIP_FINAL_VALIDATE_TRACE": "1"}):
        return False
    subprocess.run(
        [
            sys.executable,
            str(trace),
            "final_validate_passed",
            "--round-id",
            _current_round_id(),
            "--summary",
            "final case-review validation passed",
        ],
        cwd=str(ROOT),
        check=False,
    )
    if not run_validate("case-review"):
        return False
    return True


def _append_trace(args: list[str]) -> bool:
    trace = ROOT / "scripts" / "case_review_trace.py"
    r = subprocess.run([sys.executable, str(trace), *args], cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode != 0:
        if r.stderr:
            print(r.stderr, file=sys.stderr)
        return False
    return True


def _write_stage_done_marker(stage_id: str, payload: dict | None = None) -> None:
    data = {
        "stage": stage_id,
        "status": "done",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        **(payload or {}),
    }
    stage_done_marker(stage_id).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _run_case_review_perspective_finalize(stage_id: str, perspective: str) -> bool:
    lock = load_launch_lock(stage_id)
    if not lock:
        print(f"[{stage_id}] missing launch lock; stage must be launched by Hook/runner", file=sys.stderr)
        return False
    if lock.get("launcher") != "pipeline_runner":
        print(f"[{stage_id}] launch lock must come from pipeline_runner, got {lock.get('launcher')}", file=sys.stderr)
        return False
    if lock.get("stage_name") != stage_id:
        print(f"[{stage_id}] launch lock stage mismatch: {lock.get('stage_name')}", file=sys.stderr)
        return False
    slug = perspective_slug(perspective)
    findings = ARTIFACTS / f"case-review-findings-{slug}.json"
    if not findings.exists():
        print(f"[{stage_id}] missing {findings.name}", file=sys.stderr)
        return False
    lock_path = stage_lock_path(stage_id)
    try:
        if findings.stat().st_mtime < lock_path.stat().st_mtime:
            print(f"[{stage_id}] findings predates current launch lock; rerun this perspective stage", file=sys.stderr)
            return False
    except OSError as exc:
        print(f"[{stage_id}] could not compare launch/findings mtimes: {exc}", file=sys.stderr)
        return False

    r = subprocess.run(
        [
            sys.executable,
            str(VALIDATE),
            "--stage",
            "case-review-perspective",
            "--perspective",
            perspective,
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    if r.returncode != 0:
        return False

    summary = f"{perspective} independent stage finalized by runner"
    try:
        data = json.loads(findings.read_text(encoding="utf-8"))
        summary = (
            f"{perspective} verdict={data.get('verdict')} "
            f"finding_count={data.get('finding_count')}"
        )
    except Exception:
        pass
    common = [
        "--perspective",
        perspective,
        "--from-launch-lock",
        str(lock_path),
        "--round-id",
        str(lock.get("round_id") or _current_round_id()),
    ]
    if not _append_trace(
        [
            "perspective_task_completed",
            *common,
            "--agent-id-unavailable-reason",
            "stage finalized by runner; platform Task id not exposed",
            "--summary",
            summary,
        ]
    ):
        return False
    if not _append_trace(["perspective_validate_passed", *common]):
        return False
    _write_stage_done_marker(
        stage_id,
        {
            "perspective": perspective,
            "launch_id": lock.get("launch_id"),
            "round_id": lock.get("round_id"),
            "findings_path": str(findings.relative_to(ROOT)) if findings.is_relative_to(ROOT) else str(findings),
        },
    )
    return True


def check_inputs(stage: dict) -> list[str]:
    missing = []
    for inp in stage.get("inputs", []):
        if not _resolve_workspace_path(inp).exists():
            # env.json optional
            if inp.endswith("env.json"):
                continue
            missing.append(inp)
    return missing


def cleanup_outputs_for_stages(
    pipeline: dict,
    stage_ids: list[str],
    *,
    preserve_case_review_trace: bool = False,
) -> None:
    """Remove stale artifacts for stages that will be regenerated."""
    legacy_ready = ARTIFACTS / ("00-test-" + "ready-blueprint.json")
    legacy_items = [
        legacy_ready,
        ARTIFACTS / ("00-test-" + "ob" + "ligations.json"),
        ARTIFACTS / ("01-prd-" + "analysis.json"),
        ARTIFACTS / ("test-ready-" + "internal.md"),
    ]
    stage_outputs = {
        "prd-analyze": [
            ARTIFACTS / "00-test-blueprint.json",
            ARTIFACTS / "00-test-blueprint.md",
            ARTIFACTS / "00-knowledge-inventory.json",
            ARTIFACTS / "00-knowledge-inventory.md",
            ARTIFACTS / "00-knowledge-context.json",
            ARTIFACTS / "00-knowledge-context.md",
            ARTIFACTS / ".prd-analyze-complete.ok",
            *legacy_items,
        ],
        "case-generate": [
            ARTIFACTS / "02-test-cases.md",
        ],
        "case-review": [
            ARTIFACTS / ".case-review-prepare.done",
            ARTIFACTS / "03-review-report.json",
            ARTIFACTS / "03-review-report.json.tmp",
            ARTIFACTS / "03-review-report.md",
            ARTIFACTS / "prd-reject-to-product.md",
            ARTIFACTS / "case-review-pass.md",
            ARTIFACTS / ".orchestrator-prd-reject-notified",
            ARTIFACTS / ".case-review-orchestrating.lock",
            ARTIFACTS / "case-review-orchestration-failed.md",
            ARTIFACTS / "case-review-merge-needs-confirmation.md",
            ARTIFACTS / "case-review-precheck.json",
            ARTIFACTS / "prd-coverage-matrix.json",
            ARTIFACTS / "case-review-perspective-brief.json",
            ARTIFACTS / "case-review-perspective-brief.md",
            ARTIFACTS / "case-review-findings-structural.json",
            ARTIFACTS / "case-review-findings-product.json",
            ARTIFACTS / "case-review-findings-qa.json",
            ARTIFACTS / "case-review-findings-testability.json",
            ARTIFACTS / "case-review-findings-red-team.json",
            ARTIFACTS / ".subagent-launch-case-review-prepare.lock",
            ARTIFACTS / ".subagent-launch-case-review-product.lock",
            ARTIFACTS / ".subagent-launch-case-review-qa.lock",
            ARTIFACTS / ".subagent-launch-case-review-testability.lock",
            ARTIFACTS / ".subagent-launch-case-review-red-team.lock",
            ARTIFACTS / ".subagent-launch-case-review-merge.lock",
            ARTIFACTS / ".subagent-launch-case-review-product.json",
            ARTIFACTS / ".subagent-launch-case-review-qa.json",
            ARTIFACTS / ".subagent-launch-case-review-testability.json",
            ARTIFACTS / ".subagent-launch-case-review-red-team.json",
            ARTIFACTS / ".stage-done-case-review-prepare.json",
            ARTIFACTS / ".stage-done-case-review-product.json",
            ARTIFACTS / ".stage-done-case-review-qa.json",
            ARTIFACTS / ".stage-done-case-review-testability.json",
            ARTIFACTS / ".stage-done-case-review-red-team.json",
            ARTIFACTS / ".stage-done-case-review-merge.json",
        ],
        "test-execute": [
            ARTIFACTS / "04-execution-result.json",
            ARTIFACTS / "05b-bug-list.md",
        ],
        "script-convert": [
            ARTIFACTS / "05a-scripts",
        ],
    }
    if not preserve_case_review_trace:
        stage_outputs["case-review"].append(ARTIFACTS / "case-review-orchestration-trace.jsonl")
    for stage_id in stage_ids:
        lock = ARTIFACTS / f".subagent-launch-{stage_id}.lock"
        lock.unlink(missing_ok=True)
        for path in stage_outputs.get(stage_id, []):
            if preserve_case_review_trace and path.name == "case-review-orchestration-trace.jsonl":
                continue
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)


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
    extra = None
    if stage_id == "prd-analyze":
        if not _run_prd_analyze_finalize():
            mark_stage(meta, stage_id, "validation_failed")
            return "abort"
    elif stage_id == "case-review-prepare":
        if not _run_case_review_prepare_finalize():
            mark_stage(meta, stage_id, "validation_failed")
            return "abort"
        mark_stage(meta, stage_id, "done")
        subprocess.run(
            [sys.executable, str(VALIDATE), "--mark-done", stage_id],
            cwd=str(ROOT),
            check=False,
        )
        return "continue"
    elif stage_id in CASE_REVIEW_STAGE_TO_PERSPECTIVE:
        perspective = CASE_REVIEW_STAGE_TO_PERSPECTIVE[stage_id]
        if not _run_case_review_perspective_finalize(stage_id, perspective):
            mark_stage(meta, stage_id, "validation_failed")
            return "abort"
        mark_stage(meta, stage_id, "done")
        subprocess.run(
            [sys.executable, str(VALIDATE), "--mark-done", stage_id],
            cwd=str(ROOT),
            check=False,
        )
        return "continue"
    elif stage_id == "case-review-merge":
        if not _run_case_review_merge_finalize():
            mark_stage(meta, stage_id, "validation_failed")
            return "abort"
        mark_stage(meta, stage_id, "done")
        stage_id = "case-review"
    elif not run_validate(stage_id):
        mark_stage(meta, stage_id, "validation_failed")
        return "abort"
    if stage_id == "case-review":
        report = json.loads((ARTIFACTS / "03-review-report.json").read_text(encoding="utf-8"))
        extra = {
            "verdict": report.get("verdict"),
            "reject_kind": report.get("reject_kind"),
        }
        if report.get("verdict") == "reject":
            product = _product_issues(report)
            internal = _internal_issues(report)
            extra["product_issue_count"] = len(product)
            extra["internal_issue_count"] = len(internal)
            mark_stage(meta, stage_id, "rejected", extra)
            gate = resolve_case_review_gate(pipeline, meta)
            if gate == "retry_analyze":
                return "retry_analyze"
            if gate == "abort":
                _pipeline_active_clear()
                return "abort"
            if gate == "prd_rejected":
                _pipeline_active_clear()
                return "prd_rejected"
            if gate == "await_orchestrator":
                return "await_orchestrator"
        if report.get("verdict") == "pass":
            notice = write_case_review_notice()
            print(f"[case-review] PASS — 进入测试执行。评审说明: {notice}")

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
        if stage_id == "prd-analyze" and (execute or auto):
            return "abort"

    prompt_path = write_prompt(platform, stage, pipeline, meta, record_launch=auto)
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
        exit_code = launch_subagent_cli(platform, stage_id, prompt_path, pipeline)
        if exit_code != 0:
            print(f"[{stage_id}] Sub-agent CLI exited with {exit_code} (checking artifacts anyway)")
        if not artifact_ready(stage_id, respect_force=False):
            mark_stage(meta, stage_id, "failed")
            print(f"[{stage_id}] Artifact missing after sub-agent run")
            return "abort"
        return finalize_stage(stage_id, pipeline, meta)

    if execute and stage_id == "case-review-merge":
        return finalize_stage(stage_id, pipeline, meta)

    if (
        execute
        and stage_id == "case-review-prepare"
        and (ARTIFACTS / "case-review-findings-structural.json").exists()
    ):
        return finalize_stage(stage_id, pipeline, meta)

    if execute and stage_id in CASE_REVIEW_STAGE_TO_PERSPECTIVE:
        perspective = CASE_REVIEW_STAGE_TO_PERSPECTIVE[stage_id]
        slug = perspective_slug(perspective)
        if (ARTIFACTS / f"case-review-findings-{slug}.json").exists():
            return finalize_stage(stage_id, pipeline, meta)

    if not artifact_ready(stage_id):
        print(f"[{stage_id}] Waiting for artifact. Run sub-agent, then re-run with --execute")
        mark_stage(meta, stage_id, "waiting")
        return "continue"

    if execute:
        return finalize_stage(stage_id, pipeline, meta)
    return "continue"


def cursor_cli_authenticated() -> bool:
    import os

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
    if platform == "cursor" and not cursor_cli_authenticated() and not __import__("os").environ.get("CURSOR_API_KEY"):
        return False
    return r.returncode == 0


def print_ide_stage_guide(stage_id: str, prompt_path: Path, index: int, total: int) -> None:
    rel = prompt_path.relative_to(ROOT)
    print(f"\n{'#'*60}")
    print(f"# IDE-CHAIN [{index}/{total}] 当前阶段: {stage_id}")
    print(f"{'#'*60}")
    print("[主 Agent] 本回合勿用 Task 批量拉起各阶段；流水线已激活，等待 Hook followup 自动开子 Agent。")
    print(f"[Hook] 将在 stop/subagentStop 后注入 Task，执行: {rel}")
    print(f"  Prompt: {prompt_path}")
    print(f"{'#'*60}\n")


def wait_for_artifact(stage_id: str, poll_sec: int = 10, timeout_sec: int = 7200) -> bool:
    import time

    deadline = time.time() + timeout_sec
    print(f"[ide] 等待产物出现（每 {poll_sec}s 检测，超时 {timeout_sec}s）...")
    while time.time() < deadline:
        if artifact_ready(stage_id, respect_force=False):
            print(f"[ide] 检测到产物: {stage_id}")
            return True
        time.sleep(poll_sec)
    print(f"[ide] 超时: 未检测到 {stage_id} 产物", file=sys.stderr)
    return False


def cli_auto_allowed(args: argparse.Namespace) -> bool:
    """Cursor 下 --auto 须显式放行，避免主 Agent 误用后台 CLI 替代 ide-chain。"""
    if os.environ.get("QA_PIPELINE_ALLOW_CLI", "").strip().lower() in ("1", "true", "yes"):
        return True
    return bool(getattr(args, "allow_cli", False))


def refuse_cursor_auto_without_allow(args: argparse.Namespace) -> int | None:
    if not args.auto or args.platform != "cursor":
        return None
    if cli_auto_allowed(args):
        return None
    print(
        "ERROR: Cursor --auto needs explicit opt-in because it runs in the background and is not visible in the sidebar.",
        file=sys.stderr,
    )
    print(
        "  用户说「跑流水线」请用: ./orchestrators/cursor/run-pipeline.sh",
        file=sys.stderr,
    )
    print(
        "  或: ./orchestrators/cursor/run-pipeline.sh --ide-chain",
        file=sys.stderr,
    )
    print(
        "  仅当用户明确要求 CLI/无头/后台时，才用:",
        file=sys.stderr,
    )
    print(
        "    QA_PIPELINE_ALLOW_CLI=1 ./orchestrators/cursor/run-pipeline.sh --auto --allow-cli",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="QA Agent pipeline runner")
    parser.add_argument("--platform", choices=["cursor", "codex", "claude-code"], default="codex")
    parser.add_argument(
        "--project",
        default=None,
        help="Project slug (e.g. hp-feed-price-tag). Enables per-project run isolation under workspace/projects/.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Only generate prompts (default without --auto/--execute)")
    parser.add_argument("--execute", action="store_true", help="Validate existing artifacts and advance gates")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Launch sub-agents via platform CLI (Cursor: requires --allow-cli or QA_PIPELINE_ALLOW_CLI=1)",
    )
    parser.add_argument(
        "--allow-cli",
        action="store_true",
        help="Explicitly allow Cursor --auto (background cursor agent). Do not use unless user asked for CLI.",
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
    parser.add_argument(
        "--case-review-gate",
        action="store_true",
        help="Hook 用：处理 case-review 门禁，stdout 输出 retry_analyze|prd_rejected|await_orchestrator|continue|abort",
    )
    parser.add_argument(
        "--record-launch-stage",
        default=None,
        help="Hook/CLI 用：为即将真正启动的 stage 写入 launch lock 和 started trace",
    )
    args = parser.parse_args()

    if args.case_review_gate:
        pipeline = load_pipeline()
        meta = load_meta()
        print(resolve_case_review_gate(pipeline, meta))
        return 0

    if args.check_auth:
        return 0 if check_auth(args.platform) else 1

    blocked = refuse_cursor_auto_without_allow(args)
    if blocked is not None:
        return blocked

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

    # -----------------------------------------------------------------------
    # Project & run directory setup
    # -----------------------------------------------------------------------
    project = args.project or os.environ.get("QA_PROJECT")
    if project:
        from workspace_paths import slugify  # noqa: PLC0415
        project = slugify(project)

    force = (args.force or args.from_stage == "prd-analyze") and not args.no_force

    if project:
        project_dir = ROOT / "workspace" / "projects" / project
        current_link = project_dir / "current"

        # --from-stage with an existing current run means "continue this run",
        # not "create a new one".  Only create a fresh run when:
        #   1. No current run exists yet (first ever run for this project), OR
        #   2. --force is explicitly passed (user wants a clean slate), OR
        #   3. from_stage is the very first stage (prd-analyze) without --no-force
        is_first_stage = args.from_stage == "prd-analyze"
        has_current = current_link.exists() or current_link.is_symlink()
        should_create_new_run = force or not has_current

        if should_create_new_run:
            new_artifacts, run_id = _create_run(project)
        else:
            # Reuse existing current run
            new_artifacts = current_link.resolve() if current_link.is_symlink() else current_link
            meta_existing = new_artifacts / "00-meta.json"
            run_id = None
            if meta_existing.exists():
                try:
                    run_id = json.loads(meta_existing.read_text(encoding="utf-8")).get("run_id")
                except Exception:
                    pass
            if run_id is None:
                run_id = new_artifacts.name
            print(f"[pipeline] project={project}  continuing run={run_id}")

        # Re-point global ARTIFACTS so all subsequent code uses the run dir
        global ARTIFACTS, PROMPTS_DIR, INPUTS  # noqa: PLW0603
        ARTIFACTS = new_artifacts
        PROMPTS_DIR = ARTIFACTS / "prompts"
        INPUTS = ROOT / "workspace" / "projects" / project / "inputs"
        os.environ["QA_WORKSPACE"] = str(ARTIFACTS)
        os.environ["QA_INPUTS"] = str(INPUTS)
        os.environ["QA_PROJECT"] = project
        if should_create_new_run:
            print(f"[pipeline] project={project}  run={run_id}")
        print(f"[pipeline] artifacts → {ARTIFACTS}")
    else:
        run_id = None

    meta = load_meta()
    meta["platform"] = args.platform
    if project:
        meta["project_slug"] = project
    if run_id:
        meta["run_id"] = run_id
        meta["workspace"] = str(ARTIFACTS)
        meta["inputs"] = str(INPUTS)

    from_stage = "case-review-prepare" if args.from_stage == "case-review" else args.from_stage
    to_stage = "case-review-merge" if args.to_stage == "case-review" else args.to_stage
    if from_stage == "case-review-prepare" and (args.force or not (ARTIFACTS / ".case-review-prepare.done").exists()):
        _reset_case_review_round(meta, "case_review_prepare_start")
        meta = load_meta()

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
    if args.record_launch_stage:
        meta["last_launch_recorded_stage"] = args.record_launch_stage
        meta["last_launch_recorded_at"] = datetime.now(timezone.utc).isoformat()
    elif not (args.dry_run and not auto and not execute and not ide and not ide_chain):
        meta["mode"] = mode_label
    else:
        meta["last_prompt_generation_mode"] = mode_label
        meta["last_prompt_generation_at"] = datetime.now(timezone.utc).isoformat()
    save_meta(meta)

    if args.record_launch_stage:
        stage = stage_by_id(pipeline, args.record_launch_stage)
        if not stage:
            print(f"Unknown stage: {args.record_launch_stage}", file=sys.stderr)
            return 2
        path = write_prompt(args.platform, stage, pipeline, meta, record_launch=True)
        if args.record_launch_stage not in CASE_REVIEW_STAGE_TO_PERSPECTIVE:
            legacy_stage_lock_path(args.record_launch_stage).write_text(
                datetime.now(timezone.utc).isoformat(), encoding="utf-8"
            )
        print(path)
        return 0

    all_stage_ids = expand_stage_ids(LINEAR_STAGES.copy())
    stages_to_run = all_stage_ids.copy()
    if from_stage in stages_to_run:
        stages_to_run = stages_to_run[stages_to_run.index(from_stage) :]
    if to_stage and to_stage in stages_to_run:
        stages_to_run = stages_to_run[: stages_to_run.index(to_stage) + 1]
    if auto:
        _pipeline_active_touch("cli", force=force)
    elif ide_chain or ide:
        _pipeline_active_touch("ide", force=force)
    if force:
        print("[pipeline] --force：将重新拉起子 Agent，不因旧产物跳过阶段")
        # 重置将重跑阶段的 meta.stages 状态，避免历史 run 的 status=done 残留误导编排器
        meta = load_meta()
        all_stages_to_reset = stages_to_run + POST_BRANCHES
        for sid in all_stages_to_reset:
            if sid in meta.get("stages", {}):
                meta["stages"][sid]["status"] = "pending"
                meta["stages"][sid]["updated_at"] = datetime.now(timezone.utc).isoformat()
        # 同时清零 review 重试计数，避免跨 run 的 retry_count 残留
        meta.pop("review", None)
        meta.pop("orchestrator", None)
        save_meta(meta)
        for stale in (
            ARTIFACTS / "03-review-report.json",
            ARTIFACTS / "03-review-report.json.tmp",
            ARTIFACTS / "03-review-report.md",
            ARTIFACTS / "prd-reject-to-product.md",
            ARTIFACTS / "case-review-pass.md",
            ARTIFACTS / ".prd-analyze-complete.ok",
            ARTIFACTS / ".case-review-orchestrating.lock",
            ARTIFACTS / "case-review-orchestration-failed.md",
            ARTIFACTS / "case-review-orchestration-trace.jsonl",
            ARTIFACTS / "case-review-merge-needs-confirmation.md",
            ARTIFACTS / "case-review-precheck.json",
            ARTIFACTS / "prd-coverage-matrix.json",
            ARTIFACTS / "case-review-perspective-brief.json",
            ARTIFACTS / "case-review-perspective-brief.md",
            ARTIFACTS / "case-review-findings-structural.json",
            ARTIFACTS / "00-test-blueprint.json",
            ARTIFACTS / "00-test-blueprint.md",
            ARTIFACTS / "00-knowledge-inventory.json",
            ARTIFACTS / "00-knowledge-inventory.md",
            ARTIFACTS / "00-knowledge-context.json",
            ARTIFACTS / "00-knowledge-context.md",
            ARTIFACTS / "test-point-rework-to-qa.md",
            ARTIFACTS / "case-review-findings-product.json",
            ARTIFACTS / "case-review-findings-qa.json",
            ARTIFACTS / "case-review-findings-testability.json",
            ARTIFACTS / "case-review-findings-red-team.json",
        ):
            stale.unlink(missing_ok=True)

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
        print("=== QA Pipeline IDE-CHAIN mode（Task 子 Agent 在侧栏可见）===")
        print("Hook 将在 stop/subagentStop 时注入下一阶段 Task followup。\n")
    if ide:
        print("=== QA Pipeline IDE mode（使用 IDE 登录，无需 API Key）===")
        print("请在每个阶段按提示在 Composer 中执行，编排器将轮询产物并自动推进。\n")

    # Check base inputs
    for key in ("prd", "figma"):
        rel = pipeline.get("inputs", {}).get(key, "")
        if rel and not (ROOT / rel).exists():
            print(f"WARNING: missing input {rel}")

    if force:
        cleanup_outputs_for_stages(pipeline, stages_to_run + POST_BRANCHES)

    i = 0
    while i < len(stages_to_run):
        stage_id = stages_to_run[i]

        if stage_id in ("case-generate", *CASE_REVIEW_INTERNAL_STAGES) and not prd_analyze_outputs_exist():
            print(f"[{stage_id}] Gate: 请先完成 prd-analyze（唯一测试蓝图 + 知识库上下文）")
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
            prompt_path = write_prompt(args.platform, stage, pipeline, meta)
            if artifact_ready(stage_id):
                result = finalize_stage(stage_id, pipeline, meta)
                meta = load_meta()
                if result == "prd_rejected":
                    return 1
                if result == "retry_analyze":
                    st = stage_by_id(pipeline, "prd-analyze")
                    if st:
                        write_prompt(args.platform, st, pipeline, meta)
                    print(
                        "[ide-chain] 内部返工：等待 Hook 链式拉起 prd-analyze（已写入返工 prompt）\n"
                    )
                    return 0
                if result == "await_orchestrator":
                    return 1
                if result == "abort":
                    return 1
                i += 1
                continue
            print_ide_stage_guide(stage_id, prompt_path, i + 1, len(stages_to_run))
            mark_stage(meta, stage_id, "waiting_ide_task")
            print(
                f"[ide-chain] 等待 Hook 通过 followup 拉起 {stage_id} 子 Agent。"
                " 主 Agent 请勿在本回合手动 Task 各阶段。\n"
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
        if result == "await_orchestrator":
            return 1
        if result == "abort":
            return 1
        if result == "retry_generate":
            if "case-generate" in stages_to_run:
                i = stages_to_run.index("case-generate")
                continue
        if result == "retry_analyze":
            if "prd-analyze" in stages_to_run:
                st = stage_by_id(pipeline, "prd-analyze")
                if st:
                    write_prompt(args.platform, st, pipeline, meta)
                i = stages_to_run.index("prd-analyze")
                mark_stage(meta, "prd-analyze", "waiting_retry")
                if auto:
                    continue
                if ide_chain:
                    print(
                        "[ide-chain] 内部返工：等待 Hook 拉起 prd-analyze → case-generate → case-review\n"
                    )
                    return 0
                continue
        i += 1

    # Post-process
    if "test-execute" in stages_to_run or args.from_stage in POST_BRANCHES:
        post = stage_by_id(pipeline, "post-process")
        if post:
            has_pass, has_fail = execution_flags()
            if not (ARTIFACTS / "04-execution-result.json").exists() and (execute or auto):
                print("[post-process] Skipped: no execution result")
            else:
                for branch in post.get("branches", []):
                    bid = branch["id"]
                    if args.from_stage in POST_BRANCHES and bid != args.from_stage:
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

    if not meta.get("stage_result"):
        if not (args.dry_run and not auto and not execute and not ide and not ide_chain):
            meta["status"] = "completed" if (execute or auto or ide) else "dry_run"
        meta["completed_at"] = datetime.now(timezone.utc).isoformat()
    save_meta(meta)
    if auto or ide or ide_chain:
        _pipeline_active_clear()
    print("\nPipeline runner finished.")
    print(f"Meta: {ARTIFACTS / '00-meta.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
