#!/bin/sh
### -- Job name --
#BSUB -J github_mcp_eval
### -- GPU queue --
#BSUB -q gpul40s
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 8 CPU cores --
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=20GB]"
#BSUB -M 20GB
### -- Wall time: 2h for B + CD configs --
#BSUB -W 02:00
### -- Output --
#BSUB -o logs/github_mcp_eval_%J.out
#BSUB -eo logs/github_mcp_eval_%J.err
#BSUB -B
#BSUB -N

# GitHub MCP real-world evaluation (issue #36).
# Starts a local vLLM server and runs the evaluation runner for configs B and CD.
# For CDQ (AWQ quantized model), set MODEL to the AWQ variant and CONFIG=CDQ.
#
# Configs evaluated:
#   B   — baseline: no constrained decoding
#   CD  — constrained decoding (guided_choice + guided_json)
#   CDQ — constrained decoding + AWQ quantized model
#
# Usage:
#   bsub < scripts/hpc/run_github_mcp_eval.sh                          # runs B + CD
#   MODEL=Qwen/Qwen2.5-7B-Instruct-AWQ CONFIG=CDQ bsub < ...           # runs CDQ

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

PROJECT_DIR="$HOME/Documents/slm-agents"

[ -f "$HOME/.secrets" ]         && . "$HOME/.secrets"
[ -f "$PROJECT_DIR/.secrets" ]  && . "$PROJECT_DIR/.secrets"

cleanup() {
    [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
CONFIG="${CONFIG:-}"   # empty = run B then CD; set to CDQ for quantized run
VLLM_PORT=8000

case "$MODEL" in
    *-AWQ*|*-awq*) QUANT_FLAGS="--quantization awq_marlin --enforce-eager --dtype auto" ;;
    *)              QUANT_FLAGS="--dtype bfloat16" ;;
esac

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host:   $(hostname)"
echo "Date:   $(date)"
echo "Model:  $MODEL"
echo "Config: ${CONFIG:-B+CD}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

echo "=== Syncing dependencies ==="
uv sync --group hpc

echo "=== Starting vLLM server ==="
uv run --group hpc python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$VLLM_PORT" \
    $QUANT_FLAGS \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.9 \
    &
VLLM_PID=$!

echo "Waiting for vLLM (PID $VLLM_PID)..."
for i in $(seq 1 600); do
    curl -s "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1 && echo "vLLM ready after ${i}s" && break
    kill -0 "$VLLM_PID" 2>/dev/null || { echo "ERROR: vLLM process died"; exit 1; }
    sleep 1
done
curl -s "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1 \
    || { echo "ERROR: vLLM failed to start within 600s"; exit 1; }

echo "=== GPU after model load ==="
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader

EVAL="uv run --group hpc python scripts/eval_github_mcp.py --model $MODEL --vllm-url http://localhost:${VLLM_PORT}/v1"

if [ -z "$CONFIG" ] || [ "$CONFIG" = "B" ]; then
    echo "=== Config B: baseline (no constrained decoding) ==="
    $EVAL --config B
fi

if [ -z "$CONFIG" ] || [ "$CONFIG" = "CD" ]; then
    echo "=== Config CD: constrained decoding ==="
    $EVAL --config CD
fi

if [ "$CONFIG" = "CDQ" ]; then
    echo "=== Config CDQ: constrained decoding + quantized ==="
    $EVAL --config CDQ
fi

echo "=== Done === $(date)"
