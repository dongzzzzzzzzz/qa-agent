#!/usr/bin/env bash
# Smoke test: verify sub-agent prerequisites and prompt generation for the QA pipeline agents.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PYTHON="${ROOT}/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
fail=0
warn=0

ok() { echo -e "${GREEN}✓${NC} $1"; pass=$((pass + 1)); }
bad() { echo -e "${RED}✗${NC} $1"; fail=$((fail + 1)); }
warn_msg() { echo -e "${YELLOW}!${NC} $1"; warn=$((warn + 1)); }

echo "=== QA Agent 子 Agent 启动冒烟测试 ==="
echo "项目: $ROOT"
echo ""

# 1. Agent 角色文件
echo "--- 1. Agent 角色定义 (agents/) ---"
AGENTS=(prd-analyzer case-generator case-reviewer test-executor script-converter)
for a in "${AGENTS[@]}"; do
  if [[ -f "${ROOT}/agents/${a}.md" ]]; then
    ok "agents/${a}.md"
  else
    bad "缺失 agents/${a}.md"
  fi
done

# 2. Skills — 单一真相源
echo ""
echo "--- 2. Skill 文件 (.agents/skills/) ---"
SKILLS=(prd-analyze case-generate case-review test-execute script-convert bug-list-write)
for s in "${SKILLS[@]}"; do
  if [[ -f "${ROOT}/.agents/skills/${s}/SKILL.md" ]]; then
    ok ".agents/skills/${s}/SKILL.md"
  else
    bad "缺失 .agents/skills/${s}/SKILL.md"
  fi
done

# 3. 用户输入
echo ""
echo "--- 3. 流水线输入 ---"
for f in workspace/inputs/prd.md workspace/inputs/figma.url; do
  if [[ -f "${ROOT}/${f}" ]]; then
    ok "${f}"
  else
    bad "缺失 ${f}"
  fi
done

# 4. 生成各阶段 prompt（子 Agent 启动载荷）
echo ""
echo "--- 4. 生成子 Agent Prompt (pipeline_runner dry-run) ---"
if "$PYTHON" "${ROOT}/scripts/pipeline_runner.py" --platform cursor >/dev/null 2>&1; then
  ok "pipeline_runner 执行成功"
else
  bad "pipeline_runner 执行失败"
fi

EXPECTED_PROMPTS=(prd-analyze case-generate case-review test-execute)
for p in "${EXPECTED_PROMPTS[@]}"; do
  f="${ROOT}/workspace/artifacts/prompts/${p}.md"
  if [[ -f "$f" && -s "$f" ]]; then
    # 检查 prompt 是否包含角色与 Skill
    if grep -q "Agent role" "$f" && grep -q "Skill" "$f"; then
      ok "prompts/${p}.md ($(wc -c < "$f" | tr -d ' ') bytes)"
    else
      bad "prompts/${p}.md 内容不完整"
    fi
  else
    bad "缺失或空 prompts/${p}.md"
  fi
done

# post-process prompts 仅在 dry-run 全流水线时可能跳过，单独生成
"$PYTHON" "${ROOT}/scripts/pipeline_runner.py" --platform cursor --from-stage script-convert --to-stage script-convert >/dev/null 2>&1 || true
for p in script-convert; do
  f="${ROOT}/workspace/artifacts/prompts/${p}.md"
  if [[ -f "$f" && -s "$f" ]]; then
    ok "prompts/${p}.md"
  else
    warn_msg "prompts/${p}.md 未生成（需先完成 test-execute 或单独 --from-stage）"
  fi
done

# 5. 三端编排入口
echo ""
echo "--- 5. 编排入口可执行 ---"
for entry in orchestrators/cursor/run-pipeline.sh orchestrators/codex/run-pipeline.sh orchestrators/claude-code/run-pipeline.sh; do
  if [[ -x "${ROOT}/${entry}" ]]; then
    ok "${entry}"
  else
    bad "不可执行 ${entry}"
  fi
done

# 6. 契约校验器
echo ""
echo "--- 6. 产物校验器 ---"
if "$PYTHON" "${ROOT}/scripts/validate-artifacts.py" --stage prd-analyze 2>/dev/null; then
  ok "validate-artifacts.py --stage prd-analyze"
else
  warn_msg "唯一测试蓝图未通过或不存在（子 Agent 跑完后应能通过）"
fi

# 7. 自动拉起 CLI
echo ""
echo "--- 7. 自动拉起 (--auto) ---"
if [[ -x "${ROOT}/scripts/launch_subagent.py" ]]; then
  ok "scripts/launch_subagent.py"
else
  bad "缺失 launch_subagent.py"
fi
for plat in cursor codex claude-code; do
  if "$PYTHON" "${ROOT}/scripts/pipeline_runner.py" --check-auth --platform "$plat" >/dev/null 2>&1; then
    ok "check-auth --platform ${plat}"
  else
    warn_msg "check-auth 失败: ${plat}（--auto 前需登录）"
  fi
done

if command -v npx >/dev/null 2>&1; then
  ok "npx 可用（Cursor tsx 编排）"
else
  warn_msg "npx 不可用，Cursor 入口将回退到 Python"
fi

# 8. meta 断点
echo ""
echo "--- 8. 流水线 meta ---"
if [[ -f "${ROOT}/workspace/artifacts/00-meta.json" ]]; then
  ok "00-meta.json 存在"
  "$PYTHON" -c "
import json
m=json.load(open('${ROOT}/workspace/artifacts/00-meta.json'))
print('  run_id:', m.get('run_id'))
print('  stages:', list(m.get('stages', {}).keys()))
"
else
  bad "00-meta.json 不存在"
fi

echo ""
echo "=== 汇总: ${pass} 通过, ${fail} 失败, ${warn} 警告 ==="
if [[ $fail -gt 0 ]]; then
  echo ""
  echo "修复建议:"
  echo "  ./scripts/setup.sh"
  echo "  cp workspace/inputs/*.example workspace/inputs/  # 并编辑 prd.md / figma.url"
  exit 1
fi

echo ""
echo "子 Agent 启动方式:"
echo "  【推荐 Cursor】ide-chain: ./orchestrators/cursor/run-pipeline.sh"
echo "  【维护者 CLI】: QA_PIPELINE_ALLOW_CLI=1 ./orchestrators/cursor/run-pipeline.sh --auto --allow-cli"
echo "  认证检查: ./orchestrators/<platform>/run-pipeline.sh --check-auth"
echo "  手动: 打开 workspace/artifacts/prompts/<stage>.md 在 IDE Task 中执行"
exit 0
