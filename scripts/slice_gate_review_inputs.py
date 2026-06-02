#!/usr/bin/env python3
"""Build role-scoped JSON slices for prd-gate sub-reviews."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "workspace" / "artifacts"
INPUTS = ROOT / "workspace" / "inputs"
SLICES = ARTIFACTS / ".gate-slices"
BLUEPRINT = ARTIFACTS / "00-test-ready-blueprint.json"
OBLIGATIONS = ARTIFACTS / "00-test-obligations.json"
PRD = INPUTS / "prd.md"
PRECHECK = ARTIFACTS / ".test-point-coverage-precheck.json"


def load(path: Path) -> dict | list | str:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    return text


def _obligation_summary(obligations: list[dict]) -> list[dict]:
    return [
        {
            "id": o["id"],
            "statement": o.get("statement"),
            "predicate": o.get("predicate"),
            "risk": o.get("risk"),
            "kind": o.get("kind"),
            "prd_section": o.get("prd_section"),
            "source": o.get("source"),
            "covered_by_scenarios": o.get("covered_by_scenarios"),
        }
        for o in obligations
    ]


def _sc_index(scenarios: list[dict]) -> list[dict]:
    return [
        {
            "id": s["id"],
            "title": s.get("title"),
            "module_id": s.get("module_id"),
            "type": s.get("type"),
            "priority": s.get("priority"),
            "covers_obligations": s.get("covers_obligations"),
            "prd_section": s.get("prd_section"),
        }
        for s in scenarios
    ]


def _prd_excerpt(prd_text: str, sections: list[str], max_chars: int = 12000) -> str:
    if not prd_text or not sections:
        return (prd_text or "")[:max_chars]
    chunks: list[str] = []
    for sec in sections:
        marker = sec.strip()
        if not marker:
            continue
        idx = prd_text.find(marker)
        if idx >= 0:
            chunks.append(prd_text[idx : idx + 4000])
    blob = "\n---\n".join(chunks) if chunks else prd_text[:max_chars]
    return blob[:max_chars]


def build_product_slice(bp: dict, ob: dict) -> dict:
    return {
        "lens": "product",
        "prd_path": str(PRD.relative_to(ROOT)),
        "obligations": _obligation_summary(ob.get("obligations") or []),
        "scenario_index": _sc_index(bp.get("scenarios") or []),
        "assumptions": bp.get("assumptions") or [],
        "resolutions": bp.get("resolutions") or [],
        "state_machines": ob.get("state_machines") or [],
        "precheck_summary": (load(PRECHECK) or {}).get("coverage_score"),
    }


def build_dev_slice(bp: dict, ob: dict, prd_text: str) -> dict:
    p0_ids = {o["id"] for o in (ob.get("obligations") or []) if o.get("risk") == "P0"}
    sections = list(
        {
            (o.get("prd_section") or "").strip()
            for o in (ob.get("obligations") or [])
            if o.get("risk") == "P0" and o.get("prd_section")
        }
    )
    scenarios = []
    for s in bp.get("scenarios") or []:
        cov = set(s.get("covers_obligations") or [])
        if cov & p0_ids:
            scenarios.append(s)
    dc = bp.get("delivery_coverage") or {}
    figma = dc.get("figma") or {}
    return {
        "lens": "dev",
        "api_endpoints": bp.get("api_endpoints") or [],
        "field_rules": bp.get("field_rules") or [],
        "main_flows": bp.get("main_flows") or [],
        "figma_mapping": bp.get("figma_mapping") or [],
        "figma_frames_inventory": figma.get("frames_inventory") or [],
        "figma_read_complete": figma.get("read_complete"),
        "prd_excerpt": _prd_excerpt(prd_text, sections),
        "p0_scenarios_full": scenarios,
        "p0_obligation_ids": sorted(p0_ids),
    }


def build_qa_slice(bp: dict, ob: dict, precheck: dict) -> dict:
    findings_paths = [
        "workspace/artifacts/gate-findings-product.json",
        "workspace/artifacts/gate-findings-dev.json",
    ]
    prior = {}
    for rel in findings_paths:
        p = ROOT / rel
        if p.exists():
            prior[p.name] = load(p)
    return {
        "lens": "qa",
        "blueprint_path": str(BLUEPRINT.relative_to(ROOT)),
        "obligations_path": str(OBLIGATIONS.relative_to(ROOT)),
        "precheck": precheck,
        "prior_findings": prior,
        "coverage_matrix": bp.get("coverage_matrix") or [],
    }


def main() -> int:
    if not BLUEPRINT.exists() or not OBLIGATIONS.exists():
        print("Missing blueprint or obligations", file=sys.stderr)
        return 1
    bp = load(BLUEPRINT)
    ob = load(OBLIGATIONS)
    prd_text = load(PRD) if isinstance(load(PRD), str) else ""
    precheck = load(PRECHECK) if PRECHECK.exists() else {}

    SLICES.mkdir(parents=True, exist_ok=True)
    slices = {
        "product.json": build_product_slice(bp, ob),
        "dev.json": build_dev_slice(bp, ob, prd_text if isinstance(prd_text, str) else ""),
        "qa.json": build_qa_slice(bp, ob, precheck if isinstance(precheck, dict) else {}),
    }
    for name, data in slices.items():
        out = SLICES / name
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
