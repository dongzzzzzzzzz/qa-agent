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

## 步骤

1. 解析 `02-test-cases.md` 中每条用例（编号、步骤、预期）。
2. 读取 `workspace/inputs/env.json`（可选）确定环境。
3. 按用例执行（Web：Playwright MCP / agent-browser；移动端：mobile-mcp / Appium MCP）。
4. 每条记录：`status`、`evidence` 路径、`failure_reason`、`duration_ms`。
5. 证据保存至 `workspace/artifacts/evidence/{case_id}/`。
6. 汇总 `summary`，设置 `has_pass` / `has_fail`。
7. 写入 `04-execution-result.json`。
8. **若存在 fail/block**：在同一阶段写入 `05b-bug-list.md`（格式见 `skills/bug-list-write/SKILL.md`），每条失败用例对应 `## BUG-NNN`。
9. 运行 `validate-artifacts.py --stage test-execute`。

## Bug 清单（合并在本阶段，无独立 bug-list-writer）

- 仅当 `has_fail=true` 时必填 `05b-bug-list.md`
- 字段：关联用例、严重级、复现步骤、期望/实际、证据路径

## 状态定义

| status | 说明 |
|--------|------|
| pass | 符合预期 |
| fail | 不符合预期 |
| skip | 环境不具备跳过 |
| block | 阻塞无法继续 |

## 后续扩展

- 半自动模式：仅执行 P0，其余标记 skip
- CI 无头浏览器矩阵
