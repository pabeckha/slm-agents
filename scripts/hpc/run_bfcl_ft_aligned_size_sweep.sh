#!/bin/bash
# Submit BFCL eval jobs for CD+FT-aligned on all small Qwen 2.5 merged models.
#
# Prerequisite: merged models must exist under models/merged/.
# Run after train_lora_size_sweep.sh + merge step.
#
# Usage:
#   bash scripts/hpc/run_bfcl_ft_aligned_size_sweep.sh [--dry-run]

set -euo pipefail

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

SCRIPT="$(cd "$(dirname "$0")" && pwd)/run_bfcl_ft_aligned.sh"
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

submitted=0

for MODEL in "Qwen/Qwen2.5-0.5B-Instruct" "Qwen/Qwen2.5-1.5B-Instruct" "Qwen/Qwen2.5-3B-Instruct"; do
    SAFE=$(echo "$MODEL" | tr '/' '_')
    MERGED="${PROJECT_DIR}/models/merged/${SAFE}-merged-aligned"
    SIZE=$(echo "$MODEL" | grep -oP '\d+\.\d+B')

    if [[ ! -d "$MERGED" ]]; then
        echo "WARNING: merged model not found at $MERGED — skipping $MODEL"
        continue
    fi

    if [[ $DRY_RUN -eq 1 ]]; then
        echo "DRY RUN: MERGED_MODEL=$MERGED LORA_BASE=$MODEL CATEGORY=simple_python"
    else
        echo "Submitting eval for $MODEL ..."
        bsub -J "bfcl_ft_aligned_${SIZE}" \
             -env "all,MERGED_MODEL=$MERGED,LORA_BASE=$MODEL,CATEGORY=simple_python" \
             < "$SCRIPT"
        submitted=$((submitted + 1))
        sleep 0.5
    fi
done

echo ""
if [[ $DRY_RUN -eq 1 ]]; then
    echo "Dry run complete. Remove --dry-run to submit."
else
    echo "Submitted $submitted eval jobs."
    echo "Monitor: bjobs | grep bfcl_ft_aligned"
    echo "Results will appear in: data/output/bfcl_ft_aligned/<model>/non_live/"
fi
