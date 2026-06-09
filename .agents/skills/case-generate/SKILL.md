---
name: case-generate
description: >-
  从唯一测试蓝图 00-test-blueprint.json 生成面向执行人员的 Markdown 测试用例。
---

# 用例生成

## 输入输出

- 输入：
  - `workspace/artifacts/00-test-blueprint.json`
  - `workspace/artifacts/00-test-data.json`（测试数据，prd-analyze 阶段产出）
  - `workspace/inputs/config.yaml`（`execution`）
  - `workspace/inputs/env.json`（`base_url`）
- 输出：`workspace/artifacts/02-test-cases.md`（**XMind 可导入层级 Markdown**）

## 输出结构（XMind 对应）

```text
# 项目名 - 测试用例
## 需求模块名
### 测试点名（可选分组）
### TC-001: 用例标题
- 用例编号 / 需求模块 / 测试点 / 优先级 / 执行通道 / 是否可自动化
- 前置条件
  - …
- 测试数据
  - …
- 执行步骤
  - 1. …
- 预期结果
  - …
- 后置动作
  - …
- 需求依据：…
```

## 写作原则

- 一条蓝图场景生成一条 `### TC-NNN:` 用例块。
- **`open_questions[]` 中 blocking=true 对应的场景跳过，不生成用例**，在文件末尾集中列出 `## Pending - 等待产品补充`，每条注明对应的 open_question id。
- 元数据行 **执行通道**、**是否可自动化** 供 test-execute 过滤（默认只跑「是」）。
- **测试数据直接从 `00-test-data.json` 按 `scenario_id` 取值**，不自行推断或编造：
  - `url` → 前置条件的 base_url 和路径
  - `api_fixture` → api_intercept 通道的 mock 数据
  - `boundary_values` → 测试数据列表
  - `precondition_data` → 前置条件的数据要求
  - 若 `00-test-data.json` 中无对应 scenario_id 的条目，在该用例的测试数据行标注 `⚠️ 测试数据缺失，需手动补充`，不得凭空填写
- 用 Given / When / Then 思路写：
  - 前置条件：环境、账号、页面、数据状态；`browser`/`api_intercept` 须写明可访问的 `base_url`。
  - 测试数据：来自 `00-test-data.json`，listing id、fixture 路径、分桶 cookie 等执行器可直接用的值。
  - 执行步骤：每步须为单一动作（打开 URL、点击、滚动、拦截并 fulfill、断言可见文案/正则）；不得把「构造 Mock」「冷启动 App」留给执行器自行猜。
  - 预期结果：屏幕/API/业务状态上能观察到什么（含可写进 `expect` 的文案或正则）。
  - 后置动作：关闭 route、登出、删 cookie 等可执行清理。
- `automatable=否`：步骤面向人工 PC 验收；**不要**暗示 test-execute 会跑该条。
- `automatable=是`：步骤必须可被 Playwright/agent-browser 在桌面浏览器逐步执行（与 `execution_channel` 一致）。

## 禁止

- 禁止新增、删除、合并蓝图场景。
- 禁止写不可判定预期：例如“按预期”“显示正确”“记录实际展示”“行为符合 PRD”。
- 禁止写固定等待或脚本实现细节（如 `sleep 3`）；允许「等待网络空闲」「等待选择器可见」等等价自然语言。
- 禁止 `automatable=是` 却写仅原生 App 或仅 Charles 的步骤（与蓝图通道矛盾）。
- 禁止要求产品在用例执行阶段继续解释普通需求。
- `是否可自动化` 列必须与蓝图 `automatable` 一致，仅允许「是」或「否」。

## 命令

```bash
python3 scripts/render_cases_from_blueprint.py
python3 scripts/validate-artifacts.py --stage case-generate
```
