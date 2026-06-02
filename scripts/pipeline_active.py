#!/usr/bin/env python3
"""QA pipeline session marker — hooks only run while this file is fresh."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACTIVE = ROOT / "workspace" / "artifacts" / ".qa-pipeline-active"
REJECT_NOTIFY = ROOT / "workspace" / "artifacts" / ".orchestrator-prd-reject-notified"
TTL_SECONDS = 4 * 3600


def touch(launch_mode: str = "ide", force: bool = False) -> None:
    """launch_mode: ide = Task 子 Agent（会话可见）; cli = 后台 cursor agent"""
    if launch_mode in ("auto", "auto-cli"):
        launch_mode = "cli"
    ACTIVE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE.write_text(
        json.dumps(
            {
                "started_at": datetime.now(timezone.utc).isoformat(),
                "launch_mode": launch_mode,
                "reason": launch_mode,
                "force": force,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def is_force_rerun() -> bool:
    if not ACTIVE.exists():
        return False
    try:
        data = json.loads(ACTIVE.read_text(encoding="utf-8"))
        return bool(data.get("force"))
    except (json.JSONDecodeError, KeyError):
        return False


def get_launch_mode() -> str:
    if not ACTIVE.exists():
        return "ide"
    try:
        data = json.loads(ACTIVE.read_text(encoding="utf-8"))
        mode = data.get("launch_mode") or data.get("reason") or "ide"
        return "cli" if mode in ("cli", "auto", "auto-cli") else "ide"
    except (json.JSONDecodeError, KeyError):
        return "ide"


def clear() -> None:
    if ACTIVE.exists():
        ACTIVE.unlink()


def is_active() -> bool:
    if not ACTIVE.exists():
        return False
    try:
        data = json.loads(ACTIVE.read_text(encoding="utf-8"))
        started = datetime.fromisoformat(data["started_at"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - started).total_seconds()
        return age < TTL_SECONDS
    except (json.JSONDecodeError, KeyError, ValueError):
        return False


def gate_reject_fingerprint() -> str:
    report = ROOT / "workspace" / "artifacts" / "00-prd-gate-report.json"
    if not report.exists():
        return ""
    data = json.loads(report.read_text(encoding="utf-8"))
    if data.get("verdict") != "reject":
        return ""
    rk = data.get("reject_kind") or "product"
    product_issues = [
        i for i in data.get("issues") or [] if (i.get("audience") or "product") == "product"
    ]
    if rk == "internal" or not product_issues:
        return ""
    ids = [i.get("id") for i in product_issues]
    return json.dumps(
        {
            "verdict": "reject",
            "reject_kind": rk,
            "checked_at": data.get("checked_at"),
            "issue_ids": ids,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def should_notify_reject() -> bool:
    fp = gate_reject_fingerprint()
    if not fp:
        return False
    if REJECT_NOTIFY.exists() and REJECT_NOTIFY.read_text(encoding="utf-8").strip() == fp:
        return False
    return True


def gate_internal_reject() -> bool:
    report = ROOT / "workspace" / "artifacts" / "00-prd-gate-report.json"
    if not report.exists():
        return False
    data = json.loads(report.read_text(encoding="utf-8"))
    if data.get("verdict") != "reject":
        return False
    rk = data.get("reject_kind") or "product"
    if rk == "internal":
        return True
    product_issues = [
        i for i in data.get("issues") or [] if (i.get("audience") or "product") == "product"
    ]
    return not product_issues


def mark_reject_notified() -> None:
    fp = gate_reject_fingerprint()
    if fp:
        REJECT_NOTIFY.parent.mkdir(parents=True, exist_ok=True)
        REJECT_NOTIFY.write_text(fp, encoding="utf-8")


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: touch [ide|cli]|clear|active|launch-mode|should-notify-reject|mark-reject-notified",
            file=sys.stderr,
        )
        return 2
    cmd = sys.argv[1]
    if cmd == "touch":
        mode = sys.argv[2] if len(sys.argv) > 2 else "ide"
        force = "--force" in sys.argv[3:] or (len(sys.argv) > 3 and sys.argv[3] == "1")
        touch(mode, force=force)
        return 0
    if cmd == "force":
        print("1" if is_force_rerun() else "0")
        return 0
    if cmd == "clear":
        clear()
        return 0
    if cmd == "active":
        print("1" if is_active() else "0")
        return 0
    if cmd == "launch-mode":
        print(get_launch_mode())
        return 0
    if cmd == "should-notify-reject":
        print("1" if should_notify_reject() else "0")
        return 0
    if cmd == "mark-reject-notified":
        mark_reject_notified()
        return 0
    if cmd == "internal-reject":
        print("1" if gate_internal_reject() else "0")
        return 0
    print(f"unknown: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
