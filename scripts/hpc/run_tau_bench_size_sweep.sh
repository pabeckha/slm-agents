#!/bin/bash
# Submit tau-bench (retail, tool-calling) for 0.5B, 1.5B, 3B base instruct models.
# The 7B run (4.35%) is already complete; this covers the smaller sizes.
# Each job uses the same model for both agent and user simulator.
#
# Usage:
#   bash scripts/hpc/run_tau_bench_size_sweep.sh [--dry-run]

set -euo pipefail

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

SCRIPT="$(cd "$(dirname "$0")" && pwd)/run_tau_bench.sh"

submitted=0

for MODEL in "Qwen/Qwen2.5-0.5B-Instruct" "Qwen/Qwen2.5-1.5B-Instruct" "Qwen/Qwen2.5-3B-Instruct"; do
    SIZE=$(echo "$MODEL" | grep -oP '\d+(\.\d+)?B')

    if [[ $DRY_RUN -eq 1 ]]; then
        echo "DRY RUN: MODEL=$MODEL TBENV=retail AGENT_STRATEGY=tool-calling"
    else
        echo "Submitting tau-bench for $MODEL ..."
        bsub -J "tau_bench_${SIZE}" \
             -env "all,MODEL=$MODEL,TBENV=retail,AGENT_STRATEGY=tool-calling" \
             < "$SCRIPT"
        submitted=$((submitted + 1))
        sleep 0.5
    fi
done

echo ""
if [[ $DRY_RUN -eq 1 ]]; then
    echo "Dry run complete. Remove --dry-run to submit."
else
    echo "Submitted $submitted tau-bench jobs."
    echo "Monitor: bjobs | grep tau_bench"
    echo "Results: data/output/tau_bench/tool-calling/retail/"
fi
