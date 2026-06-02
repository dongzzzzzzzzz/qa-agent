#!/usr/bin/env python3
"""Validate test obligations (TOG) coverage against blueprint scenarios."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
BLUEPRINT = ARTIFACTS / "00-test-ready-blueprint.json"
OBLIGATIONS = ARTIFACTS / "00-test-obligations.json"
PRECHECK_OUT = ARTIFACTS / ".test-point-coverage-precheck.json"

TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]{2,}", re.UNICODE)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in TOKEN_RE.findall(text or "")}


def _predicate_overlap(predicate: str, scenario_blob: str) -> float:
    pred = _tokens(predicate)
    if not pred:
        return 0.0
    blob = _tokens(scenario_blob)
    if not blob:
        return 0.0
    hit = len(pred & blob)
    return hit / max(len(pred), 1)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(
    blueprint: dict,
    obligations_doc: dict,
    *,
    false_coverage_threshold: float = 0.15,
    min_predicate_tokens: int = 2,
) -> tuple[list[str], dict]:
    errors: list[str] = []
    obligations = obligations_doc.get("obligations") or []
    scenarios = blueprint.get("scenarios") or []
    ob_by_id = {o["id"]: o for o in obligations}
    sc_by_id = {s["id"]: s for s in scenarios}

    if not obligations:
        errors.append("obligations[] is empty — prd-analyze must produce 00-test-obligations.json")
        return errors, {}

    p0_obs = [o for o in obligations if o.get("risk") == "P0"]
    uncovered_p0: list[str] = []
    for o in p0_obs:
        covers = set(o.get("covered_by_scenarios") or [])
        for sc in scenarios:
            if o["id"] in (sc.get("covers_obligations") or []):
                covers.add(sc["id"])
        if not covers:
            uncovered_p0.append(o["id"])
            errors.append(
                f"P0 obligation {o['id']} has no covering scenario (covered_by_scenarios / covers_obligations)"
            )

    false_coverage: list[dict] = []
    for sc in scenarios:
        oid_list = sc.get("covers_obligations") or []
        if not oid_list:
            if sc.get("priority") == "P0":
                errors.append(f"{sc['id']}: P0 scenario missing covers_obligations[]")
            continue
        blob = " ".join(
            [
                sc.get("title", ""),
                " ".join(sc.get("steps") or []),
                " ".join(sc.get("expected") or []),
            ]
        )
        for oid in oid_list:
            if oid not in ob_by_id:
                errors.append(f"{sc['id']}: covers unknown obligation {oid}")
                continue
            pred = ob_by_id[oid].get("predicate", "")
            if len(_tokens(pred)) < min_predicate_tokens:
                continue
            overlap = _predicate_overlap(pred, blob)
            if overlap < false_coverage_threshold:
                false_coverage.append(
                    {
                        "scenario_id": sc["id"],
                        "obligation_ids": [oid],
                        "reason": (
                            f"steps/expected weakly match predicate (overlap={overlap:.2f} < {false_coverage_threshold})"
                        ),
                    }
                )

    orphan_sc = []
    all_cover_refs = set()
    for sc in scenarios:
        for oid in sc.get("covers_obligations") or []:
            all_cover_refs.add(oid)
        if not sc.get("covers_obligations") and sc.get("priority") != "P3":
            if not sc.get("prd_section") and not sc.get("figma_ref"):
                orphan_sc.append(sc["id"])

    for oid, o in ob_by_id.items():
        if o.get("risk") != "P0":
            continue
        if not (o.get("covered_by_scenarios") or oid in all_cover_refs):
            if oid not in uncovered_p0:
                uncovered_p0.append(oid)

    p0_total = len(p0_obs) or 1
    covered_p0 = p0_total - len(set(uncovered_p0))
    coverage_score = covered_p0 / p0_total

    precheck = {
        "ok": len(errors) == 0 and not false_coverage,
        "coverage_score": round(coverage_score, 4),
        "obligations_total": len(obligations),
        "obligations_p0_total": len(p0_obs),
        "obligations_p0_uncovered": sorted(set(uncovered_p0)),
        "scenarios_total": len(scenarios),
        "false_coverage": false_coverage,
        "false_coverage_count": len(false_coverage),
        "orphan_scenario_ids": orphan_sc,
    }
    return errors, precheck


def main() -> int:
    if not BLUEPRINT.exists():
        print(f"Missing {BLUEPRINT}", file=sys.stderr)
        return 1
    if not OBLIGATIONS.exists():
        print(f"Missing {OBLIGATIONS}", file=sys.stderr)
        return 1
    bp = load_json(BLUEPRINT)
    ob = load_json(OBLIGATIONS)
    errors, precheck = validate(bp, ob)
    PRECHECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    PRECHECK_OUT.write_text(json.dumps(precheck, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(precheck, ensure_ascii=False, indent=2))
    if errors:
        print("FAIL obligation coverage:", file=sys.stderr)
        for e in errors[:20]:
            print(f"  - {e}", file=sys.stderr)
        if len(errors) > 20:
            print(f"  ... {len(errors)} total", file=sys.stderr)
        return 1
    if precheck.get("false_coverage_count", 0) > 0:
        print(
            f"WARN false_coverage: {precheck['false_coverage_count']} (see {PRECHECK_OUT.name})",
            file=sys.stderr,
        )
    print(f"OK obligation coverage → {PRECHECK_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
