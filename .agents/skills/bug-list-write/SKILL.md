---
name: bug-list-write
description: >-
  将失败/阻塞用例整理为 Bug 清单 Markdown。在 post-process 的 bug-list-write
  分支由 bug-list-writer 子 Agent 调用。
---

# Bug 清单 Skill

## 何时使用

- post-process 分支，条件：`04-execution-result.json` 中 `has_fail=true`
- 或存在 `status` 为 `fail` / `block` 的用例

## 步骤

1. 读取 `04-execution-result.json`，筛选 `fail` 与 `block`。
2. 从 `workspace/artifacts/evidence/` 关联截图与日志。
3. 按模板写入 `05b-bug-list.md`：
   - `# Bug List`
   - 每条 `## BUG-NNN: 标题`
   - 字段：关联用例、严重级、复现步骤、期望/实际、证据路径
4. 严重级映射建议：block→Blocker，fail 且 P0→Critical，P1→Major，其余 Minor。
5. 运行 `validate-artifacts.py --stage bug-list-write`。

## 后续扩展

- 导出 Jira/Linear JSON
- 自动附加录屏链接
