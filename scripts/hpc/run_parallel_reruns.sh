#!/bin/sh
# Re-run the BFCL `parallel` / `parallel_multiple` cells invalidated by the
# pre-fix multi-call schema cap (see docs/decisions/cross-family-cd-results.md
# and size-sweep-results.md). The fix landed in commit 2faa0df
# (`_build_parallel_calls_schema`, src/vllm_backend.py); every parallel-category
# run with a manifest before 2026-06-16 01:14 is stale.
#
# Two failure mechanisms, so the re-run set is split:
#   * `parallel`          — pre-fix cap collapsed to min(1,5)=1 -> deterministic
#                           0%. score>0 => fix was live, so only the 0% cells
#                           (Llama-1B, gemma-1b, Phi) need a re-run.
#   * `parallel_multiple` — cap did not always collapse, so a pre-fix run can
#                           score >0; the number is NOT a validity signal. All
#                           four contrast cells are stale; Qwen 0.5/1.5/3B were
#                           never run at all (the old skip-justification rested
#                           on the parallel-0% artifact).
#
# All jobs use run_bfcl_eval.sh (MODEL + CATEGORY) at Config-CD (guided JSON,
# no other technique). Submitted as ONE serialized done() chain so no two jobs
# `uv sync` the shared NFS .venv at the same time (the venv-race lesson).
#
# Usage:
#   bash scripts/hpc/run_parallel_reruns.sh          # submit the chain
#   DRY_RUN=1 bash scripts/hpc/run_parallel_reruns.sh # print bsub commands only

set -e

HPC_DIR="$(cd "$(dirname "$0")" && pwd)"

# (MODEL, CATEGORY) cells to re-run, in chain order.
CELLS="
meta-llama/Llama-3.2-1B-Instruct:parallel
google/gemma-3-1b-it:parallel
microsoft/Phi-4-mini-instruct:parallel
Qwen/Qwen2.5-0.5B-Instruct:parallel_multiple
Qwen/Qwen2.5-1.5B-Instruct:parallel_multiple
Qwen/Qwen2.5-3B-Instruct:parallel_multiple
meta-llama/Llama-3.2-3B-Instruct:parallel_multiple
meta-llama/Llama-3.2-1B-Instruct:parallel_multiple
google/gemma-3-1b-it:parallel_multiple
microsoft/Phi-4-mini-instruct:parallel_multiple
"

PREV="-"
for cell in $CELLS; do
    MODEL="${cell%%:*}"
    CATEGORY="${cell##*:}"
    label="$(echo "$MODEL" | sed 's#.*/##') $CATEGORY"

    cmd="bsub"
    [ "$PREV" != "-" ] && cmd="$cmd -w 'done($PREV)'"
    cmd="$cmd -env \"all,MODEL=$MODEL,CATEGORY=$CATEGORY\" < $HPC_DIR/run_bfcl_eval.sh"

    echo "  [$label] $cmd"
    if [ -n "$DRY_RUN" ]; then
        PREV="DRY_$(echo "$label" | tr ' /.' '_')"
        continue
    fi
    out=$(eval "$cmd")
    echo "    $out"
    PREV=$(echo "$out" | sed -n 's/^Job <\([0-9]*\)>.*/\1/p')
    [ -z "$PREV" ] && { echo "ERROR: could not parse job id for $label"; exit 1; }
done

echo
echo "All submissions done. Track with: bjobs -w"
echo "Scores land in: data/output/bfcl/<model_slug>/scores/<category>_scores.json"
echo "Validity gate per job: 'Verified served model' line, no 'does not exist' 404s,"
echo "  manifest total_count 200 under data/output/bfcl/runs/."
