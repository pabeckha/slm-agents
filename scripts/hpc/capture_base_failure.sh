#!/bin/sh
### -- Job name --
#BSUB -J capture_base_failure
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
#BSUB -W 01:00
### -- Output --
#BSUB -o logs/capture_base_failure_%J.out
#BSUB -eo logs/capture_base_failure_%J.err
#BSUB -B
#BSUB -N

# Capture raw Base-config generations for the introduction failure-mode example.
# The Base integration (plain-text prompt, free generation, no native template,
# JSON-parsed completion) is reproduced and the raw model text is logged, which
# the BFCL result files discard. Output: data/output/base_failure_capture/.

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
NUM_BFCL="${NUM_BFCL:-20}"
REPEAT="${REPEAT:-3}"
VLLM_PORT=$((10000 + ${LSB_JOBID:-$$} % 20000))

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Model: $MODEL"
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

# ── Capture raw Base-config generations ──────────────────────────────
echo "=== Capturing Base-config generations ==="
uv run --group hpc python -m scripts.capture_base_failure \
    --model "$MODEL" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --num-bfcl "$NUM_BFCL" \
    --repeat "$REPEAT"

echo "=== Done ==="
echo "Read data/output/base_failure_capture/captures.txt and pick a real"
echo "FAILS-PARSE case to quote in the introduction."
