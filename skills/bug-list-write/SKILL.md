---
name: bug-list-write
description: >-
  Bug 清单 Markdown 格式参考。当前流水线不再单独启动 bug-list-writer；
  test-execute 阶段发现 fail/block 时直接写入 05b-bug-list.md。
---

# Bug 清单格式参考

## 何时使用

- `test-execute` 阶段存在 `status` 为 `fail` / `block` 的用例
- `test-executor` 需要在同一阶段写 `workspace/artifacts/05b-bug-list.md`

## 步骤

1. 读取 `04-execution-result.json`，筛选 `fail` 与 `block`。
2. 从 `workspace/artifacts/evidence/` 关联截图与日志。
3. 按模板写入 `05b-bug-list.md`：
   - `# Bug List`
   - 每条 `## BUG-NNN: 标题`
   - 字段：关联用例、严重级、复现步骤、期望/实际、证据路径
4. 严重级映射建议：block→Blocker，fail 且 P0→Critical，P1→Major，其余 Minor。
5. 运行 `validate-artifacts.py --stage test-execute`；仅单独检查格式时才运行 `--stage bug-list-write`。

## 后续扩展

- 导出 Jira/Linear JSON
- 自动附加录屏链接
