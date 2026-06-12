#!/bin/sh
### -- Job name --
#BSUB -J bfcl_schema_rich
### -- GPU queue --
#BSUB -q gpul40s
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 4 CPU cores --
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time (two full 400-case passes + evaluation) --
#BSUB -W 04:00
### -- Output --
#BSUB -o logs/bfcl_schema_rich_%J.out
#BSUB -eo logs/bfcl_schema_rich_%J.err
#BSUB -B
#BSUB -N

# Config CD+schema (issue #140): carry full parameter descriptions, defaults,
# and enumerations into the argument extraction prompt while keeping the
# guided_json constraint identical to Config CD.
#
# CD and CD+schema are run back-to-back in the same session because result
# files are overwritten per run and accuracies drift 1-2 cases across
# sessions; the same-session pair feeds scripts/mcnemar_bfcl.py directly.

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
OUTPUT_ROOT="${OUTPUT_ROOT:-data/output/bfcl_schema_pair}"
VLLM_PORT=$((10000 + ${LSB_JOBID:-$$} % 20000))

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Model: $MODEL"
echo "Category: $CATEGORY"
echo "Output root: $OUTPUT_ROOT"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

# ── Start vLLM server ────────────────────────────────────────────────
echo "=== Starting vLLM server ==="
uv run --group hpc python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$VLLM_PORT" \
    --dtype auto \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9 \
    &
VLLM_PID=$!

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

# ── Pass 1: Config CD (paired reference) ────────────────────────────
echo "=== Pass 1: Config CD (reference) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MODEL" \
    --category "$CATEGORY" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --output-dir "$OUTPUT_ROOT/cd"

# ── Pass 2: Config CD+schema ─────────────────────────────────────────
echo "=== Pass 2: Config CD+schema (--schema-rich) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MODEL" \
    --category "$CATEGORY" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --schema-rich \
    --output-dir "$OUTPUT_ROOT/schema_rich"

# ── Paired significance test ─────────────────────────────────────────
echo "=== McNemar paired test: CD vs CD+schema ==="
SAFE_MODEL=$(echo "$MODEL" | tr '/' '_')
uv run --group hpc python scripts/mcnemar_bfcl.py \
    "$OUTPUT_ROOT/cd/$SAFE_MODEL/non_live/BFCL_v4_${CATEGORY}_result.json" \
    "$OUTPUT_ROOT/schema_rich/$SAFE_MODEL/non_live/BFCL_v4_${CATEGORY}_result.json" \
    --category "$CATEGORY"

echo "=== Done ==="
