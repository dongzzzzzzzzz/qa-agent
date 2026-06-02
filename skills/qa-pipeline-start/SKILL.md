---
name: qa-pipeline-start
description: 用户说「帮我跑 QA Agent」「跑 QA Agent」「启动 QA 流水线」时，以 IDE 模式启动多阶段 QA 流水线（默认不用 CLI）。
---

# 启动 QA Agent 流水线

## 何时触发

用户意图为运行本仓库 QA 流水线，例如：

- **帮我跑 QA Agent**（推荐口令）
- 跑 QA Agent / 启动 QA 流水线 / 重跑 QA 流水线

## 默认：IDE 模式（禁止擅自用 CLI）

除非用户**明确要求**「用 CLI」「终端跑」「无头」「--auto」「后台跑」，否则：

- **不要**加 `--auto` / `--cli`
- **不要**让用户在终端选模式

按当前 IDE 选择编排入口（无参数 = 默认 `--ide-chain`）：

| 环境 | 命令 |
|------|------|
| Cursor | `./orchestrators/cursor/run-pipeline.sh` |
| Codex | `./orchestrators/codex/run-pipeline.sh` |
| Claude Code | `./orchestrators/claude-code/run-pipeline.sh` |

产品打回后：

```bash
./orchestrators/<平台>/run-pipeline.sh --from-stage prd-analyze
```

## 各平台推进方式

### Cursor

1. 执行上述命令（`--ide-chain`）
2. Hook 在子 Agent 结束后自动注入下一阶段 Task；侧栏可见
3. 你只做编排：gate reject 停流水线并交 `prd-reject-to-product.md`；**不要**代写阶段产物

### Codex / Claude Code

1. 执行上述命令；脚本生成当前阶段 prompt 后退出
2. **你**在本会话用子 Agent 执行该 prompt（读 `agents/<role>.md` + 对应 Skill）
3. 子 Agent 完成后**再次**运行同一条 `run-pipeline.sh`（无参数）推进下一阶段
4. 全程勿用 `--auto`，除非用户明确要求 CLI
5. `prd-gate` 会按 product/dev/qa/red-team/gatekeeper 子阶段逐个生成 prompt，依次接力

## 仅当用户明确要求 CLI 时

```bash
./orchestrators/<平台>/run-pipeline.sh --auto
# 或
./orchestrators/<平台>/run-pipeline.sh --cli
```

日志：`workspace/artifacts/logs/`

## 禁止

- 未询问即使用 `--auto`
- 让用户「自己去 Task 里选 md」
- 在主会话代写 `00-test-ready-blueprint.json`、`00-prd-gate-report.json` 等子 Agent 产物

详见 `agents/qa-orchestrator.md`、`AGENTS.md`。
