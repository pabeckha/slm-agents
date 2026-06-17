#!/bin/sh
# Re-run the TWO gemma-3-1b parallel cells that crashed in the 2026-06-16/17
# parallel re-run batch (jobs 28671151 `parallel`, 28671159 `parallel_multiple`).
#
# ROOT CAUSE (not a model collapse, not the schema-cap artifact):
#   vLLM 0.8.5 'auto' guided-decoding routes the parallel array/oneOf schemas to
#   the llguidance backend. llguidance.hf.from_tokenizer asserts the tokenizer
#   vocab >= the model's logit width; gemma-3-1b is 262144 vs 262145, so the
#   engine dies on the FIRST guided request:
#       ValueError: vocab size too small; 262144 vs 262145  -> EngineDeadError
#   The "Verified served model" health probe runs before any guided request, so
#   the crash slipped the validity gate: total_count=200 but every case is empty
#   ([] -> "Wrong number of functions") -> 0.0%. gemma's simpler simple/multiple
#   schemas stayed on xgrammar and ran fine (55.5% / 44.0%), which is why only
#   these two cells crashed.
#
# FIX (hypothesis — NOT verifiable off-HPC): force a non-llguidance backend via
#   GUIDED_BACKEND=outlines. outlines supports the array/minItems/maxItems/oneOf
#   features that pushed 'auto' off xgrammar, and does not run the llguidance
#   vocab assertion. run_bfcl_eval.sh now also FAILS the job (exit 1) if the vLLM
#   log still shows EngineDeadError / "vocab size too small" / 500s, so a re-crash
#   will be loud instead of a silent fake-0%.
#
# CAVEAT (record in the doc): the 22 valid cells in this batch all ran on the
#   guidance backend (identical schema -> identical 'auto' routing); only gemma
#   is forced onto outlines. That is a backend confound in the cross-family CD
#   table and must be flagged, not hidden.
#
# Serialized done() chain so the two jobs never `uv sync` the shared NFS .venv at
# the same time (the venv-race lesson).
#
# Usage:
#   bash scripts/hpc/run_gemma_parallel_reruns.sh
#   DRY_RUN=1 bash scripts/hpc/run_gemma_parallel_reruns.sh   # print bsub only
#   GUIDED_BACKEND=xgrammar bash scripts/hpc/run_gemma_parallel_reruns.sh  # try another

set -e

HPC_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL="google/gemma-3-1b-it"
GUIDED_BACKEND="${GUIDED_BACKEND:-outlines}"

PREV="-"
for CATEGORY in parallel parallel_multiple; do
    label="gemma-3-1b $CATEGORY ($GUIDED_BACKEND)"
    cmd="bsub"
    [ "$PREV" != "-" ] && cmd="$cmd -w 'done($PREV)'"
    cmd="$cmd -env \"all,MODEL=$MODEL,CATEGORY=$CATEGORY,GUIDED_BACKEND=$GUIDED_BACKEND\" < $HPC_DIR/run_bfcl_eval.sh"

    echo "  [$label] $cmd"
    if [ -n "$DRY_RUN" ]; then
        PREV="DRY_$(echo "$CATEGORY" | tr ' /.' '___')"
        continue
    fi
    out=$(eval "$cmd")
    echo "    $out"
    PREV=$(echo "$out" | sed -n 's/^Job <\([0-9]*\)>.*/\1/p')
    [ -z "$PREV" ] && { echo "ERROR: could not parse job id for $label"; exit 1; }
done

echo
echo "All submissions done. Track with: bjobs -w"
echo
echo "VALIDITY GATE for these re-runs (the plain gate is NOT enough — it passed the crash):"
echo "  1. Job exits 0 (run_bfcl_eval.sh now exits 1 on an engine crash)."
echo "  2. logs/vllm_<JOBID>.log shows NO 'vocab size too small' / 'EngineDeadError'."
echo "  3. Manifest under data/output/bfcl/runs/ has total_count=200 AND correct_count>0."
echo "  4. Spot-check data/output/bfcl/google_gemma-3-1b-it/non_live/BFCL_v4_<cat>_result.json"
echo "     is NOT uniformly [] (the crash signature)."
echo "  If it crashes again on outlines: retry with GUIDED_BACKEND=xgrammar or"
echo "  lm-format-enforcer, or pin a vLLM build that fixes the gemma-3 llguidance vocab."
