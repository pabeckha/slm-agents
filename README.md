# Agents with Small Language Models

DTU Master Thesis investigating which optimization techniques enable Small Language Models (SLMs) to perform reliable tool calling and agentic reasoning on consumer hardware.

## Research Question

> Which combination of constrained decoding, fine-tuning, and inference optimizations closes the gap between SLMs and large frontier models on agentic benchmarks, while running locally on consumer hardware?

## The Problem

Frontier models (Claude Opus, GPT-4) handle tool calling well but require cloud access and are expensive. SLMs (1B-13B parameters) are fast and cheap but fail at structured output: they hallucinate tool names, produce invalid JSON, and mis-reason about arguments.

## Approach

Apply optimization methods incrementally, measuring each one's impact on tool-calling accuracy:

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
thesis/
  small-llms/               # Codebase: constrained decoding and experiments
    src/                     # Implementation
    data/                    # Input/output datasets
    notebooks/               # Experiment notebooks
  methods/                   # One folder per optimization method
    constrained-decoding/
    quantization/
    inference-time-compute/
    rag/
    lora-peft/
    pruning/
    architecture/
  docs/                      # Research, architecture, meeting notes
    research/                # Literature and analysis
    architecture/            # ADRs and design docs
    meetings/                # Supervisor meeting slides
  project_plan/              # Time plan and bibliography
  thesis-written-document/   # LaTeX thesis document
```

## Setup

```bash
cd small-llms
uv sync
```

Requires `HF_TOKEN` environment variable for model access:

```bash
cp .env.example .env  # Add your HuggingFace token
source .env
```

### Run constrained decoding PoC

```bash
cd small-llms
uv run python -m src
```

## Key Documents

- [PRD.md](PRD.md) - Product requirements and experimental design
- [status.md](status.md) - Current progress on all methods
- [docs/implementation-order.md](docs/implementation-order.md) - Method implementation order
- [docs/PRD.md](docs/PRD.md) - Detailed method-level specifications

## Supervisor

Nick (DTU) - meetings tracked in `docs/meetings/`
