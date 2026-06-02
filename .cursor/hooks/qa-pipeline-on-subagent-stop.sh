#!/usr/bin/env bash
export QA_PIPELINE_HOOK_EVENT=subagentStop
exec "$(dirname "$0")/qa-pipeline-next.sh"
