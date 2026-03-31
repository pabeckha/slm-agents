---
title: "Project Plan"
lastUpdated: "2026-03-31"
status: "active"
---

# Project Plan: Agents with Small Language Models

## Thesis Framing

Each optimization method expands the boundary of what tasks a local SLM can handle reliably in a cascade architecture, reducing dependence on expensive frontier models. The experiments measure where that boundary sits for each configuration.

## Hardware

| Environment | Specs | Use |
|-------------|-------|-----|
| Local machine | Intel i7-1255U, 8GB RAM, no GPU (WSL2) | Code editing, scripting, small tests |
| DTU HPC cluster | GPU nodes (A100 80GB, V100 32GB, H100 80GB) | All model inference, training, and BFCL evaluation |

Development workflow: edit code locally, submit GPU jobs to DTU HPC via SLURM.

## Current State (2026-03-31)

**Done:**
- Literature review
- PRD and research documents
- Constrained decoding PoC (Qwen3-0.6B, 95%+ tool-call accuracy, 100% valid JSON)
- Project plan document (formal)

**Not started:** Everything else.

---

## Phase 0: HPC Setup (Week 1, April 1-6)

**Goal:** Get the development environment running on DTU HPC so all GPU work can proceed.

| Task | Deliverable |
|------|-------------|
| Set up HPC job scripts (SLURM) for model inference | `scripts/hpc/` with job templates |
| Install dependencies (PyTorch, transformers, vLLM/SGLang) on HPC | Working Python environment on HPC |
| Test constrained decoding PoC runs on HPC GPU node | Verified PoC output matches local results |
| Set up workflow: edit locally, run on HPC | Documented dev workflow |

**Exit criteria:** Can submit GPU jobs and get results back reliably.

---

## Phase 1: Establish Baselines (Weeks 1-3, April 1-20)

**Goal:** Get hard numbers for the unoptimized and CD-only configurations on BFCL.

| Week | Task | Deliverable |
|------|------|-------------|
| 1 | HPC setup (Phase 0) | Working GPU environment |
| 2 | Set up BFCL evaluation pipeline | `scripts/eval_bfcl.py` running end-to-end |
| 2 | Run baseline (B) on all candidate models | Baseline accuracy numbers per model |
| 2 | Run constrained decoding (CD) on all candidate models | CD accuracy numbers per model |
| 3 | Implement quantization (AWQ INT4) | Quantized model artifacts |
| 3 | Run CD+Q on all candidate models | CD+Q accuracy numbers |
| 3 | Pick top 2-3 models based on results | Model selection decision documented |

**Exit criteria:** Baseline, CD, and CD+Q results on BFCL for all candidate models. Top models selected for remaining experiments.

---

## Phase 2: No-Retraining Methods (Weeks 4-5, April 21 - May 4)

**Goal:** Stack inference-time compute and RAG on top of CD+Q baseline.

| Week | Task | Deliverable |
|------|------|-------------|
| 4 | Implement CoT/ReAct prompting strategies | Prompt templates for ITC |
| 4 | Run CD+Q+ITC on selected models | ITC accuracy numbers |
| 4 | Build RAG pipeline for tool schema retrieval | `src/rag/` with embedding + retrieval |
| 5 | Run CD+Q+RAG on selected models | RAG accuracy numbers |
| 5 | Run CD+Q+ITC+RAG combined | Combined accuracy numbers |
| 5 | Analyze Phase 1-2 results, write up findings | Results table, initial analysis |

**Exit criteria:** All no-retraining configurations benchmarked. Clear picture of how far SLMs go without fine-tuning.

---

## Phase 3: Fine-Tuning (Weeks 6-8, May 5 - May 25)

**Goal:** LoRA fine-tuning to push the SLM tier further.

| Week | Task | Deliverable |
|------|------|-------------|
| 6 | Prepare LoRA training pipeline | Training script + data loading |
| 6 | Prepare training data (ToolBench / Glaive function-calling) | Processed dataset |
| 7 | Train LoRA adapters on selected models | Trained adapter weights |
| 7 | Run CD+Q+FT on BFCL | Fine-tuned accuracy numbers |
| 8 | Run CD+Q+FT+RAG (best expected combo) | Combined accuracy numbers |
| 8 | Run frontier baselines (Claude Opus, GPT-4.1, Claude Sonnet) on BFCL | Frontier baseline numbers |

**Exit criteria:** All experiment configurations benchmarked. Head-to-head comparison with frontier models.

---

## Phase 4: Analysis and Architecture Comparison (Weeks 9-10, May 26 - June 8)

**Goal:** Complete the experimental picture.

| Week | Task | Deliverable |
|------|------|-------------|
| 9 | Architecture comparison (Flash Attention, MoE, GQA variants) | Architecture comparison table |
| 9 | Pruning experiments (if time allows) | Pruning results or justification for skipping |
| 9 | Cascade routing analysis: what % of tasks stay local per config? | Escalation rate per configuration |
| 10 | Statistical analysis of all results | Final results tables, significance tests |
| 10 | Latency and memory profiling for all configs | Secondary metrics table |

**Exit criteria:** All data collected. Ready to write.

---

## Phase 5: Thesis Writing (Weeks 7-14, May 12 - June 30)

Writing overlaps with experimentation starting in Week 7.

| Week | Task | Deliverable |
|------|------|-------------|
| 7-8 | Background chapter draft | Background chapter |
| 8-9 | Methodology chapter draft | Methodology chapter |
| 10-11 | Results chapter draft | Results chapter |
| 11-12 | Discussion chapter (cascade framing, cost analysis) | Discussion chapter |
| 12-13 | Introduction, abstract, conclusion | Remaining chapters |
| 13-14 | Review, revisions, final formatting | Submission-ready thesis |

---

## Experiment Configurations (cumulative)

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
CD+Q+FT+RAG          + LoRA + RAG (best expected combo)
  |
Compare all vs. Claude Opus / GPT-4.1 / Claude Sonnet on BFCL
```

Each configuration answers: **"Does this method expand what the SLM tier can handle?"**

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| HPC queue times slow down iteration | Batch multiple experiments per job; run small tests locally on CPU first |
| LoRA training takes longer than expected | Phase 1-2 results are already publishable without fine-tuning |
| BFCL eval pipeline setup is complex | Start Week 2, block everything else on it |
| Candidate models don't fit in GPU memory | Quantization (AWQ INT4) is Week 3; prune model list early |
| Writing falls behind | Overlapping writing with Phase 3-4; background/methodology don't depend on final results |

---

## Success Criteria

- At least one SLM configuration achieves >85% tool call accuracy on BFCL
- The optimized SLM reaches within 10% of Claude Sonnet 4.6 on end-to-end task success
- Constrained decoding reduces argument hallucination rate to <5%
- The best configuration runs on a single RTX 4090 (24GB VRAM)
- Clear demonstration that each method expands the cascade boundary

---

## Related Documents

- [PRD](../../PRD.md)
- [Implementation Order](implementation-order.md)
- [Status](../../status.md)
