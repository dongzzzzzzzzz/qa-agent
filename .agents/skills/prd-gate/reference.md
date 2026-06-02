# PRD 门禁裁决清单（prd-gate）

> 审查 **prd-analyze 产物** + **PRD/Figma 原文**。任一不满足 → 写入 `issues[]` → **reject**。

## 通过标准

任一未闭合发现都会阻断进入用例生成，因此门禁采用单一规则：

```text
issues 为空  → pass（可进入 case-generate）
issues ≥ 1   → reject（与 severity 无关；产品须先修订 PRD/Figma）
```

## 前置

- [ ] `00-test-ready-blueprint.json` 已存在
- [ ] `01-prd-analysis.json` 已存在且与蓝图一致（模块/主流程不矛盾）

## 1. 蓝图质量（analyze 产出）

- [ ] `blocking_gaps` 为空数组
- [ ] 每个 P0 模块至少 1 条 P0 场景
- [ ] P0 模块在 `coverage_matrix` 中 functional/boundary/exception 均为 true
- [ ] `source=assumption` 的场景均有合法 `assumption_id`
- [ ] 场景数在规模上限内（小 ≤30 / 中 ≤60 / 大 ≤100 / xlarge ≤150）
- [ ] 无「需产品确认」「待产品补充」等措辞（含 assumptions 文案）

## 2. 交付物（PRD / Figma 原文）

- [ ] PRD 结构完整（背景、角色、功能、非功能等），非空占位
- [ ] Figma 可访问（否则记 issue：`figma_delivery`）
- [ ] 主流程在 PRD 与设计中可对齐
- [ ] 关键规则在 PRD 或蓝图中可测（锁定、频控、字段校验等）
- [ ] PRD 与蓝图无未决议冲突（`resolutions[]` 应已闭合）

## 2b. PRD × Figma 四色差距（抽检，不重跑五层分析）

对照 [prd-analyze/reference-prd-figma-alignment.md](../prd-analyze/reference-prd-figma-alignment.md)：

- [ ] PRD 明文规则在设计稿、场景或 `assumptions[]` 中有落点（缺失 → `alignment` / `prd_functional`）
- [ ] Figma 有 Disabled/Empty/Error 等态时，蓝图有对应场景或 `figma_states` issue
- [ ] PRD 与 Figma 冲突项已在 `resolutions[]` 闭合或记入 `issues[]`（`prd_consistency`）
- [ ] `delivery_coverage.figma.read_complete=false` 时，未假装已有 UI 基线（勿仅 reject 蓝图而忽略交付物问题）

## 3. 分析 JSON

- [ ] `01-prd-analysis.json` 与蓝图 `modules`/`roles` 一致
- [ ] 边界/异常列表与蓝图场景类型覆盖不矛盾
- [ ] 无「PRD 未明确，需确认」类条目

## issue 字段

| 字段 | 要求 |
|------|------|
| `id` | `GATE-001` 递增 |
| `description` | 原因说明 |
| `suggestion` | **产品需补充**（可执行） |
| `category` | 见下表 |

### category 枚举

`prd_structure` | `prd_scope` | `prd_roles` | `prd_functional` | `prd_data` | `prd_api` | `prd_nfr` | `prd_consistency` | `figma_delivery` | `figma_flow` | `figma_states` | `figma_ui` | `alignment` | `testability` | `blueprint_gap` | `analysis_gap`

## 打回后循环

```text
reject → 产品改 PRD/Figma → prd-analyze → prd-gate → …
```

重跑命令：`--from-stage prd-analyze`。仅重跑 `prd-gate` 时蓝图未随 PRD 更新，产品文档会与全文分析脱节。
