# 交付物全文阅读

## 目标

在编写场景之前，必须读完用户提供的 PRD 每一页、Figma 每一个 Frame。覆盖证明不要单独写成旧摘要字段，而是落到唯一测试蓝图的 `source_refs`、测试点依据、测试范围和待产品确认问题中。

## PRD

1. 阅读 `workspace/inputs/prd.md`，以及输入中记录的原 PDF/DOCX 路径。
2. 按业务主题归并 PRD 内容，不按章节机械拆点。
3. 每个范围内功能点都要落到一个需求模块或测试点，并在 `source_refs` 写清来源。
4. 明确写「本期不做」的条目，放入对应测试点的 `scope.exclude` 或模块说明中，不生成测试场景。

大型 PRD 要按业务主题完整覆盖，不用硬凑场景数量；宁可少而清楚，也不要生成不可判定场景。

## Figma

1. 按 [reference-figma-analysis.md](reference-figma-analysis.md) 用 Figma MCP 读完每个 URL（须真实 `node_id`）。
2. 将主流程与 Empty/Error/Disabled 等态写入相关测试点的依据、范围或场景。
3. PRD 与稿面差异按 [reference-prd-figma-alignment.md](reference-prd-figma-alignment.md) 写入 `open_questions[]`，或转成可执行场景。
4. 若无设计稿或仅占位链接：在 `open_questions[]` 写明缺失影响；由 case-review 决定是否打回。
5. 可选：先运行 `python3 scripts/prefetch_figma_snapshot.py` 生成 `figma-snapshot.json` 辅助清点 Frame。

## 执行归属

蓝图必须由 `prd-analyzer` 子 Agent 输出。主编排只负责启动和校验，不代写蓝图。

## 校验前自检

- [ ] 每个需求模块都有清楚目标和来源
- [ ] 每个测试点都有验收规则和测试范围
- [ ] 每个场景都有前置条件、测试数据、步骤、预期结果、后置动作
- [ ] PRD/Figma 不闭合的问题进入 `open_questions[]`
- [ ] 场景文案中无「需产品确认」类表述
