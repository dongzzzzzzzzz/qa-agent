#!/usr/bin/env python3
"""Append auditable case-review orchestration trace events."""

from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERSPECTIVE_SLUGS = {
    "product": "product",
    "qa": "qa",
    "testability": "testability",
    "red_team": "red-team",
    "red-team": "red-team",
}


def artifacts_dir() -> Path:
    if os.environ.get("QA_WORKSPACE"):
        return Path(os.environ["QA_WORKSPACE"])
    return ROOT / "workspace" / "artifacts"


def trace_path() -> Path:
    return artifacts_dir() / "case-review-orchestration-trace.jsonl"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def prompt_path(perspective: str) -> str:
    slug = PERSPECTIVE_SLUGS[perspective]
    return display_path(artifacts_dir() / "prompts" / f"case-review-{slug}.md")


def findings_path(perspective: str) -> str:
    slug = PERSPECTIVE_SLUGS[perspective]
    return display_path(artifacts_dir() / f"case-review-findings-{slug}.json")


def append_event(event: dict) -> Path:
    path = trace_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    event.setdefault("at", datetime.now(timezone.utc).isoformat())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def load_launch_lock(path_str: str | None) -> dict:
    if not path_str:
        return {}
    path = Path(path_str)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        return {"launch_lock_path": display_path(path), "launch_lock_missing": True}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "launch_lock_path": display_path(path),
            "launch_lock_error": str(exc),
        }
    data["launch_lock_path"] = display_path(path)
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("event")
    parser.add_argument("--perspective", choices=["product", "qa", "testability", "red_team", "red-team"])
    parser.add_argument("--agent-id")
    parser.add_argument("--agent-id-unavailable-reason")
    parser.add_argument("--summary")
    parser.add_argument("--validate-result", choices=["pass", "fail"])
    parser.add_argument("--validate-command")
    parser.add_argument("--error")
    parser.add_argument("--stage-name")
    parser.add_argument("--launch-id")
    parser.add_argument("--launch-lock-path")
    parser.add_argument("--from-launch-lock")
    parser.add_argument("--launched-by")
    parser.add_argument("--round-id")
    args = parser.parse_args()

    perspective = "red_team" if args.perspective == "red-team" else args.perspective
    event = {"event": args.event}
    lock_data = load_launch_lock(args.from_launch_lock or args.launch_lock_path)
    if lock_data:
        for key in ("stage_name", "launch_id", "launch_lock_path", "prompt_path"):
            if lock_data.get(key) and key not in event:
                event[key] = lock_data[key]
        if lock_data.get("round_id"):
            event["round_id"] = lock_data["round_id"]
        if lock_data.get("launch_lock_missing"):
            event["launch_lock_missing"] = True
        if lock_data.get("launch_lock_error"):
            event["launch_lock_error"] = lock_data["launch_lock_error"]
    if args.stage_name:
        event["stage_name"] = args.stage_name
    if args.launch_id:
        event["launch_id"] = args.launch_id
    if args.launch_lock_path:
        event["launch_lock_path"] = display_path(Path(args.launch_lock_path))
    if args.launched_by:
        event["launched_by"] = args.launched_by
    if args.round_id:
        event["round_id"] = args.round_id
    if perspective:
        event["perspective"] = perspective
        if args.event in {
            "perspective_task_started",
            "perspective_task_completed",
            "perspective_task_failed",
            "perspective_task_cancelled",
            "perspective_validate_passed",
        }:
            event["prompt_path"] = prompt_path(perspective)
            event["findings_path"] = findings_path(perspective)
    if args.agent_id:
        event["agent_id"] = args.agent_id
    if args.agent_id_unavailable_reason:
        event["agent_id_unavailable_reason"] = args.agent_id_unavailable_reason
    if args.summary:
        event["summary"] = args.summary
    if args.validate_result:
        event["validate_result"] = args.validate_result
    if args.validate_command:
        event["validate_command"] = args.validate_command
    elif perspective and args.event == "perspective_validate_passed":
        event["validate_command"] = (
            f"python3 scripts/validate-artifacts.py --stage case-review-perspective --perspective {perspective}"
        )
        event.setdefault("validate_result", "pass")
    if args.error:
        event["error"] = args.error
    event.setdefault("trace_event_id", str(uuid.uuid4()))
    path = append_event(event)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
