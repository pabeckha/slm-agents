#!/bin/sh
### -- Job name --
#BSUB -J slm_poc
### -- GPU queue --
#BSUB -q gpul40s
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 4 CPU cores --
#BSUB -n 4
#BSUB -R "span[hosts=1]"
### -- 8GB per core (32GB total) --
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time --
#BSUB -W 01:00
### -- Output --
#BSUB -o logs/poc_%J.out
#BSUB -eo logs/poc_%J.err
### -- Notifications --
#BSUB -B
#BSUB -N

# Exit on error
set -e

# Load HPC modules
module load python3/3.12.11
module load cuda/12.6.3

# Project root
PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
nvidia-smi

echo "=== Installing dependencies ==="
uv sync --group hpc

echo "=== Running constrained decoding PoC ==="
uv run --group hpc python -m src --input data/input --output data/output/poc_gpu_results.json

echo "=== Done ==="
echo "Results written to data/output/poc_gpu_results.json"
