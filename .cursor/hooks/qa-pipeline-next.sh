#!/usr/bin/env bash
# Cursor Hook: 流水线激活后推进下一阶段
# - ide 模式：Task followup（侧栏可见，与昨日一致）
# - cli 模式：后台 cursor agent（仅 --auto，日志见 workspace/artifacts/logs/）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="${ROOT}/.venv/bin/python"
[[ -x "$PYTHON" ]] || PYTHON="python3"
ACTIVE_PY="${ROOT}/scripts/pipeline_active.py"
LAUNCHER="${ROOT}/scripts/launch_subagent.py"
PLATFORM="${QA_PIPELINE_PLATFORM:-cursor}"
HOOK_EVENT="${QA_PIPELINE_HOOK_EVENT:-unknown}"

# Resolve ARTIFACTS dynamically: prefer QA_WORKSPACE env (set by pipeline_runner
# when using --project), then fall back to reading workspace field from meta.json,
# then fall back to legacy default.
_default_artifacts="${ROOT}/workspace/artifacts"
_meta_candidates=(
  "${QA_WORKSPACE:-}"
  "$(jq -r '.workspace // empty' "${_default_artifacts}/00-meta.json" 2>/dev/null || true)"
)
ARTIFACTS="${_default_artifacts}"
for _candidate in "${_meta_candidates[@]}"; do
  if [[ -n "$_candidate" && -d "$_candidate" ]]; then
    ARTIFACTS="$_candidate"
    break
  fi
done
# Re-export so all child processes (python scripts) pick it up
export QA_WORKSPACE="${ARTIFACTS}"

PROMPTS="${ARTIFACTS}/prompts"
LOGS="${ARTIFACTS}/logs"

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

force_rerun() {
  "$PYTHON" "$ACTIVE_PY" force 2>/dev/null | grep -q '^1$'
}

touch_pipeline_active() {
  "$PYTHON" "$ACTIVE_PY" touch "$(launch_mode)" 2>/dev/null || true
}

clear_pipeline_active() {
  "$PYTHON" "$ACTIVE_PY" clear 2>/dev/null || true
}

should_notify_reject() {
  pipeline_active && [[ "$("$PYTHON" "$ACTIVE_PY" should-notify-reject)" == "1" ]]
}

mark_reject_notified() {
  "$PYTHON" "$ACTIVE_PY" mark-reject-notified 2>/dev/null || true
  clear_pipeline_active
}

read_stage_result() {
  local meta="${ARTIFACTS}/00-meta.json"
  [[ -f "$meta" ]] || return 1
  jq -r '.stage_result // empty' "$meta" 2>/dev/null
}

read_meta_stage() {
  local meta="${ARTIFACTS}/00-meta.json"
  [[ -f "$meta" ]] || return 1
  jq -r '.stage // empty' "$meta" 2>/dev/null
}

prd_analyze_ready() {
  local stage_result
  stage_result=$(read_stage_result 2>/dev/null || echo "")
  local meta_stage
  meta_stage=$(read_meta_stage 2>/dev/null || echo "")

  # 优先读 00-meta.json 的 stage_result
  if [[ "$meta_stage" == "prd-analyze" ]]; then
    case "$stage_result" in
      STAGE_DONE) return 0 ;;
      PRODUCT_REJECT|INTERNAL_REWORK|PIPELINE_BLOCKED) return 0 ;;
    esac
  fi

  # 兜底：检查产物文件（兼容旧逻辑）
  [[ -f "${ARTIFACTS}/00-test-blueprint.json" ]] \
    && [[ -f "${ARTIFACTS}/00-test-blueprint.md" ]] \
    && [[ -f "${ARTIFACTS}/00-knowledge-context.json" ]] \
    && jq -e '.decision_owner == "prd-analyzer-subagent"' "${ARTIFACTS}/00-knowledge-context.json" >/dev/null 2>&1
}

artifact_ready() {
  if force_rerun; then
    return 1
  fi
  case "$1" in
    prd-analyze) prd_analyze_ready ;;
    case-generate) [[ -f "${ARTIFACTS}/02-test-cases.md" ]] ;;
    case-review-prepare) [[ -f "${ARTIFACTS}/.stage-done-case-review-prepare.json" ]] ;;
    case-review-product) [[ -f "${ARTIFACTS}/.stage-done-case-review-product.json" ]] ;;
    case-review-qa) [[ -f "${ARTIFACTS}/.stage-done-case-review-qa.json" ]] ;;
    case-review-testability) [[ -f "${ARTIFACTS}/.stage-done-case-review-testability.json" ]] ;;
    case-review-red-team) [[ -f "${ARTIFACTS}/.stage-done-case-review-red-team.json" ]] ;;
    case-review-merge) [[ -f "${ARTIFACTS}/.stage-done-case-review-merge.json" ]] ;;
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

case_review_orchestrating() {
  local lock="${ARTIFACTS}/.case-review-orchestrating.lock"
  [[ -f "$lock" ]] || return 1
  local expires
  expires=$(jq -r '.expires_at // empty' "$lock" 2>/dev/null || true)
  if [[ -z "$expires" ]]; then
    return 0
  fi
  local now_s expires_s
  now_s=$(date -u +%s)
  expires_s=$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$expires" +%s 2>/dev/null || date -d "$expires" +%s 2>/dev/null || echo 0)
  if (( expires_s == 0 || now_s < expires_s )); then
    return 0
  fi
  return 1
}

case_review_orchestration_expired() {
  local lock="${ARTIFACTS}/.case-review-orchestrating.lock"
  [[ -f "$lock" ]] || return 1
  ! case_review_orchestrating
}

handle_expired_case_review_lock() {
  local lock="${ARTIFACTS}/.case-review-orchestrating.lock"
  local failed="${ARTIFACTS}/case-review-orchestration-failed.md"
  [[ -f "$lock" ]] || return 1
  if [[ -f "${ARTIFACTS}/03-review-report.json" ]]; then
    rm -f "$lock"
    return 1
  fi
  {
    echo "# Case Review Orchestration Failed"
    echo
    echo "- reason: lock expired before 03-review-report.json was published"
    echo "- detected_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo
    echo "## Lock"
    echo
    echo '```json'
    cat "$lock"
    echo
    echo '```'
  } >"$failed"
  rm -f "$lock"
  return 0
}

case_review_reject() {
  [[ -f "${ARTIFACTS}/03-review-report.json" ]] || return 1
  local verdict
  verdict=$(jq -r '.verdict // "fail"' "${ARTIFACTS}/03-review-report.json")
  [[ "$verdict" == "reject" || "$verdict" == "fail" ]]
}

case_review_product_reject() {
  case_review_reject || return 1
  jq -e '[.issues[]? | select((.audience // "product") == "product")] | length > 0' \
    "${ARTIFACTS}/03-review-report.json" >/dev/null
}

case_review_internal_reject() {
  case_review_reject || return 1
  jq -e '
    [.issues[]?
      | select(
          (.audience // "") == "internal"
          or (.root_cause // "") == "qa_undercoverage"
          or (.root_cause // "") == "case_generation"
          or (.retry_target // "") == "prd-analyze"
          or (.retry_target // "") == "case-generate"
        )
    ] | length > 0
  ' "${ARTIFACTS}/03-review-report.json" >/dev/null
}

next_stage() {
  local stage_result
  stage_result=$(read_stage_result 2>/dev/null || echo "")
  local meta_stage
  meta_stage=$(read_meta_stage 2>/dev/null || echo "")

  # 优先使用 00-meta.json 的 stage_result 枚举值决定下一步
  if [[ -n "$stage_result" && -n "$meta_stage" ]]; then
    case "$stage_result" in
      PRODUCT_REJECT)
        if case_review_internal_reject; then
          gate=$("$PYTHON" "${ROOT}/scripts/pipeline_runner.py" --case-review-gate 2>/dev/null | tail -1 || true)
          case "$gate" in
            retry_analyze)
              touch_pipeline_active
              echo "prd-analyze"
              return 0
              ;;
            prd_rejected)
              echo "ORCHESTRATOR_PRD_REJECT"
              return 0
              ;;
            await_orchestrator|abort)
              echo "ORCHESTRATOR_INTERNAL"
              return 0
              ;;
          esac
        fi
        echo "ORCHESTRATOR_PRD_REJECT"
        return 0
        ;;
      INTERNAL_REWORK)
        touch_pipeline_active
        echo "prd-analyze"
        return 0
        ;;
      PIPELINE_BLOCKED)
        echo "ORCHESTRATOR_INTERNAL"
        return 0
        ;;
      STAGE_DONE)
        # 根据当前完成的阶段决定下一阶段
        case "$meta_stage" in
          prd-analyze)  echo "case-generate"; return 0 ;;
          case-generate) echo "case-review-prepare";   return 0 ;;
          case-review-prepare) echo "case-review-product"; return 0 ;;
          case-review-product) echo "case-review-qa"; return 0 ;;
          case-review-qa) echo "case-review-testability"; return 0 ;;
          case-review-testability) echo "case-review-red-team"; return 0 ;;
          case-review-red-team) echo "case-review-merge"; return 0 ;;
          case-review-merge)
            if review_passed; then
              echo "test-execute"
            else
              echo "ORCHESTRATOR_INTERNAL"
            fi
            return 0
            ;;
          case-review)
            if review_passed; then
              echo "test-execute"
            else
              echo "ORCHESTRATOR_INTERNAL"
            fi
            return 0
            ;;
          test-execute)
            if jq -e '.has_pass == true' "${ARTIFACTS}/04-execution-result.json" >/dev/null 2>&1; then
              if ! artifact_ready "script-convert"; then
                echo "script-convert"
                return 0
              fi
            fi
            echo ""
            return 0
            ;;
        esac
        ;;
    esac
  fi

  # 兜底：检查产物文件（兼容未写 stage_result 的旧子 Agent）
  if ! prd_analyze_ready; then
    echo "prd-analyze"
    return 0
  fi
  local linear=(case-generate case-review-prepare case-review-product case-review-qa case-review-testability case-review-red-team case-review-merge)
  local s
  for s in "${linear[@]}"; do
    if ! artifact_ready "$s"; then
      echo "$s"
      return 0
    fi
  done
  if case_review_reject; then
    gate=$("$PYTHON" "${ROOT}/scripts/pipeline_runner.py" --case-review-gate 2>/dev/null | tail -1 || true)
    case "$gate" in
      retry_analyze)
        touch_pipeline_active
        echo "prd-analyze"
        return 0
        ;;
      prd_rejected)
        echo "ORCHESTRATOR_PRD_REJECT"
        return 0
        ;;
      await_orchestrator|abort)
        echo "ORCHESTRATOR_INTERNAL"
        return 0
        ;;
    esac
    if case_review_product_reject; then
      echo "ORCHESTRATOR_PRD_REJECT"
      return 0
    fi
    echo "ORCHESTRATOR_INTERNAL"
    return 0
  fi
  if ! review_passed; then
    echo "case-review"
    return 0
  fi
  if ! artifact_ready "test-execute"; then
    echo "test-execute"
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

ensure_stage_prompt() {
  local stage="$1"
  mkdir -p "$LOGS" "$PROMPTS"
  if [[ ! -f "${PROMPTS}/${stage}.md" ]]; then
    "$PYTHON" "${ROOT}/scripts/pipeline_runner.py" --platform "$PLATFORM" --dry-run \
      --from-stage "$stage" --to-stage "$stage" >/dev/null 2>&1 || true
  fi
}

stage_has_raw_artifact() {
  case "$1" in
    case-review-product) [[ -f "${ARTIFACTS}/case-review-findings-product.json" ]] ;;
    case-review-qa) [[ -f "${ARTIFACTS}/case-review-findings-qa.json" ]] ;;
    case-review-testability) [[ -f "${ARTIFACTS}/case-review-findings-testability.json" ]] ;;
    case-review-red-team) [[ -f "${ARTIFACTS}/case-review-findings-red-team.json" ]] ;;
    case-review-merge) [[ -f "${ARTIFACTS}/case-review-findings-product.json" && -f "${ARTIFACTS}/case-review-findings-qa.json" && -f "${ARTIFACTS}/case-review-findings-testability.json" && -f "${ARTIFACTS}/case-review-findings-red-team.json" ]] ;;
    *) return 1 ;;
  esac
}

finalize_raw_stage() {
  local stage="$1"
  mkdir -p "$LOGS"
  local log="${LOGS}/hook-finalize-${stage}.log"
  QA_WORKSPACE="$ARTIFACTS" "$PYTHON" "${ROOT}/scripts/pipeline_runner.py" --platform "$PLATFORM" --execute \
    --from-stage "$stage" --to-stage "$stage" >"$log" 2>&1
}

record_stage_launch() {
  local stage="$1"
  "$PYTHON" "${ROOT}/scripts/pipeline_runner.py" --platform "$PLATFORM" \
    --record-launch-stage "$stage" >/dev/null 2>&1 || true
}

emit_ide_task_followup() {
  local stage="$1"
  local msg
  msg="【QA 流水线 · ${stage}】请立即用 **Task 子 Agent**（generalPurpose）执行：

\`workspace/artifacts/prompts/${stage}.md\`

要求：
1. 用户必须在侧栏看到子 Agent 的完整过程（不要用后台 cursor agent CLI）
2. 按 prompt 内角色与 Skill 写入约定产物
3. 完成后执行: \`python3 scripts/validate-artifacts.py --stage ${stage}\`
4. 完成后 Hook 会自动推进下一阶段"
  jq -n --arg msg "$msg" '{ followup_message: $msg }'
}

advance_stage() {
  local stage="$1"
  if [[ "$stage" == "case-review-merge" ]]; then
    if case_review_orchestrating; then
      echo '{}'
      return 0
    fi
    if case_review_orchestration_expired && handle_expired_case_review_lock; then
      jq -n --arg msg "【QA 流水线 · case-review】四视角编排锁已过期且最终报告未生成，已写入 case-review-orchestration-failed.md。请主 Agent 阅读失败文件并决定重跑 case-review 或人工介入。" '{ followup_message: $msg }'
      return 0
    fi
  fi
  if artifact_ready "$stage"; then
    return 0
  fi
  if stage_has_raw_artifact "$stage"; then
    if finalize_raw_stage "$stage"; then
      echo '{}'
      return 0
    fi
    jq -n --arg msg "【QA 流水线 · ${stage}】产物已存在但阶段落账/校验失败。请主 Agent 阅读 ${LOGS}/hook-finalize-${stage}.log 后修复。" '{ followup_message: $msg }'
    return 0
  fi
  if ! force_rerun && stage_lock_recent "$stage"; then
    return 0
  fi
  touch_pipeline_active
  ensure_stage_prompt "$stage"
  record_stage_launch "$stage"

  if [[ "$(launch_mode)" == "cli" ]]; then
    nohup "$PYTHON" "$LAUNCHER" --platform "$PLATFORM" --stage "$stage" \
      >>"${LOGS}/hook-auto-${stage}.log" 2>&1 &
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
  echo '{}'
  exit 0
fi

if [[ "$STAGE" == "case-review-merge" ]]; then
  merge_log="${LOGS}/hook-case-review-merge.log"
  mkdir -p "$LOGS"
  if ! QA_WORKSPACE="$ARTIFACTS" "$PYTHON" "${ROOT}/scripts/pipeline_runner.py" --platform "$PLATFORM" --execute \
    --from-stage case-review-merge --to-stage case-review-merge >"$merge_log" 2>&1; then
    clear_pipeline_active
    jq -n --arg msg "【QA 流水线 · case-review】四视角已完成，但自动合并/最终校验失败。请主 Agent 阅读 ${merge_log}、03-review-report.json（如存在）和 case-review-orchestration-trace.jsonl 后修复。" '{ followup_message: $msg }'
    exit 0
  fi
  STAGE=$(next_stage)
fi

if [[ "$STAGE" == "ORCHESTRATOR_INTERNAL" ]]; then
  if [[ "$HOOK_EVENT" != "stop" ]]; then
    echo '{}'
    exit 0
  fi
  clear_pipeline_active
  followup="【主 Agent · 内部返工已达上限或未自动返工】请阅读 03-review-report.json 与 test-point-rework-to-qa.md，检查子 Agent 是否已把评审项落入蓝图/用例。可执行: ./orchestrators/cursor/run-pipeline.sh --from-stage prd-analyze --force 。若仅剩产品问题，交 prd-reject-to-product.md。"
  jq -n --arg msg "$followup" '{ followup_message: $msg }'
  exit 0
fi

if [[ "$STAGE" == "ORCHESTRATOR_PRD_REJECT" ]]; then
  if [[ "$HOOK_EVENT" != "stop" ]]; then
    clear_pipeline_active
    echo '{}'
    exit 0
  fi
  if should_notify_reject; then
    mark_reject_notified
    clear_pipeline_active
    followup="【主 Agent】用例评审门禁发现 PRD/Figma 问题，流水线已停止。请将 prd-reject-to-product.md 交产品；修订后说「重跑 QA 流水线」即可。"
    jq -n --arg msg "$followup" '{ followup_message: $msg }'
    exit 0
  fi
  echo '{}'
  exit 0
fi

if review_passed; then
  rm -f "${ARTIFACTS}/.orchestrator-prd-reject-notified" 2>/dev/null || true
fi

# ide：stop / subagentStop 均用 Task followup（会话可见）
# cli：仅 subagentStop 后台拉起
should_advance=false
if [[ "$HOOK_EVENT" == "subagentStop" ]]; then
  should_advance=true
elif [[ "$HOOK_EVENT" == "stop" ]] && [[ "$(launch_mode)" == "ide" ]]; then
  should_advance=true
fi

if $should_advance; then
  advance_stage "$STAGE"
  exit 0
fi

echo '{}'
exit 0
