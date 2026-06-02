# Figma 深度分析（prd-analyze）

> 改编自 senior-qa-brain 五层框架，输出落到 `00-test-ready-blueprint.json`，不是独立 Markdown 报告。

## 何时读本文

- `workspace/inputs/figma.url` 中有**可访问**的 Figma 链接时：必须按本文执行后再设 `figma.read_complete: true`。
- 仅有占位链接或产品未交付设计稿：设 `figma.read_complete: false`，Frame 清单可空；UI 细节进 `assumptions[]`，由 gate 记 `figma_delivery`。

## MCP 调用顺序（Cursor Figma MCP）

对每个 URL（含 `node-id` 深链）按序执行：

| 顺序 | 工具 | 用途 |
|------|------|------|
| 1 | `get_metadata` | 页面/Frame 树、节点 ID 清单 |
| 2 | `get_design_context` | 组件、文案、表单、变体（Disabled/Loading 等） |
| 3 | `get_screenshot` | 对关键 Frame 截图备查（复杂态、空态、错误态） |

从 URL 解析 `fileKey` 与 `node-id`（`-` 转 `:`）。**禁止**用 `prd-p2` 等 PRD 章节代号充当 `node_id`。

## 五层分析 → 蓝图字段

```
Figma URL
  → 第1层 结构 → modules[]、figma_mapping[]、frames_inventory[]
  → 第2层 交互 → field_rules[]、scenarios[]（figma_ref）
  → 第3层 数据 → field_rules[]、api_endpoints[]
  → 第4层 边界 → scenarios[]（type=边界/异常）
  → 第5层 隐藏需求 → api_endpoints[]、assumptions[]（勿写 blocking_gaps）
```

### 第1层：结构（约 15% 精力）

- 识别页面/模块分组、导航关系、共用组件与变体。
- 填入 `delivery_coverage.figma.frames_inventory[]`，每项建议字段：

| 字段 | 说明 |
|------|------|
| `name` | Frame/页面名（必填） |
| `node_id` | Figma 节点 ID，如 `12:345`（有真实稿时必填） |
| `flow` | 主流程 / 会员态 / 异常态 等 |
| `state_type` | `default` / `loading` / `empty` / `error` / `disabled` / `locked` 等 |
| `prd_section` | 对应 PRD 章节，如 `§3.1 筛选` |
| `elements_summary` | 一句话：主要控件（搜索框、表格、弹窗等） |

- 同步 `figma_mapping[]`：`prd_section` ↔ `figma_ref`（URL 或 `fileKey/nodeId`）。

### 第2层：交互（约 20% 精力）

- 枚举表单控件：输入框、下拉、按钮、开关、上传等。
- 从文案推断规则（如「8-20 位密码」）→ `field_rules[]`。
- 识别状态机：Default → Loading → Success/Error；Disabled 前置条件。
- 每个可测交互点至少 1 条 `scenarios[]`，`source: figma`，带 `figma_ref`。

常见状态命名（Figma）：Default、Hover、Active、Disabled、Loading、Empty、Error。

### 第3层：数据（约 15% 精力）

- 从字段标签/占位符/帮助文案提取：字段名、类型、必填、格式。
- 写入 `field_rules[]`；接口形态写入 `api_endpoints[]`（列表页→GET，提交→POST）。

### 第4层：边界（约 15% 精力）

- 视觉：超长文案、缺图、列表为空。
- 交互：快速连点、超时、网络失败（设计有提示则写场景，无则 assumption）。
- 数据：最小/最大长度、特殊字符、枚举边界。

对应 `scenarios[]`，`type` 为 `边界` 或 `异常`。

### 第5层：隐藏需求（约 20% 精力）

- 从设计推断：接口路径、按钮禁用规则、权限/会员差异。
- 设计未画但 PRD 明文要求的 → 见 [reference-prd-figma-alignment.md](reference-prd-figma-alignment.md)，记入 `resolutions[]` 或 `assumptions[]`。
- 风险（表单注入、XSS、频控等）→ `risks[]`。

### 风险（约 15% 精力）

- 有表单 → 注入/校验类风险；有 UGC 展示 → XSS；有验证码/邮件 → 频控。

## 工作笔记模板（分析时自用，最终写入 JSON）

```markdown
【页面结构】
├─ 模块A (N 个 Frame)
│  └─ Frame 名 (node_id)

【交互元素】
| 元素 | 规则 | 依据 |

【数据字段】
| 字段 | 类型 | 必填 | 规则 |

【待确认 → assumptions】
- ASM-xxx: ...
```

## 无 Figma 时的诚实策略

| 情况 | `read_complete` | `frames_inventory` | 场景来源 |
|------|-----------------|-------------------|----------|
| 占位/无法打开链接 | `false` | `[]` 或仅 note | `source: prd` + assumption |
| 真实链接且 MCP 读完 | `true` | 全量 Frame + 真实 node_id | `figma` / `prd` |

## 校验前自检（Figma 部分）

- [ ] 每个 `frames_inventory[].node_id` 来自 MCP，非 PRD 页码代号
- [ ] 主流程 + Empty/Error/Disabled 等关键态有 Frame 或 assumption 覆盖
- [ ] `figma_mapping` 与 `sections_inventory` 可交叉索引
- [ ] 占位 URL 时未设 `read_complete: true`

## 延伸阅读

- PRD×Figma 差距四色：[reference-prd-figma-alignment.md](reference-prd-figma-alignment.md)
- 可选预抓取节点树：`python3 scripts/prefetch_figma_snapshot.py` → `workspace/artifacts/figma-snapshot.json`
