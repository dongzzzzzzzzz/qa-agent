#!/usr/bin/env bash
# Cursor Hook: 流水线激活后推进下一阶段
# - ide 模式：仅 subagentStop + 已发出 followup 等待标记 → Task followup
# - cli 模式：subagentStop 后台 cursor agent（--auto）
# - stop：仅用于 PRD reject 主 Agent 通知，不注入下一阶段 Task
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ARTIFACTS="${ROOT}/workspace/artifacts"
PROMPTS="${ARTIFACTS}/prompts"
LOGS="${ARTIFACTS}/logs"
PYTHON="${ROOT}/.venv/bin/python"
[[ -x "$PYTHON" ]] || PYTHON="python3"
ACTIVE_PY="${ROOT}/scripts/pipeline_active.py"
LAUNCHER="${ROOT}/scripts/launch_subagent.py"
PLATFORM="${QA_PIPELINE_PLATFORM:-cursor}"
HOOK_EVENT="${QA_PIPELINE_HOOK_EVENT:-unknown}"
AWAITING="${ARTIFACTS}/.qa-pipeline-awaiting-subagent"
LAST_FOLLOWUP="${ARTIFACTS}/.qa-pipeline-last-followup"
FOLLOWUP_COOLDOWN_SEC=1800

input=$(cat)
status=$(echo "$input" | jq -r '.status // "completed"')

if [[ "$status" != "completed" ]]; then
  echo '{}'
  exit 0
fi

pipeline_active() {
  "$PYTHON" "$ACTIVE_PY" active | grep -q '^1$'
}

launch_mode() {
  "$PYTHON" "$ACTIVE_PY" launch-mode 2>/dev/null || echo "ide"
}

touch_pipeline_active() {
  "$PYTHON" "$ACTIVE_PY" touch "$(launch_mode)" 2>/dev/null || true
}

clear_pipeline_active() {
  "$PYTHON" "$ACTIVE_PY" clear 2>/dev/null || true
}

clear_awaiting() {
  rm -f "$AWAITING" 2>/dev/null || true
}

set_awaiting() {
  local stage="$1"
  mkdir -p "$ARTIFACTS"
  printf '%s\n' "$stage" >"$AWAITING"
}

get_awaiting() {
  [[ -f "$AWAITING" ]] || return 1
  tr -d '\n' <"$AWAITING"
}

should_notify_reject() {
  pipeline_active && [[ "$("$PYTHON" "$ACTIVE_PY" should-notify-reject)" == "1" ]]
}

mark_reject_notified() {
  "$PYTHON" "$ACTIVE_PY" mark-reject-notified 2>/dev/null || true
  clear_pipeline_active
  clear_awaiting
}

prd_analyze_ready() {
  [[ -f "${ARTIFACTS}/00-test-ready-blueprint.json" ]] \
    && [[ -f "${ARTIFACTS}/01-prd-analysis.json" ]]
}

prd_analyze_complete() {
  [[ -f "${ARTIFACTS}/.prd-analyze-complete.ok" ]]
}

gate_report_exists() {
  [[ -f "${ARTIFACTS}/00-prd-gate-report.json" ]]
}

prd_gate_passed() {
  gate_report_exists || return 1
  [[ "$(jq -r '.verdict' "${ARTIFACTS}/00-prd-gate-report.json")" == "pass" ]]
}

prd_gate_reject() {
  gate_report_exists || return 1
  [[ "$(jq -r '.verdict' "${ARTIFACTS}/00-prd-gate-report.json")" == "reject" ]]
}

artifact_ready() {
  case "$1" in
    prd-analyze) prd_analyze_ready && prd_analyze_complete ;;
    prd-gate) prd_gate_passed ;;
    prd-gate-product-review) [[ -f "${ARTIFACTS}/gate-findings-product.json" ]] ;;
    prd-gate-dev-review) [[ -f "${ARTIFACTS}/gate-findings-dev.json" ]] ;;
    prd-gate-qa-review) [[ -f "${ARTIFACTS}/gate-findings-qa.json" ]] ;;
    prd-gate-red-team) [[ -f "${ARTIFACTS}/gate-findings-red-team.json" ]] ;;
    case-generate) [[ -f "${ARTIFACTS}/02-test-cases.md" ]] ;;
    case-review) [[ -f "${ARTIFACTS}/03-review-report.json" ]] ;;
    test-execute)
      [[ -f "${ARTIFACTS}/04-execution-result.json" ]] || return 1
      if jq -e '.has_fail == true' "${ARTIFACTS}/04-execution-result.json" >/dev/null 2>&1; then
        [[ -f "${ARTIFACTS}/05b-bug-list.md" ]]
      else
        return 0
      fi
      ;;
    script-convert) [[ -d "${ARTIFACTS}/05a-scripts" ]] && [[ -n "$(ls -A "${ARTIFACTS}/05a-scripts" 2>/dev/null)" ]] ;;
    *) return 1 ;;
  esac
}

review_passed() {
  [[ -f "${ARTIFACTS}/03-review-report.json" ]] || return 1
  verdict=$(jq -r '.verdict // "fail"' "${ARTIFACTS}/03-review-report.json")
  score=$(jq -r '.coverage_score // 0' "${ARTIFACTS}/03-review-report.json")
  awk -v v="$verdict" -v s="$score" 'BEGIN { exit !(v == "pass" && s >= 0.85) }'
}

# prd-gate 复合阶段：先四评审，再 gatekeeper 归并
prd_gate_next_substage() {
  if [[ ! -f "${ARTIFACTS}/gate-findings-product.json" ]]; then
    echo "prd-gate-product-review"
    return 0
  fi
  if [[ ! -f "${ARTIFACTS}/gate-findings-dev.json" ]]; then
    echo "prd-gate-dev-review"
    return 0
  fi
  if [[ ! -f "${ARTIFACTS}/gate-findings-qa.json" ]]; then
    echo "prd-gate-qa-review"
    return 0
  fi
  if [[ ! -f "${ARTIFACTS}/gate-findings-red-team.json" ]]; then
    echo "prd-gate-red-team"
    return 0
  fi
  echo "prd-gate"
}

next_stage() {
  if ! prd_analyze_ready || ! prd_analyze_complete; then
    echo "prd-analyze"
    return 0
  fi
  if ! prd_gate_passed; then
    if prd_gate_reject && [[ "$("$PYTHON" "$ACTIVE_PY" internal-reject)" != "1" ]]; then
      echo "ORCHESTRATOR_PRD_REJECT"
      return 0
    fi
    if prd_gate_reject && [[ "$("$PYTHON" "$ACTIVE_PY" internal-reject)" == "1" ]]; then
      echo "prd-analyze"
      return 0
    fi
    # 无 gate 报告但有产品打回 MD → 视为已 reject，勿再注入 prd-gate Task
    if ! gate_report_exists && [[ -f "${ARTIFACTS}/prd-reject-to-product.md" ]]; then
      echo "ORCHESTRATOR_PRD_REJECT"
      return 0
    fi
    prd_gate_next_substage
    return 0
  fi
  local linear=(case-generate case-review test-execute)
  local s
  for s in "${linear[@]}"; do
    if ! artifact_ready "$s"; then
      echo "$s"
      return 0
    fi
  done
  if ! review_passed; then
    echo "case-generate"
    return 0
  fi
  if jq -e '.has_pass == true' "${ARTIFACTS}/04-execution-result.json" >/dev/null 2>&1; then
    if ! artifact_ready "script-convert"; then
      echo "script-convert"
      return 0
    fi
  fi
  echo ""
}

stage_lock_recent() {
  local stage="$1"
  local lock="${ARTIFACTS}/.subagent-launch-${stage}.lock"
  [[ -f "$lock" ]] || return 1
  local now mtime
  now=$(date +%s)
  mtime=$(stat -f %m "$lock" 2>/dev/null || stat -c %Y "$lock" 2>/dev/null || echo 0)
  (( now - mtime < 7200 ))
}

followup_recent_duplicate() {
  local stage="$1"
  [[ -f "$LAST_FOLLOWUP" ]] || return 1
  local last_stage last_ts now
  last_stage=$(jq -r '.stage // ""' "$LAST_FOLLOWUP" 2>/dev/null || echo "")
  last_ts=$(jq -r '.ts // 0' "$LAST_FOLLOWUP" 2>/dev/null || echo 0)
  now=$(date +%s)
  [[ "$last_stage" == "$stage" ]] && (( now - last_ts < FOLLOWUP_COOLDOWN_SEC ))
}

record_followup() {
  local stage="$1"
  jq -n --arg stage "$stage" --argjson ts "$(date +%s)" \
    '{stage:$stage, ts:$ts}' >"$LAST_FOLLOWUP"
}

ensure_stage_prompt() {
  local stage="$1"
  mkdir -p "$LOGS" "$PROMPTS"
  if [[ ! -f "${PROMPTS}/${stage}.md" ]]; then
    "$PYTHON" "${ROOT}/scripts/pipeline_runner.py" --platform "$PLATFORM" --dry-run \
      --from-stage "$stage" --to-stage "$stage" >/dev/null 2>&1 || true
  fi
}

emit_ide_task_followup() {
  local stage="$1"
  local msg
  msg="【QA 流水线 · ${stage}】请用 **Task 子 Agent**（generalPurpose）执行：

\`workspace/artifacts/prompts/${stage}.md\`

要求：
1. 侧栏可见完整过程（勿用后台 cursor agent CLI）
2. 按 prompt 角色与 Skill 写入约定产物
3. 完成后: \`python3 scripts/validate-artifacts.py --stage ${stage}\`
4. 子 Agent 结束后 Hook 自动推进（勿在主会话代写产物）"
  record_followup "$stage"
  set_awaiting "$stage"
  jq -n --arg msg "$msg" '{ followup_message: $msg }'
}

advance_stage() {
  local stage="$1"
  if artifact_ready "$stage"; then
    clear_awaiting
    echo '{}'
    return 0
  fi
  if stage_lock_recent "$stage" || followup_recent_duplicate "$stage"; then
    echo '{}'
    return 0
  fi
  touch_pipeline_active
  ensure_stage_prompt "$stage"
  date -u +"%Y-%m-%dT%H:%M:%SZ" >"${ARTIFACTS}/.subagent-launch-${stage}.lock"

  if [[ "$(launch_mode)" == "cli" ]]; then
    nohup "$PYTHON" "$LAUNCHER" --platform "$PLATFORM" --stage "$stage" \
      >>"${LOGS}/hook-auto-${stage}.log" 2>&1 &
    set_awaiting "$stage"
    echo '{}'
    return 0
  fi

  emit_ide_task_followup "$stage"
}

if ! pipeline_active; then
  echo '{}'
  exit 0
fi

STAGE=$(next_stage)

if [[ -z "$STAGE" ]]; then
  clear_pipeline_active
  clear_awaiting
  echo '{}'
  exit 0
fi

if [[ "$STAGE" == "ORCHESTRATOR_PRD_REJECT" ]]; then
  if [[ "$HOOK_EVENT" != "stop" ]]; then
    clear_pipeline_active
    clear_awaiting
    echo '{}'
    exit 0
  fi
  if should_notify_reject; then
    mark_reject_notified
    followup="【主 Agent】PRD 门禁 reject，流水线已停止。请将 prd-reject-to-product.md 交产品；修订后说「重跑 QA 流水线」即可。"
    jq -n --arg msg "$followup" '{ followup_message: $msg }'
    exit 0
  fi
  echo '{}'
  exit 0
fi

if prd_gate_passed; then
  rm -f "${ARTIFACTS}/.orchestrator-prd-reject-notified" 2>/dev/null || true
fi

# IDE：仅 subagentStop 且曾发出 QA followup 等待标记 → 推进
# stop：不注入下一阶段 Task（避免普通对话结束突然弹出 prd-gate）
should_advance=false
if [[ "$HOOK_EVENT" == "subagentStop" ]]; then
  if [[ "$(launch_mode)" == "cli" ]]; then
    should_advance=true
  elif get_awaiting >/dev/null 2>&1; then
    should_advance=true
  fi
fi

if $should_advance; then
  # 子 Agent 刚完成：若产物已就绪则清等待并尝试下一阶段；否则仅校验当前等待阶段
  awaiting=$(get_awaiting 2>/dev/null || true)
  if [[ -n "$awaiting" ]] && artifact_ready "$awaiting"; then
    clear_awaiting
    rm -f "${ARTIFACTS}/.subagent-launch-${awaiting}.lock" 2>/dev/null || true
  fi
  advance_stage "$STAGE"
  exit 0
fi

echo '{}'
exit 0
