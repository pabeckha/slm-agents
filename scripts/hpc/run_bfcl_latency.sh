#!/bin/sh
### -- Job name --
#BSUB -J slm_bfcl_latency
### -- GPU queue: L40S, same hardware as the thesis accuracy runs --
#BSUB -q gpul40s
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 4 CPU cores --
#BSUB -n 4
#BSUB -R "span[hosts=1]"
### -- 8GB per core (32GB total) --
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time --
#BSUB -W 02:00
### -- Output --
#BSUB -o logs/bfcl_latency_%J.out
#BSUB -eo logs/bfcl_latency_%J.err
### -- Notifications --
#BSUB -B
#BSUB -N

# Latency measurement for thesis issue 7 (Task 3 in
# docs/handoff-hpc-examiner-fixes.md): run B, CD, and CD+Q on the first 100
# simple_python cases on the same GPU and record per-request wall time. The
# adapter prints per-case latency and writes a latency summary into the run
# manifest under data/output/bfcl_latency/<config>/runs/.

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MODEL_FP16="${MODEL_FP16:-Qwen/Qwen2.5-7B-Instruct}"
MODEL_AWQ="${MODEL_AWQ:-Qwen/Qwen2.5-7B-Instruct-AWQ}"
CATEGORY="${CATEGORY:-simple_python}"
LIMIT="${LIMIT:-100}"
VLLM_PORT=$((10000 + ${LSB_JOBID:-$$} % 20000))

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "FP16 model: $MODEL_FP16"
echo "AWQ model: $MODEL_AWQ"
echo "Category: $CATEGORY, limit: $LIMIT"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"

echo "=== Syncing dependencies ==="
uv sync --group hpc

start_vllm() {
    # $1: model, $2: extra flags
    uv run --group hpc python -m vllm.entrypoints.openai.api_server \
        --model "$1" \
        --port "$VLLM_PORT" \
        --dtype auto \
        --max-model-len 4096 \
        --gpu-memory-utilization 0.9 \
        $2 \
        &
    VLLM_PID=$!
    echo "Waiting for vLLM server (PID $VLLM_PID) ..."
    for i in $(seq 1 1800); do
        if curl -s "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
            echo "vLLM ready after ${i}s"
            SERVED_MODEL=$(curl -s "http://localhost:${VLLM_PORT}/v1/models" \
                | python3 -c "import json,sys; print(json.load(sys.stdin)['data'][0]['id'])" 2>/dev/null)
            if [ "$SERVED_MODEL" != "$1" ]; then
                echo "ERROR: server at port ${VLLM_PORT} serves '$SERVED_MODEL', expected '$1'"
                echo "(another job's vLLM server may be answering on this port)"
                exit 1
            fi
            echo "Verified served model: $SERVED_MODEL"
            return 0
        fi
        if ! kill -0 "$VLLM_PID" 2>/dev/null; then
            echo "ERROR: vLLM process died"
            exit 1
        fi
        sleep 1
    done
    echo "ERROR: vLLM failed to start within 1800s"
    exit 1
}

stop_vllm() {
    kill "$VLLM_PID" 2>/dev/null || true
    wait "$VLLM_PID" 2>/dev/null || true
    VLLM_PID=""
    sleep 10
}

# ── FP16 server: B and CD ────────────────────────────────────────────
echo "=== Starting vLLM (FP16) ==="
start_vllm "$MODEL_FP16" ""

echo "=== Config B (no guided decoding, limit $LIMIT) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MODEL_FP16" \
    --category "$CATEGORY" \
    --no-guided \
    --limit "$LIMIT" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --output-dir "data/output/bfcl_latency/b"

echo "=== Config CD (guided decoding, limit $LIMIT) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MODEL_FP16" \
    --category "$CATEGORY" \
    --limit "$LIMIT" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --output-dir "data/output/bfcl_latency/cd"

echo "=== Stopping FP16 server ==="
stop_vllm

# ── AWQ server: CD+Q ─────────────────────────────────────────────────
echo "=== Starting vLLM (AWQ INT4) ==="
start_vllm "$MODEL_AWQ" "--quantization awq_marlin --enforce-eager"

echo "=== Config CD+Q (guided decoding + AWQ, limit $LIMIT) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MODEL_AWQ" \
    --category "$CATEGORY" \
    --limit "$LIMIT" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --output-dir "data/output/bfcl_latency/cdq"

echo "=== Done ==="
echo "Latency manifests:"
ls data/output/bfcl_latency/*/runs/ 2>/dev/null || true
