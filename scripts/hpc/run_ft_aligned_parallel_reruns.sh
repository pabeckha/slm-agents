#!/bin/sh
# Re-run the CD+FT-aligned `parallel` / `parallel_multiple` cells invalidated by
# the pre-fix multi-call schema cap (commit 2faa0df). These cells back
# size-sweep-results.md:110-194 and the thesis tab:bfcl-parallel-multiple +
# Capability-Decomposition subsection; all parallel-category numbers there are
# the deterministic single-call artifact, not a capability result.
#
# The Qwen aligned-merged FP16 checkpoints were deleted (work3 pool6 quota), but
# the aligned LoRA adapters survive (models/lora/Qwen_Qwen2.5-*-Instruct-aligned),
# so each size is a MERGE -> eval(parallel) -> eval(parallel_multiple) -> cleanup,
# NOT a retrain. parallel_multiple is now run at all sizes (the old "skip below
# 7B" justification rested on the parallel-0% artifact).
#
# Disk: pool6 has ~16.7 GiB free; a 7B FP16 merge is ~15 GiB. The chain is strictly
# LINEAR and deletes each merged checkpoint before merging the next, so at most one
# is ever on disk. Sizes processed largest-first (7B headline cell first).
#
# Venv race: every merge/eval `uv sync`es the shared NFS .venv. The whole chain is
# anchored behind ANCHOR (default 28671160, the last plain-CD parallel re-run) with
# ended(), so no uv sync overlaps a still-running job.
#
# Usage:
#   bash scripts/hpc/run_ft_aligned_parallel_reruns.sh
#   DRY_RUN=1 bash scripts/hpc/run_ft_aligned_parallel_reruns.sh
#   ANCHOR=<jobid> SIZES="7B 3B" bash scripts/hpc/run_ft_aligned_parallel_reruns.sh

set -e

HPC_DIR="$(cd "$(dirname "$0")" && pwd)"
SIZES="${SIZES:-7B 3B 1.5B 0.5B}"
ANCHOR="${ANCHOR:-28671160}"
WORK_MERGED="/work3/s242779/models/models/merged"

# submit <label> <varlist|-> <dep-expr|-> <script>; sets SUBMITTED_ID
submit() {
    label="$1"; vars="$2"; dep="$3"; script="$4"
    cmd="bsub"
    [ "$dep" != "-" ] && cmd="$cmd -w '$dep'"
    if [ "$vars" != "-" ]; then cmd="$cmd -env \"all,$vars\""; else cmd="$cmd -env all"; fi
    cmd="$cmd < $HPC_DIR/$script"
    echo "  [$label] $cmd"
    if [ -n "$DRY_RUN" ]; then SUBMITTED_ID="DRY_$(echo "$label" | tr ' /.' '___')"; return 0; fi
    out=$(eval "$cmd"); echo "    $out"
    SUBMITTED_ID=$(echo "$out" | sed -n 's/^Job <\([0-9]*\)>.*/\1/p')
    [ -z "$SUBMITTED_ID" ] && { echo "ERROR: no job id for $label"; exit 1; }
    return 0
}

# First link waits on the anchor (ended = proceed even if the plain-CD chain fails;
# we only need its uv syncs to be finished).
PREV_DEP="ended($ANCHOR)"

for SIZE in $SIZES; do
    SAFE="Qwen_Qwen2.5-${SIZE}-Instruct"
    ADAPTER="models/lora/${SAFE}-aligned"
    MERGED="${WORK_MERGED}/${SAFE}-merged-aligned"
    BASE="Qwen/Qwen2.5-${SIZE}-Instruct"
    echo "=== ${SIZE} ==="

    submit "merge ${SIZE}" "ADAPTER_DIR=$ADAPTER,OUTPUT_DIR=$MERGED" "$PREV_DEP" merge_lora.sh
    MERGE_ID="$SUBMITTED_ID"

    submit "eval parallel ${SIZE}" \
        "MERGED_MODEL=$MERGED,LORA_BASE=$BASE,CATEGORY=parallel" "done($MERGE_ID)" run_bfcl_ft_aligned.sh
    EVP_ID="$SUBMITTED_ID"

    submit "eval parallel_multiple ${SIZE}" \
        "MERGED_MODEL=$MERGED,LORA_BASE=$BASE,CATEGORY=parallel_multiple" "done($EVP_ID)" run_bfcl_ft_aligned.sh
    EVPM_ID="$SUBMITTED_ID"

    # delete the merged checkpoint once both evals finished (free disk for next size)
    submit "cleanup ${SIZE}" "TARGET=$MERGED" "done($EVPM_ID)" cleanup_path.sh
    PREV_DEP="done($SUBMITTED_ID)"
done

echo
echo "All submissions done. Track with: bjobs -w"
echo "Scores land in: data/output/bfcl_ft_aligned/<merged_model_slug>/scores/<category>_scores.json"
echo "Validity gate per eval: 'Verified served model' line, no 404s, manifest total_count 200."
