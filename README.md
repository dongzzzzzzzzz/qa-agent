# QA Agent — 资深 QA 多 Agent 流水线

将 Cursor、Codex、Claude Code 编排为资深 QA 工程师角色：输入 PRD + Figma 后，自动完成需求分析 → 用例生成 → 用例评审 → 测试执行 → 成功转脚本 / 失败转 Bug 清单。

## 快速开始

### 1. 准备输入

```bash
cp workspace/inputs/prd.md.example workspace/inputs/prd.md
cp workspace/inputs/figma.url.example workspace/inputs/figma.url
# 编辑 prd.md 与 figma.url 为实际内容
```

可选：

```bash
cp workspace/inputs/config.yaml.example workspace/inputs/config.yaml
cp workspace/inputs/env.json.example workspace/inputs/env.json
```

`env.json` 只放测试环境信息（如 `base_url`、浏览器、设备），不要放 token、password、API key 等密钥。

### 2. 初始化环境（首次）

```bash
./scripts/setup.sh
```

或手动：

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./scripts/sync-skills.sh
```

### 3. 运行流水线

在 **Cursor / Codex / Claude Code** 的 Composer 里说：

> **帮我跑 QA Agent**

主 Agent 会按 [AGENTS.md](AGENTS.md) 与 [qa-pipeline-start](skills/qa-pipeline-start/SKILL.md) 执行；**默认 IDE 模式**，不会擅自用 CLI。

| 平台 | 默认命令（无参数 = `--ide-chain`） |
|------|-----------------------------------|
| Cursor | `./orchestrators/cursor/run-pipeline.sh` |
| Codex | `./orchestrators/codex/run-pipeline.sh` |
| Claude Code | `./orchestrators/claude-code/run-pipeline.sh` |

**默认行为（`--ide-chain`）**：Cursor 下 Hook 用 **Task followup** 链式推进，子 Agent **侧栏可见**。Codex/Claude Code 无 Cursor Hook，属于 **IDE 半自动链式推进**：主 Agent 按每阶段 prompt 拉子 Agent，子 Agent 完成后再次运行上表命令；runner 会按阶段产物继续推进。**仅当用户明确要求 CLI** 时才加 `--auto` 或 `--cli`（后台，见 `workspace/artifacts/logs/`）。

产品打回后：

```bash
./orchestrators/cursor/run-pipeline.sh --from-stage prd-analyze
```

说「**帮我跑 QA Agent**」时，主 Agent 应执行上表命令（勿默认 `--auto`）；Cursor 下 Hook 还会在阶段结束时自动启动下一子 Agent。

<details><summary>维护者选项（用户可忽略）</summary>

| 标志 | 说明 |
|------|------|
| `--dry-run` | 只生成 prompt，不拉起子 Agent |
| `--execute` | 只校验已有产物 |
| `--ide` | 仅轮询产物（不自动 launch，旧模式） |

</details>

**认证（`--auto` 前必做）**

```bash
# Cursor
export CURSOR_API_KEY=xxx   # 或 cursor agent login
./orchestrators/cursor/run-pipeline.sh --check-auth

# Codex
codex login
./orchestrators/codex/run-pipeline.sh --check-auth

# Claude Code
# 配置 Anthropic API / claude login
./orchestrators/claude-code/run-pipeline.sh --check-auth
```

**在 IDE 里自动调起 Agent（推荐，无需 API Key）**

Cursor **没有**公开 API 从终端直接打开 Composer 窗口，但可用 **Hooks + Task 子 Agent** 在 IDE 内自动链式推进：

1. 项目已配置 [`.cursor/hooks.json`](.cursor/hooks.json)（`run-pipeline.sh` 激活后 Hook 才推进；**仅子 Agent 结束 `subagentStop`** 链式推进，主会话 `stop` 不会突然注入 prd-gate）
2. 在 Composer 中说：**「帮我跑 QA Agent」**（见 [qa-pipeline-ide-auto](.cursor/rules/qa-pipeline-ide-auto.mdc)、[AGENTS.md](AGENTS.md)）
3. 用 **Task** 跑各阶段 prompt；**子 Agent 结束后** Hook 自动提交下一阶段 follow-up

你会在 IDE 里**看到**每个 Task 子 Agent 的执行过程，而不是终端黑盒。

**终端轮询备选（仍可见 prompt，需手动 Composer）：**

```bash
./orchestrators/cursor/run-pipeline.sh --ide
```

**只有 IDE 账号、CLI 需单独登录：**

```bash
cursor agent login   # 浏览器 OAuth，仍无需 API Key
./orchestrators/cursor/run-pipeline.sh --auto   # 终端 cursor agent -p，IDE 内不可见
```

**自动 CLI 模式（需 `cursor agent login` 或 API Key）**

```bash
# Cursor — 使用 cursor agent -p
./orchestrators/cursor/run-pipeline.sh --auto

# Codex — 使用 codex exec
./orchestrators/codex/run-pipeline.sh --auto

# Claude Code — 使用 claude -p
./orchestrators/claude-code/run-pipeline.sh --auto
```

无人值守（跳过工具确认，慎用）：

```bash
export QA_AGENT_YOLO=1
./orchestrators/codex/run-pipeline.sh --auto
```

`QA_AGENT_YOLO=1` 会让 Codex 使用 `--dangerously-bypass-approvals-and-sandbox`，让 Claude Code 使用危险跳过权限参数。只应在外部已隔离的维护者环境使用，普通 IDE 模式不要开启。

**手动 / dry-run**

```bash
./orchestrators/cursor/run-pipeline.sh --dry-run
./orchestrators/codex/run-pipeline.sh --from-stage case-generate
```

日志：`workspace/artifacts/logs/<platform>-<stage>.log`

### 4. 校验产物

```bash
python3 scripts/validate-artifacts.py --all
python3 scripts/validate-artifacts.py --stage prd-analyze
```

## 目录结构

| 路径 | 说明 |
|------|------|
| `pipeline.yaml` | 阶段定义、依赖、重试策略 |
| `contracts/` | 各阶段 JSON Schema |
| `agents/` | 子 Agent 角色（平台无关） |
| `skills/` | Skill 源码（同步到三平台） |
| `orchestrators/` | Cursor / Codex / Claude Code 编排入口 |
| `workspace/` | 运行时输入与产物 |

## 流水线阶段

**主 Agent**：[`agents/qa-orchestrator.md`](agents/qa-orchestrator.md)

1. **prd-analyze**（**子 Agent 全文必读**）→ 蓝图 + **`00-test-obligations.json`（TOG）**；每条 `SC-xxx` 映射 `covers_obligations`。xlarge ≥80 场景
2. **prd-gate**（TOG 校验 + **产品/研发/测试** 三评审 + **红队** + 归并）→ `00-prd-gate-report.json`  
   - `audience=product` → `prd-reject-to-product.md`  
   - 仅 `internal`（QA 漏设计/假覆盖）→ `test-point-rework-to-qa.md`，自动回 **prd-analyze**  
   - pass → `prd-gate-pass-to-product.md`  
   - `--auto` 顺序拉起 4 个评审子 Agent + gatekeeper；IDE 见 `workspace/artifacts/prompts/prd-gate*.md`
3. **case-generate** → 从蓝图渲染 `02-test-cases.md`（`scripts/render_cases_from_blueprint.py`，不增删场景）
4. **case-review** → `03-review-report.json`（fail 最多重试 2 次，否则主 Agent 升级人工）
5. **test-execute** → `04-execution-result.json`；有失败时同阶段写 `05b-bug-list.md`
6. **script-convert**（仅有 pass）→ `05a-scripts/`

## 子 Agent 与 Skill

每个阶段由独立子 Agent 执行，具体步骤在对应 Skill 中定义（`skills/<name>/SKILL.md`）。Figma 五层分析见 `skills/prd-analyze/reference-figma-analysis.md`；可先运行 `python3 scripts/prefetch_figma_snapshot.py`。

`01-prd-analysis.json` 是从 `00-test-ready-blueprint.json` 同步出的兼容摘要；门禁与用例生成以蓝图和 `00-test-obligations.json` 为准。

主 Agent 不应代写阶段产物。技术兜底包括：蓝图必须声明 `delivery_coverage.executed_by=prd-analyzer-subagent`，gate 前会校验全文分析 marker，prompt 也要求子 Agent 只完成本阶段、不进入下一阶段。

## 断点续跑

`workspace/artifacts/00-meta.json` 记录当前阶段与状态。编排器支持：

```bash
./orchestrators/codex/run-pipeline.sh --from-stage test-execute
```

## 开发说明

- 修改 Skill 后运行 `./scripts/sync-skills.sh`
- 当前核心 Skill 已包含可执行流程；新增/修改阶段时请同步更新 `pipeline.yaml`、`agents/`、`skills/`、`contracts/` 与自测。
- `workspace/artifacts/` 是运行时目录，不是稳定样例；需要样例时请放入单独 fixtures 目录。
- `.gitignore` 已排除运行产物、用户输入、env 与日志；如果把本目录初始化为 Git 仓库或复制到其他仓库，请确认这些规则仍然生效。
