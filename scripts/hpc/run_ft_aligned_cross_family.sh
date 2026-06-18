#!/bin/sh
# FT-aligned (Config CD+FT) cross-family chain — Phase 2 extension beyond Qwen2.5.
#
# For each contrast model, runs the full aligned-LoRA pipeline:
#   train_lora_aligned -> merge_lora_aligned -> run_bfcl_ft_aligned (guided)
#     -> run_bfcl_ft_aligned_no_guided -> cleanup_path (drop the merged checkpoint)
#
# Everything is ONE serialized done() chain across all models. Reasons:
#   * venv race: every stage `uv sync`es the shared NFS .venv; concurrent syncs
#     corrupt it (project_uv_sync_venv_race). Serial = safe.
#   * pool6 quota: /work3 storagepool 6 had ~23 GiB free at launch. Four bf16
#     merges (~18 GiB) do NOT comfortably co-exist, and this exact model set
#     (gemma, Phi) already died once on a work3 disk-quota overflow. The
#     per-model cleanup_path keeps AT MOST ONE merged checkpoint on disk.
#
# Llama-3.2-3B already has a complete aligned adapter
# (models/lora/meta-llama_Llama-3.2-3B-Instruct-aligned, adapter_model.safetensors
# present) — its train stage is SKIPPED and the existing adapter reused. The other
# three are trained from scratch by current code. Asymmetry to note in the draft.
#
# CATEGORY defaults to simple_python — the headline FT metric, directly comparable
# to the cross-family CD simple_python column. Harder categories are a follow-up
# chain, not this one.
#
# Usage:
#   bash scripts/hpc/run_ft_aligned_cross_family.sh
#   DRY_RUN=1 bash scripts/hpc/run_ft_aligned_cross_family.sh   # print bsub only
#   CATEGORY=multiple bash scripts/hpc/run_ft_aligned_cross_family.sh

set -e

HPC_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$HPC_DIR/../.."   # project root — the [ -f "$ADAPTER_DIR" ] checks use relative paths
MERGED_ROOT="/work3/s242779/models/models/merged"
CATEGORY="${CATEGORY:-simple_python}"

# Models to run, in order (serial chain). Llama-3B reuses its existing adapter.
MODELS="google/gemma-3-1b-it meta-llama/Llama-3.2-1B-Instruct meta-llama/Llama-3.2-3B-Instruct microsoft/Phi-4-mini-instruct"

PREV="-"

# submit <label> <bsub-tail-after--env>  — chains on $PREV, updates $PREV to new job id
submit() {
    label="$1"; shift
    cmd="bsub"
    [ "$PREV" != "-" ] && cmd="$cmd -w 'done($PREV)'"
    cmd="$cmd $*"
    echo "  [$label] $cmd"
    if [ -n "$DRY_RUN" ]; then
        PREV="DRY_$(echo "$label" | tr ' /.:' '____')"
        return 0
    fi
    out=$(eval "$cmd")
    echo "    $out"
    PREV=$(echo "$out" | sed -n 's/^Job <\([0-9]*\)>.*/\1/p')
    if [ -z "$PREV" ]; then echo "ERROR: could not parse job id for $label"; exit 1; fi
    return 0
}

for MODEL in $MODELS; do
    SLUG=$(echo "$MODEL" | tr '/' '_')
    ADAPTER_DIR="models/lora/${SLUG}-aligned"
    MERGED="${MERGED_ROOT}/${SLUG}-merged-aligned"

    echo "=== $MODEL (slug $SLUG) ==="

    # 1. Train (skip if a complete adapter already exists).
    if [ -f "$ADAPTER_DIR/adapter_model.safetensors" ]; then
        echo "  [train] SKIP — reusing existing adapter $ADAPTER_DIR"
    else
        submit "train $SLUG" \
            "-env \"all,MODEL=$MODEL,ADAPTER_DIR=$ADAPTER_DIR\" < $HPC_DIR/train_lora_aligned.sh"
    fi

    # 2. Merge adapter -> bf16 checkpoint on work3.
    submit "merge $SLUG" \
        "-env \"all,ADAPTER_DIR=$ADAPTER_DIR,OUTPUT_DIR=$MERGED\" < $HPC_DIR/merge_lora_aligned.sh"

    # 3. Eval guided (CD+FT-aligned).
    submit "eval $SLUG" \
        "-env \"all,MERGED_MODEL=$MERGED,LORA_BASE=$MODEL,CATEGORY=$CATEGORY\" < $HPC_DIR/run_bfcl_ft_aligned.sh"

    # 4. Eval no-guided (FT-aligned only).
    submit "eval-ng $SLUG" \
        "-env \"all,MERGED_MODEL=$MERGED,LORA_BASE=$MODEL,CATEGORY=$CATEGORY\" < $HPC_DIR/run_bfcl_ft_aligned_no_guided.sh"

    # 5. Drop the merged checkpoint before the next model's merge (pool6 quota).
    submit "cleanup $SLUG" \
        "-env \"all,TARGET=$MERGED\" < $HPC_DIR/cleanup_path.sh"
done

echo
echo "All submissions done. Track with: bjobs -w"
echo
echo "VALIDITY GATE (run_bfcl_ft_aligned*.sh has NO correct_count/400 gate — check by hand):"
echo "  1. Each job exits 0; bjobs -w shows no EXIT/PEND-stranded jobs mid-chain."
echo "  2. 'Verified served model' line present in each eval log (no port cross-talk)."
echo "  3. Manifest under data/output/bfcl_ft_aligned{,_no_guided}/runs/ has total_count=200."
echo "  4. SPOT-CHECK the result json is NOT uniformly [] (the fake-0% crash signature),"
echo "     especially gemma (the model that just crashed on guided parallel)."
echo "  5. Confirm cleanup ran: 'ls $MERGED_ROOT' should hold <=1 merged dir at a time."
