#!/bin/sh
### -- Job name --
#BSUB -J merge_lora
### -- CPU-only queue --
#BSUB -q hpc
### -- 8 CPU cores --
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=5GB]"
#BSUB -M 5GB
### -- Wall time --
#BSUB -W 02:00
### -- Output --
#BSUB -o logs/merge_lora_%J.out
#BSUB -eo logs/merge_lora_%J.err
#BSUB -B
#BSUB -N

# Merge a LoRA adapter into the base model for vLLM serving.
# Run after train_lora job completes; submit run_bfcl_ft.sh after this.

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

module load python3/3.12.11

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

ADAPTER_DIR="${ADAPTER_DIR:-models/lora/Qwen_Qwen2.5-7B-Instruct}"
OUTPUT_DIR="${OUTPUT_DIR:-models/merged/Qwen_Qwen2.5-7B-Instruct-merged}"

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Adapter: $ADAPTER_DIR"
echo "Output:  $OUTPUT_DIR"

echo "=== Syncing dependencies ==="
uv sync --group hpc

echo "=== Merging LoRA adapter ==="
uv run --group hpc python scripts/merge_lora.py \
    --adapter "$ADAPTER_DIR" \
    --output  "$OUTPUT_DIR"

echo "=== Merge complete ==="
echo "Merged model saved to: $OUTPUT_DIR"
echo ""
echo "Next step: bsub < scripts/hpc/run_bfcl_ft.sh"
