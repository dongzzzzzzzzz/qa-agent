---
name: prd-analyze
description: >-
  全文阅读 PRD/Figma，并结合 AI 自选知识库上下文，产出唯一测试蓝图
  00-test-blueprint.json/md。适用于 QA 流水线 prd-analyze 阶段。
disable-model-invocation: true
---

# PRD 分析（唯一测试蓝图）

## 核心原则

- 本阶段只产出一份测试蓝图：`workspace/artifacts/00-test-blueprint.json/md`。
- 不产出过渡蓝图、内部编号、旧追溯图谱，也不把机器编号泄露给用户。
- 蓝图要让普通产品、QA、研发都能读懂：需求模块 → 测试点 → 测试范围 → 场景。
- PRD/Figma 是最高依据；知识库只补充业务背景、历史风险和模块术语。

## 工作流

### 步骤 1：读取约束边界

读取 `workspace/inputs/config.yaml`，仅提取以下内容供后续使用，**不以此限定测试范围**：
- `target_platform`、`exclude_test_types`、`exclude_topics`（排除项是硬约束）
- `required_coverage` + `prd_contract_obligations`（作为最低兜底清单，稍后与 AI 推断结果合并）
- `execution` 配置

### 步骤 2：独立提取 PRD 义务列表（先于 config 对账）

**每次都必须从零重新推断，即使 workspace/artifacts/snapshots/ 里有历史快照。**

原因：PRD 文档每次可能有细微变化（用户重新提交了 PDF、产品补充了内容），快照记录的是上一次的推断结果，如果直接用快照恢复蓝图，新内容完全不会被分析到，覆盖矩阵显示 pass 但实际上遗漏了新增义务。快照的用途是产品补充文档后的分区重跑对比（判断哪些场景受影响），不是本次分析的输入。

**全文阅读 `workspace/inputs/prd.md`**，从零推断"这份 PRD 要求测什么"，生成 `ai-inferred-obligations`。

每条义务项必须包含：
- `source`：来自 PRD 哪一段（段落标题 + 关键原文）
- `obligation_text`：一句话描述这条义务
- `confidence`：`explicit`（PRD 原文明确）或 `inferred`（根据上下文推断）

提取规则，以下任一形式均构成义务项：
1. 含"应/须/需要/必须/will/shall/must"的功能描述句
2. 所有条件分支：`if X then show/display/calculate Y`
3. 所有 API 字段与 UI 展示的对应规则
4. 所有枚举值的差异化展示逻辑
5. 所有"不展示/不显示/隐藏"的负向规则
6. PRD 明确列出的 in-scope 范围条目

**`confidence=inferred` 的义务项**：在此阶段直接评估能否从 PRD 找到明确验收标准。找不到时写入 `open_questions[]` 而不是生成场景——基于猜测生成的场景会把不确定性带入后续所有阶段，case-review 无法识别这是推断还是事实，最终可能花时间测了一个根本没有 PRD 依据的行为，白白消耗所有下游工作。

### 步骤 3：独立提取 Figma 状态列表（与 PRD 独立，避免先入为主）

按 [reference-figma-analysis.md](reference-figma-analysis.md) 读完整 Figma 原型，**独立**生成 Figma 状态清单（不参考步骤 2 的结论）：
- 每个独立 UI 状态（不同数据条件下的不同展示）
- 每个字段在不同条件下的视觉差异
- 与 PRD 描述明显不一致的地方

### 步骤 4：PRD × Figma 并行对照

将步骤 2 的 PRD 义务列表与步骤 3 的 Figma 状态清单并排对照，按 [reference-prd-figma-alignment.md](reference-prd-figma-alignment.md) 的四色标记分类每条义务项：
- **已覆盖**：PRD 有描述，Figma 有对应状态，一致 → 正常生成场景
- **覆盖不完整**：能测的补场景，不能测的写入 `open_questions[]`
- **设计缺失**：PRD 明文要求但 Figma 未体现 → 写入 `open_questions[]`，标 `blocking=true`。原因：Figma 缺失意味着 UI 预期无从验收，后续用例只能靠猜测写预期结果，即使测了也无法判断结果是否正确
- **设计冲突**：PRD 与 Figma 不一致 → 写入 `open_questions[]`，标 `blocking=true`。原因：两份文档给出了互相矛盾的预期，任何一种理解生成的场景都可能是错的，需要产品先明确以哪个为准，否则测试结论没有意义

发现问题后继续执行后续步骤，不停止流程——问题会在 case-review 结束后统一汇总给产品，这样产品拿到的是完整清单而不是零碎的单条打回。无依据的义务项只写 `open_questions[]`，不生成场景，后续步骤自动跳过。

### 步骤 5：与 config 合并对账

将 AI 推断的义务列表与 `config.yaml` 的 `required_coverage` + `prd_contract_obligations` 做合并：
- config 有、AI 也推断出来的：正常
- config 有、AI **未推断出来**的：强制补入义务列表，并在 `00-knowledge-context.md` 标记 `⚠️ config 兜底补入，AI 未从 PRD 推断到此项，请确认 PRD 是否遗漏`
- AI 推断出来、config **没有**的：自动补入义务列表，在 `00-knowledge-context.md` 标记 `ℹ️ AI 新增，config 未登记`

### 步骤 6：知识库选择（带明确理由）

运行 `python3 scripts/build_knowledge_inventory.py` 生成目录，然后按以下优先级选择文档：

1. 文档名称或内容与本次义务列表中出现的**业务模块名称直接匹配**的
2. 文档包含义务列表中出现的**业务术语**（如"price_frequency"、"FREE 标签"、"pm/pw"）
3. 历史测试用例中涉及**同一功能模块**的用例文档

写 `00-knowledge-context.json/md`，每条 `selected_documents[]` 必须含 `reason`（说明选这份文档解决了哪个义务项的背景理解），不能只列文件名。`excluded_candidates[]` 同样要写排除原因。

### 步骤 7：处理 pending rework

若存在 `workspace/artifacts/.pending-rework-issues.json`：**必须**按其中每条内部项补场景后再 validate（脚本会核销）。

### 步骤 8：提取测试数据（仅针对有依据的场景）

在写蓝图之前，为每个有明确依据的场景提取具体测试数据，写入 `workspace/artifacts/00-test-data.json`，契约见 `contracts/test-data.schema.json`。

每个场景提取：
- `url`：测试入口 URL（browser 通道必填，从 PRD/Figma 的入口描述提取）
- `api_fixture`：api_intercept 通道的 mock 数据（从 PRD 的 API 字段规则提取）
- `boundary_values`：边界值列表（从 PRD 的条件分支和边界描述提取）
- `precondition_data`：前置数据（账号类型、房源状态等）
- `data_source`：必须引用具体的 PRD 段落或 Figma frame，不能只写"来自 PRD"

`open_questions[]` 中 blocking=true 的义务项对应的场景**跳过**，不提取测试数据。

### 步骤 9：写蓝图

写 `00-test-blueprint.json`，契约见 `contracts/test-blueprint.schema.json`。

每个场景必须填写两个字段：

**`derivation`**（推断依据）：
```json
{
  "prd_source": "PRD section 3.2，原文：rent/month 价格展示为 X/pm",
  "figma_source": "Figma frame #价格标签-租赁（可选）",
  "expected_result_basis": "PRD section 3.2 原文直接引用",
  "confidence": "explicit"
}
```

**`covers`**（义务覆盖声明）：列出这个场景**核心目的**对应的 config 义务项 id。

填写原则：只填这个场景存在的根本原因对应的义务，不要因为场景描述里顺带提到某个词就填进来。
- `S-01.01.01`（测月租价格展示格式）→ `covers: ["rent-pm-display"]`
- `S-03.01.01`（测 Property To Rent 子类目入口）→ `covers: ["property-to-rent"]`，不填 `rent-pm-display`，即使场景步骤里出现了"pm"
- `S-04.02.01`（测 API type=FREE amount=0）→ `covers: ["api-free-amount-zero"]`
- 纯回归或边界场景，不对应任何 config 义务 → `covers: []`

这个字段是覆盖矩阵准确性的基础——脚本直接读 covers 来判断每条义务是否被覆盖，而不是猜测场景描述里的关键词。如果填错，覆盖矩阵会给出错误信号，影响后续评审判断。

`open_questions[]` 已在步骤 2-4 中提前写入，蓝图场景**只包含有明确依据的条目**。

### 步骤 10：自检

```bash
python3 scripts/check_prd_coverage.py   # 有 FAIL 则补场景重跑直至 exit 0
python3 scripts/render_test_blueprint.py
python3 scripts/validate-artifacts.py --stage prd-analyze
```

自检通过后，把当前所有场景写入快照：

```bash
python3 scripts/snapshot_blueprint.py   # 生成 00-approved-snapshot.json
```

快照用于产品补充文档后的分区重跑，记录每个场景的 scenario_id + derivation + expected_results hash。

**若 `open_questions[]` 中有 blocking=true 的条目**：自检通过后，额外生成打回报告 `workspace/artifacts/PRD-REJECTED.md`，列出所有产品问题，格式：

```markdown
# 需要产品补充的问题

## 已完成部分
- 共 N 个场景已生成蓝图，可继续执行后续流程

## 需要产品补充（共 M 条）
### Q-01 [设计冲突]
位置：PRD section X vs Figma frame Y
问题：...
影响：无法生成对应测试场景

产品补充后重跑，系统自动处理剩余部分。
```

流水线在 case-review 结束后统一判断是否需要停止并交付此报告。

## 蓝图写法

蓝图必须按业务主题聚合，不要按 PRD 小节机械拆散。推荐模块：

- 租赁价格展示
- 出售房价格保持不变
- Feed 与 PDP 一致性
- Feed API / 数据契约可测点
- A/B 实验与指标
- 异常/脏数据
- 范围外回归

每个测试点必须写清：

- 依据：来自 PRD 哪一段、Figma 哪个页面、或知识库哪份参考。
- 验收规则：一句能判断 pass/fail 的业务规则。
- 测试范围：包含哪些入口、平台、数据、状态；不包含什么。
- 场景：具体条件下验证什么结果；必填 `execution_channel`（`browser` / `api_intercept` / `native_app` / `manual`）；`automatable` 仅「是」或「否」，且须与通道一致（见 [reference-blueprint.md](reference-blueprint.md)）。

## 禁止做的事，以及为什么

- 不要产出多份蓝图或过渡蓝图：只有一份蓝图才能保证下游所有阶段用的是同一份真相，多份蓝图会让 case-generate 和 case-review 不知道以哪个为准。
- 不要把 PRD 未闭合的问题伪装成可执行场景：这样生成的场景预期结果是猜测的，执行后无法判断 pass/fail 是需求问题还是代码问题，失去了测试的意义。
- 不要写”行为符合 PRD””记录实际展示””待后续裁定”这类预期结果：这些描述在自动化执行时无法转化为断言条件，等于没有预期。

## 完成标准

```bash
python3 scripts/render_test_blueprint.py
python3 scripts/validate-artifacts.py --stage prd-analyze
```
