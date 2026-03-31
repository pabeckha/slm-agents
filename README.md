# SLM Agents

DTU Master Thesis investigating which optimization techniques enable Small Language Models (SLMs) to perform reliable tool calling and agentic reasoning on consumer hardware.

## Research Question

> Which combination of constrained decoding, fine-tuning, and inference optimizations closes the gap between SLMs and large frontier models on agentic benchmarks, while running locally on consumer hardware?

## The Problem

Frontier models (Claude Opus, GPT-4) handle tool calling well but require cloud access and are expensive. SLMs (1B-13B parameters) are fast and cheap but fail at structured output: they hallucinate tool names, produce invalid JSON, and mis-reason about arguments.

## Approach

Each optimization method expands the boundary of what a local SLM can handle reliably in a cascade architecture, reducing dependence on expensive frontier models:

1. **Constrained Decoding** - Force valid JSON output via logit masking (PoC complete, 95%+ accuracy on Qwen3-0.6B)
2. **Quantization** - AWQ INT4 compression for reduced memory/latency
3. **Inference-Time Compute** - CoT and ReAct prompting
4. **RAG** - Runtime tool schema retrieval
5. **LoRA / PEFT** - Fine-tuning on function-calling datasets
6. **Pruning** - Structured model compression
7. **Architecture benchmarking** - Compare pre-trained variants (Flash Attention, MoE)

Evaluated on [BFCL (Berkeley Function Calling Leaderboard)](https://gorilla.cs.berkeley.edu/leaderboard.html) and compared against Claude Opus 4.6 and GPT-4.1.

## Project Structure

```
src/                       # Constrained decoding pipeline
llm_sdk/                   # Model wrapper (Small_LLM_Model)
scripts/                   # HPC job scripts, evaluation scripts
data/                      # Input/output datasets
notebooks/                 # Experiment notebooks
docs/                      # Research, planning, decisions
project_plan/              # Formal project plan and bibliography
thesis/                    # LaTeX thesis document
```

## Setup

```bash
uv sync
```

Requires `HF_TOKEN` environment variable for model access:

```bash
cp .env.example .env  # Add your HuggingFace token
source .env
```

### Run constrained decoding PoC

```bash
uv run python -m src
```

## Supervisor

Nick (DTU) - meetings tracked in `docs/meetings/`
