# Thesis Status

**Last updated:** 2026-04-11
**Deadline:** 2026-07-05 (12 weeks remaining)

## Research Question

> Which combination of constrained decoding, fine-tuning, and inference optimizations closes the gap between SLMs and large frontier models on agentic benchmarks, while running locally on consumer hardware?

---

## Task

Tool calling evaluated first on BFCL v4 simple_python (single-call). Multi-turn agentic evaluation on t-bench is scope-at-risk given the 12-week budget; see "Priority order" below.

## Models

| Model | Size | Role |
|-------|------|------|
| **Qwen 2.5 7B (AWQ INT4)** | 7B | Primary |
| Qwen3-0.6B | 0.6B | Stretch goal |
| Phi-4 Mini | 3.8B | Stretch goal |

## Methods

| # | Method | Status | Phase | Headline |
|---|--------|--------|-------|----------|
| 0 | Baseline (no guided decoding) | **Done** | Reference | 1.5% (Config B, Job 28142319) |
| 1 | Prompt Engineering / Few-shot | **Done** | No training | 70.25%, −1.75 pp vs CD+Q (Config PE, Job 28148815) |
| 2 | Constrained Decoding | **Done** | No training | 72.75% (Config CD, Job 28142188) |
| 3 | Quantization (AWQ INT4) | **Done** | No training | 72.0%, −0.75 pp vs CD (Config CD+Q, Job 28149459) — 63.5% less VRAM |
| 4 | Inference-Time Compute (CoT) | **Done** | No training | **65.5%, −6.5 pp vs CD+Q** (Config CD+Q+ITC, Job 28187017) — *strongly negative* |
| 5 | RAG | **Not started** | No training | Next Phase 1 config (Issue #7) |
| 6 | LoRA / PEFT | **Not started** | Training | Critical path for the 85% target (Issue #22) |

Knowledge distillation has been dropped from the thesis scope (see `docs/planning/project-plan.md`).

## Experiment Configs (cumulative chain, aligned with project-plan.md)

| Config | Status | BFCL simple_python | Notes |
|--------|--------|--------------------|-------|
| B | **Done** | 1.5% (6/400) | Raw model cannot produce valid JSON |
| CD | **Done** | 72.75% (291/400) | Guided decoding alone |
| CD+Q | **Done** | **72.0% (288/400)** | Baseline for all subsequent configs |
| CD+Q+ITC | **Done** | **65.5% (262/400)** | Strongly negative — CoT argues model into wrong answers |
| CD+Q+RAG | Not started | — | Issue #7 — next run |
| CD+Q+FT | Not started | — | First LoRA run |
| CD+Q+FT+RAG | Not started | — | Full no-training + LoRA stack |

Side configs: PE (70.25%, 281/400) tested as an isolated prompt-engineering comparison vs CD; not in the cumulative chain.

## Running-picture headline

- **No-training ceiling is Config CD+Q at 72.0%.** Two prompt-only techniques (PE −1.75 pp, CoT −6.5 pp) have now *both* regressed against it, the second one with a clean mechanistic explanation: CoT reasoning moves the model toward linguistically natural values and away from BFCL's arbitrary-convention ground truths. Prompt-only interventions cannot close the gap.
- **The 13 pp gap to the 85% target must come from LoRA** (or a different training approach). The rest of the thesis depends on LoRA working.
- **Quantization is effectively free.** AWQ INT4 costs 0.75 pp and fits comfortably on an RTX 4090 (5.2 GiB model memory, 78% VRAM headroom).

## Metrics

- **BFCL simple_python:** AST accuracy (primary)
- **t-bench:** task success rate (planned — scope at risk)
- **Secondary:** failure-mode breakdown, latency, memory, flip analysis (CD+Q vs later configs)

## Frontier Baselines

Two tracks:

1. **Published leaderboard scores** (BFCL v4, accessed April 2026): Claude Opus 4.5 76.83%, Gemini 3 Pro 79.58%, GPT-4.1 72.67%, Claude Sonnet 4.5 72.58%, Claude Haiku 4.5 71.00%. The Qwen 2.5 7B + CD result (72.75%) already matches GPT-4.1 and Claude Sonnet on this single category.
2. **Our own frontier runs** via `src/frontier_backend.py` — GPT and Claude backends implemented, full BFCL runs pending.

See `docs/decisions/frontier-baselines-bfcl.md` for the full table and caveats about why simple_python alone does not predict general agentic capability.

## Success Criteria

| Criterion | Target | Current | Status |
|-----------|--------|---------|--------|
| BFCL simple_python AST accuracy | ≥85% | 72.0% (CD+Q) | No-training ceiling reached; LoRA is the only remaining path |
| Gap to Sonnet 4.5 on t-bench | ≤15% | TBD | Pending; t-bench at risk of being deferred |
| Format validity with CD | <2% errors | ~0.3% | Met |
| Runs on RTX 4090 | 24 GB VRAM | 5.2 GiB (AWQ) | Met — 78% headroom |

---

## Revised Timeline (2026-04-14 → 2026-07-05)

### Phase 1 closeout + writing start (Week 1, Apr 14–20)

- [x] Config B baseline (1.5%)
- [x] Config CD baseline (72.75%)
- [x] Config PE (70.25%, −1.75 pp vs CD+Q)
- [x] Config CD+Q (72.0%, −0.75 pp vs CD — 63.5% less VRAM)
- [x] Config CD+Q+ITC (65.5%, −6.5 pp vs CD+Q — negative)
- [x] Frontier leaderboard baselines referenced; own GPT + Claude backends built
- [ ] **Config CD+Q+RAG** (Issue #7) — closes Phase 1 no-training stack
- [ ] **Methodology chapter outline** — start this week, draft from `docs/decisions/`
- [ ] Full BFCL run of own GPT + Claude backends for the frontier comparison table
- [ ] Supervision meeting 2026-04-13 (online, Nicki)

### Phase 2 LoRA (Weeks 2–4, Apr 21 – May 11)

- [ ] Prepare LoRA training data — Glaive single-turn + BFCL train split (Issue #9)
- [ ] LoRA training pipeline on HPC (Issue #22)
- [ ] Config CD+Q+FT — first LoRA run
- [ ] LoRA hyperparameter iteration (2–3 runs)
- [ ] Config CD+Q+FT+RAG — full stack headline
- [ ] Methodology chapter complete; Results chapter Phase 1 section written

### Phase 3 breadth and analysis (Weeks 5–6, May 12–25)

- [ ] Optional: one additional BFCL category (multi_turn or multiple) for breadth
- [ ] Failure-mode analysis and latency / memory profiling across all configs
- [ ] Cascade escalation-rate analysis per configuration
- [ ] Results chapter Phase 2 section; Discussion chapter started

### Phase 4 writing-only (Weeks 7–12, May 26 – Jul 5)

- [ ] Background chapter finished
- [ ] Discussion chapter (cascade framing, cost analysis, limitations)
- [ ] Conclusion chapter
- [ ] Introduction polish + abstract
- [ ] Full-draft review cycle with Nicki
- [ ] Revisions, figure regeneration, formatting
- [ ] **2026-07-05** — submission

---

## Scope-at-risk (likely deferred or cut)

| Item | Reason |
|------|--------|
| t-bench (Issue #4) | Multi-turn eval is expensive to set up; may be written as future work |
| Additional SLMs (Phi-4 Mini, Llama 3.2, Qwen3-0.6B — Issue #16) | Breadth over depth; LoRA on Qwen 2.5 7B is the contribution |
| Full ablation matrix across all BFCL categories (Issue #24) | Limit to simple_python + one additional category |
| Architecture comparison (MoE, Flash Attention, GQA) | Cite from literature rather than run experiments |
| Pruning | Already discarded as risky in the March 16 slides |

## Key Risks

| Risk | Mitigation |
|------|-----------|
| LoRA training pipeline issues | Start prep in Week 1 (not Week 2); budget 3 weeks |
| LoRA result is disappointing | Start early enough to iterate on training data, hyperparameters, and data source (Glaive → BFCL train → synthetic) |
| Writing falls behind | Write Methodology NOW, Results as experiments complete. Never batch writing to the end. |
| Scope creep | Hard cut list above; revisit weekly |

## Priority order (if time runs short)

1. **Must have:** CD+Q+RAG, CD+Q+FT, CD+Q+FT+RAG, fresh frontier runs on BFCL, complete thesis draft
2. **Should have:** One additional BFCL category for breadth; latency/memory profiling
3. **Nice to have:** t-bench on key configs; additional SLMs

---

## HPC Infrastructure

- **Scheduler:** LSF (`bsub`)
- **GPU queues:** gpua100, gpul40s (primary — runs CD+Q+ITC validated here), gpuv100, gpua10, gpua40, gpuh100
- **Python:** module `python3/3.12.11`
- **CUDA:** module `cuda/12.6.3` (GPU nodes only)
- **Setup:** Two-step — login node (clone repos, basic deps) then GPU node job (vLLM + flash-attn)
- **Scripts:** `scripts/hpc/` — `run_bfcl.sh` (CD), `run_bfcl_no_guided.sh` (B), `run_bfcl_few_shot.sh` (PE), `run_bfcl_quant.sh` (CD+Q), `run_bfcl_itc.sh` (CD+Q+ITC)
- **Environment spec:** `docs/infrastructure/hpc-environment.md`

## Open Questions (for supervision meeting 2026-04-13)

- Is two-out-of-two prompt-only failures enough evidence to commit hard to LoRA as the answer for RQ2?
- τ-bench pulled forward or cut entirely?
- Ceiling gap: is 13 pp realistic on Qwen 2.5 7B with Glaive? Alternative data sources?
- Breadth (more SLMs) vs depth (Qwen-only + training)?
- Methodology chapter writing cadence — start this week or wait for Phase 2?
