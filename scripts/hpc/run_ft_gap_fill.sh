#!/bin/sh
# Fill the FT size-sweep gaps for 0.5B / 1.5B / 3B.
#
# Two arms, each submitted as an LSF dependency chain per size:
#
#   Plain FT (v1, deprecated misaligned format — reproduces the 7B plain-FT
#   diagnostic at smaller sizes):
#       train_lora.sh (FORMAT_VERSION=v1)
#         -> merge_lora.sh
#              -> run_bfcl_ft.sh            (guided   -> data/output/bfcl_ft)
#              -> run_bfcl_ft_no_guided.sh  (no-guide -> data/output/bfcl_ft_no_guided)
#
#   CD+Q+FT (aligned + AWQ — uses the current aligned merged models):
#       quantize_merged_lora_awq.sh
#         -> run_bfcl_cdqft_aligned.sh      (guided   -> data/output/bfcl_cdqft_aligned)
#
# Usage:
#   bash scripts/hpc/run_ft_gap_fill.sh            # submit everything
#   DRY_RUN=1 bash scripts/hpc/run_ft_gap_fill.sh  # print the bsub commands only
#   SIZES="0.5B 1.5B" bash scripts/hpc/run_ft_gap_fill.sh
#   ARMS="plain" / ARMS="cdqft" to run one arm only (default: both)

set -e

HPC_DIR="$(cd "$(dirname "$0")" && pwd)"
SIZES="${SIZES:-0.5B 1.5B 3B}"
ARMS="${ARMS:-plain cdqft}"
WORK_MERGED="/work3/s242779/models/models/merged"

# submit <human-label> <varlist|-> <dep-jobid|-> <script-name>
# echoes and runs bsub; on success prints "<label> -> <jobid>" and returns the id via SUBMITTED_ID
submit() {
    label="$1"; vars="$2"; dep="$3"; script="$4"
    cmd="bsub"
    [ "$dep" != "-" ] && cmd="$cmd -w 'done($dep)'"
    if [ "$vars" != "-" ]; then
        cmd="$cmd -env \"all,$vars\""
    else
        cmd="$cmd -env all"
    fi
    cmd="$cmd < $HPC_DIR/$script"
    echo "  [$label] $cmd"
    if [ -n "$DRY_RUN" ]; then
        SUBMITTED_ID="DRY_${label}"
        return 0
    fi
    out=$(eval "$cmd")
    echo "    $out"
    SUBMITTED_ID=$(echo "$out" | sed -n 's/^Job <\([0-9]*\)>.*/\1/p')
    [ -z "$SUBMITTED_ID" ] && { echo "ERROR: could not parse job id for $label"; exit 1; }
    return 0
}

for SIZE in $SIZES; do
    MODEL="Qwen/Qwen2.5-${SIZE}-Instruct"
    SAFE="Qwen_Qwen2.5-${SIZE}-Instruct"
    echo "=== ${SIZE} ==="

    case " $ARMS " in *" plain "*)
        submit "train ${SIZE}" \
            "MODEL=$MODEL,ADAPTER_DIR=models/lora/$SAFE,FORMAT_VERSION=v1" \
            "-" train_lora.sh
        TRAIN_ID="$SUBMITTED_ID"

        submit "merge ${SIZE}" \
            "ADAPTER_DIR=models/lora/$SAFE,OUTPUT_DIR=models/merged/${SAFE}-merged" \
            "$TRAIN_ID" merge_lora.sh
        MERGE_ID="$SUBMITTED_ID"

        submit "eval-guided ${SIZE}" \
            "MERGED_MODEL=models/merged/${SAFE}-merged,LORA_BASE=$MODEL" \
            "$MERGE_ID" run_bfcl_ft.sh

        submit "eval-noguided ${SIZE}" \
            "MERGED_MODEL=models/merged/${SAFE}-merged,LORA_BASE=$MODEL" \
            "$MERGE_ID" run_bfcl_ft_no_guided.sh
    ;; esac

    case " $ARMS " in *" cdqft "*)
        submit "quantize ${SIZE}" \
            "MERGED_MODEL=${WORK_MERGED}/${SAFE}-merged-aligned,OUTPUT_DIR=${WORK_MERGED}/${SAFE}-merged-aligned-AWQ" \
            "-" quantize_merged_lora_awq.sh
        QUANT_ID="$SUBMITTED_ID"

        submit "eval-cdqft ${SIZE}" \
            "MODEL=${WORK_MERGED}/${SAFE}-merged-aligned-AWQ,LORA_BASE=$MODEL" \
            "$QUANT_ID" run_bfcl_cdqft_aligned.sh
    ;; esac
done

echo
echo "All submissions done. Track with: bjobs -w"
echo "Plain-FT scores land in:   data/output/bfcl_ft/<model>/scores/ and data/output/bfcl_ft_no_guided/<model>/scores/"
echo "CD+Q+FT scores land in:    data/output/bfcl_cdqft_aligned/<model>/scores/"
