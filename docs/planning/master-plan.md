---
title: "Master Plan: SLM Agents Thesis"
category: "project"
lastUpdated: "2026-05-16"
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
| Config FT-aligned-ng | Format-aligned LoRA, no CD | Done — 13.25% AST |
| Config CD+FT-aligned | CD + format-aligned LoRA | Done — **76.75% AST** ← best |
| Config CD+Q+FT-aligned | CD + AWQ INT4 + format-aligned LoRA (post-merge AWQ, job 28395175) | Done — **74.25% AST** |
| τ-bench CD (retail) | Multi-step agentic, tool-calling, 115 tasks | Done — **4.35% pass rate** |
| Model-size sweep | CD+Q, PE, CD+Q+ITC, CD+Q+RAG, CD+FT-aligned × 0.5B/1.5B/3B | **Submitted — pending HPC** (issues #48–#52) |
| Technique isolation ablation | few-shot / CoT / RAG each run without CD, to isolate CD's contribution | **Submitted — pending HPC** (issue #64, sub-tasks #60–#62) |

Full result analyses: `docs/decisions/`

---

## Thesis Writing

| Chapter | Status |
|---------|--------|
| 1. Introduction | Draft — needs sharpening with final numbers (#55) |
| 2. Background | Draft |
| 3. Methodology | Complete — 7 configs in eval ladder, all sections written |
| 4. Results | Complete — all 11 configs written; model-size section pending scale-study results |
| 5. Discussion | Draft — related work connections to deepen (#40) |
| 6. Conclusion | Draft |
| Appendix | Not started — AI tool usage disclosure (Vancouver Convention) |

Current page count: ~50 pages. Target: 60–100 pages.

---

## Open Tasks

### Experiments
- [ ] Model-size sweep: 0.5B, 1.5B, 3B × 5 configs — submitted, awaiting results (issues #48–#52)
- [ ] Technique isolation ablation: few-shot / CoT / RAG without CD — submitted, awaiting results (issue #64, sub-tasks #60–#62)
- [ ] CD+FT-aligned size sweep: merge jobs running, eval to follow (issue #52)
- [ ] BFCL multiple + parallel categories (issue #36 — real-world evaluation)

### Writing (unblocked now)
- [ ] #40 — Deepen discussion chapter with related work connections
- [ ] #55 — Sharpen introduction with final results preview
- [ ] #57 — Update master-plan (this task)
- [ ] Appendix: AI tool usage disclosure (Vancouver Convention)

### Writing (blocked on scale-study results)
- [ ] Results section: Model-Size Scaling — fill in once #48–#52 complete
- [ ] Discussion: scaling analysis implications

### Polish (pre-submission)
- [ ] #56 — Full read-through: figures, cross-references, bibliography, config label consistency

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
| CD+Q+FT approach | Post-merge AWQ (autoawq + compatible transformers pin) | QLoRA ruled out; post-merge quantization viable with dependency fix |

---

## Out of Scope (Dropped)

- Pruning — time constraints
- Knowledge distillation — time constraints
- Multiple model families (Phi-4 Mini, Llama 3.2) — narrowed to Qwen 2.5
- CoT/ReAct on single-call BFCL — ITC was a strong negative result; ReAct reserved for τ-bench only

---

## Related Documents

- `docs/planning/experiment-spec.md` — benchmark and pipeline details
- `docs/decisions/` — per-config result analyses
- `docs/decisions/phase1-ablation-summary.md` — Phase 1 consolidated results
- `thesis/chapters/03_methodology.tex` — methodology chapter
