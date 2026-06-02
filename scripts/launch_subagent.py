#!/usr/bin/env python3
"""Launch a QA pipeline sub-agent via platform CLI (Cursor / Codex / Claude Code)."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "workspace" / "artifacts" / "prompts"
LOGS = ROOT / "workspace" / "artifacts" / "logs"
DEFAULT_LOG_CHAR_LIMIT = 200_000


def wrap_launch_prompt(stage_id: str, prompt_path: Path) -> str:
    """Short launcher prompt — full task lives in prompts/{stage}.md."""
    rel = prompt_path.relative_to(ROOT)
    return f"""【QA 子 Agent 自动任务】阶段: {stage_id}

你是资深 QA 流水线中的独立子 Agent。请立即执行：

1. 打开并完整阅读任务文件: {rel}
2. 严格按其中 Agent 角色、Skill、输入/输出路径执行
3. 将产物写入任务文件规定的 workspace/artifacts/ 路径
4. 完成后在终端执行: python3 scripts/validate-artifacts.py --stage {stage_id}

项目根目录: {ROOT}
禁止进入下一流水线阶段，只完成本阶段。
"""


def check_platform(platform: str) -> tuple[bool, str]:
    if platform == "cursor":
        if shutil.which("cursor"):
            return True, "cursor CLI"
        return False, "未找到 cursor 命令"
    if platform == "codex":
        if shutil.which("codex"):
            return True, "codex CLI"
        return False, "未找到 codex 命令"
    if platform == "claude-code":
        if shutil.which("claude"):
            return True, "claude CLI"
        return False, "未找到 claude 命令"
    return False, f"未知平台: {platform}"


def check_auth_status(platform: str) -> tuple[bool, str]:
    ok, msg = check_platform(platform)
    if not ok:
        return ok, msg
    try:
        if platform == "cursor":
            if os.environ.get("CURSOR_API_KEY"):
                return True, "CURSOR_API_KEY 已设置"
            r = subprocess.run(
                ["cursor", "agent", "status"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            out = (r.stdout or "") + (r.stderr or "")
            if r.returncode == 0 and "not logged" not in out.lower():
                return True, "cursor agent CLI 已登录"
            return False, "Cursor CLI 未登录；请运行 cursor agent login"
        if platform == "codex":
            r = subprocess.run(
                ["codex", "doctor", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            try:
                data = json.loads(r.stdout or "{}")
                auth = (data.get("checks") or {}).get("auth.credentials") or {}
                if auth.get("status") == "ok":
                    return True, auth.get("summary") or "codex auth is configured"
            except json.JSONDecodeError:
                pass
            return False, "Codex CLI auth check failed; run codex login"
        if platform == "claude-code":
            r = subprocess.run(
                ["claude", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            out = (r.stdout or "") + (r.stderr or "")
            if r.returncode == 0 and "not" not in out.lower():
                return True, "claude auth status passed"
            return False, "Claude Code auth check failed; run claude auth login"
    except Exception as exc:
        return False, f"auth check failed: {exc}"
    return False, f"未知平台: {platform}"


def build_cmd(platform: str, stage_id: str, prompt_path: Path, model: str | None) -> list[str]:
    wrapper = wrap_launch_prompt(stage_id, prompt_path)
    full_prompt_path = prompt_path.resolve()

    if platform == "cursor":
        cmd = [
            "cursor", "agent", "-p",
            "--trust",
            "--force",
            "--workspace", str(ROOT),
            "--print",
            "--output-format", "stream-json",
            "--stream-partial-output",
        ]
        if model:
            cmd.extend(["--model", model])
        cmd.append(wrapper)
        return cmd

    if platform == "codex":
        cmd = ["codex", "exec", "--cd", str(ROOT)]
        if model:
            cmd.extend(["-m", model])
        if os.environ.get("QA_AGENT_YOLO") == "1":
            cmd.append("--dangerously-bypass-approvals-and-sandbox")
        return cmd

    if platform == "claude-code":
        cmd = [
            "claude", "-p",
            "--add-dir", str(ROOT),
            "--append-system-prompt", wrapper,
        ]
        if os.environ.get("QA_AGENT_YOLO") == "1":
            cmd.append("--allow-dangerously-skip-permissions")
        if model:
            cmd.extend(["--model", model])
        # Main prompt: read file instruction
        cmd.append(
            f"Execute QA stage {stage_id}. Read {full_prompt_path} and follow it exactly."
        )
        return cmd

    raise ValueError(platform)


def redact_cmd(cmd: list[str]) -> list[str]:
    redacted: list[str] = []
    skip_next = False
    for part in cmd:
        if skip_next:
            redacted.append("***REDACTED***")
            skip_next = False
            continue
        redacted.append(part)
        if part in ("--api-key", "--header"):
            skip_next = True
    return redacted


def truncate_log(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    head = text[: limit // 2]
    tail = text[-limit // 2 :]
    return f"{head}\n\n...[truncated {len(text) - limit} chars]...\n\n{tail}"


def stdin_payload(platform: str, stage_id: str, prompt_path: Path) -> str | None:
    if platform != "codex":
        return None
    wrapper = wrap_launch_prompt(stage_id, prompt_path)
    body = prompt_path.read_text(encoding="utf-8")
    return f"{wrapper}\n\n---\n\n{body}"


def launch(
    platform: str,
    stage_id: str,
    prompt_path: Path | None = None,
    model: str | None = None,
    timeout_sec: int = 3600,
) -> int:
    prompt_path = prompt_path or (PROMPTS / f"{stage_id}.md")
    if not prompt_path.exists():
        print(f"ERROR: prompt not found: {prompt_path}", file=sys.stderr)
        return 2

    ok, msg = check_platform(platform)
    if not ok:
        print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"{platform}-{stage_id}.log"
    summary_path = LOGS / f"{platform}-{stage_id}.summary.json"

    cmd = build_cmd(platform, stage_id, prompt_path, model)
    print(f"[launch] platform={platform} stage={stage_id}")
    print(f"[launch] cmd: {' '.join(cmd[:8])}...")
    print(f"[launch] log: {log_path}")

    env = os.environ.copy()
    env["QA_AGENT_ROOT"] = str(ROOT)
    env["QA_PIPELINE_STAGE"] = stage_id

    stdin_data = stdin_payload(platform, stage_id, prompt_path)
    log_limit = int(os.environ.get("QA_AGENT_LOG_CHAR_LIMIT", str(DEFAULT_LOG_CHAR_LIMIT)))
    full_logs = os.environ.get("QA_AGENT_LOG_FULL") == "1"
    try:
        with log_path.open("w", encoding="utf-8") as logf:
            logf.write(f"command: {redact_cmd(cmd)}\n\n")
            logf.flush()
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT),
                env=env,
                input=stdin_data,
                text=True,
                capture_output=True,
                timeout=timeout_sec,
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            logf.write("=== stdout ===\n")
            logf.write(stdout if full_logs else truncate_log(stdout, log_limit))
            logf.write("\n=== stderr ===\n")
            logf.write(stderr if full_logs else truncate_log(stderr, log_limit))
            logf.write(f"\n=== exit code: {proc.returncode} ===\n")
            summary_path.write_text(
                json.dumps(
                    {
                        "platform": platform,
                        "stage": stage_id,
                        "prompt": str(prompt_path.relative_to(ROOT)),
                        "log": str(log_path.relative_to(ROOT)),
                        "exit_code": proc.returncode,
                        "stdout_chars": len(stdout),
                        "stderr_chars": len(stderr),
                        "truncated": not full_logs and (len(stdout) > log_limit or len(stderr) > log_limit),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        if proc.stdout:
            print(proc.stdout[-4000:] if len(proc.stdout) > 4000 else proc.stdout)
        if proc.returncode != 0 and proc.stderr:
            print(proc.stderr[-2000:], file=sys.stderr)
        return proc.returncode
    except subprocess.TimeoutExpired:
        print(f"ERROR: stage {stage_id} timed out after {timeout_sec}s", file=sys.stderr)
        return 124
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch QA sub-agent via platform CLI")
    parser.add_argument("--platform", required=True, choices=["cursor", "codex", "claude-code"])
    parser.add_argument("--stage", required=True, help="Stage id, e.g. prd-analyze")
    parser.add_argument("--prompt", type=Path, help="Path to prompt markdown")
    parser.add_argument("--model", help="Override model for platform CLI")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--check", action="store_true", help="Only check CLI availability")
    args = parser.parse_args()

    if args.check:
        ok, msg = check_auth_status(args.platform)
        print(f"{'OK' if ok else 'FAIL'}: {msg}")
        if args.platform == "cursor" and not ok:
            if os.environ.get("CURSOR_API_KEY"):
                print("OK: CURSOR_API_KEY 已设置（可用于 --auto）")
            else:
                try:
                    r = subprocess.run(
                        ["cursor", "agent", "status"],
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )
                    out = (r.stdout or "") + (r.stderr or "")
                    if "logged in" in out.lower() and "not logged" not in out.lower():
                        print("OK: cursor agent CLI 已登录（可用于 --auto）")
                    else:
                        print("WARN: IDE 已登录 ≠ CLI 已登录")
                        print("  方案 A: 终端执行  cursor agent login  （浏览器，无需 API Key）")
                        print("  方案 B: Cursor 设置 → 生成 API Key → export CURSOR_API_KEY=...")
                        print("  方案 C: 使用  ./orchestrators/cursor/run-pipeline.sh --ide  （在 IDE 里手动跑）")
                except Exception:
                    print("WARN: 无法检测 cursor agent 登录态")
        return 0 if ok else 1

    return launch(args.platform, args.stage, args.prompt, args.model, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
