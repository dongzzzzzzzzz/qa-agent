---
name: test-execute
description: >-
  按用例文档执行测试并输出 execution-result JSON 与证据文件。在 test-execute
  阶段由 test-executor 子 Agent 调用。
---

# 测试执行 Skill

## 何时使用

- 流水线阶段 `test-execute`
- 前置：`03-review-report.json` 中 `verdict=pass`

## 执行范围（默认）

- 读取 `config.yaml` → `execution.run_scope`（默认 `automatable_only`）。
- **仅对** `02-test-cases.md` 中 **`是否可自动化=是`** 的用例启动 Playwright / agent-browser。
- **`是否可自动化=否`**：不打开浏览器、不跑步骤；在 `04-execution-result.json` 记 `status=skip`，`failure_reason` 写「本期仅执行可自动化用例」。
- 不要求一次跑完全部用例；`summary.total` 可等于「是」+「否」条数，其中 pass/fail/block 只来自「是」的子集。

## 步骤

1. 读取 `execution.primary_runner`（`playwright` 或 `agent-browser`）、`viewport: desktop`（PC 端）。
2. 解析 `02-test-cases.md`（XMind 层级格式）：按 `### TC-NNN:` 分块，读取 `- 是否可自动化`、`- 执行通道`、`- 执行步骤`、`- 预期结果` 子列表。
3. 读取 `env.json` 的 `base_url`；占位域名 → 对将执行的「是」用例标 `block`。
4. **对每条用例**：
   - `是否可自动化=否` → `skip`（不执行）。
   - `是否可自动化=是` 且 `执行通道=browser` → navigate、locator、assert；证据截图。
   - `是否可自动化=是` 且 `执行通道=api_intercept` → `page.route` / fulfill 后再 DOM 或 JSON 断言。
   - `是` 但步骤无法逐步执行 → `block`，勿标 `pass`。
5. 每条记录：`status`、`evidence`、`failure_reason`、`duration_ms`。
6. 证据目录：`workspace/artifacts/evidence/{case_id}/`。
8. **跨用例一致性检查（所有用例执行完后）**：

   找出同一功能点下既有 `browser` 通道又有 `api_intercept` 通道的用例组（通过蓝图的 `scenario_id` 前缀归组，如 S-01.01.xx 属于同一组）：

   对每个用例组：
   - browser 用例观测到的 UI 展示值（如价格文案）
   - api_intercept 用例的 fixture 数据（如 API 返回的 price 字段）
   - 两者是否一致：UI 展示的值是否与 API fixture 数据的预期展示规则吻合

   不一致时标记为 `cross_case_conflict`，写入 `04-execution-result.json`：
   ```json
   {
     "conflict_id": "CONFLICT-001",
     "browser_case": "TC-003",
     "api_case": "TC-004",
     "conflict_description": "TC-003 观测到价格展示为 1500/pm，TC-004 的 fixture 返回 price_frequency=pw，两者不一致",
     "severity": "major"
   }
   ```

9. **执行后推断（infer_uncovered，每条 pass 用例必做）**：
   对每条 `status=pass` 的用例，在记录结果后追加推断：
   - 这个功能还有哪些**数据变体**没有被其他用例覆盖？（例如：测了 rent/month，有没有测 rent/week？）
   - 这个功能在**其他入口或页面**有对应展示吗？如果有，是否有用例覆盖？（例如：list 页测过了，detail 页同一字段有没有测？）
   - 我刚才的断言能否排除"前端硬编码而非 API 实时返回"的可能性？如果不能，是否需要补一条 api_intercept 用例？

   推断结果写入 `workspace/artifacts/coverage-gap.json`，格式：
   ```json
   [
     {
       "source_case": "TC-003",
       "gap_type": "data_variant | cross_page | data_source",
       "description": "具体描述缺少什么覆盖",
       "suggested_steps": "建议的补充验证步骤（可选）"
     }
   ]
   ```

10. **gap 闭环（所有用例执行完后）**：
    若 `coverage-gap.json` 存在且非空：
    - 能补的：直接执行，将结果追加到 `04-execution-result.json`，gap 标记 `resolved`。
    - 不能补的：gap 保留，在 `summary` 中增加 `unresolved_gaps` 字段说明原因。

11. 汇总 `summary`，设置 `has_pass` / `has_fail`，包含 `cross_case_conflicts[]` 和 `unresolved_gaps[]`。
12. 写入 `04-execution-result.json`。
13. 若存在 fail/block 或 cross_case_conflict：写 `05b-bug-list.md`。
14. `validate-artifacts.py --stage test-execute`。

## Bug 清单

- 仅当 `has_fail=true` 时必填 `05b-bug-list.md`

## 状态定义

| status | 说明 |
|--------|------|
| pass | 符合预期（仅「是」且已执行） |
| fail | 不符合预期 |
| skip | 未执行：含「否」及 run_scope 排除 |
| block | 环境/步骤不可执行 |

## 禁止

- 对 `是否可自动化=否` 的用例启动浏览器仍标 pass
- 修改用例或评审报告
