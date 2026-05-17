#!/bin/bash
# Submit tau-bench (retail, tool-calling) for all CD+FT-aligned merged models.
# Covers 0.5B, 1.5B, 3B, 7B merged-aligned — tests whether LoRA FT affects
# the model's native tool-calling capability on multi-step agentic tasks.
#
# Note: the LoRA was trained for JSON arg extraction (BFCL pipeline), not for
# the hermes tool-call format that tau-bench uses. Results may differ from the
# base instruct models depending on how much FT altered the chat template path.
#
# Usage:
#   bash scripts/hpc/run_tau_bench_ft_aligned_size_sweep.sh [--dry-run]

set -euo pipefail

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

SCRIPT="$(cd "$(dirname "$0")" && pwd)/run_tau_bench.sh"
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

submitted=0

for BASE_MODEL in "Qwen/Qwen2.5-0.5B-Instruct" "Qwen/Qwen2.5-1.5B-Instruct" "Qwen/Qwen2.5-3B-Instruct" "Qwen/Qwen2.5-7B-Instruct"; do
    SAFE=$(echo "$BASE_MODEL" | tr '/' '_')
    MERGED="${PROJECT_DIR}/models/merged/${SAFE}-merged-aligned"
    SIZE=$(echo "$BASE_MODEL" | grep -oP '\d+(\.\d+)?B')

    if [[ ! -d "$MERGED" ]]; then
        echo "WARNING: merged model not found at $MERGED — skipping $BASE_MODEL"
        continue
    fi

    if [[ $DRY_RUN -eq 1 ]]; then
        echo "DRY RUN: MODEL=$MERGED TBENV=retail AGENT_STRATEGY=tool-calling"
    else
        echo "Submitting tau-bench FT-aligned for $SIZE ..."
        bsub -J "tau_bench_fta_${SIZE}" \
             -env "all,MODEL=$MERGED,TBENV=retail,AGENT_STRATEGY=tool-calling" \
             < "$SCRIPT"
        submitted=$((submitted + 1))
        sleep 0.5
    fi
done

echo ""
if [[ $DRY_RUN -eq 1 ]]; then
    echo "Dry run complete. Remove --dry-run to submit."
else
    echo "Submitted $submitted tau-bench FT-aligned jobs."
    echo "Monitor: bjobs | grep tau_bench_fta"
    echo "Results: data/output/tau_bench/tool-calling/retail/"
fi
