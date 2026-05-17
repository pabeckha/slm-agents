#!/bin/bash
# Submit BFCL multiple + parallel eval jobs for 0.5B, 1.5B, 3B.
# Runs two configs per model per category:
#   CD           — plain guided decoding (FP16 base instruct)
#   CD+FT-aligned — guided decoding + format-aligned LoRA (merged models)
#
# 7B results already exist (0/200 on both categories, CD+Q and B configs).
# This completes the size sweep for the multi-call categories.
#
# Total: 3 sizes × 2 categories × 2 configs = 12 jobs
#
# Usage:
#   bash scripts/hpc/run_bfcl_multicat_size_sweep.sh [--dry-run]

set -euo pipefail

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CD_SCRIPT="${SCRIPT_DIR}/run_bfcl_eval.sh"
FTA_SCRIPT="${SCRIPT_DIR}/run_bfcl_ft_aligned.sh"

submitted=0

for MODEL in "Qwen/Qwen2.5-0.5B-Instruct" "Qwen/Qwen2.5-1.5B-Instruct" "Qwen/Qwen2.5-3B-Instruct"; do
    SAFE=$(echo "$MODEL" | tr '/' '_')
    MERGED="${PROJECT_DIR}/models/merged/${SAFE}-merged-aligned"
    SIZE=$(echo "$MODEL" | grep -oP '\d+(\.\d+)?B')

    for CATEGORY in "multiple" "parallel"; do

        # CD config — plain guided decoding, FP16 base instruct
        if [[ $DRY_RUN -eq 1 ]]; then
            echo "DRY RUN: MODEL=$MODEL CATEGORY=$CATEGORY (CD)"
        else
            echo "Submitting CD $SIZE $CATEGORY ..."
            bsub -J "bfcl_cd_${SIZE}_${CATEGORY}" \
                 -env "all,MODEL=$MODEL,CATEGORY=$CATEGORY" \
                 < "$CD_SCRIPT"
            submitted=$((submitted + 1))
            sleep 0.5
        fi

        # CD+FT-aligned config — merged model
        if [[ ! -d "$MERGED" ]]; then
            echo "WARNING: merged model not found at $MERGED — skipping FT-aligned for $MODEL $CATEGORY"
            continue
        fi
        if [[ $DRY_RUN -eq 1 ]]; then
            echo "DRY RUN: MERGED_MODEL=$MERGED LORA_BASE=$MODEL CATEGORY=$CATEGORY (CD+FT-aligned)"
        else
            echo "Submitting CD+FT-aligned $SIZE $CATEGORY ..."
            bsub -J "bfcl_fta_${SIZE}_${CATEGORY}" \
                 -env "all,MERGED_MODEL=$MERGED,LORA_BASE=$MODEL,CATEGORY=$CATEGORY" \
                 < "$FTA_SCRIPT"
            submitted=$((submitted + 1))
            sleep 0.5
        fi

    done
done

echo ""
if [[ $DRY_RUN -eq 1 ]]; then
    echo "Dry run complete (up to 12 jobs). Remove --dry-run to submit."
else
    echo "Submitted $submitted jobs."
    echo "Monitor: bjobs | grep bfcl_cd"
    echo "CD results:         data/output/bfcl/<model>/non_live/BFCL_v4_{multiple,parallel}_result.json"
    echo "FT-aligned results: data/output/bfcl_ft_aligned/<model>/non_live/BFCL_v4_{multiple,parallel}_result.json"
fi
