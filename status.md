# Thesis Status

**Last updated:** 2026-05-02
**Deadline:** 2026-07-05 (9 weeks remaining)

## Research Question

> Which combination of constrained decoding, fine-tuning, and inference optimizations closes the gap between SLMs and large frontier models on agentic benchmarks, while running locally on consumer hardware?

---

## Models

| Model | Size | Role |
|-------|------|------|
| **Qwen 2.5 7B (FP16 + AWQ INT4)** | 7B | Primary — all Phase 1 configs done |
| Qwen 2.5 3B / 1.5B / 0.5B | 0.5B–3B | Model-size sweep — scripts ready, not yet submitted |

Phi-4 Mini, Llama 3.2, Qwen3-0.6B dropped. Narrowed to Qwen 2.5 family only.

---

## Experiment Configs — BFCL simple_python (400 tasks, AST accuracy)

| Config | Status | Accuracy | Notes |
|--------|--------|----------|-------|
| B (no guided decoding) | **Done** | 1.5% (6/400) | Raw model cannot produce valid JSON |
| PE (few-shot + CD) | **Done** | 70.25% (281/400) | −2.5 pp vs CD |
| CD (constrained decoding) | **Done** | 72.75% (291/400) | Guided decoding alone — the enabler |
| CD+Q (CD + AWQ INT4) | **Done** | 72.25% (289/400) | −0.5 pp vs CD; 63.5% less VRAM |
| CD+Q+ITC (CD+Q + CoT) | **Done** | 65.5% (262/400) | −7.25 pp — strongly negative |
| CD+Q+RAG (CD+Q + RAG top-5) | **Done** | 47.75% (191/400) | −24.5 pp — disambiguation failure |
| FT-only (LoRA, no CD/Q) | **Done** | 13.75% (55/400) | LoRA alone insufficient without CD |
| CD+FT (CD + LoRA, misaligned) | **Done** | 69.75% (279/400) | −3 pp vs CD — format mismatch |
| FT-aligned-ng (format-aligned, no CD) | **Done** | 13.25% (53/400) | Aligned format breaks unguided eval |
| CD+FT-aligned (CD + format-aligned LoRA) | **Done** | **76.75% (307/400)** | **Best result — beats no-training ceiling** |

Full ablation summary: `docs/decisions/phase1-ablation-summary.md`

---

## Running-picture headline

- **No-training ceiling confirmed at CD ~72.75%.** Three prompt-only techniques all regressed (PE −2.5 pp, CoT −7.25 pp, RAG −24.5 pp).
- **Constrained decoding is the essential enabler** (+71.25 pp over raw baseline). Without it the model is non-functional.
- **AWQ quantization is essentially free** (−0.5 pp, 63.5% less VRAM).
- **Format-aligned LoRA breaks the ceiling**: CD+FT-aligned at **76.75%** is +4.0 pp over CD and within 0.08 pp of Claude Opus 4.5 (76.83%).
- **τ-bench reveals the agentic gap**: despite 72.75% single-call accuracy, multi-step pass rate is only 4.3% — the cascade architecture motivation in one number.
- **All planned experiments are complete.** Focus now is thesis writing.

---

## Agentic Benchmark (τ-bench)

- **Done**: 3 full runs × 115 retail tasks, Config CD (tool-calling strategy, temperature 0.0, seed 42)
- **Pass rate: 4.3%** (mean across 3 runs: 4/6/5 tasks passed)
- User simulator: same local vLLM instance (Qwen 2.5 7B), not gpt-4o-mini
- See `docs/decisions/tau-bench-retail-results.md` for failure analysis

---

## Frontier Baselines

Published BFCL v4 leaderboard (accessed April 2026):

| Model | simple_python |
|-------|--------------|
| Claude Opus 4.5 | 76.83% |
| Gemini 3 Pro | 79.58% |
| GPT-4.1 | 72.67% |
| Claude Sonnet 4.5 | 72.58% |
| Claude Haiku 4.5 | 71.00% |
| **Qwen 2.5 7B + CD** | **72.75%** |

The 7B model already matches GPT-4.1 and Sonnet on simple_python with constrained decoding alone.

---

## Success Criteria

| Criterion | Target | Current | Status |
|-----------|--------|---------|--------|
| BFCL simple_python AST accuracy | ≥85% | 76.75% (CD+FT-aligned) | Not met — leaderboard ceiling is ~80% (no model hits 85%) |
| Gap to Sonnet 4.5 on τ-bench | ≤15% | 4.3% vs unknown Sonnet τ-bench | Not evaluated for Sonnet |
| Format validity with CD | <2% errors | ~0.3% | Met |
| Runs on RTX 4090 | 24 GB VRAM | 5.2 GiB (AWQ) | Met — 78% headroom |

Note: the 85% target was set against older BFCL v2/v3 leaderboard numbers. BFCL v4 (July 2025) tightened evaluation — the current leaderboard ceiling is ~80% (Gemini 3 Pro). The 85% target needs revision in the thesis.

---

## Thesis Writing

| Chapter | Status | Notes |
|---------|--------|-------|
| 1. Introduction | Draft | Polish after results final |
| 2. Background | Draft | Agents with LLMs section still a stub |
| 3. Methodology | In progress | PE, RAG, LoRA, τ-bench sections stubs |
| 4. Results | **Empty** | All data in hand — write now |
| 5. Discussion | **Empty** | |
| 6. Conclusion | **Empty** | |
| Appendix | Not started | AI tool usage disclosure (Vancouver Convention) |

Current: ~28 pages. Target: 50–60 pages.

---

## Timeline (2026-05-02 → 2026-07-05)

All experiments complete. Writing is now the only path to submission.

### Weeks 1–2 (May 2–15) — Methodology + Results

- [ ] Methodology: PE, RAG, LoRA, τ-bench sections
- [ ] Background: Agents with LLMs stub
- [ ] Results chapter: Phase 1 (CD, PE, Q, ITC, RAG) + Phase 2 (LoRA ablation)
- [ ] Results chapter: τ-bench section

### Weeks 3–4 (May 16–29) — Discussion

- [ ] Discussion: cascade framing (BFCL vs τ-bench gap)
- [ ] Discussion: cost/size tradeoffs (AWQ neutrality)
- [ ] Discussion: limitations and scope (simple_python only, 85% target revision)

### Weeks 5–8 (Jun 1–28) — Completion + Polish

- [ ] Conclusion chapter
- [ ] Introduction polish + abstract
- [ ] Appendix: AI tool usage disclosure
- [ ] Full-draft review with Nicki
- [ ] Figures, formatting, revisions

### Week 9 (Jun 29 – Jul 5) — Submission buffer

- [ ] **2026-07-05** — submission

---

## HPC Infrastructure

- **Scheduler:** LSF (`bsub`)
- **Primary queue:** `gpul40s` (L40S 46GB) — less congested than gpua100
- **Backup queues:** gpua100, gpuh100 (0 pending when checked)
- **Python:** `python3/3.12.11` | **CUDA:** `cuda/12.6.3`
- **Key scripts:** `scripts/hpc/` — all configs have dedicated job scripts
- **Sweep script:** `scripts/hpc/run_bfcl_sweep.sh` — submits matrix across models/configs/categories

## Open Issues (GitHub)

| # | Title | Status |
|---|-------|--------|
| #22 | LoRA fine-tuning pipeline | Done — CD+FT-aligned 76.75% |
| #23 | CoT/ReAct hybrid | Closed — ITC negative; ReAct on τ-bench deferred |
| #24 | Full ablation matrix | Done — all 10 configs complete |
| #26 | Results + Discussion + Conclusion | **Active — writing phase** |
| #4 | τ-bench harness | Done — 4.3% pass rate, 3 runs |
