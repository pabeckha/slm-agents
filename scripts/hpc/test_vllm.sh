#!/bin/sh
### -- Job name --
#BSUB -J slm_vllm_test
### -- GPU queue --
#BSUB -q gpua100
### -- 1 GPU --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- 4 CPU cores --
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
### -- Wall time --
#BSUB -W 01:00
### -- Output --
#BSUB -o logs/vllm_test_%J.out
#BSUB -eo logs/vllm_test_%J.err
#BSUB -B
#BSUB -N

set -e

cleanup() { [ -n "${VLLM_PID:-}" ] && kill "$VLLM_PID" 2>/dev/null && wait "$VLLM_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

module load python3/3.12.11
module load cuda/12.6.3

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"
mkdir -p logs

MODEL="Qwen/Qwen2.5-7B-Instruct"
VLLM_PORT=8000

echo "=== Job info ==="
echo "Job ID: $LSB_JOBID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Model: $MODEL"
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
for i in $(seq 1 180); do
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
    echo "ERROR: vLLM failed to start within 180s"
    kill "$VLLM_PID" 2>/dev/null
    exit 1
fi

# ── Test 1: Basic completion ─────────────────────────────────────────
echo "=== Test 1: Basic completion ==="
curl -sf "http://localhost:${VLLM_PORT}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "'"$MODEL"'",
        "messages": [{"role": "user", "content": "Say hello in one sentence."}],
        "max_tokens": 50
    }' > /tmp/test1_response.json
python3 -m json.tool /tmp/test1_response.json

# ── Test 2: Tool call ────────────────────────────────────────────────
echo "=== Test 2: Tool call ==="
curl -sf "http://localhost:${VLLM_PORT}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "'"$MODEL"'",
        "messages": [{"role": "user", "content": "What is the weather in Paris?"}],
        "tools": [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"}
                    },
                    "required": ["location"]
                }
            }
        }],
        "max_tokens": 200
    }' > /tmp/test2_response.json
python3 -m json.tool /tmp/test2_response.json

# ── Cleanup ──────────────────────────────────────────────────────────
echo "=== Stopping vLLM ==="
kill "$VLLM_PID" 2>/dev/null
wait "$VLLM_PID" 2>/dev/null || true

echo "=== All tests passed ==="
