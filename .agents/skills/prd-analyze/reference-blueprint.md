# 唯一测试蓝图参考

蓝图结构固定为：

```text
需求模块
  -> 测试点
    -> 测试范围
      -> 场景
```

## 需求模块

表达“这次需求到底改什么”，不要直接照搬 PRD 章节标题。

示例：

- 租赁价格展示
- 出售房价格保持不变
- Feed 与 PDP 一致性
- A/B 实验与指标

## 测试点

表达“这个模块必须验证什么规则”。

每个测试点必须包含：

- 依据：PRD/Figma/知识库来源。
- 验收规则：能直接判断通过或失败。
- 优先级：P0/P1/P2/P3。

## 测试范围

表达“测什么、不测什么”。

必须写清：

- 包含的平台、入口、类目、状态、数据。
- 排除的平台、入口、非功能项或本期不做内容。

## 场景

`config.yaml` 的 **`required_coverage`** + **`prd_contract_obligations`**：合并为 PRD 契约清单；`check_prd_coverage.py` / `prd-coverage-matrix.json` / `validate-artifacts --stage prd-analyze` 强制检查。API 类义务须 `execution_channel=api_intercept` 且步骤/预期含对应字段（如 `price_frequency`、`type=FREE`+`amount=0`）。

返工轮若存在 **`.pending-rework-issues.json`**：须闭合其中 `resolution_check`（如子类目 coverage_ids），否则 prd-analyze 校验失败。

场景是后续用例生成的唯一来源。每个场景必须有：

- 前置条件
- 测试数据
- 执行步骤
- 预期结果
- 后置动作
- **执行通道** `execution_channel`（必填，四选一）：
  - `browser`：Playwright / agent-browser 打开 `env.json` 的 `base_url`，用 DOM 操作与可见断言完成。
  - `api_intercept`：同上打开页面，用 `page.route`（或等价）注入 Feed 响应后再断言 DOM 或 JSON 字段。
  - `native_app`：仅当 `config.yaml` 明确放开 App 端时使用；**默认 `target_platform: pc_web` 时不生成此类场景**。
  - `manual`：PC 上需人工对照、且无 Playwright 逐步动作（如纯线下核对）；`automatable=否`。
- 是否可自动化（**仅填「是」或「否」**，禁止「部分」）

**可自动化判定**（与 `workspace/inputs/config.yaml` → `execution` 对齐）：

- `automatable=是` **仅当** `execution_channel` 为 `browser` 或 `api_intercept`，且从 `base_url` 到断言的**每一步**都能写成单一浏览器动作（navigate / click / fill / scroll / expect visible / route.fulfill），**禁止**「构造 Mock」「触发 BFF」「冷启动 App」等无 URL、无选择器、无 route 的笼统句。
- `native_app` / `manual` → `automatable=否`；缺造数、无 fixture、无 `base_url` → `否`，在 `automation_note` 写明阻塞。
- `config.yaml` 为 `target_platform: pc_web` 时：所有 UI 场景用 `browser`（桌面 Chromium），PRD 中的 iOS/Android 表述映射为同一 Web 验收路径，**禁止**写「冷启动 App」步骤。
- `automatable=是`：表示后续 test-execute **会**用 Playwright/agent-browser 执行；`否`：用例仍保留在 `02-test-cases.md` 供人工，**不会**被自动执行。

**browser 步骤模板**（每步一句动作）：

1. 打开 `{base_url}`（与 `env.json` 一致，禁止 `example.com` 占位）
2. （可选）登录或选择分桶 cookie/header
3. 滚动/定位 Feed 内目标房产卡片（写清 `data-testid` / role / 文案锚点，或「首条含 TO RENT 的卡片」）
4. 断言价格区文本（写清正则或精确文案，如 `£1,200 pm`）

**api_intercept 步骤模板**：

1. 打开 `{base_url}`
2. 注册路由拦截 `**/…feed…**`（写清 URL 片段或方法）
3. `fulfill` 固定 JSON fixture（路径或内联字段：`price`、`price_period`）
4. 刷新或滚动至 Feed，断言 DOM 或网络响应体字段

预期结果必须是可观察、可判断的屏幕文案、状态、API 输出或业务结果。
