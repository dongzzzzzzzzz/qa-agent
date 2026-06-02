---
name: case-review
description: >-
  Reviews test cases for fidelity to test-ready blueprint and render quality.
  Does not re-interpret PRD or request product input. Use in case-review stage.
---

# 用例评审（蓝图对照）

## 何时使用

- 流水线阶段 `case-review`
- 输入：`00-test-ready-blueprint.json` + `02-test-cases.md`
- 参考：`01-prd-analysis.json`（可选）

## 评审范围（仅限）

- [ ] 每个 blueprint `scenarios[].id` 在表格中出现且仅出现一次
- [ ] 无蓝图外的额外用例编号
- [ ] 步骤可执行、预期可验证
- [ ] 优先级/类型与蓝图一致（允许文案润色差异）
- [ ] 无「需产品确认」「待产品补充」等表述

## 禁止作为 fail 理由

- 「PRD 未写」类缺口（应已在 prd-gate reject 或已进 `assumptions[]`）
- 要求产品补充需求

## 步骤

1. 对照 `coverage_matrix` 与蓝图场景分布计算 `coverage_score`。
2. `gaps` 仅列：**漏渲染**、**多余用例**、**不可执行**，并映射到 `SC-xxx`。
3. `coverage_score < pass_threshold`（默认 0.85）→ `verdict=fail`，`revision_hints` 指向 case-generator 修正渲染。
4. 写入 `03-review-report.json`，运行 `validate-artifacts.py --stage case-review`。

## 注意

- 不直接改 `02-test-cases.md`。
