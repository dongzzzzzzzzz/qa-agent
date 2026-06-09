#!/usr/bin/env python3
"""
Centralized workspace path resolution for all QA pipeline scripts.

Priority order for workspace resolution:
1. QA_WORKSPACE env var (full path to artifacts dir)
2. QA_PROJECT env var (project slug → workspace/projects/<slug>/current)
3. Default: workspace/artifacts (backward compatible)

Usage:
    from workspace_paths import get_artifacts_dir, get_inputs_dir

    ARTIFACTS = get_artifacts_dir()
    INPUTS = get_inputs_dir()
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def slugify(name: str) -> str:
    """Convert a project name to a filesystem-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:64]


def get_project_slug() -> str | None:
    """Return project slug from env, or auto-detect from config.yaml."""
    if os.environ.get("QA_PROJECT"):
        return slugify(os.environ["QA_PROJECT"])

    config_path = ROOT / "workspace" / "inputs" / "config.yaml"
    if config_path.exists():
        try:
            import yaml  # type: ignore
            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            name = (cfg or {}).get("project_name", "")
            if name:
                return slugify(name)
        except Exception:
            pass

    return None


def get_run_id(artifacts_dir: Path | None = None) -> str | None:
    """Read run_id from 00-meta.json in the given artifacts dir."""
    target = artifacts_dir or get_artifacts_dir()
    meta_path = target / "00-meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            return meta.get("run_id")
        except Exception:
            pass
    return None


def get_artifacts_dir() -> Path:
    """
    Return the active artifacts directory.

    Resolution order:
    1. QA_WORKSPACE env var (full path)
    2. QA_PROJECT env var or auto-detected slug → projects/<slug>/current
    3. Default: workspace/artifacts
    """
    if os.environ.get("QA_WORKSPACE"):
        return Path(os.environ["QA_WORKSPACE"])

    slug = get_project_slug()
    if slug:
        current = ROOT / "workspace" / "projects" / slug / "current"
        # current is a symlink to the latest run; if it exists use it
        if current.exists() or current.is_symlink():
            return current
        # project exists but no run yet — fall through to default so first run
        # can be bootstrapped by pipeline_runner.py

    return ROOT / "workspace" / "artifacts"


def get_inputs_dir() -> Path:
    """
    Return the active inputs directory.

    For a project-based workspace, inputs live at:
      workspace/projects/<slug>/inputs/

    Falls back to workspace/inputs/ for backward compatibility.
    """
    if os.environ.get("QA_INPUTS"):
        return Path(os.environ["QA_INPUTS"])

    slug = get_project_slug()
    if slug:
        project_inputs = ROOT / "workspace" / "projects" / slug / "inputs"
        if project_inputs.exists():
            return project_inputs

    return ROOT / "workspace" / "inputs"
