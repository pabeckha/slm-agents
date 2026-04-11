# HPC Environment Specification

**Recorded:** 2026-04-06
**Cluster:** DTU HPC (gbar.dtu.dk)
**Purpose:** Reproducibility documentation for thesis experiments

## Operating System

- **OS:** AlmaLinux 9.7 (Moss Jungle Cat)
- **Kernel:** 6.1.166-1.el9.elrepo.x86_64
- **Scheduler:** LSF (bsub/bjobs/bkill)

## Software Modules (GPU nodes)

| Module | Version |
|--------|---------|
| Python | 3.12.11 (module `python3/3.12.11`) |
| CUDA | 12.6.3 (module `cuda/12.6.3`) |
| System Python | 3.9.25 (login node only, too old for vLLM) |

## Package Manager

- **uv:** 0.5.13
- **Dependencies:** managed via `pyproject.toml` + `uv.lock`
- **Dependency groups:** `hpc` (vLLM, transformers, bfcl-eval)

## Key Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| vllm | 0.8.5 | Model serving + guided decoding |
| transformers | >=4.40, <5 | Tokenizer, model loading |
| openai | >=1.0 | vLLM OpenAI-compatible API client |
| pydantic | >=2.0 | Schema definitions |
| bfcl-eval | vendored | BFCL evaluation framework |

## GPU Hardware Used

### NVIDIA A100 80GB PCIe (gpua100 queue)
- **Driver:** 595.58.03
- **CUDA Version:** 13.2
- **VRAM:** 80 GB
- **Used for:** Config B (Job 28142319), Config CD (Job 28142188), Config PE (Job 28148815)

### NVIDIA L40S (gpul40s queue)
- **Driver:** 595.58.03
- **CUDA Version:** 13.2
- **VRAM:** 46 GB
- **Used for:** Config CD+Q AWQ attempts (Jobs 28149085, 28149324)

### Available queues

| Queue | GPU | VRAM |
|-------|-----|------|
| gpua100 | NVIDIA A100 | 40/80 GB |
| gpuv100 | NVIDIA V100 | 32 GB |
| gpua40 | NVIDIA A40 | 48 GB |
| gpul40s | NVIDIA L40S | 46 GB |
| gpua10 | NVIDIA A10 | 24 GB |
| gpuh100 | NVIDIA H100 | 80 GB |

## vLLM Server Configuration

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --port 8000 \
    --dtype auto \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9
```

### Full-precision model (Config B, CD, PE)
- **Model:** Qwen/Qwen2.5-7B-Instruct
- **dtype:** auto (bfloat16)
- **Model memory:** 14.25 GiB
- **torch.compile time:** ~36 seconds
- **Graph capture:** ~27 seconds, 0.45 GiB
- **KV cache:** 953,936 tokens
- **Avg prompt throughput:** ~700 tokens/s
- **Avg generation throughput:** ~47 tokens/s

### Quantized model (Config CD+Q)
- **Model:** Qwen/Qwen2.5-7B-Instruct-AWQ
- **Quantization:** AWQ INT4 (awq_marlin backend)
- **dtype:** auto (float16)
- **Expected model memory:** ~4-5 GiB

## Inference Parameters

| Parameter | Value |
|-----------|-------|
| temperature | 0 |
| max_tokens (function selection) | 50 |
| max_tokens (argument extraction) | 512 |
| guided_choice | enabled (function selection) |
| guided_json | enabled (argument extraction) |

## Job Resource Requests

```bash
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -n 4              # 4 CPU cores
#BSUB -R "rusage[mem=8GB]"  # 8 GB per core (32 GB total)
#BSUB -M 8GB
#BSUB -W 02:00          # 2 hour wall time
```

## Storage

- **Home directory:** 30 GB quota (shared across all usage)
- **HuggingFace cache:** ~/.cache/huggingface/hub/
- **Scratch:** /work3/s242779/ (pending request)

## Reproducing an Experiment

```bash
# 1. SSH to login node
ssh s242779@gbarlogin1.gbar.dtu.dk

# 2. Navigate to project
cd ~/Documents/slm-agents

# 3. Submit a job (example: Config CD)
bsub < scripts/hpc/run_bfcl.sh

# 4. Monitor
bjobs
tail -f logs/bfcl_<JOBID>.out

# 5. Results appear in
# data/output/bfcl/scores/simple_python_scores.json
```
