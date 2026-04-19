#!/bin/sh
### -- Job name --
#BSUB -J download_model
### -- No GPU needed, just network + disk --
#BSUB -q hpc
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time --
#BSUB -W 02:00
### -- Output --
#BSUB -o logs/download_%J.out
#BSUB -eo logs/download_%J.err
#BSUB -B
#BSUB -N

set -e

module load python3/3.12.11

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"

echo "=== Syncing dependencies ==="
uv sync

echo "=== Downloading Qwen/Qwen2.5-7B-Instruct ==="
uv run python -c "
from huggingface_hub import snapshot_download
snapshot_download('Qwen/Qwen2.5-7B-Instruct')
print('Download complete.')
"

echo "=== Done ==="
