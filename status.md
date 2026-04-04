# Thesis Status

**Last updated:** 2026-04-03

## Research Question

> Which combination of constrained decoding, fine-tuning, and inference optimizations closes the gap between SLMs and large frontier models on agentic benchmarks, while running locally on consumer hardware?

---

## Task

ReAct agent loop: reason → call tool → observe result → repeat. Evaluated on BFCL Simple (single-call) and τ-bench (multi-step agentic).

## Models

| Model | Size | Role |
|-------|------|------|
| **Qwen 2.5 7B** | 7B | Primary |
| Qwen3-0.6B | 0.6B | Stretch goal |
| Phi-4 Mini | 3.8B | Stretch goal |

## Methods

| # | Method | Status | Phase | Notes |
|---|--------|--------|-------|-------|
| 0 | Baseline | **Not started** | Reference | Raw model, no optimization |
| 1 | Prompt Engineering / Few-shot | **Not started** | No training | Cheapest improvement |
| 2 | Constrained Decoding | **PoC done** | No training | 95%+ accuracy on Qwen3-0.6B (single-shot). Needs redesign for ReAct hybrid mode. |
| 3 | Inference-Time Compute (CoT/ReAct) | **Not started** | No training | Improves reasoning in agent loop |
| 4 | RAG | **Not started** | No training | Retrieves relevant tool schemas |
| 5 | Quantization (AWQ INT4) | **Not started** | No training | Fits larger models on hardware |
| 6 | LoRA / PEFT | **Not started** | Training | Highest expected impact |

## Experiment Configs (Ablation)

| Config | What it isolates |
|--------|-----------------|
| B | Raw model baseline |
| PE | Prompt engineering alone |
| CD | Constrained decoding alone |
| FT | LoRA alone |
| CD+FT | CD + LoRA compounding |
| CD+Q+FT | + Quantization impact |
| CD+Q+FT+ITC | + CoT/ReAct reasoning |
| CD+Q+FT+RAG | + RAG tool retrieval |
| CD+Q+FT+ITC+RAG | Full stack |

## Metrics

- **BFCL Simple:** AST accuracy (primary)
- **τ-bench:** Task success rate (primary)
- **Secondary:** Per-step tool accuracy, failure mode breakdown, latency, memory

## Frontier Baselines

Claude Sonnet 4.6, GPT-4.1 (fixed reference lines)

## Success Criteria

- ≥85% AST accuracy on BFCL Simple (best config)
- Within 15% of Sonnet 4.6 on τ-bench (best config)
- <2% format errors with constrained decoding
- Runs on single RTX 4090 (24GB VRAM)

---

## Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| Literature review | March 2026 | **Done** |
| PRD and research docs | March 2026 | **Done** |
| Constrained decoding PoC (single-shot) | March 2026 | **Done** |
| Experiment spec | March 2026 | **Done** |
| vLLM serving on HPC + BFCL eval + τ-bench setup | Week 1 (April) | **In progress** |
| Baseline + PE + CD on BFCL | Week 2 (April) | **Not started** |
| τ-bench integration + CoT/ReAct + RAG | Week 3 (April) | **Not started** |
| LoRA fine-tuning + Quantization | Week 4 (April) | **Not started** |
| Ablation runs (all configs × model) | Week 5 (May) | **Not started** |
| Frontier baselines + analysis + writing | Week 6 (May) | **Not started** |

---

## HPC Infrastructure

- **Scheduler:** LSF (bsub), not SLURM
- **GPU queues:** gpua100, gpuv100, gpua10, gpua40, gpul40s
- **Python:** module `python3/3.12.11` (system Python 3.9 too old)
- **CUDA:** module `cuda/12.6.3` (only available on GPU nodes)
- **Setup:** Two-step — login node (clone repos, basic deps) then GPU node job (vLLM + flash-attn)
- **Scripts:** `scripts/hpc/setup_bfcl.sh` (login), `setup_gpu.sh` (GPU), `run_poc.sh`, `run_bfcl.sh`
- **GitHub issue:** #1 — HPC infrastructure setup & BFCL baseline evaluation

## Open Questions

- What is the minimum model size that achieves acceptable tool-call accuracy with full optimization?
- Can constrained decoding compensate for a model not fine-tuned on tool-use data?
- ~~Compute resources: what GPU access is available through DTU HPC?~~ Answered: A100, V100, A10, A40, L40S via LSF queues
- LoRA training data: Glaive (single-turn) + small synthetic ReAct traces from frontier API. Budget TBD.
