# 交付物全文阅读

## 目标

在编写场景之前，必须读完用户提供的 PRD 每一页、Figma 每一个 Frame。覆盖证明写在 `delivery_coverage` 中。

## PRD

1. 阅读 `workspace/inputs/prd.md`，以及 `prd.sources` 中记录的原 PDF/DOCX 路径。
2. 在 `delivery_coverage.prd.sources[]` 中记录：路径、`pages_total`、`pages_read`、`characters`、`read_complete: true`。
3. 构建 `sections_inventory[]`：每个章节一条；明确写「本期不做」的条目标 `in_scope: false`（仍要列入清单）。
4. 每个范围内功能点映射到 `scenario_ids[]`（每点至少 1 条）。

大型 PRD（31+ 页）：使用 `project_scale: xlarge`，场景数 ≥80。

## Figma

1. 按 [reference-figma-analysis.md](reference-figma-analysis.md) 用 Figma MCP 读完每个 URL（须真实 `node_id`）。
2. 在 `figma.frames_inventory[]` 填写主流程与 Empty/Error/Disabled 等态（含 `state_type`、`prd_section` 等，见该文档）。
3. PRD 与稿面差异按 [reference-prd-figma-alignment.md](reference-prd-figma-alignment.md) 写入 `resolutions[]` / `assumptions[]`。
4. 若无设计稿或仅占位链接：设 `figma.read_complete: false`；gate 可记 `figma_delivery`。
5. 可选：先运行 `python3 scripts/prefetch_figma_snapshot.py` 生成 `figma-snapshot.json` 辅助清点 Frame。

## 执行归属

将 `delivery_coverage.executed_by` 设为 `prd-analyzer-subagent`，表明本阶段在独立子 Agent 会话中完成。

由主编排会话代写的蓝图缺少子 Agent 追溯，无法通过同类校验。

## 校验前自检

- [ ] `sections_inventory` 覆盖 PRD 全部章节
- [ ] `functional_points_mapped` 等于范围内功能点数量
- [ ] `scenarios.length` ≥ `scenario_minimum_required`
- [ ] 每条场景均有 `prd_section` 或 `figma_ref`
- [ ] 场景文案中无「需产品确认」类表述（灰区进 `assumptions[]`）
