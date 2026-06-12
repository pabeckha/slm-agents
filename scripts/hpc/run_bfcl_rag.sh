#!/bin/sh
### -- Job name --
#BSUB -J bfcl_rag
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
#BSUB -o logs/bfcl_rag_%J.out
#BSUB -eo logs/bfcl_rag_%J.err
#BSUB -B
#BSUB -N

# Config CD+Q+RAG: BFCL evaluation WITH guided decoding on AWQ INT4 quantized
# model, using RAG to retrieve top-k functions from a pooled corpus instead of
# providing the ground-truth function directly.
#
# Measures whether RAG-based tool retrieval maintains accuracy when the model
# must select from a larger candidate set (370 functions) rather than being
# given the exact function.
#
# Baseline: Config CD+Q at 72.0%.

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct-AWQ}"
CATEGORY="${CATEGORY:-simple_python}"
VLLM_PORT=$((10000 + ${LSB_JOBID:-$$} % 20000))
RAG_TOP_K="${RAG_TOP_K:-5}"

# Auto-detect quantization from model name.
QUANT_FLAGS=""
case "$MODEL" in
    *-AWQ*|*-awq*) QUANT_FLAGS="--quantization awq_marlin --enforce-eager" ;;
    *-GPTQ*|*-gptq*) QUANT_FLAGS="--quantization gptq" ;;
esac

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Model: $MODEL"
echo "Category: $CATEGORY"
echo "Quant flags: ${QUANT_FLAGS:-none}"
echo "Config: CD+Q+RAG (guided decoding + quantization + RAG top-${RAG_TOP_K})"
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
    ${QUANT_FLAGS} \
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

# Report VRAM usage after model load
echo "=== GPU memory after model load ==="
nvidia-smi

# ── Run BFCL evaluation (guided decoding + quantized + RAG) ─────────
echo "=== Running BFCL evaluation (Config CD+Q+RAG: guided + AWQ INT4 + RAG top-${RAG_TOP_K}) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MODEL" \
    --category "$CATEGORY" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --output-dir "data/output/bfcl_rag" \
    --rag \
    --rag-top-k "$RAG_TOP_K"

echo "=== Done ==="
echo "Config CD+Q+RAG results in data/output/bfcl_rag/"
echo "Compare against Config CD+Q results in data/output/bfcl_quant/"
