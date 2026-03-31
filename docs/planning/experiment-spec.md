# Experiment Specification

## Task

ReAct agent loop: the model receives a user request, reasons about it (Thought), calls tools (Action), observes results (Observation), and repeats until the task is done.

## Benchmarks

| Benchmark | Purpose | Primary Metric |
|-----------|---------|---------------|
| **BFCL Simple** | Single-call sanity check | AST accuracy |
| **τ-bench** | Multi-step agentic evaluation | Task success rate |

## Models

| Model | Size | Role |
|-------|------|------|
| **Qwen 2.5 7B** | 7B | Primary model for all experiments |
| Qwen3-0.6B | 0.6B | Small tier (if time permits) |
| Phi-4 Mini | 3.8B | Medium tier (if time permits) |

## Methods

| # | Method | Phase | What it addresses |
|---|--------|-------|-------------------|
| 0 | Baseline (raw model) | Reference | Reference point, no optimization |
| 1 | Prompt Engineering / Few-shot | No training | Cheapest improvement, establishes prompting ceiling |
| 2 | Constrained Decoding | No training | Guarantees valid output structure (JSON, tool names) |
| 3 | Inference-Time Compute (CoT/ReAct) | No training | Improves reasoning in the agent loop |
| 4 | RAG | No training | Retrieves relevant tool schemas, reduces hallucination |
| 5 | Quantization (AWQ INT4) | No training | Fits larger models on consumer hardware |
| 6 | LoRA / PEFT | Training | Teaches tool-calling directly, highest expected impact |

## Experiment Configurations (Ablation)

The experiment design is ablation-style: isolated configs measure individual method impact, combined configs measure compounding effects.

| Config | What it isolates |
|--------|-----------------|
| B | How bad is the raw model? |
| PE | Does prompt engineering alone help? |
| CD | Does constrained decoding alone help? |
| FT | Does LoRA alone help? |
| CD+FT | Do CD and LoRA compound? |
| CD+Q+FT | Does quantization hurt when combined? |
| CD+Q+FT+ITC | Does CoT/ReAct add value on top? |
| CD+Q+FT+RAG | Does RAG add value on top? |
| CD+Q+FT+ITC+RAG | Full stack |

## Pipeline Architecture

Hybrid generation in the agent loop:
- **Free generation** for reasoning (Thought steps)
- **Constrained decoding** activates for tool calls (Action steps) — logit masking forces valid function name and argument structure

This is a redesign from the current single-shot pipeline into a loop that detects the transition from reasoning to tool call and switches decoding mode.

## Metrics

### Primary
- **BFCL Simple:** AST accuracy
- **τ-bench:** Task success rate (binary per task — did the agent complete the user's goal?)

### Secondary
- **Per-step tool accuracy** — at each step, did it pick the right tool with right args?
- **Failure mode breakdown** — wrong tool, wrong args, hallucinated tool, reasoning error, infinite loop
- **Latency** — TTFT, tokens per second
- **Memory footprint** — peak VRAM usage

The failure mode breakdown maps directly to which optimization method addresses which type of error.

## Frontier Baselines

| Model | Role |
|-------|------|
| Claude Sonnet 4.6 | Primary comparison target (mid-tier frontier) |
| GPT-4.1 | Second data point (different provider) |

Run once per benchmark as fixed reference lines. They do not vary across optimization configs.

## Success Criteria

| Criterion | Benchmark | Target |
|-----------|-----------|--------|
| Single-call accuracy | BFCL Simple | ≥85% AST accuracy (best config) |
| Agentic task success | τ-bench | Within 15% of Sonnet 4.6 task success rate (best config) |
| Format validity | Both | <2% invalid tool call format with constrained decoding |
| Hardware constraint | All | Single RTX 4090, 24GB VRAM |

## LoRA Training Data

- **Glaive function-calling dataset** — single-turn tool-call examples
- **Small synthetic set** — multi-turn ReAct traces generated from frontier model API calls (~500-1000 traces). Details TBD when reaching LoRA phase.

## Benchmark Details

### BFCL Simple

- **Repo:** [ShishirPatil/gorilla](https://github.com/ShishirPatil/gorilla) → `berkeley-function-call-leaderboard/`
- **Dataset:** [gorilla-llm/Berkeley-Function-Calling-Leaderboard](https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard) (HuggingFace)
- **Category:** `simple_python` (~400 test cases)
- **Format:** Each test has a user prompt + one function definition → model must produce the correct function call with correct arguments
- **Metric:** AST accuracy — parsed function call compared structurally against ground truth (correct name, correct params, correct values, correct types)
- **Local model integration:** Serve model via vLLM, then run `bfcl generate --skip-server-setup` pointing at the endpoint, followed by `bfcl evaluate`
- **LoRA support:** Native with vLLM backend via `--enable-lora --lora-modules`

```bash
# Install
git clone https://github.com/ShishirPatil/gorilla.git
cd gorilla/berkeley-function-call-leaderboard
pip install -e .[oss_eval_vllm]

# Run (with vLLM serving your model)
bfcl generate --model MODEL_NAME --test-category simple_python --backend vllm --num-gpus 1
bfcl evaluate --model MODEL_NAME --test-category simple_python
```

### τ-bench

- **Repo:** [sierra-research/tau-bench](https://github.com/sierra-research/tau-bench)
- **Paper:** [arXiv 2406.12045](https://arxiv.org/abs/2406.12045)
- **Domains:** `retail` (15 tools, shopping/orders) and `airline` (12 tools, flights/bookings)
- **Format:** A user simulator (LLM) converses with the agent (model under test) over multiple turns. The agent reasons, calls tools, observes results. Success = final database state matches the annotated goal state.
- **Metric:** Task success rate (pass^k for reliability — probability that at least 1 of k trials succeeds)
- **Agent strategies:** `tool-calling`, `act`, `react`, `few-shot` (via `--agent-strategy`)
- **Local model integration:** Serve model via vLLM, then use the built-in `VLLMChatModel` / `VLLMCompletionModel`. Or subclass `ChatModel` and implement `generate_message()`.
- **Note:** The user simulator requires a frontier model API key (e.g., OpenAI). Only the agent under test runs locally.

```bash
# Install
git clone https://github.com/sierra-research/tau-bench && cd tau-bench
pip install -e .

# Run (with vLLM serving your model on port 8000)
python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-7B --port 8000
# Then point tau-bench at localhost:8000
```

## Shared Infrastructure: vLLM

Both benchmarks use vLLM as the standard serving layer for local models. The workflow on DTU HPC:

1. **Start a vLLM server** on a GPU node serving your model (with optional quantization / LoRA adapters)
2. **Run benchmark client** (BFCL or τ-bench) pointing at the vLLM endpoint
3. **Collect results** — scores, logs, failure breakdowns

This means the core infra to build is: **HPC job scripts that launch vLLM + run each benchmark.**

## Implementation Sequence

| Week | Focus | Deliverable |
|------|-------|-------------|
| Week 1 (April) | vLLM serving on HPC + BFCL eval harness + τ-bench setup | Infra ready for experiments |
| Week 2 | Baseline + Prompt Engineering + CD on BFCL | First results, harness validated |
| Week 3 | τ-bench integration + CoT/ReAct + RAG | Agentic eval, no-training methods complete |
| Week 4 | LoRA fine-tuning + Quantization | Training phase complete |
| Week 5 | Ablation runs (all configs × model) | Full experiment matrix |
| Week 6 | Frontier baselines + analysis + writing | Background + Methodology chapters drafted |
