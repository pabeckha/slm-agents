#!/bin/sh
### -- Job name --
#BSUB -J download_param
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

# Parameterised model downloader for the cross-family contrast runs.
# Reads $MODEL (pass via: bsub -env "all, MODEL=...").
# For gated repos (Llama, Gemma) it loads HF_TOKEN from .env without printing it.
# The Qwen-specific download_model.sh is intentionally left untouched.

set -e

module load python3/3.12.11

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

# ── Load HF_TOKEN from .env for gated repos (never printed) ────────────
if [ -z "${HF_TOKEN:-}" ] && [ -f .env ]; then
    HF_TOKEN=$(grep -E '^HF_TOKEN=' .env | head -1 | cut -d= -f2- | tr -d '"'"'"'')
    export HF_TOKEN
fi
if [ -n "${HF_TOKEN:-}" ]; then
    echo "HF_TOKEN: loaded (gated repos enabled)"
else
    echo "HF_TOKEN: not set (ungated repos only)"
fi

MODEL="${MODEL:?set MODEL via bsub -env \"all, MODEL=org/name\"}"

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Model: $MODEL"

echo "=== Syncing dependencies ==="
uv sync

echo "=== Downloading $MODEL ==="
uv run python -c "
import os
from huggingface_hub import snapshot_download
snapshot_download('$MODEL', token=os.environ.get('HF_TOKEN'))
print('Download complete.')
"

echo "=== Done ==="
