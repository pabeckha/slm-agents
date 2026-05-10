#!/bin/bash
# Submit LoRA training jobs for Qwen 2.5 small sizes (0.5B, 1.5B, 3B).
#
# Usage:
#   bash scripts/hpc/train_lora_size_sweep.sh [--dry-run]
#
# After all training jobs complete, run the merge commands printed at the end
# (on the login node, no GPU needed), then submit eval jobs:
#   bash scripts/hpc/run_bfcl_ft_aligned_size_sweep.sh

set -euo pipefail

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

SCRIPT="$(cd "$(dirname "$0")" && pwd)/train_lora_aligned.sh"

submitted=()

for ENTRY in \
    "Qwen/Qwen2.5-0.5B-Instruct:02:00" \
    "Qwen/Qwen2.5-1.5B-Instruct:03:00" \
    "Qwen/Qwen2.5-3B-Instruct:05:00"
do
    MODEL="${ENTRY%%:*}"
    WALL="${ENTRY#*:}"
    SIZE=$(echo "$MODEL" | grep -oP '[0-9]+\.[0-9]+B')
    SAFE=$(echo "$MODEL" | tr '/' '_')
    ADAPTER_DIR="models/lora/${SAFE}-aligned"

    if [[ $DRY_RUN -eq 1 ]]; then
        echo "DRY RUN: MODEL=$MODEL ADAPTER_DIR=$ADAPTER_DIR  (wall: $WALL)"
    else
        echo "Submitting training job for $MODEL (wall: $WALL) ..."
        bsub -W "$WALL" -J "train_lora_${SIZE}" \
             -env "all,MODEL=$MODEL,ADAPTER_DIR=$ADAPTER_DIR" \
             < "$SCRIPT"
        submitted+=("$MODEL -> $ADAPTER_DIR")
        sleep 0.5
    fi
done

echo ""
if [[ $DRY_RUN -eq 1 ]]; then
    echo "Dry run complete. Remove --dry-run to submit."
else
    echo "Submitted ${#submitted[@]} training jobs."
    echo "Monitor: bjobs | grep train_lora"
    echo ""
    echo "=== After all training jobs complete: merge adapters (login node) ==="
    for MODEL in "Qwen/Qwen2.5-0.5B-Instruct" "Qwen/Qwen2.5-1.5B-Instruct" "Qwen/Qwen2.5-3B-Instruct"; do
        SAFE=$(echo "$MODEL" | tr '/' '_')
        echo "uv run --group hpc python scripts/merge_lora.py \\"
        echo "    --adapter models/lora/${SAFE}-aligned \\"
        echo "    --output models/merged/${SAFE}-merged-aligned"
        echo ""
    done
    echo "=== Then submit eval jobs ==="
    echo "bash scripts/hpc/run_bfcl_ft_aligned_size_sweep.sh"
fi
