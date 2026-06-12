#!/bin/sh
### -- Job name --
#BSUB -J slm_bfcl
### -- GPU queue --
#BSUB -q gpua40
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 8 CPU cores --
#BSUB -n 8
#BSUB -R "span[hosts=1]"
### -- 8GB per core (64GB total) --
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time --
#BSUB -W 04:00
### -- Output --
#BSUB -o logs/bfcl_%J.out
#BSUB -eo logs/bfcl_%J.err
### -- Notifications --
#BSUB -B
#BSUB -N

# Exit on error
set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

# Load HPC modules
module load python3/3.12.11
module load cuda/12.6.3

# ── Configuration ──────────────────────────────────────────────────────
MODEL="${MODEL:-Qwen/Qwen2.5-7B}"
VLLM_PORT=$((10000 + ${LSB_JOBID:-$$} % 20000))
# ───────────────────────────────────────────────────────────────────────

PROJECT_DIR="$HOME/Documents/slm-agents"
GORILLA_DIR="$PROJECT_DIR/vendor/gorilla/berkeley-function-call-leaderboard"
cd "$PROJECT_DIR"
mkdir -p logs

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Model: $MODEL"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

# ── Step 0: Ensure hpc deps are installed ─────────────────────────────
echo "=== Syncing dependencies ==="
uv sync --group hpc

# ── Step 1: Start vLLM server in background ───────────────────────────
echo "=== Starting vLLM server ==="
uv run --group hpc python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$VLLM_PORT" \
    --dtype auto \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9 \
    &
VLLM_PID=$!

# Wait for vLLM to be ready
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
    kill "$VLLM_PID" 2>/dev/null
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

# ── Step 2: Run BFCL evaluation ───────────────────────────────────────
echo "=== Running BFCL generate ==="
cd "$GORILLA_DIR"

# Extract short model name for BFCL (e.g. "Qwen2.5-7B")
MODEL_SHORT=$(echo "$MODEL" | tr '/' '_')

bfcl generate \
    --model "$MODEL" \
    --test-category simple \
    --backend vllm \
    --num-gpus 1 \
    --skip-server-setup

echo "=== Running BFCL evaluate ==="
bfcl evaluate \
    --model "$MODEL" \
    --test-category simple

# ── Cleanup ───────────────────────────────────────────────────────────
echo "=== Stopping vLLM ==="
kill "$VLLM_PID" 2>/dev/null
wait "$VLLM_PID" 2>/dev/null || true

echo "=== Done ==="
echo "Check BFCL results in $GORILLA_DIR/result/"
