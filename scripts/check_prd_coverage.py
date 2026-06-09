#!/usr/bin/env python3
"""Print PRD obligation coverage matrix; exit 1 if any obligation fails."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from load_project_config import load_project_config  # noqa: E402
from qa_coverage_checks import (  # noqa: E402
    build_prd_coverage_matrix,
    validate_prd_obligations,
    write_prd_coverage_matrix,
)

import os as _os
BLUEPRINT = (__import__("pathlib").Path(_os.environ["QA_WORKSPACE"]) if _os.environ.get("QA_WORKSPACE") else ROOT / "workspace" / "artifacts") / "00-test-blueprint.json"


def main() -> int:
    if not BLUEPRINT.exists():
        print(f"missing blueprint: {BLUEPRINT}", file=sys.stderr)
        return 1
    blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    config = load_project_config()
    matrix = build_prd_coverage_matrix(blueprint, config)
    out = write_prd_coverage_matrix(blueprint, config)
    print(f"wrote {out}")
    for row in matrix.get("obligations") or []:
        mark = "PASS" if row.get("status") == "pass" else "FAIL"
        print(
            f"  [{mark}] {row.get('id')}: {row.get('label')} "
            f"({row.get('matched_count')}/{row.get('min_scenarios')})"
        )
    errors = validate_prd_obligations(blueprint, config)
    if errors:
        print("\nUnresolved:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("\nAll PRD obligations satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
