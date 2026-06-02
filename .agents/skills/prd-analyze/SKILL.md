---
name: prd-analyze
description: >-
  全文阅读用户提供的 PRD 与 Figma，将范围内每个功能点映射为测试就绪蓝图场景，并产出
  delivery_coverage 证明。在 prd-gate 之前由 prd-analyzer 子 Agent 执行。适用于 prd-analyze
  阶段、测试就绪蓝图、或多模块 xlarge 规模 PRD 全文分析。
disable-model-invocation: true
---

# PRD 分析（测试就绪蓝图）

## 快速开始

1. 全文阅读用户提供的每一页 PRD / 每一个 Figma Frame（见 [reference-full-read.md](reference-full-read.md)、[reference-figma-analysis.md](reference-figma-analysis.md)）。
2. 构建 `delivery_coverage`（章节清单 + 阅读证明）。
3. 按 [reference-obligations.md](reference-obligations.md) 抽取 TOG，再按 [reference-blueprint.md](reference-blueprint.md) 设计 `scenarios[]`（含 `covers_obligations`）。
4. 将 `delivery_coverage.executed_by` 设为 `prd-analyzer-subagent`。
5. 运行校验脚本；修复错误直至两个阶段均通过。

## 为何必须全文阅读

PRD 分析不完整会导致线上漏测。流水线仅在 `delivery_coverage` 能证明「全部来源已读」且「每个范围内功能点至少对应一条 `SC-xxx`」时，才认定 analyze 完成。

摘要式阅读、模板拼场景、或由主编排会话代写蓝图，会因缺少追溯关系与场景不足而无法通过校验。

## 何时使用

- 流水线阶段 `prd-analyze`（始终在 `prd-gate` 之前）。
- 产品修订 PRD/Figma 后：从本阶段**全量重跑**（不要只改一小段 JSON）。

## 产出物

| 文件 | 作用 |
|------|------|
| `workspace/artifacts/00-test-ready-blueprint.json` | 用例唯一真相源（必填 `delivery_coverage`） |
| `workspace/artifacts/00-test-obligations.json` | 测试义务图谱 TOG |
| `workspace/artifacts/01-prd-analysis.json` | 由蓝图同步生成 |
| `workspace/artifacts/test-ready-internal.md` | 内部 QA 摘要 |

门禁报告与面向产品的 Markdown 属于 `prd-gate` 阶段，不在本阶段产出。

## 工作流

```
- [ ] 阅读全部 PRD 来源（每一页；见 delivery_coverage.prd.sources）
- [ ] 可选：`python3 scripts/prefetch_figma_snapshot.py` → 清点 URL
- [ ] 按 reference-figma-analysis 用 MCP 读完 Frame（无稿则 figma.read_complete=false）
- [ ] PRD×Figma 差距见 [reference-prd-figma-alignment.md](reference-prd-figma-alignment.md)
- [ ] 填写 sections_inventory（范围外条目也列出，并标 in_scope:false）
- [ ] 每个范围内功能点 → 至少 1 条场景，且带 prd_section 或 figma_ref
- [ ] 设置 project_scale 与 scenario_minimum_required
- [ ] 运行下方脚本；失败则修复后重跑直至通过
```

## 场景规模

| project_scale | 典型体量 | 场景数（最少–最多） |
|---------------|----------|---------------------|
| small | ≤10 页 | 15–30 |
| medium | 11–20 页 | 35–60 |
| large | 21–30 页 | 55–100 |
| xlarge | 31+ 页或多模块 | 80–150 |

`scenario_minimum_required` 不得低于所选规模对应的下限。

## 校验循环

```bash
python3 scripts/validate-artifacts.py --stage test-ready-blueprint
python3 scripts/sync_blueprint_to_analysis.py
python3 scripts/validate-artifacts.py --stage prd-analyze --finalize
python3 scripts/render_test_ready_internal.py
```

仅当 `prd-analyze` 校验通过（会生成 `.prd-analyze-complete.ok`）后，才可进入 `prd-gate`。

## 边界与 redirect

| 情况 | 应停止或转交的原因 |
|------|-------------------|
| 只读了短摘要 | 校验要求 `pages_read == pages_total` 且完整的 `sections_inventory` |
| 未按功能点映射就批量生成场景 | `functional_points_mapped` 必须等于范围内功能点数量 |
| 主编排会话被要求代写蓝图 | `executed_by` 必须为 `prd-analyzer-subagent`，否则 gate 会被拦截 |
| 需求灰区 | 写入 `assumptions[]` 并给出 `test_rule`；场景文案中避免「需产品确认」类表述 |

## 延伸阅读

- Figma 五层 + MCP：[reference-figma-analysis.md](reference-figma-analysis.md)
- PRD×Figma 对齐：[reference-prd-figma-alignment.md](reference-prd-figma-alignment.md)
- 交付物检查清单：[reference-deliverables.md](reference-deliverables.md)
- 蓝图字段说明：[reference-blueprint.md](reference-blueprint.md)
