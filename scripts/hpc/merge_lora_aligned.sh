#!/bin/sh
### -- Job name --
#BSUB -J merge_lora_aligned
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
#BSUB -o logs/merge_lora_aligned_%J.out
#BSUB -eo logs/merge_lora_aligned_%J.err
#BSUB -B
#BSUB -N

# Merge the format-aligned LoRA adapter into the base model for vLLM serving.
# Run after train_lora_aligned job completes.

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

module load python3/3.12.11

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

ADAPTER_DIR="${ADAPTER_DIR:-models/lora/Qwen_Qwen2.5-7B-Instruct-aligned}"
OUTPUT_DIR="${OUTPUT_DIR:-models/merged/Qwen_Qwen2.5-7B-Instruct-merged-aligned}"

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Adapter: $ADAPTER_DIR"
echo "Output:  $OUTPUT_DIR"

echo "=== Syncing dependencies ==="
uv sync --group hpc

echo "=== Merging LoRA adapter (aligned) ==="
uv run --group hpc python scripts/merge_lora.py \
    --adapter "$ADAPTER_DIR" \
    --output  "$OUTPUT_DIR"

echo "=== Merge complete ==="
echo "Merged model saved to: $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "  bsub < scripts/hpc/run_bfcl_ft_aligned.sh"
echo "  bsub < scripts/hpc/run_bfcl_ft_aligned_no_guided.sh"
