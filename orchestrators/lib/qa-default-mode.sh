#!/usr/bin/env bash
# 各平台 run-pipeline 共用：未指定模式时默认 --ide-chain（IDE 内子 Agent）
# 用户明确要求 CLI/无头/终端 时才传 --auto 或 --cli（--cli 等同 --auto）
_qa_has_mode=false
for _a in "$@"; do
  case "$_a" in
    --auto|--cli|--ide-chain|--execute|--dry-run|--ide|--check-auth|--force|--no-force)
      _qa_has_mode=true
      ;;
  esac
done
if ! $_qa_has_mode; then
  set -- --ide-chain "$@"
fi

_qa_argv=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --cli) _qa_argv+=(--auto); shift ;;
    *) _qa_argv+=("$1"); shift ;;
  esac
done
set -- "${_qa_argv[@]}"
