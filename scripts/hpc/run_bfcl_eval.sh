#!/bin/sh
### -- Job name --
#BSUB -J bfcl_eval
### -- GPU queue --
#BSUB -q gpua100
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

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="Qwen/Qwen2.5-7B-Instruct"
CATEGORY="simple_python"
VLLM_PORT=8000

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Model: $MODEL"
echo "Category: $CATEGORY"
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

# ── Run BFCL evaluation ─────────────────────────────────────────────
echo "=== Running BFCL evaluation ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MODEL" \
    --category "$CATEGORY" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1"

# ── Run BFCL official evaluator as fallback ──────────────────────────
echo "=== Running BFCL official evaluator ==="
BFCL_DIR="vendor/gorilla/berkeley-function-call-leaderboard"
RESULT_DIR="data/output/bfcl"

# Copy results to where bfcl evaluate expects them
mkdir -p "${BFCL_DIR}/result/$(echo $MODEL | tr '/' '_')/non_live"
cp "${RESULT_DIR}/$(echo $MODEL | tr '/' '_')/non_live/BFCL_v4_${CATEGORY}_result.json" \
   "${BFCL_DIR}/result/$(echo $MODEL | tr '/' '_')/non_live/" 2>/dev/null || true

uv run --group hpc bfcl evaluate \
    --model "$MODEL" \
    --test-category "$CATEGORY" \
    --result-dir "${BFCL_DIR}/result" \
    --partial-eval 2>&1 || echo "BFCL evaluate failed (non-critical)"

echo "=== Done ==="
