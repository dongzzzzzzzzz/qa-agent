---
name: case-generate
description: >-
  Renders 02-test-cases.md from 00-test-ready-blueprint.json without adding or
  removing scenarios. Use in case-generate stage or when converting blueprint to
  Markdown test cases.
---

# 用例生成（蓝图渲染）

## 何时使用

- 流水线阶段 `case-generate`
- 主输入：`workspace/artifacts/00-test-ready-blueprint.json`
- 参考：`01-prd-analysis.json`（可选，仅背景）

## 规则

1. **禁止**新增、删除或合并 `scenarios[]` 中的场景（`SC-xxx` 与蓝图一一对应）。
2. 评审重试时：仅可按 `revision_hints` 润色步骤/预期措辞，**不得**新增 `SC-xxx` 编号。
3. 禁止出现：需产品确认、待产品补充、找产品。

## 步骤

```bash
python3 scripts/render_cases_from_blueprint.py
python3 scripts/validate-artifacts.py --stage case-generate
```

或手写 `02-test-cases.md`，但须通过 fidelity 校验（表格编号集 = blueprint 场景 id 集）。

## 输出格式

- 顶部 Markdown 表格：编号 | 模块 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 测试类型
- 编号使用蓝图 `scenarios[].id`（如 `SC-001`）
- 下方 XMind 层级：`# 模块` → `## 类型` → `### 标题`

## 参考

- 格式细则：`reference.md`（若存在）
