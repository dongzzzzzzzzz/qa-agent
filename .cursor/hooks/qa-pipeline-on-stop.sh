#!/usr/bin/env bash
export QA_PIPELINE_HOOK_EVENT=stop
exec "$(dirname "$0")/qa-pipeline-next.sh"
