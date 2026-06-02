# PRD × Figma 对齐（prd-analyze / prd-gate）

> 改编自 senior-qa-brain `03_diff_with_prd`。analyze 阶段写入蓝图；gate 阶段对未闭合项开 issue。

## 四色差距（分析时标记）

对比 **PRD 原文** 与 **Figma MCP 分析结果**（及已写入蓝图的内容）：

| 标记 | 含义 | analyze 落点 | gate 动作 |
|------|------|--------------|----------|
| 已覆盖 | PRD 要求在设计/蓝图/场景中已有 | 无需额外输出 | 跳过 |
| 覆盖不完整 | 有涉及但缺规则/缺状态 | 补 `scenarios[]` 或 `assumptions[]` | 可记 `testability` / `figma_states` |
| 报告缺失 | PRD 明文但设计未体现、蓝图无场景 | 补场景；设计缺失记 `resolutions[]` | 记 `prd_functional` / `alignment` |
| 设计冲突 | PRD 与 Figma 表述不一致 | `resolutions[]`（test_basis + 说明） | 记 `prd_consistency` / `alignment` |

**设计冲突是高价值测试点**：即使产品暂未统一口径，也要写场景验证「实际实现遵循 PRD 还是设计」。

## analyze 阶段操作步骤

1. 从 PRD 提取：功能点、业务规则、字段/枚举、错误文案、AC、Out of Scope。
2. 从 Figma 提取：Frame、控件、状态、文案（见 [reference-figma-analysis.md](reference-figma-analysis.md)）。
3. 逐项对比，**仅输出** 不完整 / 缺失 / 冲突（已覆盖不写入，减少噪音）。
4. 写入蓝图：
   - **冲突/缺口已有产品口径** → `resolutions[]`（`id`, `description`, `test_basis`, `prd_section`, `figma_ref`）
   - **PRD 未写清、需按某规则测** → `assumptions[]` + 关联 `SC-xxx`
   - **可测且设计缺失** → 新增 `scenarios[]`，`prd_section` 必填

## resolutions[] 示例

```json
{
  "id": "RES-001",
  "prd_section": "§3.1 登录",
  "figma_ref": "12:345",
  "description": "PRD 要求三次失败后禁用按钮，Figma 主流程 Frame 按钮始终为可点击态",
  "test_basis": "prd",
  "basis_id": null
}
```

## gate 阶段抽检（prd-gatekeeper）

在 `analyze_gate_prerequisites.py` 通过后，用四色思维扫一遍（不必重跑五层 Figma 分析）：

- [ ] PRD 明文枚举/规则是否在 PRD 章节、Figma Frame 或 `assumptions[]` 中有落点
- [ ] `resolutions[]` 是否已闭合（无「待产品定稿」类悬空描述）
- [ ] 设计冲突项是否在 `issues[]` 或已转化为可测场景
- [ ] `figma.read_complete=false` 时，UI 场景是否主要靠 `assumption` 且 gate 已接受或打回 `figma_delivery`
- [ ] 通过时：未闭合的 PRD 明文规则不应静默遗漏（应 issue 或 assumption 已在 pass MD 列出）

## issue 类别建议

| 差距类型 | category |
|----------|----------|
| 设计稿缺状态/缺页面 | `figma_states` / `figma_flow` |
| PRD 有、设计无 | `alignment` / `prd_functional` |
| PRD 与 Figma 矛盾 | `prd_consistency` / `alignment` |
| 蓝图缺场景 | `blueprint_gap` |

## 与「待确认」的边界

- analyze **不要**在场景正文写「需产品确认」。
- gumtree 的「待确认」→ 本项目的 `assumptions[]` + `test_rule`。
- gate reject 时 `suggestion` 须写清产品应改 PRD 还是 Figma。
