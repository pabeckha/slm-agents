#!/bin/sh
### -- Job name --
#BSUB -J bfcl_cdqft_aligned
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
#BSUB -o logs/bfcl_cdqft_aligned_%J.out
#BSUB -eo logs/bfcl_cdqft_aligned_%J.err
#BSUB -B
#BSUB -N

# Config CD+Q+FT: BFCL eval with guided decoding on AWQ-quantized format-aligned LoRA model.
# Compare against:
#   CD+FT-aligned (76.75%) — data/output/bfcl_ft_aligned/  (FP16 merged)
#   CD+Q          (72.25%) — data/output/bfcl_quant/        (AWQ, no LoRA)
# Question: does quantizing the LoRA-tuned model recover/preserve the 76.75% gain?

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="${MODEL:-/work3/s242779/models/models/merged/Qwen_Qwen2.5-7B-Instruct-merged-aligned-AWQ}"
LORA_BASE="${LORA_BASE:-Qwen/Qwen2.5-7B-Instruct}"
CATEGORY="${CATEGORY:-simple_python}"
VLLM_PORT=8000

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Model: $MODEL"
echo "Category: $CATEGORY"
echo "Config: CD+Q+FT (guided + AWQ INT4 + format-aligned LoRA)"
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
    --quantization awq_marlin \
    --enforce-eager \
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

echo "=== Running BFCL evaluation (Config CD+Q+FT) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MODEL" \
    --category "$CATEGORY" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --output-dir "data/output/bfcl_cdqft_aligned" \
    --lora-base-model "$LORA_BASE"

echo "=== Done ==="
echo "CD+Q+FT results in data/output/bfcl_cdqft_aligned/"
echo "Compare: CD+FT-aligned=76.75%, CD+Q=72.25%, CD=72.75%"
