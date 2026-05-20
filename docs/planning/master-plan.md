---
title: "Master Plan: SLM Agents Thesis"
category: "project"
lastUpdated: "2026-05-20"
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
| Model-size sweep | CD+Q, PE, CD+Q+ITC, CD+Q+RAG, CD+FT-aligned × 0.5B/1.5B/3B | Done — see `size-sweep-results.md`, `config-ft-aligned-size-sweep.md` |
| Technique isolation ablation | few-shot / CoT / RAG each run without CD, to isolate CD's contribution | Done — see `config-technique-isolation-ablation.md` |
| BFCL multiple + parallel size sweep | CD + CD+FT-aligned × 0.5B/1.5B/3B on multiple + parallel categories | Done — CD: 42/53.5/62%; FT-aligned multiple: 55.5/61/60.5%; parallel: 0% all sizes |
| BFCL multiple + parallel — 7B FT-aligned | CD+FT-aligned 7B on multiple + parallel | Done — multiple **70.5%**, parallel **0.0%** (jobs 28468135/28468136) |
| BFCL parallel_multiple — 7B | CD + CD+FT-aligned 7B on parallel_multiple category | Done — CD: **38.5%**, FT-aligned: **30.5%** (jobs 28468267/28468268) |
| τ-bench size sweep | CD config × 0.5B/1.5B/3B retail domain | Done — 0.5B: 3.48%, 1.5B: 1.74%, 3B: 4.35% (jobs 28461727–29) |
| τ-bench CD+FT-aligned size sweep | CD+FT-aligned merged models × all 4 sizes retail domain | Done — 0.5B: 0%, 1.5B: 3.48%, 3B: 4.35%, 7B: 3.48%; see `tau-bench-retail-results.md` |

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
- [x] Model-size sweep: 0.5B, 1.5B, 3B × 5 configs (issues #48–#52)
- [x] Technique isolation ablation: few-shot / CoT / RAG without CD (issue #64, sub-tasks #60–#62)
- [x] CD+FT-aligned size sweep: 0.5B 59.2%, 1.5B 66.0%, 3B 66.8% (issue #52)
- [x] BFCL multiple + parallel size sweep (0.5B/1.5B/3B) — done; see `size-sweep-results.md`
- [x] BFCL multiple — 7B FT-aligned: 70.5% (job 28468135)
- [x] τ-bench size sweep (0.5B/1.5B/3B) — done; see `tau-bench-retail-results.md`
- [x] τ-bench CD+FT-aligned size sweep (all 4 sizes) — done; see `tau-bench-retail-results.md`
- [x] BFCL parallel — 7B FT-aligned: 0.0% (job 28468136)
- [x] BFCL parallel_multiple — 7B: CD 38.5%, FT-aligned 30.5% (jobs 28468267/28468268)

### Writing (unblocked now)
- [ ] #40 — Deepen discussion chapter with related work connections
- [ ] #55 — Sharpen introduction with final results preview
- [ ] #57 — Update master-plan (this task)
- [ ] Appendix: AI tool usage disclosure (Vancouver Convention)

### Writing (unblocked — all scale-study results in)
- [ ] Results section: multi-category BFCL (multiple/parallel/parallel_multiple) — all results in; ready to write
- [ ] Results section: τ-bench size sweep — fill in from `tau-bench-retail-results.md`
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
| τ-bench user simulator | Same local vLLM instance as agent model | Avoids OpenAI cost; each size-sweep run uses the same model for both agent and user simulator |
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
