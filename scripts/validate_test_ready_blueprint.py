#!/usr/bin/env python3
"""Business validation for test-ready blueprint."""

from __future__ import annotations

import json
import re
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent.parent / "workspace" / "artifacts"

PRODUCT_PHRASES = (
    "需产品确认",
    "待产品确认",
    "待产品补充",
    "请产品",
    "找产品",
)

SCENARIO_MAX = {"small": 30, "medium": 60, "large": 100, "xlarge": 150}

SCALE_MIN_SCENARIOS = {"small": 15, "medium": 35, "large": 55, "xlarge": 80}

FIGMA_PLACEHOLDER_MARKERS = (
    "placeholder",
    "figma-not-provided",
    "not-provided",
    "example.com",
    "qa-agent.invalid",
)

# Figma node id: digits:digits; reject PRD page aliases like prd-p12
FIGMA_NODE_ID_RE = re.compile(r"^\d+:\d+$")
PRD_FAKE_NODE_RE = re.compile(r"^prd-p\d+$", re.I)


def _figma_url_is_placeholder(url: str) -> bool:
    lower = (url or "").lower()
    return any(m in lower for m in FIGMA_PLACEHOLDER_MARKERS)


def _validate_figma_delivery(figma: dict) -> list[str]:
    errors: list[str] = []
    urls = [u for u in (figma.get("urls") or []) if u and str(u).strip()]
    read_complete = figma.get("read_complete") is True
    any_placeholder = any(_figma_url_is_placeholder(u) for u in urls)

    if any_placeholder and read_complete:
        errors.append(
            "delivery_coverage.figma.read_complete cannot be true when figma.url is placeholder"
        )
        return errors

    if not read_complete:
        if urls and not any_placeholder:
            errors.append(
                "delivery_coverage.figma.read_complete is false but non-placeholder URLs exist — "
                "complete Figma MCP read or remove URLs"
            )
        return errors

    if not urls:
        errors.append("delivery_coverage.figma.read_complete=true requires figma.urls[]")
        return errors

    if any_placeholder:
        errors.append("cannot mark figma read_complete with placeholder URLs")

    frames = figma.get("frames_inventory") or []
    if len(frames) < 1:
        errors.append(
            "delivery_coverage.figma.frames_inventory must list Frames when read_complete=true"
        )

    for i, fr in enumerate(frames):
        prefix = f"delivery_coverage.figma.frames_inventory[{i}]"
        nid = (fr.get("node_id") or "").strip()
        if not nid:
            errors.append(f"{prefix}: node_id required when figma.read_complete=true")
        elif PRD_FAKE_NODE_RE.match(nid):
            errors.append(
                f"{prefix}: node_id '{nid}' looks like PRD alias, not Figma — use MCP metadata id"
            )
        elif not FIGMA_NODE_ID_RE.match(nid):
            errors.append(
                f"{prefix}: node_id '{nid}' should match Figma format (e.g. 12:345)"
            )

    return errors


def validate_delivery_coverage(data: dict, scenarios: list) -> list[str]:
    errors: list[str] = []
    dc = data.get("delivery_coverage")
    if not dc:
        errors.append("missing delivery_coverage (全文阅读与功能点映射证明)")
        return errors

    if dc.get("executed_by") != "prd-analyzer-subagent":
        errors.append(
            "delivery_coverage.executed_by must be 'prd-analyzer-subagent' "
            "(禁止主 Agent/脚本代写 analyze)"
        )

    scale = dc.get("project_scale", "")
    if scale not in SCENARIO_MAX:
        errors.append(f"invalid project_scale: {scale}")
    else:
        min_table = SCALE_MIN_SCENARIOS[scale]
        min_declared = dc.get("scenario_minimum_required", 0)
        if min_declared < min_table:
            errors.append(
                f"scenario_minimum_required {min_declared} < scale minimum {min_table} for {scale}"
            )
        if len(scenarios) < min_declared:
            errors.append(
                f"scenarios count {len(scenarios)} < scenario_minimum_required {min_declared}"
            )
        if len(scenarios) < min_table:
            errors.append(
                f"scenarios count {len(scenarios)} < scale floor {min_table} ({scale})"
            )
        if len(scenarios) > SCENARIO_MAX[scale]:
            errors.append(f"scenarios count {len(scenarios)} > max {SCENARIO_MAX[scale]}")

    prd = dc.get("prd") or {}
    if not prd.get("read_complete"):
        errors.append("delivery_coverage.prd.read_complete must be true")
    for i, src in enumerate(prd.get("sources") or []):
        if not src.get("read_complete"):
            errors.append(f"delivery_coverage.prd.sources[{i}].read_complete must be true")
        pt = src.get("pages_total")
        pr = src.get("pages_read")
        if pt is not None and pr is not None and pr < pt:
            errors.append(
                f"delivery_coverage.prd.sources[{i}]: pages_read {pr} < pages_total {pt}"
            )

    fp_count = prd.get("functional_points_count", 0)
    fp_mapped = prd.get("functional_points_mapped", 0)
    if fp_count < 1:
        errors.append("functional_points_count must be >= 1")
    if fp_mapped < fp_count:
        errors.append(
            f"functional_points_mapped {fp_mapped} < functional_points_count {fp_count}"
        )

    in_scope_missing = []
    for i, sec in enumerate(prd.get("sections_inventory") or []):
        if not sec.get("in_scope"):
            continue
        ids = sec.get("scenario_ids") or []
        if not ids:
            in_scope_missing.append(sec.get("section_id") or sec.get("title") or f"[{i}]")
    if in_scope_missing:
        preview = ", ".join(in_scope_missing[:5])
        suffix = "..." if len(in_scope_missing) > 5 else ""
        errors.append(
            f"in_scope sections without scenario_ids: {preview}{suffix} ({len(in_scope_missing)} total)"
        )

    figma = dc.get("figma") or {}
    errors.extend(_validate_figma_delivery(figma))

    return errors


def validate_test_ready_blueprint(data: dict) -> list[str]:
    errors: list[str] = []
    gaps = data.get("blocking_gaps") or []
    if gaps:
        errors.append(f"blocking_gaps must be empty, got {len(gaps)}")

    modules = {m["id"]: m for m in data.get("modules") or []}
    p0_modules = [m["id"] for m in data.get("modules") or [] if m.get("priority") == "P0"]
    scenarios = data.get("scenarios") or []

    errors.extend(validate_delivery_coverage(data, scenarios))

    p0_scenario_modules = {
        s["module_id"] for s in scenarios if s.get("priority") == "P0"
    }
    for mid in p0_modules:
        if mid not in p0_scenario_modules:
            errors.append(f"P0 module {mid} has no P0 scenario")

    assumptions = {a["id"]: a for a in data.get("assumptions") or []}
    obligations_path = ARTIFACTS / "00-test-obligations.json"
    obligation_ids: set[str] = set()
    if obligations_path.exists():
        try:
            ob_doc = json.loads(obligations_path.read_text(encoding="utf-8"))
            obligation_ids = {o["id"] for o in ob_doc.get("obligations") or []}
        except json.JSONDecodeError:
            errors.append("invalid 00-test-obligations.json")
    else:
        errors.append(
            "missing workspace/artifacts/00-test-obligations.json — "
            "prd-analyze must produce test obligations (TOG)"
        )

    for i, sc in enumerate(scenarios):
        prefix = f"scenarios[{i}]"
        covers = sc.get("covers_obligations") or []
        if sc.get("priority") in ("P0", "P1") and not covers:
            errors.append(f"{prefix}: covers_obligations required for P0/P1 scenarios")
        for oid in covers:
            if obligation_ids and oid not in obligation_ids:
                errors.append(f"{prefix}: unknown obligation {oid} in covers_obligations")
        if sc.get("source") == "assumption":
            aid = sc.get("assumption_id")
            if not aid or aid not in assumptions:
                errors.append(f"{prefix}: assumption_id required and must exist in assumptions[]")
        if not sc.get("prd_section") and not sc.get("figma_ref"):
            errors.append(f"{prefix}: requires prd_section or figma_ref (traceability)")
        blob = " ".join(
            [
                sc.get("title", ""),
                " ".join(sc.get("steps") or []),
                " ".join(sc.get("expected") or []),
            ]
        )
        for phrase in PRODUCT_PHRASES:
            if phrase in blob:
                errors.append(f"{prefix}: contains product-escalation phrase '{phrase}'")

    for i, asm in enumerate(data.get("assumptions") or []):
        blob = f"{asm.get('statement', '')} {asm.get('test_rule', '')}"
        for phrase in PRODUCT_PHRASES:
            if phrase in blob:
                errors.append(f"assumptions[{i}]: contains '{phrase}'")

    matrix = {row["module_id"]: row for row in data.get("coverage_matrix") or []}
    for mid in p0_modules:
        row = matrix.get(mid)
        if not row:
            errors.append(f"coverage_matrix missing P0 module {mid}")
            continue
        for key in ("functional", "boundary", "exception"):
            if not row.get(key):
                errors.append(f"coverage_matrix.{mid}.{key} must be true for P0")

    return errors
