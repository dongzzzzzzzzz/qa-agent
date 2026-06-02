# 义务级评审与归并（gatekeeper）

## 归并 findings → issues

1. 读取四份 `gate-findings-*.json`，`verdict=fail` 的 finding 转为 `GATE-NNN`
2. 合并同一 `obligation_ids` / `prd_section` 的重复项
3. 冲突优先级：**PRD 明文缺失** > **qa_undercoverage**

## issue 字段

| 字段 | 说明 |
|------|------|
| `dimension` | `delivery` / `test_point_coverage` / `obligation_coverage` |
| `root_cause` | `prd` / `figma` / `qa_undercoverage` / `assumption_unresolved` |
| `audience` | `product`（打回产品）/ `internal`（回 analyze） |
| `obligation_ids` | 关联 O-xxx |
| `scenario_ids` | 关联 SC-xxx |

## test_point_review（报告顶层）

从 precheck 与四份 findings 汇总：

- `coverage_score`, `obligations_total`, `false_coverage_count`
- `tri_party.product/dev/qa/red_team`: `{ verdict, finding_count }`

## false_coverage

将 `.test-point-coverage-precheck.json` 的 `false_coverage[]` 复制到 gate 报告；QA 视角 finding 可升级为 internal issue。

## reject_kind

- 仅 `audience=internal` → `internal`（不写产品 MD）
- 仅 product → `product`
- 两者皆有 → `mixed`
