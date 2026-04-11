---
title: "Implementation Order — Optimization Methods"
lastUpdated: "2026-04-11"
status: "active"
---

# Implementation Order — Optimization Methods

The methods are ordered by: **no retraining first** (highest signal for lowest effort), then **training-based** improvement on top of a strong baseline.

Knowledge distillation is out of scope for this thesis; see `docs/planning/project-plan.md` for the current plan of record.

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
CD+Q+FT+RAG          + LoRA + RAG (full stack, best expected combo)
  ↓
Compare all vs. Claude Opus / GPT-4.1 / Claude Sonnet on BFCL
```

---

## Related

- [`docs/planning/project-plan.md`](project-plan.md) — plan of record
- [`docs/planning/experiment-spec.md`](experiment-spec.md) — method inventory and success criteria
