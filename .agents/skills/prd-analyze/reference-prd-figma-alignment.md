# PRD × Figma 对齐（prd-analyze / case-review）

> 改编自 senior-qa-brain `03_diff_with_prd`。analyze 阶段写入蓝图；case-review 阶段对未闭合项开 issue。

## 四色差距（分析时标记）

对比 **PRD 原文** 与 **Figma MCP 分析结果**（及已写入蓝图的内容）：

| 标记 | 含义 | analyze 落点 | case-review 动作 |
|------|------|--------------|----------|
| 已覆盖 | PRD 要求在设计/蓝图/场景中已有 | 无需额外输出 | 跳过 |
| 覆盖不完整 | 有涉及但缺规则/缺状态 | 能测则补场景；不能测则写入 `open_questions[]` | 可记 `testability` / `figma_states` |
| 报告缺失 | PRD 明文但设计未体现、蓝图无场景 | 补场景；设计缺失写入 `open_questions[]` | 记 `prd_functional` / `alignment` |
| 设计冲突 | PRD 与 Figma 表述不一致 | 写入 `open_questions[]`，不要自行裁决 | 记 `prd_consistency` / `alignment` |

**设计冲突是高价值风险**：产品暂未统一口径时，不要伪装成可执行场景，应在用例评审门禁打回产品确认。

## analyze 阶段操作步骤

1. 从 PRD 提取：功能点、业务规则、字段/枚举、错误文案、AC、Out of Scope。
2. 从 Figma 提取：Frame、控件、状态、文案（见 [reference-figma-analysis.md](reference-figma-analysis.md)）。
3. 逐项对比，**仅输出** 不完整 / 缺失 / 冲突（已覆盖不写入，减少噪音）。
4. 写入蓝图：
   - **冲突/缺口已有产品口径** → 写入相关测试点依据和场景来源
   - **PRD 未写清、需按某规则测** → 写入 `open_questions[]`
   - **可测且设计缺失** → 新增场景，`source_refs` 必填

## open_questions[] 示例

```json
{
  "id": "Q-001",
  "source_refs": ["PRD §3.1 登录", "Figma 12:345"],
  "owner": "product",
  "blocking": true,
  "impact": "无法判断三次失败后按钮应禁用还是继续可点击。",
  "description": "PRD 要求三次失败后禁用按钮，Figma 主流程 Frame 按钮始终为可点击态",
  "suggestion": "请明确三次失败后的按钮状态和错误文案。"
}
```

## case-review 阶段抽检

在 `analyze_prerequisites.py` 通过后，用四色思维扫一遍（不必重跑五层 Figma 分析）：

- [ ] PRD 明文枚举/规则是否在来源、测试点或场景中有落点
- [ ] `open_questions[]` 是否已把未闭合问题讲清楚
- [ ] 设计冲突项是否在 `issues[]` 或已转化为可测场景
- [ ] 缺 Figma 时，UI 场景是否只覆盖 PRD 能支撑的内容
- [ ] 通过时：未闭合的 PRD 明文规则不应静默遗漏

## issue 类别建议

| 差距类型 | category |
|----------|----------|
| 设计稿缺状态/缺页面 | `figma_states` / `figma_flow` |
| PRD 有、设计无 | `alignment` / `prd_functional` |
| PRD 与 Figma 矛盾 | `prd_consistency` / `alignment` |
| 蓝图缺场景 | `blueprint_gap` |

## 与「待确认」的边界

- analyze **不要**在场景正文写「需产品确认」。
- 待确认内容统一进入 `open_questions[]`。
- case-review reject 时 `suggestion` 须写清产品应改 PRD 还是 Figma。
