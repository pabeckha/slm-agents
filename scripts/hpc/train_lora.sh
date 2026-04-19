#!/bin/sh
### -- Job name --
#BSUB -J train_lora
### -- GPU queue (A100 for training) --
#BSUB -q gpua100
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 8 CPU cores --
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time: 8h for 7B, 3h for 1.5B --
#BSUB -W 08:00
### -- Output --
#BSUB -o logs/train_lora_%J.out
#BSUB -eo logs/train_lora_%J.err
#BSUB -B
#BSUB -N

# LoRA fine-tuning on Qwen2.5 for function calling.
# Trains on Salesforce/xlam-function-calling-60k using TRL SFTTrainer.
# After training, run scripts/merge_lora.py to merge the adapter, then
# submit scripts/hpc/run_bfcl_ft.sh to evaluate.

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"
export HF_TOKEN="${HF_TOKEN:-}"

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
ADAPTER_DIR="${ADAPTER_DIR:-models/lora/$(echo "$MODEL" | tr '/' '_')}"
EPOCHS="${EPOCHS:-2}"
RANK="${RANK:-16}"
MAX_SAMPLES="${MAX_SAMPLES:-}"  # empty = use all

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Base model: $MODEL"
echo "Adapter output: $ADAPTER_DIR"
echo "Epochs: $EPOCHS  Rank: $RANK"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

echo "=== Starting LoRA training ==="
MAX_SAMPLES_ARG=""
[ -n "$MAX_SAMPLES" ] && MAX_SAMPLES_ARG="--max-samples $MAX_SAMPLES"

uv run --group hpc python scripts/train_lora.py \
    --model "$MODEL" \
    --output-dir "$ADAPTER_DIR" \
    --epochs "$EPOCHS" \
    --rank "$RANK" \
    --bf16 \
    ${MAX_SAMPLES_ARG}

echo "=== Training complete ==="
echo "Adapter saved to: $ADAPTER_DIR"
echo ""
echo "Next steps:"
echo "  1. Merge adapter:   uv run --group hpc python scripts/merge_lora.py --adapter $ADAPTER_DIR --output models/merged/$(basename $ADAPTER_DIR)-merged"
echo "  2. Evaluate:        bsub < scripts/hpc/run_bfcl_ft.sh"
