#!/bin/bash
# Setup step 1 — runs on the login node (no GPU needed).
# Clones BFCL repo and installs non-GPU deps.
set -e

module load python3/3.12.11

echo "Python: $(python3 --version)"

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"

echo "=== Creating virtual environment with system Python 3.12 ==="
uv venv --python $(which python3)
uv sync

echo "=== Cloning Gorilla (BFCL) ==="
mkdir -p vendor
cd vendor

if [ -d "gorilla" ]; then
    echo "Gorilla already cloned, pulling latest..."
    cd gorilla && git pull && cd ..
else
    git clone https://github.com/ShishirPatil/gorilla.git
fi

echo "=== Login node setup complete ==="
echo ""
echo "Next: submit the GPU setup job to install vLLM + BFCL on a GPU node:"
echo "  bsub < scripts/hpc/setup_gpu.sh"
