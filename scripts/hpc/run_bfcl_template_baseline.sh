#!/bin/sh
### -- Job name --
#BSUB -J bfcl_template_baseline
### -- GPU queue --
#BSUB -q gpul40s
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 4 CPU cores --
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time --
#BSUB -W 02:00
### -- Output --
#BSUB -o logs/bfcl_template_baseline_%J.out
#BSUB -eo logs/bfcl_template_baseline_%J.err
#BSUB -B
#BSUB -N

# Config B-template: BFCL evaluation through the model's NATIVE tool-calling
# chat template (free generation, no guided decoding). Third reference point
# next to Config B (generic prompt, run_bfcl_no_guided.sh) and Config CD
# (guided decoding, run_bfcl_eval.sh):
#
#   B           generic prompt, free generation   -> model-agnostic floor
#   B-template  native template, free generation  -> model-specific, no guarantee
#   CD          generic prompt, guided decoding   -> guaranteed format
#
# Addresses examiner issue 1 (docs/thesis-examiner-issues.md): replaces the
# cited ToLeaP reference point with our own measurement under one harness.

set -e

export HF_HOME="${HF_HOME:-/work3/s242779/huggingface}"

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
CATEGORY="${CATEGORY:-simple_python}"
VLLM_PORT=$((10000 + ${LSB_JOBID:-$$} % 20000))

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Model: $MODEL"
echo "Category: $CATEGORY"
echo "Config: B-template (native chat template, no guided decoding)"
echo "GPU: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"
nvidia-smi

echo "=== Syncing dependencies ==="
uv sync --group hpc

# ── Start vLLM server ────────────────────────────────────────────────
echo "=== Starting vLLM server ==="
uv run --group hpc python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$VLLM_PORT" \
    --dtype auto \
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

SERVED_MODEL=$(curl -s "http://localhost:${VLLM_PORT}/v1/models" \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['data'][0]['id'])" 2>/dev/null)
if [ "$SERVED_MODEL" != "$MODEL" ]; then
    echo "ERROR: server at port ${VLLM_PORT} serves '$SERVED_MODEL', expected '$MODEL'"
    echo "(another job's vLLM server may be answering on this port)"
    exit 1
fi
echo "Verified served model: $SERVED_MODEL"

# ── Run BFCL evaluation (native template, free generation) ──────────
echo "=== Running BFCL evaluation (Config B-template) ==="
uv run --group hpc python -m src.bfcl_adapter \
    --backend vllm-template \
    --model "$MODEL" \
    --category "$CATEGORY" \
    --vllm-url "http://localhost:${VLLM_PORT}/v1" \
    --no-guided \
    --output-dir "data/output/bfcl_template_baseline"

echo "=== Done ==="
echo "Config B-template results in data/output/bfcl_template_baseline/"
echo "Compare against Config B (data/output/bfcl_no_guided/) and"
echo "Config CD (data/output/bfcl/)."
