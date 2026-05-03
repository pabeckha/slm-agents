#!/bin/sh
### -- Job name --
#BSUB -J quantize_merged_lora_awq
### -- GPU queue (AWQ calibration needs GPU) --
#BSUB -q gpul40s
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 8 CPU cores --
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=32GB]"
#BSUB -M 32GB
### -- Wall time --
#BSUB -W 04:00
### -- Output --
#BSUB -o logs/quantize_merged_lora_awq_%J.out
#BSUB -eo logs/quantize_merged_lora_awq_%J.err
#BSUB -B
#BSUB -N

# Quantize the format-aligned merged LoRA model with AWQ INT4.
# Produces Config CD+Q+FT: CD + AWQ quantization + LoRA fine-tuning.
# Run after merge_lora_aligned job (or if merged model already exists).

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"
export PYTHONUNBUFFERED=1

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MERGED_MODEL="${MERGED_MODEL:-/work3/s242779/models/models/merged/Qwen_Qwen2.5-7B-Instruct-merged-aligned}"
OUTPUT_DIR="${OUTPUT_DIR:-/work3/s242779/models/models/merged/Qwen_Qwen2.5-7B-Instruct-merged-aligned-AWQ}"

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Input model:  $MERGED_MODEL"
echo "Output model: $OUTPUT_DIR"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

echo "=== Quantizing merged LoRA model with AutoAWQ INT4 ==="
uv run --group hpc python scripts/quantize_lora_merged.py \
    --model  "$MERGED_MODEL" \
    --output "$OUTPUT_DIR" \
    --bits 4 \
    --group-size 128

echo "=== Quantization complete ==="
echo "Quantized model saved to: $OUTPUT_DIR"
echo ""
echo "Next step:"
echo "  bsub < scripts/hpc/run_bfcl_cdqft_aligned.sh"
