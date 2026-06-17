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
# FIX HISTORY:
#   1. Forced GUIDED_BACKEND=outlines — died at argument-parse: vLLM 0.8.5 V1
#      only offers {auto,guidance,xgrammar} (config.py GuidedDecodingBackendV1).
#   2. Forced GUIDED_BACKEND=xgrammar (jobs 28686566/28686567) — every case 400'd:
#      "The provided JSON schema contains features not supported by xgrammar".
#      vLLM's xgrammar gate (guided_decoding/utils.py:18-22) lists array
#      minItems/maxItems as unsupported; with the backend *forced*, there is no
#      'auto' fallback, so it hard-rejects. The off-HPC smoke test passed because
#      it compiled the STANDALONE xgrammar lib, which DOES support those keys —
#      a false-confidence gap (it never exercised vLLM's request-path gate).
#
# CURRENT FIX: keep GUIDED_BACKEND=xgrammar and drop the array bounds via
#   BFCL_PARALLEL_DROP_ARRAY_BOUNDS=1 (src/vllm_backend.py). oneOf/const ARE
#   supported by the gate, so the trimmed schema compiles. The bounds only ever
#   *weaken* the constraint (allow 0 or >cap calls), so at temp-0 their removal
#   cannot bias gemma's score upward. run_bfcl_eval.sh now also FAILS (exit 1) on
#   a client-side 400 or a correct_count=0 score, so any re-failure is loud.
#
# CAVEAT (record in the doc): the other parallel cells ran under 'auto' (which
#   routed this schema to guidance) with the full min/maxItems schema; gemma
#   alone is pinned to xgrammar with the trimmed schema. That backend+schema
#   asymmetry in the cross-family CD table must be flagged, not hidden.
#
# Serialized done() chain so the two jobs never `uv sync` the shared NFS .venv at
# the same time (the venv-race lesson).
#
# Usage:
#   bash scripts/hpc/run_gemma_parallel_reruns.sh
#   DRY_RUN=1 bash scripts/hpc/run_gemma_parallel_reruns.sh   # print bsub only
#   GUIDED_BACKEND=guidance bash scripts/hpc/run_gemma_parallel_reruns.sh  # override

set -e

HPC_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL="google/gemma-3-1b-it"
GUIDED_BACKEND="${GUIDED_BACKEND:-xgrammar}"

PREV="-"
for CATEGORY in parallel parallel_multiple; do
    label="gemma-3-1b $CATEGORY ($GUIDED_BACKEND)"
    cmd="bsub"
    [ "$PREV" != "-" ] && cmd="$cmd -w 'done($PREV)'"
    cmd="$cmd -env \"all,MODEL=$MODEL,CATEGORY=$CATEGORY,GUIDED_BACKEND=$GUIDED_BACKEND,BFCL_PARALLEL_DROP_ARRAY_BOUNDS=1\" < $HPC_DIR/run_bfcl_eval.sh"

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
echo "     is NOT uniformly [] (the crash/400 signature)."
echo "  run_bfcl_eval.sh now also fails the job on a client-side 400 or correct_count=0,"
echo "  so a re-failure exits non-zero instead of banking a silent fake-0%."
