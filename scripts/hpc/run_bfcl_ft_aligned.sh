#!/bin/sh
### -- Job name --
#BSUB -J bfcl_ft_aligned
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
#BSUB -o logs/bfcl_ft_aligned_%J.out
#BSUB -eo logs/bfcl_ft_aligned_%J.err
#BSUB -B
#BSUB -N

# Config CD+FT-aligned: BFCL eval on the format-aligned LoRA model (with guided decoding).
# Compare against:
#   CD baseline (72.75%)  — data/output/bfcl/
#   CD+FT v1   (69.75%)  — data/output/bfcl_ft/   (format-misaligned)
#   CD+FT-aligned (this) — data/output/bfcl_ft_aligned/
#
# If aligned > v1: format mismatch was the primary cause of the regression.
# If aligned ≈ v1: xlam argument semantics differ from BFCL ground truth.

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MERGED_MODEL="${MERGED_MODEL:-models/merged/Qwen_Qwen2.5-7B-Instruct-merged-aligned}"
LORA_BASE="${LORA_BASE:-Qwen/Qwen2.5-7B-Instruct}"
CATEGORY="${CATEGORY:-simple_python}"
VLLM_PORT=8000

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Merged model: $MERGED_MODEL"
echo "Config: CD+FT-aligned (guided decoding + format-aligned LoRA)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

echo "=== Starting vLLM server ==="
uv run --group hpc python -m vllm.entrypoints.openai.api_server \
    --model "$MERGED_MODEL" \
    --port "$VLLM_PORT" \
    --dtype bfloat16 \
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

echo "=== GPU memory after model load ==="
nvidia-smi

echo "=== Running BFCL evaluation (CD+FT-aligned) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MERGED_MODEL" \
    --category "$CATEGORY" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --output-dir "data/output/bfcl_ft_aligned" \
    --lora-base-model "$LORA_BASE"

echo "=== Done ==="
echo "CD+FT-aligned results in data/output/bfcl_ft_aligned/"
