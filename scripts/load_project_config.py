#!/usr/bin/env python3
"""Load workspace/inputs/config.yaml for project-specific QA scope."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = Path(os.environ.get("QA_INPUTS", str(ROOT / "workspace" / "inputs"))) / "config.yaml"

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def load_project_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or DEFAULT_CONFIG
    if not cfg_path.exists() or yaml is None:
        return {}
    with cfg_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def excluded_test_types(config: dict[str, Any] | None = None) -> set[str]:
    cfg = config if config is not None else load_project_config()
    raw = cfg.get("exclude_test_types") or []
    return {str(x).strip() for x in raw if str(x).strip()}


def excluded_modules(config: dict[str, Any] | None = None) -> set[str]:
    cfg = config if config is not None else load_project_config()
    raw = cfg.get("exclude_module_ids") or []
    return {str(x).strip() for x in raw if str(x).strip()}


def scope_notes(config: dict[str, Any] | None = None) -> str:
    cfg = config if config is not None else load_project_config()
    return (cfg.get("test_scope_notes") or "").strip()
