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

### 2. 初始化环境（首次）

```bash
./scripts/setup.sh
```

或手动：

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./scripts/sync-skills.sh
```

### 3. 运行流水线（用户只需这一条）

```bash
./orchestrators/cursor/run-pipeline.sh
```

**默认行为（`--ide-chain`）**：Hook 用 **Task followup** 链式推进，子 Agent 在 **侧栏可见**。主 Agent **不得**擅自加 `--auto`（脚本会拒绝，见下方维护者小节）。

产品打回后：

```bash
./orchestrators/cursor/run-pipeline.sh --from-stage prd-analyze
```

在 Cursor 里说「启动 QA 流水线」时，主 Agent 应执行上述命令；Hook 也会在阶段结束时自动启动下一子 Agent。

<details><summary>维护者：无头 CLI（用户未要求时勿用）</summary>

Cursor 后台 `cursor agent` 须**显式放行**，否则 exit 1：

```bash
QA_PIPELINE_ALLOW_CLI=1 ./orchestrators/cursor/run-pipeline.sh --auto --allow-cli
```

| 标志 | 说明 |
|------|------|
| `--dry-run` | 只生成 prompt，不拉起子 Agent |
| `--execute` | 只校验已有产物 |
| `--ide` | 仅轮询产物（不自动 launch，旧模式） |
| `--allow-cli` | 与 `--auto` 同用，表示用户/维护者确认走 CLI |

硬约束规则：`.cursor/rules/qa-pipeline-no-auto-cli.mdc`（`alwaysApply`）

</details>

**认证（维护者 `--auto` 前必做）**

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

1. 项目已配置 [`.cursor/hooks.json`](.cursor/hooks.json)（`run-pipeline.sh` 激活后 Hook 链式推进；`loop_limit: null`）
2. 在 Composer 中说：**「启动 QA 流水线」** 即可——主 Agent **默认**只跑一条 `run-pipeline.sh`，**不会**在同一轮手动连开三个 Task（见 [qa-pipeline-ide-auto](.cursor/rules/qa-pipeline-ide-auto.mdc)）
3. 各阶段子 Agent 由 Hook **followup** 自动拉起；侧栏可见完整过程

### 其他模式（非默认）

| 模式 | 命令 | 说明 |
|------|------|------|
| 轮询 | `./orchestrators/cursor/run-pipeline.sh --ide` | Hook 不可用时备选 |
| 无头 CLI | `QA_PIPELINE_ALLOW_CLI=1 ... --auto --allow-cli` | 维护者；侧栏不可见 |

**终端轮询备选（仍可见 prompt，需手动 Composer）：**

```bash
./orchestrators/cursor/run-pipeline.sh --ide
```

**维护者无头 CLI（Cursor，侧栏不可见）：**

```bash
cursor agent login
QA_PIPELINE_ALLOW_CLI=1 ./orchestrators/cursor/run-pipeline.sh --auto --allow-cli
```

**Codex / Claude Code 无 IDE Hook，默认可 `--auto`：**

```bash
./orchestrators/codex/run-pipeline.sh --auto
./orchestrators/claude-code/run-pipeline.sh --auto
```

无人值守（跳过工具确认，慎用）：

```bash
export QA_AGENT_YOLO=1
export QA_PIPELINE_ALLOW_CLI=1
./orchestrators/codex/run-pipeline.sh --auto
```

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

1. **prd-analyze**（**子 Agent 全文必读**）→ 脚本只生成 GT 知识库目录清单，子 Agent 结合 PRD/Figma 自主选择相关知识库，产出 `00-test-blueprint.json/md`：需求 → 测试点 → 测试范围 → 具体场景。
2. **case-generate** → 从蓝图渲染 `02-test-cases.md`（XMind 可导入层级 Markdown：`##` 模块 → `### TC-NNN` → `-` 属性；`scripts/render_cases_from_blueprint.py`）。

**确定性增强（脚本层）**

| 能力 | 说明 |
|------|------|
| ① 返工核销 | 内部 reject 后写入 `.pending-rework-issues.json`；下次 prd-analyze 须补全，否则 validate 失败 |
| ② 蓝图模板 | `config.yaml` → `required_coverage` 强制 In Scope 子类目场景数 |
| ③ 评审预检 | case-review 时生成 `case-review-precheck.json`（GATE-xxx）；pass 不得忽略 |
| ④ 快照 | `python3 scripts/snapshot_blueprint.py save` / `compare` / `list` |

```bash
python3 scripts/snapshot_blueprint.py save --label baseline
python3 scripts/snapshot_blueprint.py compare <旧快照名>
```
3. **case-review** → 唯一质量门禁，输出 `03-review-report.json/md`；**之后由主 Agent 决策**（脚本不自动回跑 prd-analyze）：
   - **内部问题**（蓝图/用例）：主 Agent 判断是否 Task 再跑 prd-analyze，修正后重走 generate→review，直至仅剩产品问题或 pass。
   - **仅剩产品问题**：停流水线，交 `prd-reject-to-product.md` 给产品。
   - **pass**：进入执行阶段。
4. **test-execute** → `04-execution-result.json`；有失败时同阶段写 `05b-bug-list.md`。
5. **script-convert**（仅有 pass）→ `05a-scripts/`。

## 子 Agent 与 Skill

每个阶段由独立子 Agent 执行，具体步骤在对应 Skill 中定义（`skills/<name>/SKILL.md`）。Figma 五层分析见 `skills/prd-analyze/reference-figma-analysis.md`；可先运行 `python3 scripts/prefetch_figma_snapshot.py`。

## 断点续跑

`workspace/artifacts/00-meta.json` 记录当前阶段与状态。编排器支持：

```bash
./orchestrators/codex/run-pipeline.sh --from-stage test-execute
```

## 开发说明

- 修改 Skill 后运行 `./scripts/sync-skills.sh`
- Phase 1/2 Skill 内容为占位，由你后续填充 MCP 与具体流程
