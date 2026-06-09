---
name: case-review
description: >-
  用例评审门禁：prepare 生成共享 brief 与结构 findings，流水线独立执行四视角，再合并 findings，决定产品修订、内部返工或放行。
---

# Case Review Gate

case-review 对外仍是一个业务阶段，但实现上拆成 6 个流水线内部阶段：

```text
case-review-prepare
case-review-product
case-review-qa
case-review-testability
case-review-red-team
case-review-merge
```

这样拆分的目的不是形式化分工，而是让每个视角都有独立 prompt、独立 launch lock、独立 trace 和独立 findings。最终校验只信这些可审计证据；单个编排者一次性写出四份 findings 不能证明四个角色真的评审过。

## case-review-prepare

本阶段准备共享输入，不做四视角语义评审。

1. 运行 `python3 scripts/build_case_review_perspective_brief.py`。
2. 追加 `python3 scripts/case_review_trace.py brief_built --summary "case-review perspective brief generated"`。
3. 运行 `python3 scripts/validate-artifacts.py --stage case-review-precheck`。
4. 追加 `python3 scripts/case_review_trace.py precheck_done --summary "case-review precheck generated and validated"`。
5. 只写 `workspace/artifacts/case-review-findings-structural.json`。
6. 追加 `python3 scripts/case_review_trace.py structural_findings_written --summary "structural findings written"`。
7. 写入 `workspace/artifacts/.case-review-prepare.done`。

structural findings 范围：

- GATE precheck 是否被吸收
- coverage matrix fail
- 蓝图场景与用例数量是否 1:1
- 缺文件、缺字段、明显结构错误
- high-risk derivation 抽检

structural 不替四视角做完整语义评审。

## 四个 perspective 阶段

四个阶段由 Hook/runner 按顺序拉起：

- `case-review-product`
- `case-review-qa`
- `case-review-testability`
- `case-review-red-team`

每个 perspective 子 Agent 只写自己的 findings。可以自检：

```bash
python3 scripts/validate-artifacts.py --stage case-review-perspective --perspective <id>
```

Hook/runner 在真实拉起子 Agent 前写 `.subagent-launch-case-review-<slug>.json` 和 `perspective_task_started` trace。子 Agent 完成后，runner 负责 validate、追加 `perspective_task_completed` / `perspective_validate_passed`、写 `.stage-done-case-review-<slug>.json`。

如果能从侧栏或工具回执拿到真实 Agent ID，使用 `--agent-id <id>`；拿不到时必须写 `--agent-id-unavailable-reason`。
如果某个 perspective 需要重试，上一轮 started 先补一条终止事件：

```bash
python3 scripts/case_review_trace.py perspective_task_failed --perspective <id> --summary "<失败原因>"
# 或
python3 scripts/case_review_trace.py perspective_task_cancelled --perspective <id> --summary "<取消原因>"
```

最终校验会检查 stage_name、launch_id、launch_lock_path、prompt_path、findings_path、validate 结果、逐题回答、知识库证据和最小执行时长。缺任何关键证据都失败。

不要把四个 perspective 合并成一个 Task。即使一个 Task 顺序写出四份 findings，也只能证明同一上下文完成了四份文件，不能证明四个角色独立评审。runner 只会按当前 stage 写一个 `.stage-done-*` marker，后续视角仍必须逐阶段拉起。

## case-review-merge

本阶段由 runner 确定性执行合并脚本，不新增语义问题：

```bash
python3 scripts/merge_case_review_findings.py
python3 scripts/case_review_trace.py merge_done --summary "five findings merged into review report"
python3 scripts/validate-artifacts.py --stage case-review
python3 scripts/case_review_trace.py final_validate_passed --summary "final case-review validation passed"
python3 scripts/validate-artifacts.py --stage case-review
python3 scripts/validate-artifacts.py --mark-done case-review
```

`--mark-done case-review` 会写入阶段状态，并在存在内部返工问题时触发 case-review gate 决策。mixed reject 的处理原则是：先自动清理内部蓝图/用例问题并重跑，等内部项清零后，若仍有产品问题再交付产品修订说明。这样产品收到的是 QA 自身已处理完后的需求缺口，不会夹杂内部漏测噪音。

`--mark-done case-review` 必须写入 `00-meta.json.stage_result`：

- `STAGE_DONE`：无产品问题、无内部问题
- `PRODUCT_REJECT`：存在产品问题
- `INTERNAL_REWORK`：仅存在内部问题
- `PIPELINE_BLOCKED`：无法归类或需要人工介入

## 失败处理

任何命令失败时，写清失败文件或日志，交主 Agent/Hooks 处理。建议包含：

- 失败命令
- stderr 摘要
- 已完成 perspectives
- 当前 trace / launch lock 摘要

不要通过补写 trace 绕过失败。trace 是审计证据，证据不足时应该失败并重跑对应阶段。

## 归因路由

- `prd` / `figma` / `assumption_unresolved` → `audience=product`, `retry_target=product`
- `qa_undercoverage` → `audience=internal`, `retry_target=prd-analyze`
- `case_generation` → `audience=internal`, `retry_target=case-generate`

脚本发现不合法路由会 fail；不要让脚本替你改归因。
