# QA Agent（Claude Code）

用户说 **「帮我跑 QA Agent」** 时：

1. 默认 **IDE 模式**，执行：

```bash
./orchestrators/claude-code/run-pipeline.sh
```

2. **不要**使用 `--auto`，除非用户明确要求 CLI/终端无头。
3. 每阶段按 `workspace/artifacts/prompts/<stage>.md` 拉起子 Agent；完成后再次运行上条命令推进。
4. 编排与门禁规则见 `AGENTS.md` 与 `agents/qa-orchestrator.md`。
