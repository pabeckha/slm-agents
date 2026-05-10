#!/bin/sh
### -- Job name --
#BSUB -J bfcl_itc
### -- GPU queue --
#BSUB -q gpul40s
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 4 CPU cores --
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time (~2x CD+Q due to extra reasoning call) --
#BSUB -W 03:00
### -- Output --
#BSUB -o logs/bfcl_itc_%J.out
#BSUB -eo logs/bfcl_itc_%J.err
#BSUB -B
#BSUB -N

# Config CD+Q+ITC: BFCL evaluation with guided decoding on AWQ INT4 model,
# plus a chain-of-thought reasoning step before argument extraction.
# Compare against:
#   CD+Q (72.25%) — data/output/bfcl_quant/
# Expected: small positive or negative delta; reasoning may help numeric
# precision but hurt by steering toward natural-language value conventions.

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
VLLM_PORT=8000

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
echo "Config: CD+Q+ITC (guided + AWQ INT4 + chain-of-thought reasoning)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

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

echo "=== GPU memory after model load ==="
nvidia-smi

echo "=== Running BFCL evaluation (Config CD+Q+ITC: guided + AWQ INT4 + CoT) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MODEL" \
    --category "$CATEGORY" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --output-dir "data/output/bfcl_itc" \
    --cot

echo "=== Done ==="
echo "Config CD+Q+ITC results in data/output/bfcl_itc/"
echo "Compare against CD+Q results in data/output/bfcl_quant/"
