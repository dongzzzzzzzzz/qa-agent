# Perspective Brief Reference

`case-review-perspective-brief.json` 由脚本生成，用于给四个视角提供最低必答问题和推荐知识库阅读清单。

## 字段

- `perspectives.<id>.questions[]`: 本视角最低必答问题。子 Agent 必须在 `perspective_notes[]` 中逐题回答。
- `knowledge_reading_list.<id>[]`: 推荐阅读文档，不是白名单。子 Agent 可以读取 `00-knowledge-context.json` 中其他相关文档，但要记录原因。
- `question_id`: findings 中 `perspective_notes[].question_id` 必须与 brief 对齐。
- `scenario_id` / `point_id` / `obligation_id`: 问题锚点，用于帮助审稿，不代表只能审这些对象。

## 视角

- `product`: 产品验收、PRD/Figma 闭合、可裁定性。
- `qa`: 主链路、边界、异常、状态组合、漏测。
- `testability`: 执行通道、测试数据、环境状态、断言可观察性、自动化可行性。
- `red_team`: 历史回归、未知枚举、空值、金额、状态、降级和线上高风险表现。
