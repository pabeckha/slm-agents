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
# Agent model: vLLM-served Qwen2.5-7B (OpenAI-compatible endpoint).
# User simulator: OpenAI gpt-4o-mini (requires OPENAI_API_KEY in env).
#
# Configs:
#   AGENT_STRATEGY: tool-calling | react  (default: tool-calling)
#   ENV:            retail | airline      (default: retail)
#   MODEL:          HuggingFace model ID  (default: Qwen/Qwen2.5-7B-Instruct)
#   END_INDEX:      number of tasks       (default: -1 = all)
#
# Usage:
#   bsub < scripts/hpc/run_tau_bench.sh
#   AGENT_STRATEGY=react bsub < scripts/hpc/run_tau_bench.sh

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

# Required: OPENAI_API_KEY must be set in your HPC environment.
# Add to ~/.bashrc on HPC: export OPENAI_API_KEY=sk-...
if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "ERROR: OPENAI_API_KEY is not set. Add it to your HPC environment."
    exit 1
fi

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
ENV="${ENV:-retail}"
AGENT_STRATEGY="${AGENT_STRATEGY:-tool-calling}"
USER_MODEL="${USER_MODEL:-gpt-4o-mini}"
END_INDEX="${END_INDEX:--1}"
VLLM_PORT=8000

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Agent model: $MODEL"
echo "Agent strategy: $AGENT_STRATEGY"
echo "Environment: $ENV"
echo "User simulator: $USER_MODEL (OpenAI)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

# ── Start vLLM server ────────────────────────────────────────────────
echo "=== Starting vLLM server ==="
uv run --group hpc python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$VLLM_PORT" \
    --dtype bfloat16 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9 \
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

echo "=== GPU memory after model load ==="
nvidia-smi

# ── Run tau-bench ────────────────────────────────────────────────────
# Point litellm at the local vLLM endpoint via OPENAI_API_BASE.
export OPENAI_API_BASE="http://localhost:${VLLM_PORT}/v1"
export OPENAI_API_KEY="vllm-local"  # vLLM accepts any key

LOG_DIR="data/output/tau_bench/${AGENT_STRATEGY}/${ENV}"
mkdir -p "$LOG_DIR"

echo "=== Running tau-bench (strategy=$AGENT_STRATEGY, env=$ENV) ==="
uv run --group hpc python vendor/tau-bench/run.py \
    --agent-strategy "$AGENT_STRATEGY" \
    --env "$ENV" \
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
