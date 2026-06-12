#!/bin/sh
### -- Job name --
#BSUB -J tau_bench
### -- GPU queue --
#BSUB -q gpul40s
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 8 CPU cores (vLLM + tau-bench runner) --
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=16GB]"
#BSUB -M 16GB
### -- Wall time: 4h for full retail test split --
#BSUB -W 04:00
### -- Output --
#BSUB -o logs/tau_bench_%J.out
#BSUB -eo logs/tau_bench_%J.err
#BSUB -B
#BSUB -N

# tau-bench evaluation: multi-step agentic benchmark (retail + airline domains).
# Agent model: vLLM-served Qwen2.5-7B (OpenAI-compatible endpoint at localhost).
# User simulator: same local vLLM by default (set USER_MODEL_PROVIDER=openai and
#   add a real OPENAI_API_KEY to ~/.secrets to use gpt-4o-mini instead).
#
# Configs:
#   AGENT_STRATEGY:    tool-calling | react  (default: tool-calling)
#   TBENV:             retail | airline      (default: retail)
#   MODEL:             HuggingFace model ID  (default: Qwen/Qwen2.5-7B-Instruct)
#   USER_MODEL:        user-sim model        (default: same as MODEL)
#   END_INDEX:         number of tasks       (default: -1 = all)
#
# Usage:
#   bsub < scripts/hpc/run_tau_bench.sh
#   AGENT_STRATEGY=react bsub < scripts/hpc/run_tau_bench.sh

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

PROJECT_DIR="$HOME/Documents/slm-agents"

# Load API keys from ~/.secrets or project .secrets if present.
[ -f "$HOME/.secrets" ] && . "$HOME/.secrets"
[ -f "$PROJECT_DIR/.secrets" ] && . "$PROJECT_DIR/.secrets"

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
TBENV="${TBENV:-retail}"
AGENT_STRATEGY="${AGENT_STRATEGY:-tool-calling}"
# Default: route user simulator through the same local vLLM (no real API key needed).
USER_MODEL="${USER_MODEL:-$MODEL}"
END_INDEX="${END_INDEX:--1}"
VLLM_PORT=$((10000 + ${LSB_JOBID:-$$} % 20000))

# Auto-detect quantization from model name.
case "$MODEL" in
    *-AWQ*|*-awq*) QUANT_FLAGS="--quantization awq_marlin --enforce-eager --dtype auto" ;;
    *)              QUANT_FLAGS="--dtype bfloat16" ;;
esac

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Agent model: $MODEL"
echo "Agent strategy: $AGENT_STRATEGY"
echo "Environment: $TBENV"
echo "User simulator: $USER_MODEL (local vLLM)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

# ── Start vLLM server ────────────────────────────────────────────────
echo "=== Starting vLLM server ==="
uv run --group hpc python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$VLLM_PORT" \
    $QUANT_FLAGS \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.9 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    &
VLLM_PID=$!

echo "Waiting for vLLM server (PID $VLLM_PID) ..."
for i in $(seq 1 1800); do
    if curl -s "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
        echo "vLLM ready after ${i}s"
        break
    fi
    if ! kill -0 "$VLLM_PID" 2>/dev/null; then
        echo "ERROR: vLLM process died"
        exit 1
    fi
    sleep 1
done

if ! curl -s "http://localhost:${VLLM_PORT}/health" > /dev/null 2>&1; then
    echo "ERROR: vLLM failed to start within 1800s"
    exit 1
fi

SERVED_MODEL=$(curl -s "http://localhost:${VLLM_PORT}/v1/models" \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['data'][0]['id'])" 2>/dev/null)
if [ "$SERVED_MODEL" != "$MODEL" ]; then
    echo "ERROR: server at port ${VLLM_PORT} serves '$SERVED_MODEL', expected '$MODEL'"
    echo "(another job's vLLM server may be answering on this port)"
    exit 1
fi
echo "Verified served model: $SERVED_MODEL"

echo "=== GPU memory after model load ==="
nvidia-smi

# ── Run tau-bench ────────────────────────────────────────────────────
# Both agent and user-sim route through local vLLM via OPENAI_API_BASE.
export OPENAI_API_BASE="http://localhost:${VLLM_PORT}/v1"
export OPENAI_API_KEY="${OPENAI_API_KEY:-vllm-local}"

LOG_DIR="data/output/tau_bench/${AGENT_STRATEGY}/${TBENV}"
mkdir -p "$LOG_DIR"

echo "=== Running tau-bench (strategy=$AGENT_STRATEGY, env=$TBENV) ==="
uv run --group hpc python vendor/tau-bench/run.py \
    --agent-strategy "$AGENT_STRATEGY" \
    --env "$TBENV" \
    --model "$MODEL" \
    --model-provider openai \
    --user-model "$USER_MODEL" \
    --user-model-provider openai \
    --user-strategy llm \
    --task-split test \
    --end-index "$END_INDEX" \
    --max-concurrency 1 \
    --log-dir "$LOG_DIR" \
    --temperature 0.0 \
    --seed 42

echo "=== Done ==="
echo "Results in $LOG_DIR"
