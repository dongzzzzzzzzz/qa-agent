---
name: case-review-perspective
description: >-
  case-review 四视角子 Agent 执行规范：读取 perspective brief 与知识库，逐题作答并输出单视角 findings。
---

# Case Review Perspective

你是 case-review 流水线独立阶段拉起的视角子 Agent。你的任务是只从一个 perspective 审稿，并写一份可审计 findings。

## 输入

- `workspace/artifacts/case-review-perspective-brief.json`
- `workspace/artifacts/00-test-blueprint.json`
- `workspace/artifacts/02-test-cases.md`
- `workspace/artifacts/00-knowledge-context.json`
- brief 中 `knowledge_reading_list.<perspective>[]` 推荐的知识库原文
- `workspace/artifacts/.subagent-launch-case-review-<slug>.json`

## 输出契约

写入 `workspace/artifacts/case-review-findings-<slug>.json`：

- product → `case-review-findings-product.json`
- qa → `case-review-findings-qa.json`
- testability → `case-review-findings-testability.json`
- red_team → `case-review-findings-red-team.json`

`red_team` 的 JSON 字段值必须是 `red_team`，只有文件 slug 使用 `red-team`。

## 必做流程

1. 读取 brief 中本视角 `questions[]`，这是最低必答清单。
2. 读取推荐知识库原文至少 1 份；如果没有相关历史，在 `knowledge_docs_read[]` 写明 `no relevant history in selected knowledge context`。
3. `knowledge_docs_read[]` 只记录实际读取过的文档；`perspective_notes[].knowledge_ref` 若引用知识库，必须能对应到已读文档。
4. 对每个 question 写一条 `perspective_notes[]`，包含 `question_id`、`verdict`、`rationale`。
5. 发现问题时写入 `issues[]`；发现非阻断观察写入 `extra_notes[]`。
6. PRD 已明确写出的分支、枚举、fallback 或验收义务如果未覆盖，不能只写 `extra_notes[]`，必须写入 `issues[]`。默认 `root_cause=qa_undercoverage`、`audience=internal`、`retry_target=prd-analyze`；若影响 P0 主链路，severity 用 `major`，否则用 `minor`。
7. 只要 `issues[]` 非空，本视角至少一条相关 `perspective_notes[].verdict` 必须是 `fail` 或 `blocked`，不能出现“问题存在但所有问题回答都是 pass”。
8. `extra_notes[]` 里如果提到历史、惯例、同类问题、回归或知识库，必须填写 `knowledge_ref`。
9. 可自检 `python3 scripts/validate-artifacts.py --stage case-review-perspective --perspective <id>`。
10. 不写 completed/validate trace，不写 `.stage-done-*` marker；这些由 runner/Hook 在阶段边界统一落账。这样做能避免一个子 Agent 在同一上下文里把四个视角都“补成已完成”。

这些字段是审计证据，不只是 schema 字段。`knowledge_docs_read[]` 证明知识库确实被纳入判断；逐题 `perspective_notes[]` 证明本视角审了什么；`issues[]` 与 fail/blocked note 对齐，能避免“报告说有问题，但看不出哪类评审发现了问题”。

## 归因

- PRD 缺失、TBD、章节矛盾 → `root_cause=prd`, `audience=product`, `retry_target=product`
- Figma 缺状态或与 PRD 冲突 → `root_cause=figma`, `audience=product`, `retry_target=product`
- PRD 可支持两种合理解读 → `root_cause=assumption_unresolved`, `audience=product`, `retry_target=product`
- PRD/Figma 清晰但蓝图漏测或 false coverage → `root_cause=qa_undercoverage`, `audience=internal`, `retry_target=prd-analyze`
- 蓝图正确但 Markdown 用例步骤、数据或预期写法有问题 → `root_cause=case_generation`, `audience=internal`, `retry_target=case-generate`

## 边界说明

- 不写 `03-review-report.json`，因为最终报告由 merge 阶段统一合并五份 findings，避免单个视角覆盖其他视角证据。
- 不修改蓝图、用例、PRD 或配置；本阶段负责评审，返工由 gate 路由到 prd-analyze 或 case-generate。
- 不把 questions 当作上限；brief 只是最低必答清单，本视角发现的额外风险也要补充。
- 不为了通过校验手填 `finding_count=0`；它必须等于 `issues.length`，否则后续合并计数和产品/内部路由会失真。
