# Thesis Status

**Last updated:** 2026-03-31

## Research Question

> Which combination of constrained decoding, fine-tuning, and inference optimizations closes the gap between SLMs and large frontier models on agentic benchmarks, while running locally on consumer hardware?

---

## Methods

| # | Method | Status | Phase | Notes |
|---|--------|--------|-------|-------|
| 1 | Constrained Decoding | **Done** | No retraining | PoC built from scratch on Qwen3-0.6B. 95%+ tool-call accuracy, 100% valid JSON. Full BFCL eval pending. |
| 2 | Quantization | **Not started** | No retraining | AWQ INT4 compression. Measure latency and quality delta on top of CD. |
| 3 | Inference-Time Compute | **Not started** | No retraining | CoT, ReAct prompting. Cheap to test, strong empirical backing. |
| 4 | RAG | **Not started** | No retraining | Retrieve relevant tool schemas at runtime. Reduces hallucination of tool names/args. |
| 5 | LoRA / PEFT | **Not started** | Requires training | Fine-tune on ToolBench / Glaive function-calling data. Highest expected direct impact. |
| 6 | Knowledge Distillation | **Out of scope** | Requires training | CoT traces from Claude Opus. Removed due to API cost, time constraints, and marginal benefit over LoRA alone. |
| 7 | Pruning | **Not started** | Requires training | Risky for instruction-following. Evaluate only after model performs well. |
| 8 | Architecture | **Not started** | Benchmarking only | Compare pre-trained variants (Flash Attention, MoE, GQA). No modifications. |

---

## Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| Literature review | March 2026 | **Done** |
| PRD and research docs | March 2026 | **Done** |
| Constrained decoding PoC | March 2026 | **Done** |
| Full BFCL eval (CD baseline) | Week 1-2 (April) | **Not started** |
| Quantization (AWQ INT4) | Week 1-2 (April) | **Not started** |
| LoRA fine-tuning pipeline | Week 3-4 (April) | **Not started** |
| CD+Q+FT results | Week 4 (April) | **Not started** |
| Background chapter draft | Week 6 | **Not started** |
| Methodology chapter draft | Week 6 | **Not started** |

---

## Experiment Configurations

```
B                    Baseline (no optimization)
  |
CD                   + Constrained Decoding
  |
CD+Q                 + Quantization (AWQ INT4)
  |
CD+Q+ITC             + Inference-Time Compute (CoT / ReAct)
  |
CD+Q+RAG             + RAG (tool-definition retrieval)
  |
CD+Q+FT              + LoRA Fine-tuning
  |
CD+Q+FT+RAG          + LoRA + RAG
  |
Compare all vs. Claude Opus / GPT-4 on BFCL
```

---

## Candidate Models

| Model | Size | Notes |
|-------|------|-------|
| Qwen3-0.6B | 0.6B | Current PoC model |
| Phi-4 Mini | 3.8B | Strong reasoning for size |
| Llama 3.2 | 3B / 8B | Tool-use fine-tuned variants available |
| Qwen 2.5 | 3B / 7B | Strong instruction following |
| Gemma 3 | 4B | Efficient architecture |
| SmolLM2 | 1.7B | Extreme edge case |

---

## Open Questions

- Depth vs. breadth: go deep on 3-4 methods (CD + LoRA + RAG) or cover all with shallower eval?
- Which pruning method degrades tool-call accuracy the least?
- Can constrained decoding compensate for a model not fine-tuned on tool-use data?
- What is the minimum model size that achieves acceptable tool-call accuracy with full optimization?
- Compute resources: what GPU access is available through DTU?
