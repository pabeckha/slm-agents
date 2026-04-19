---
title: "Master Plan: SLM Agents Thesis"
category: "project"
lastUpdated: "2026-04-19"
status: "active"
---

# Master Plan: SLM Agents Thesis

Single source of truth for project state.

---

## Experiments

| Config | Description | Status |
|--------|-------------|--------|
| Config B | Baseline, no optimization | Done — 1.5% AST |
| Config CD | + Constrained decoding | Done — 72.75% AST |
| Config PE | + Few-shot prompting | Done — 70.25% AST |
| Config CD+Q | + AWQ INT4 quantization | Done — 72.0% AST |
| Config CD+Q+RAG | + RAG | Done — see results doc |
| Config CD+Q+FT | + LoRA fine-tuning | Running on HPC (job 28236720) |

Next: run all configs across 4 model sizes (0.5B, 1.5B, 3B, 7B) once 7B results
are complete. Then run BFCL multiple_function and parallel_function categories.
Tau-bench planned after ablation matrix is complete.

---

## Thesis Writing

| Chapter | Status |
|---------|--------|
| 1. Introduction | Draft |
| 2. Background | Draft |
| 3. Methodology | In progress — hardware, eval framework, models, baseline, CD, quantization done; PE, RAG, LoRA, tau-bench stubs remain |
| 4. Results | Empty — waiting for experiment completion |
| 5. Discussion | Empty |
| 6. Conclusion | Empty |

Current page count: ~28 pages. Target: 50-60 pages.

---

## Open Tasks

### Experiments
- [ ] Wait for CD+Q+FT LoRA job to complete
- [ ] Run ablation matrix across all 4 model sizes
- [ ] Run BFCL multiple_function and parallel_function categories
- [ ] Set up and run tau-bench

### Writing (Methodology remaining)
- [ ] Section: Prompt Engineering and Few-Shot
- [ ] Section: Retrieval-Augmented Generation
- [ ] Section: LoRA Fine-Tuning
- [ ] Section: tau-bench (after running it)

### Writing (Pending experiments)
- [ ] Chapter 4: Results
- [ ] Chapter 5: Discussion
- [ ] Chapter 6: Conclusion
- [ ] Appendix: AI tool usage disclosure (Vancouver Convention)

---

## Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Model family | Qwen 2.5 (0.5B–7B) | Single architecture, full size range, AWQ variants available |
| Inference stack | vLLM 0.8.5 | Guided decoding, HuggingFace compatible |
| Quantization method | AWQ INT4 (awq_marlin) | Best accuracy/compression tradeoff, pre-quantized available |
| LoRA dataset | Salesforce/xlam-function-calling-60k | Large, high-quality, function-calling specific |
| Primary benchmark | BFCL v4 (simple_python + multiple + parallel) | Standard, reproducible, leaderboard for comparison |
| Agentic benchmark | tau-bench | Multi-step agent loop, retail + airline domains |
| Frontier baseline source | BFCL leaderboard (published scores) | Canonical, avoids API cost |
| GPU | A100 80GB (gpua100) | All experiments on same hardware for comparability |

---

## Out of Scope (Dropped)

- Pruning — time constraints
- Knowledge distillation — time constraints
- Multiple model families (Phi-4 Mini, Llama 3.2) — narrowed to Qwen 2.5

---

## Related Documents

- `docs/planning/PRD.md` — research questions, results, success criteria
- `docs/planning/experiment-spec.md` — benchmark and pipeline details
- `docs/decisions/` — per-config result analyses
- `thesis/chapters/03_methodology.tex` — methodology chapter
