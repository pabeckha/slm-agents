---
title: "Master Plan: SLM Agents Thesis"
category: "project"
lastUpdated: "2026-05-02"
status: "active"
---

# Master Plan: SLM Agents Thesis

Single source of truth for project state.

---

## Experiments

| Config | Description | Status |
|--------|-------------|--------|
| Config B | Baseline, no constrained decoding | Done — 1.5% AST |
| Config CD | + Constrained decoding | Done — 72.75% AST |
| Config PE | + Few-shot prompting | Done — 70.25% AST |
| Config CD+Q | + AWQ INT4 quantization | Done — 72.25% AST |
| Config CD+Q+ITC | + Chain-of-thought | Done — 65.5% AST (negative) |
| Config CD+Q+RAG | + RAG top-5 retrieval | Done — 47.75% AST (negative) |
| Config CD+FT | + LoRA fine-tuning, misaligned format | Done — 69.75% AST |
| Config FT-only | LoRA alone, no CD or Q | Done — 13.75% AST |
| Config FT-aligned-ng | Format-aligned LoRA, no CD | Done — 13.2% AST |
| Config CD+FT-aligned | CD + format-aligned LoRA | Done — **76.8% AST** ← best |
| Config CD+Q+FT | CD + AWQ quant + LoRA (requires QLoRA or post-merge AWQ) | Not started |
| τ-bench CD (retail) | Multi-step agentic, tool-calling, 115 tasks | Done — **4.3% pass rate** |

Full Phase 1 + Phase 2 summary: `docs/decisions/phase1-ablation-summary.md`

---

## Thesis Writing

| Chapter | Status |
|---------|--------|
| 1. Introduction | Draft |
| 2. Background | Draft — "TALK ABOUT AGENTS" section still a stub |
| 3. Methodology | In progress — PE, RAG, LoRA, τ-bench sections still stubs |
| 4. Results | **Empty** — Phase 1 data ready to write now |
| 5. Discussion | Empty |
| 6. Conclusion | Empty |
| Appendix | Not started — AI tool usage disclosure (Vancouver Convention) |

Current page count: ~28 pages. Target: 50–60 pages.

---

## Open Tasks

### Experiments
- [x] FT alone (no CD/Q) — done, 13.75%
- [x] FT-aligned-ng — done, 13.2%
- [x] CD+FT-aligned — done, 76.8%
- [x] τ-bench full run (retail domain) — done, 4.3% pass rate
- [ ] CD+Q+FT: requires QLoRA or post-merge AWQ quantization of merged model
- [ ] Model-size sweep: 0.5B, 1.5B, 3B × CD + B (script ready: `run_bfcl_sweep.sh`)
- [ ] BFCL multiple + parallel categories

### Writing (Methodology remaining)
- [ ] Section: Prompt Engineering and Few-Shot
- [ ] Section: Retrieval-Augmented Generation
- [ ] Section: LoRA Fine-Tuning
- [ ] Section: τ-bench (data in hand — write now)
- [ ] Section: Background — Agents with LLMs stub

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
| LoRA dataset | Local xlam-format JSONL (54k train / 6k val) | Prepared from Salesforce/xlam-function-calling-60k |
| Primary benchmark | BFCL v4 (simple_python + multiple + parallel) | Standard, reproducible, leaderboard for comparison |
| Agentic benchmark | τ-bench (original repo) | Multi-step agent loop, retail + airline domains |
| τ-bench user simulator | gpt-4o-mini (OpenAI) | Sufficient for user simulation, much cheaper than gpt-4o |
| Frontier baseline source | BFCL leaderboard (published scores) | Canonical, avoids API cost |
| Primary GPU queue | gpul40s (L40S 46GB) | Less congested than gpua100 |

---

## Out of Scope (Dropped)

- Pruning — time constraints
- Knowledge distillation — time constraints
- Multiple model families (Phi-4 Mini, Llama 3.2) — narrowed to Qwen 2.5
- CoT/ReAct on single-call BFCL — ITC was a strong negative result; ReAct reserved for τ-bench only

---

## Related Documents

- `status.md` — current state, timeline, success criteria
- `docs/planning/experiment-spec.md` — benchmark and pipeline details
- `docs/decisions/` — per-config result analyses
- `docs/decisions/phase1-ablation-summary.md` — Phase 1 consolidated results
- `thesis/chapters/03_methodology.tex` — methodology chapter
