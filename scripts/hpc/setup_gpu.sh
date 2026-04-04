#!/bin/sh
### -- Job name --
#BSUB -J slm_setup
### -- GPU queue (short job, use any available) --
#BSUB -q gpua40
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 4 CPU cores --
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Short walltime (just installing) --
#BSUB -W 00:30
### -- Output --
#BSUB -o logs/setup_%J.out
#BSUB -eo logs/setup_%J.err
#BSUB -B
#BSUB -N

set -e

module load python3/3.12.11
module load cuda/12.6.3

# Use local /tmp for cache to avoid filling home directory quota
export UV_CACHE_DIR="/tmp/uv-cache-$USER"
export PIP_CACHE_DIR="/tmp/pip-cache-$USER"

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

echo "=== GPU node info ==="
nvidia-smi
python3 --version

echo "=== Cleaning up ==="
rm -rf "$PROJECT_DIR/.venv"
uv cache clean

echo "=== Installing everything (single pass via uv sync) ==="
uv sync --group hpc --python "$(which python3)"
echo "WARNING: flash-attn skipped, vLLM will use fallback attention"

echo "=== Verifying ==="
cd "$PROJECT_DIR"
uv run python -c "import vllm; print(f'vLLM {vllm.__version__} OK')"
uv run python -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}')"

echo "=== GPU setup complete ==="
echo "Now submit experiments:"
echo "  bsub < scripts/hpc/run_poc.sh"
echo "  bsub < scripts/hpc/run_bfcl.sh"
