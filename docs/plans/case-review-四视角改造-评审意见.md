# case-review 四视角改造方案 — 评审意见

> 评审对象：[`/Users/a58/.cursor/plans/case-review_四视角改造_b1ec26e6.plan.md`](/Users/a58/.cursor/plans/case-review_四视角改造_b1ec26e6.plan.md)  
> 评审日期：2026-06-05  
> 总评：**7.5 / 10** — 方向正确，机制设计成熟，但复杂度与若干「靠约定而非程序强制」的环节仍偏高。

---

## 一、总评摘要

| 维度 | 评分 | 一句话 |
|------|------|--------|
| 问题诊断 | 9/10 | 单 Agent 四视角不可审计，判断准确 |
| 方案设计 | 8/10 | 编排者 + 4 子 Agent + merge + Hook 锁，结构合理 |
| 可落地性 | 7/10 | 工作量大，嵌套 Task 合规仍靠 Skill 约定 |
| QA 收益 | 7/10 | 内部漏测有望下降，产品打回率几乎不变 |
| 性价比 | 6.5/10 | 值得做，但建议分 MVP / Full 两阶段 |

**结论**：可作为实施依据；建议先补本文「必须修订项」再动手写代码。

---

## 二、必须修订项（动手前建议写进方案）

### 2.1 嵌套 Task 无法被程序强制

**问题**：方案依赖 case-reviewer「必须用 Task 拉起四视角」，但 Cursor 侧没有 API 供 `validate` 校验「是否真的起了 4 个子 Agent」。编排者理论上仍可自己写齐 4 份 `findings-*.json`（比写最终 report 更繁琐，但可行）。

**影响**：方案把保证程度从「Skill 自觉」提升到「产物契约 + 分文件 validate」，是实质性进步，但**不是 100% 防偷懒**。

**建议**：

- 在方案中明确这一上限，避免过度承诺「一定能按流程走」。
- 长期：若 Cursor 暴露子 Agent 调用记录，再接入校验。

---

### 2.2 orchestrating lock 缺少失败 / 过期清理

**问题**：`.case-review-orchestrating.lock` 若因编排者崩溃、超时、validate 失败而残留，在 `stage_lock_recent`（2h）内 Hook 可能既不注入 followup，也没有最终报告，流水线**静默卡住**。

**建议补进方案**：

- lock 增加 `expires_at`（建议 3h）与 `perspectives_completed[]` 进度字段。
- Hook 检测 lock 过期 → 清理 lock + 可选写 `case-review-orchestration-failed.md` + 返回 `PIPELINE_BLOCKED` 交主 Agent。
- validate 失败时编排者 Skill 要求删除 lock 前写入失败原因文件。

---

### 2.3 precheck 入口写法二选一未定

**问题**：方案 §2.1 步骤 1 写「`build_case_review_precheck.py` **或** `validate --stage case-review-precheck`」，实现时容易分叉成两套路径。

**建议**：**只保留一种**——推荐 `validate-artifacts.py --stage case-review-precheck` 内部调用现有 `run_case_review_precheck()`，不新增平行脚本。

---

### 2.4 `extra_notes[]` 在正文出现但 schema 未定义

**问题**：§一、§三允许子 Agent 写 `extra_notes[]`，但 §4.1 findings schema 示例中**没有该字段**，validate 无法校验。

**建议**：在 `case-review-findings.schema.json` 中正式增加 `extra_notes[]`（可选数组），或统一并入 `perspective_notes` 并约定 `question_id: "EXTRA-*"`。

---

### 2.5 串行 vs 并行未拍板

**问题**：§2.3 写「推荐串行」，mermaid 写「串行或并行」，实现与测试标准不一致。

**建议**：**P0 默认串行**；并行标 P2，并单独写 Hook 压测与侧栏行为说明。

---

### 2.6 编排者「三层结构评审」与四视角职责重叠

**问题**：编排者步骤 2 做 derivation / coverage / 用例 1:1 全量审查，qa / product 视角在 brief 里也会问覆盖与验收，**重复劳动 + 编排者上下文过长**，质量反而可能下降。

**建议**：

| 类型 | 建议负责方 |
|------|------------|
| GATE 吸收、矩阵 fail、用例条数 1:1 | 编排者 → `findings-structural.json`（可部分脚本化） |
| derivation 全量对抗审查 | 编排者仅抽检 `confidence=inferred` 场景 |
| PRD 义务是否可验收 | product 视角 |
| 边界 / 漏测 / 历史回归 | qa + red_team 视角 |
| 通道 / 数据 / 断言可执行性 | testability 视角 |

在方案中增加「职责边界表」，避免五份 findings 报同一问题五次。

---

## 三、架构与工程风险

### 3.1 case-review 耗时与成本显著上升

- 每次审稿：**1 编排 + 4 视角 ≈ 5 次 LLM 会话**，外加多次 validate、brief 生成、merge。
- 无人值守总时长和 token 账单明显上涨，需在汇报 / 文档中设预期，避免被质疑「变慢了」。

### 3.2 维护面变宽

改动 `review-report.schema` 时需同步：

- merge 脚本
- 4 个 perspective agent + 共用 Skill
- `validate` 分阶段逻辑
- `render_case_review_notice` 展示

缺少单一契约源时，容易出现「merge 过了但 notice 展示错」的漂移。

### 3.3 与现有代码的 breaking change

当前 [`scripts/validate-artifacts.py`](../scripts/validate-artifacts.py) 在 `--stage case-review` 时**边校验边跑 precheck**。方案要求拆出 `case-review-precheck`，属于**行为变更**，`selftest` 与现有跑批文档需一并更新。

### 3.4 `red_team` vs `red-team` 命名

方案已提醒 JSON 字段用 `red_team`、文件 slug 用 `red-team`。实现时 validate / merge / pipeline_runner 清理列表极易错配，**必须在 selftest 用真实文件名覆盖**。

### 3.5 文档与规则未同步的风险

以下文件仍描述「case-review = 1 个审稿 AI」：

- [`.cursor/rules/qa-pipeline-ide-auto.mdc`](../.cursor/rules/qa-pipeline-ide-auto.mdc)
- [`reports/qa-agent-progress-demo.html`](../reports/qa-agent-progress-demo.html)
- [`agents/case-reviewer.md`](../agents/case-reviewer.md)（改造前）

方案将 HTML / 架构 yaml 标为「可选」，**建议升为 P0 必做**，否则团队认知与实现脱节。

---

## 四、QA 有效性层面的局限

### 4.1 对产品打回帮助有限

以 HP Feed 跑批为例：6 条产品 blocker（Figma PLACEHOLDER、A/B TBD、格式矛盾等）来自 GATE / open_questions，**四视角子 Agent 读再多知识库也解决不了**。

改造的主要收益在：

- 内部漏测（如未知 type 回退、live Feed 可测性）
- 审稿过程可审计、可 citing 历史用例

**不应把「提高 pass 率」作为本方案核心 KPI。**

### 4.2 brief 脚本质量是天花板

四子 Agent 再独立，也只能围绕 brief 的 `questions[]` 和 seed 逻辑发挥。若 brief 仅从关键词拼题、不绑定 `scenario_id` / `obligation id`，动态审稿仍会**显死板**。

**建议 brief 验收标准（写进方案）**：

- 每个 perspective ≥ 2 题；
- 全 brief 至少 50% 的题绑定具体 `scenario_id` 或 `prd_contract_obligations.id`；
- red_team 至少 1 题来自蓝图 API/枚举字段，而非纯模板句。

### 4.3 去重可能掩盖问题

merge 保守去重合理，但若 `finding_count_raw - finding_count_merged` 超过阈值（建议 ≥3 或 ≥30%），应 **fail merge** 并要求编排者人工确认，避免静默吞 issue。

---

## 五、方案写得好的部分（保留，勿改方向）

1. **Hook 仍只拉起 case-review 一次**，不破坏 ide-chain。
2. **precheck 与 final validate 拆分**，避免「报告不存在却跑 case-review validate」的现网坑。
3. **`03-review-report.json.tmp` 原子发布**，防止 Hook 把半成品当完成态。
4. **`structural` 与 `tri_party` 计数分离**，汇报与门禁更清晰。
5. **AI / 脚本边界表**（§一），merge 不得静默改归因。
6. **知识库推荐阅读非白名单**，兼顾弹性与背景补充。
7. **复用** `pipeline_runner` 已预埋的 `case-review-findings-*.json` 清理路径。

---

## 六、建议的实施分期（方案十二的补充）

方案原顺序合理，建议显式拆为两阶段，降低一次性翻车风险：

### Phase A — MVP（验证机制，约 1～2 天）

- Hook orchestrating lock + 过期清理
- 4 个 perspective agent / prompt / 共用 Skill
- **手写或静态** brief 样例（可先不实现 brief 脚本）
- 简化 merge（先拼接、弱去重）
- 跑通 1 次 HP Feed case-review，确认侧栏可见 **1 编排 + 4 视角** Task

**通过标准**：五份 findings 齐全 → merge → validate 通过；Hook 不误推进。

### Phase B — Full（补智能与严校验，约 2～3 天）

- `build_case_review_perspective_brief.py`
- `case-review-precheck` 独立 stage
- 严格 merge 去重 + `finding_count_raw/merged` 校验
- selftest 全覆盖
- 更新 rules / 汇报 HTML / qa-orchestrator 说明

**明确不在 MVP 做**：四视角提升为 Hook 级独立 stage；并行 4 Task；修改 GATE 规则本身。

---

## 七、待你拍板的问题

| # | 问题 | 选项 |
|---|------|------|
| 1 | 四视角 Task 顺序 | A. 串行（推荐） B. 并行 |
| 2 | brief 首版 | A. MVP 用手写样例 B. 一步到位上脚本 |
| 3 | 编排者 structural 范围 | A. 全量三层 B. 仅 GATE + 矩阵 + 1:1 + inferred 抽检（推荐） |
| 4 | 评审意见文件放哪 | 当前：`docs/plans/`（可提交 git） |

---

## 八、修订后预期效果（设 realistic 预期）

| 指标 | 改造前 | 改造后（合理预期） |
|------|--------|-------------------|
| 四视角是否可审计 | 难，仅 tri_party 数字 | 五份 findings + perspective_notes |
| 内部漏测检出 | 依赖单 Agent 发挥 | qa/red_team 独立上下文，有望提升 |
| 产品打回率 | 由 PRD/Figma 闭合度决定 | **基本不变** |
| case-review 耗时 | 1× Agent | 约 3～5× |
| 防编排者偷懒 | 无 | 产物契约级，非程序强制 Task |

---

*本文档由方案评审产出，不代表已实现；实现时请以修订后的 plan 为准。*
