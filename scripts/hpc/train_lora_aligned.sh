#!/bin/sh
### -- Job name --
#BSUB -J train_lora_aligned
### -- GPU queue --
#BSUB -q gpul40s
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 8 CPU cores --
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time: 8h for 7B --
#BSUB -W 08:00
### -- Output --
#BSUB -o logs/train_lora_aligned_%J.out
#BSUB -eo logs/train_lora_aligned_%J.err
#BSUB -B
#BSUB -N

# LoRA fine-tuning with format-aligned training data (v2).
#
# Ablation purpose: isolate whether the CD+FT regression (v1, 69.75%) was
# caused by the training format mismatch. In v1, format_xlam_example produced
# Python call syntax (name(arg=val, ...)) while the inference pipeline extracts
# JSON args via guided_json. This version trains on the exact prompt+output
# format used by build_args_extraction_prompt / _extract_args at inference.
#
# Same hyperparameters as v1; only format_xlam_example differs.
# Compare output against: models/lora/Qwen_Qwen2.5-7B-Instruct (v1)

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"
export HF_TOKEN="${HF_TOKEN:-}"

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
ADAPTER_DIR="${ADAPTER_DIR:-models/lora/Qwen_Qwen2.5-7B-Instruct-aligned}"
EPOCHS="${EPOCHS:-2}"
RANK="${RANK:-16}"
MAX_SAMPLES="${MAX_SAMPLES:-}"

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Base model: $MODEL"
echo "Adapter output: $ADAPTER_DIR"
echo "Epochs: $EPOCHS  Rank: $RANK"
echo "Training format: aligned (JSON args, arg-extraction prompt)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

TRAIN_DATA="data/input/lora_train.jsonl"
DATA_PATH_ARG=""
if [ -f "$TRAIN_DATA" ]; then
    echo "Using local training data: $TRAIN_DATA"
    DATA_PATH_ARG="--data-path $TRAIN_DATA"
else
    echo "Local data not found — downloading from HuggingFace (set HF_TOKEN)"
fi

echo "=== Starting LoRA training (aligned format) ==="
MAX_SAMPLES_ARG=""
[ -n "$MAX_SAMPLES" ] && MAX_SAMPLES_ARG="--max-samples $MAX_SAMPLES"

uv run --group hpc python scripts/train_lora.py \
    --model "$MODEL" \
    --output-dir "$ADAPTER_DIR" \
    --epochs "$EPOCHS" \
    --rank "$RANK" \
    --bf16 \
    ${DATA_PATH_ARG} \
    ${MAX_SAMPLES_ARG}

echo "=== Training complete ==="
echo "Adapter saved to: $ADAPTER_DIR"
echo ""
echo "Next steps:"
echo "  1. Merge: uv run --group hpc python scripts/merge_lora.py \\"
echo "         --adapter $ADAPTER_DIR \\"
echo "         --output models/merged/Qwen_Qwen2.5-7B-Instruct-merged-aligned"
echo "  2. Eval:  bsub < scripts/hpc/run_bfcl_ft_aligned.sh"
echo "            bsub < scripts/hpc/run_bfcl_ft_aligned_no_guided.sh"
