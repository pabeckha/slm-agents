# Thesis Status

**Last updated:** 2026-04-21
**Deadline:** 2026-07-05 (10 weeks remaining)

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
| CD+Q+FT (CD+Q + LoRA) | **Running** | — | Job 28248383 on gpul40s (pos. 123) |
| FT alone (LoRA, no CD) | Not started | — | Needed for ablation |
| CD+FT (CD + LoRA, no Q) | Not started | — | Needed for ablation |

Phase 1 summary: `docs/decisions/phase1-ablation-summary.md`

---

## Running-picture headline

- **No-training ceiling is CD at 72.75% / CD+Q at 72.25%.** Three prompt-only techniques (PE −2.5 pp, CoT −7.25 pp, RAG −24.5 pp) all regressed. The ceiling is confirmed.
- **Constrained decoding is the essential enabler** (+71.25 pp over raw baseline). Without it the model is non-functional for tool calling.
- **AWQ quantization is free** (−0.5 pp, 63.5% less VRAM, fits RTX 4090 at 5.2 GiB).
- **The 12–13 pp gap to the 85% target must come from LoRA.** Pipeline built, training job running.

---

## Agentic Benchmark (τ-bench)

- Harness set up: `vendor/tau-bench` cloned, job script `scripts/hpc/run_tau_bench.sh` ready
- User simulator: `gpt-4o-mini` (OpenAI), API key in project `.secrets`
- Smoke test (3 tasks, retail): **Job 28248389 pending on gpul40s** (pos. 124)
- Full run: pending smoke test validation

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
| BFCL simple_python AST accuracy | ≥85% | 72.25% (CD+Q) | LoRA is the only remaining path |
| Gap to Sonnet 4.5 on τ-bench | ≤15% | TBD | Smoke test running |
| Format validity with CD | <2% errors | ~0.3% | Met |
| Runs on RTX 4090 | 24 GB VRAM | 5.2 GiB (AWQ) | Met — 78% headroom |

---

## Thesis Writing

| Chapter | Status | Notes |
|---------|--------|-------|
| 1. Introduction | Draft | Needs polish after results are final |
| 2. Background | Draft | "TALK ABOUT AGENTS" section still a stub |
| 3. Methodology | In progress | PE, RAG, LoRA, τ-bench sections still stubs |
| 4. Results | **Empty** | Phase 1 data ready to write now |
| 5. Discussion | **Empty** | |
| 6. Conclusion | **Empty** | |
| Appendix | Not started | AI tool usage disclosure (Vancouver Convention) |

Current: ~28 pages. Target: 50–60 pages.

---

## Revised Timeline (2026-04-21 → 2026-07-05)

### Now — Week 2 (Apr 21–27)

- [x] Phase 1 ablation complete (6 configs, all documented)
- [x] LoRA training pipeline built and fixed
- [x] τ-bench harness set up
- [ ] CD+Q+FT result (Job 28248383)
- [ ] τ-bench smoke test validation (Job 28248389)
- [ ] Submit model-size sweep (0.5B, 1.5B, 3B) after queue clears

### Weeks 3–4 (Apr 28 – May 11)

- [ ] LoRA hyperparameter iteration if needed (2–3 runs)
- [ ] FT alone + CD+FT ablation configs
- [ ] τ-bench full run on retail domain
- [ ] Start Results chapter (Phase 1 section)
- [ ] Methodology stubs: PE, RAG, LoRA sections

### Weeks 5–6 (May 12–25)

- [ ] Model-size sweep results and analysis
- [ ] BFCL multiple + parallel categories (breadth)
- [ ] Results chapter Phase 2 section (LoRA results)
- [ ] Discussion chapter started

### Weeks 7–12 (May 26 – Jul 5)

- [ ] Discussion chapter (cascade framing, cost analysis, limitations)
- [ ] Background chapter stub finished
- [ ] Conclusion chapter
- [ ] Introduction polish + abstract
- [ ] Full-draft review with Nicki
- [ ] Revisions, figures, formatting
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
| #22 | LoRA fine-tuning pipeline | In progress |
| #23 | CoT/ReAct hybrid | Keep open for ReAct on τ-bench |
| #24 | Full ablation matrix | 6/9 configs done |
| #26 | Results + Discussion + Conclusion | Not started |
| #4 | τ-bench harness | Smoke test running |
