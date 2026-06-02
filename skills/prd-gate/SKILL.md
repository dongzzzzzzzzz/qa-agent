---
name: prd-gate
description: >-
  TOG 义务覆盖校验 + 产品/研发/测试三角评审 + 红队 + 门禁归并。产出 pass/reject 与产品/QA
  分流 MD。适用于 prd-gate 阶段与子 Agent 编排。
disable-model-invocation: true
---

# PRD 门禁 v2（TOG + 三角评审 + 红队）

## 流程概览

```text
scripts 前置 → product-review → dev-review → qa-review → red-team → gatekeeper 归并
```

| 子阶段 | Agent | 产出 |
|--------|-------|------|
| 脚本 | — | `.test-point-coverage-precheck.json`, `.gate-slices/*.json` |
| 产品 | gate-product-reviewer | `gate-findings-product.json` |
| 研发 | gate-dev-reviewer | `gate-findings-dev.json` |
| 测试 | gate-qa-reviewer | `gate-findings-qa.json` |
| 红队 | test-point-red-team | `gate-findings-red-team.json` |
| 归并 | prd-gatekeeper | `00-prd-gate-report.json` |

`--auto` 模式由 `pipeline_runner` 顺序拉起；IDE 模式见 `workspace/artifacts/prompts/prd-gate*.md`。

## 前置

```bash
python3 scripts/analyze_gate_prerequisites.py
python3 scripts/validate_obligation_coverage.py
python3 scripts/slice_gate_review_inputs.py
```

须存在 `00-test-obligations.json`（由 prd-analyze 产出 TOG）。

## 裁决

| verdict | 条件 | 后续 |
|---------|------|------|
| pass | `issues[]` 空 + `coverage_score` ≥ 阈值（默认 0.90） | case-generate |
| reject + product issues | `audience=product` | `prd-reject-to-product.md`，停流水线 |
| reject + 仅 internal | `qa_undercoverage` 等 | `test-point-rework-to-qa.md`，回 prd-analyze |

每条 issue 必填：`dimension`, `root_cause`, `audience`, `retry_target`。

## 脚本

```bash
python3 scripts/generate_gate_prompts.py
python3 scripts/validate-artifacts.py --stage prd-gate
python3 scripts/render_prd_gate_notice.py
```

## 延伸阅读

- [reference.md](reference.md) — 交付物维度
- [reference-test-point-review.md](reference-test-point-review.md) — 义务评审与归并
- [examples.md](examples.md)
