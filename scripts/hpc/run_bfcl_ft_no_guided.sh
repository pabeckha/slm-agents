#!/bin/sh
### -- Job name --
#BSUB -J bfcl_ft_no_guided
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
#BSUB -o logs/bfcl_ft_no_guided_%J.out
#BSUB -eo logs/bfcl_ft_no_guided_%J.err
#BSUB -B
#BSUB -N

# Config FT: BFCL evaluation on the merged LoRA model WITHOUT guided decoding.
# Isolates the contribution of fine-tuning alone (no constrained decoding).
# Compare against Config B (base, no guided) and Config CD+FT (run_bfcl_ft.sh).

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MERGED_MODEL="${MERGED_MODEL:-${MODEL:-models/merged/Qwen_Qwen2.5-7B-Instruct-merged}}"
LORA_BASE="${LORA_BASE:-Qwen/Qwen2.5-7B-Instruct}"
CATEGORY="${CATEGORY:-simple_python}"
VLLM_PORT=8000

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Merged model: $MERGED_MODEL"
echo "Base model (for manifest): $LORA_BASE"
echo "Category: $CATEGORY"
echo "Config: FT (LoRA fine-tuned, no guided decoding)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

# ── Start vLLM server (merged LoRA model, bf16, no tool parser) ──────
echo "=== Starting vLLM server (merged LoRA model) ==="
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

# ── Run BFCL evaluation (no guided decoding) ─────────────────────────
echo "=== Running BFCL evaluation (Config FT: LoRA fine-tuned, no guided decoding) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm \
    --model "$MERGED_MODEL" \
    --category "$CATEGORY" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --no-guided \
    --output-dir "data/output/bfcl_ft_no_guided" \
    --lora-base-model "$LORA_BASE"

echo "=== Done ==="
echo "Config FT results in data/output/bfcl_ft_no_guided/"
echo "Compare against Config B in data/output/bfcl_no_guided/"
echo "Compare against Config CD+FT in data/output/bfcl_ft/"
