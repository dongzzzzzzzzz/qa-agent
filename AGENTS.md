# QA Agent — 仓库级 Agent 说明

本文件供 **Cursor、Codex、Claude Code** 等 IDE 中的主 Agent 读取。

## 启动口令（对用户说这一句即可）

> **帮我跑 QA Agent**

同义：**跑 QA Agent**、**启动 QA 流水线**、**重跑 QA 流水线**。

## 默认行为：IDE，不是 CLI

- **默认**：IDE 内子 Agent 推进（`--ide-chain`），编排脚本**不要**加 `--auto`。
- **仅当用户明确说**要用 CLI / 终端无头 / `--auto` / 后台跑时，才使用 `--auto` 或 `--cli`。

| 平台 | 默认命令 |
|------|----------|
| Cursor | `./orchestrators/cursor/run-pipeline.sh` |
| Codex | `./orchestrators/codex/run-pipeline.sh` |
| Claude Code | `./orchestrators/claude-code/run-pipeline.sh` |

产品修订 PRD 后：

```bash
./orchestrators/<平台>/run-pipeline.sh --from-stage prd-analyze
```

## 主 Agent 职责

1. 运行上表命令（或按平台重复执行以推进阶段）
2. **不要**代替子 Agent 写入阶段产物
3. `prd-gate` 为 `reject` 时停止，交付 `workspace/artifacts/prd-reject-to-product.md`
4. 子 Agent 失败时查看 `workspace/artifacts/logs/`

角色边界：`agents/qa-orchestrator.md`  
流水线定义：`pipeline.yaml`  
Cursor 细则：`.cursor/rules/qa-pipeline-ide-auto.mdc`

## Cursor 特有

已配置 `.cursor/hooks.json`：`--ide-chain` 激活后，**仅 `subagentStop`** 且存在等待标记时注入下一阶段 followup（主会话 `stop` 不会误弹 Task 指令）。

## Codex / Claude Code

无 Cursor Hook 时属于 IDE 半自动链：每阶段脚本生成 prompt 后退出 → 主 Agent 拉起子 Agent 执行 prompt → 子 Agent 产物就绪后，主 Agent 再运行同一条 `run-pipeline.sh` 进入下一阶段。不要让用户手动挑 prompt；主 Agent 负责接力。

## 维护者：CLI 模式

```bash
./orchestrators/<平台>/run-pipeline.sh --auto   # 或 --cli
```

需对应平台 CLI 已登录（见 README）。
