#!/bin/sh
### -- Job name --
#BSUB -J bfcl_eval
### -- GPU queue --
#BSUB -q gpul40s
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 4 CPU cores --
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time --
#BSUB -W 02:00
### -- Output --
#BSUB -o logs/bfcl_eval_%J.out
#BSUB -eo logs/bfcl_eval_%J.err
#BSUB -B
#BSUB -N

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
CATEGORY="${CATEGORY:-simple_python}"
# Optional: override the vLLM guided-decoding backend (e.g. GUIDED_BACKEND=outlines).
# Default (unset) keeps vLLM's 'auto' routing. Needed for gemma-3, whose 262144-vs-262145
# vocab crashes the llguidance backend that 'auto' picks for the parallel array/oneOf
# schemas — see docs/decisions/cross-family-cd-results.md.
GUIDED_BACKEND="${GUIDED_BACKEND:-}"
BACKEND_ARG=""
[ -n "$GUIDED_BACKEND" ] && BACKEND_ARG="--guided-decoding-backend $GUIDED_BACKEND"
VLLM_PORT=$((10000 + ${LSB_JOBID:-$$} % 20000))
VLLM_LOG="logs/vllm_${LSB_JOBID:-$$}.log"

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Model: $MODEL"
echo "Category: $CATEGORY"
echo "Guided backend: ${GUIDED_BACKEND:-auto (vLLM default)}"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

# ── Start vLLM server ────────────────────────────────────────────────
echo "=== Starting vLLM server ==="
# Server stdout/stderr go to $VLLM_LOG so the post-eval health check can scan it
# for an engine crash (the "Verified served model" health probe runs BEFORE any
# guided request, so a guided-decoding engine-death otherwise passes the gate while
# every case fails silently — exactly the gemma-3 262144-vs-262145 trap).
uv run --group hpc python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$VLLM_PORT" \
    --dtype auto \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9 \
    $BACKEND_ARG \
    > "$VLLM_LOG" 2>&1 &
VLLM_PID=$!
echo "vLLM server log: $VLLM_LOG"

echo "Waiting for vLLM server (PID $VLLM_PID) ..."
for i in $(seq 1 1800); do
    if curl -s "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
        echo "vLLM ready after ${i}s"
        break
    fi
    if ! kill -0 "$VLLM_PID" 2>/dev/null; then
        echo "ERROR: vLLM process died"
        exit 1
    fi
    sleep 1
done

if ! curl -s "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
    echo "ERROR: vLLM failed to start within 1800s"
    exit 1
fi

SERVED_MODEL=$(curl -s "http://localhost:${VLLM_PORT}/v1/models" \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['data'][0]['id'])" 2>/dev/null)
if [ "$SERVED_MODEL" != "$MODEL" ]; then
    echo "ERROR: server at port ${VLLM_PORT} serves '$SERVED_MODEL', expected '$MODEL'"
    echo "(another job's vLLM server may be answering on this port)"
    exit 1
fi
echo "Verified served model: $SERVED_MODEL"

# ── Run BFCL evaluation ─────────────────────────────────────────────
# Tee the eval output so the validity gate below can inspect it: a forced
# guided backend (e.g. xgrammar) rejects an unsupported schema with a per-request
# client-side 400 (BadRequestError) that NEVER reaches $VLLM_LOG, so the
# engine-health grep alone cannot catch it.
echo "=== Running BFCL evaluation ==="
EVAL_LOG="$(mktemp)"
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MODEL" \
    --category "$CATEGORY" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" 2>&1 | tee "$EVAL_LOG"

# ── Engine-health gate ──────────────────────────────────────────────
# A guided-decoding engine death (e.g. llguidance "vocab size too small") leaves
# the server returning 500s while BFCL records 200 empty/failed cases — a 0% that
# is an infra artifact, NOT a capability result. Fail loudly so a chained done()
# does not treat the crash as a clean run.
echo "=== Checking vLLM engine health ==="
if grep -qE 'EngineDeadError|vocab size too small|engine dead|500 Internal Server Error' "$VLLM_LOG"; then
    echo "FATAL: vLLM engine crashed during evaluation — results for $MODEL/$CATEGORY are INVALID"
    grep -nE 'EngineDeadError|vocab size too small|engine dead|ValueError|500 Internal Server Error' "$VLLM_LOG" | tail -20
    exit 1
fi
echo "Engine healthy: no crash markers in $VLLM_LOG"

# ── Results-validity gate ───────────────────────────────────────────
# Catch the client-side failure modes the engine grep misses: a forced backend
# rejecting the schema (400 BadRequestError, "not supported by xgrammar") makes
# every case fail with an empty call -> 0% that is infra, not capability. Fail if
# any 400 appears OR if the run scored exactly zero correct cases.
echo "=== Checking results validity ==="
if grep -qE 'not supported by xgrammar|BadRequestError|Error code: 400' "$EVAL_LOG"; then
    echo "FATAL: guided backend returned a 400 (schema rejected) — results for $MODEL/$CATEGORY are INVALID"
    grep -nE 'not supported by xgrammar|BadRequestError|Error code: 400' "$EVAL_LOG" | tail -5
    rm -f "$EVAL_LOG"
    exit 1
fi
rm -f "$EVAL_LOG"

MODEL_SLUG="$(printf '%s' "$MODEL" | tr '/' '_')"
SCORE_FILE="data/output/bfcl/${MODEL_SLUG}/scores/${CATEGORY}_scores.json"
if [ -f "$SCORE_FILE" ]; then
    CORRECT="$(grep -oE '"correct_count"[[:space:]]*:[[:space:]]*[0-9]+' "$SCORE_FILE" | grep -oE '[0-9]+$')"
    if [ "$CORRECT" = "0" ]; then
        echo "FATAL: $SCORE_FILE has correct_count=0 — treating as an infra failure, not a 0% result"
        exit 1
    fi
    echo "Results valid: correct_count=$CORRECT in $SCORE_FILE"
else
    echo "WARNING: expected score file $SCORE_FILE not found"
fi

echo "=== Done ==="
