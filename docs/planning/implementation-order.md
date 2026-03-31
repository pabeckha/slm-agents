---
title: "Implementation Order — Optimization Methods"
lastUpdated: "2026-03-12"
status: "active"
---

# Implementation Order — Optimization Methods

The methods are ordered by: **no retraining first** (highest signal for lowest effort), then **training-based** improvements on top of a strong baseline, then **benchmarking only**.

---

## Phase 1 — No retraining, highest impact first

| # | Method | Folder | Rationale |
|---|---|---|---|
| 1 | **Constrained Decoding** | `methods/constrained-decoding` | Core thesis claim — PoC done. Run full BFCL eval to establish the baseline. |
| 2 | **Quantization** | `methods/quantization` | No retraining — compress the model (AWQ INT4). Establishes the CD+Q baseline. |
| 3 | **Inference-Time Compute** | `methods/inference-time-compute` | No retraining — CoT, ReAct prompting. Cheap to test, strong empirical backing. |
| 4 | **RAG** | `methods/rag` | No retraining — retrieve tool schemas at runtime. Reduces hallucination of tool names/args. |

## Phase 2 — Requires training

| # | Method | Folder | Rationale |
|---|---|---|---|
| 5 | **LoRA / PEFT** | `methods/lora-peft` | Highest direct impact — teaches the model the exact JSON schema and tool-call decision logic. |
| 6 | **Knowledge Distillation** | `methods/knowledge-distilation` | CoT traces from Claude Opus. Builds on the LoRA setup already in place. |
| 7 | **Pruning** | `methods/pruning` | Risky — can degrade instruction-following. Evaluate only after the model is already performing well. |

## Phase 3 — Benchmarking only

| # | Method | Folder | Rationale |
|---|---|---|---|
| 8 | **Architecture** | `methods/architecture` | Pre-trained variants only (Flash Attention, MoE, GQA). Compare, don't modify. |

---

## Experiment Configs (cumulative)

```
B                    Baseline (no optimization)
  ↓
CD                   + Constrained Decoding
  ↓
CD+Q                 + Quantization (AWQ INT4)
  ↓
CD+Q+ITC             + Inference-Time Compute (CoT / ReAct)
  ↓
CD+Q+RAG             + RAG (tool-definition retrieval)
  ↓
CD+Q+FT              + LoRA Fine-tuning
  ↓
CD+Q+KD              + Knowledge Distillation
  ↓
CD+Q+FT+KD           + LoRA + Distillation
  ↓
CD+Q+FT+KD+RAG       Full stack (best expected combo)
  ↓
Compare all vs. Claude Opus / GPT-4 on BFCL
```

---

## Related

- [`docs/PRD.md`](PRD.md) — full experimental design and success criteria
- `methods/` — one folder per method
