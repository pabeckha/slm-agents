# Thesis Status

**Last updated:** 2026-04-06
**Deadline:** 2026-07-05 (13 weeks remaining)

## Research Question

> Which combination of constrained decoding, fine-tuning, and inference optimizations closes the gap between SLMs and large frontier models on agentic benchmarks, while running locally on consumer hardware?

---

## Task

ReAct agent loop: reason -> call tool -> observe result -> repeat. Evaluated on BFCL Simple (single-call) and t-bench (multi-step agentic).

## Models

| Model | Size | Role |
|-------|------|------|
| **Qwen 2.5 7B** | 7B | Primary |
| Qwen3-0.6B | 0.6B | Stretch goal |
| Phi-4 Mini | 3.8B | Stretch goal |

## Methods

| # | Method | Status | Phase | Notes |
|---|--------|--------|-------|-------|
| 0 | Baseline | **Done** | Reference | 1.5% AST accuracy (Config B, Job 28142319) |
| 1 | Prompt Engineering / Few-shot | **Done** | No training | 70.25% AST accuracy, -2.5 pp vs CD (Config PE, Job 28148815) |
| 2 | Constrained Decoding | **Done** | No training | 72.75% AST accuracy (Config CD, Job 28142188) |
| 3 | Inference-Time Compute (CoT/ReAct) | **Not started** | No training | Needs hybrid free/constrained decoding mode |
| 4 | RAG | **Not started** | No training | Retrieves relevant tool schemas |
| 5 | Quantization (AWQ INT4) | **Done** | No training | 72.0% AST accuracy, -0.75 pp vs CD, 63.5% less VRAM (Config CD+Q, Job 28149459) |
| 6 | LoRA / PEFT | **Not started** | Training | Highest expected impact |

## Experiment Configs (Ablation)

| Config | What it isolates | Status | BFCL Result |
|--------|-----------------|--------|-------------|
| B | Raw model baseline | **Done** | 1.5% (6/400) |
| PE | Prompt engineering alone | **Done** | 70.25% (281/400) |
| CD | Constrained decoding alone | **Done** | 72.75% (291/400) |
| CD+Q | + Quantization | **Done** | 72.0% (288/400) |
| FT | LoRA alone | Not started | - |
| CD+FT | CD + LoRA compounding | Not started | - |
| CD+Q+FT | + Quantization impact | Not started | - |
| CD+Q+FT+ITC | + CoT/ReAct reasoning | Not started | - |
| CD+Q+FT+RAG | + RAG tool retrieval | Not started | - |
| CD+Q+FT+ITC+RAG | Full stack | Not started | - |

## Metrics

- **BFCL Simple:** AST accuracy (primary)
- **t-bench:** Task success rate (primary)
- **Secondary:** Per-step tool accuracy, failure mode breakdown, latency, memory

## Frontier Baselines

Using published BFCL v4 leaderboard scores (accessed April 2026). Key references:
- Claude Opus 4.5: 76.83% | Claude Sonnet 4.5: 72.58% | GPT-4.1: 72.67% | Gemini 3 Pro: 79.58%
- Our CD config (72.75%) matches GPT-4.1 and Claude Sonnet on Simple Function.
- See `docs/decisions/frontier-baselines-bfcl.md` for full table and caveats.

## Success Criteria

| Criterion | Target | Current | Status |
|-----------|--------|---------|--------|
| BFCL Simple AST accuracy | >=85% | 72.75% (CD) / 72.0% (CD+Q) | Note: BFCL v4 ceiling is ~80%. Target may need revision. |
| Gap to Sonnet 4.6 on t-bench | <=15% | TBD | Pending |
| Format validity with CD | <2% errors | ~0.3% | Met |
| Runs on RTX 4090 | 24GB VRAM | 5.2 GiB (AWQ) | Met — 78% headroom |

---

## Revised Timeline (April 6 - July 5, 2026)

### Phase 1: No-training methods + writing start (Weeks 1-2, Apr 7-20)

- [x] Config B baseline (1.5%)
- [x] Config CD baseline (72.75%)
- [x] Config PE (70.25%, -2.5 pp — few-shot hurts slightly)
- [x] Config CD+Q (72.0%, -0.75 pp — quantization is neutral, 63.5% less VRAM)
- [x] Frontier baselines from BFCL leaderboard (CD matches GPT-4.1 and Claude Sonnet)
- [ ] Start writing Methodology chapter

### Phase 2: LoRA fine-tuning + t-bench (Weeks 3-4, Apr 21 - May 4)

- [ ] Prepare LoRA training data (Glaive + synthetic) -- issue #9
- [ ] LoRA training pipeline on HPC
- [ ] Config FT, CD+FT, CD+Q+FT runs
- [ ] t-bench integration -- issue #4
- [ ] Continue Methodology chapter, start Results sections

### Phase 3: Reasoning + RAG + ablation matrix (Weeks 5-6, May 5-18)

- [ ] CoT/ReAct hybrid decoding mode (free reasoning + constrained tool calls)
- [ ] RAG pipeline for tool schema retrieval -- issue #7
- [ ] Config CD+Q+FT+ITC, CD+Q+FT+RAG, CD+Q+FT+ITC+RAG runs
- [ ] Full ablation matrix on BFCL
- [ ] Draft Results chapter as numbers come in

### Phase 4: Additional models + analysis (Weeks 7-8, May 19 - Jun 1)

- [ ] Run best configs on additional SLMs (Phi-4 Mini, Qwen3-0.6B) -- issue #16
- [ ] t-bench runs on key configs (if not done in Phase 2)
- [ ] Failure mode analysis and statistical tests
- [ ] Finish Results chapter, start Discussion

### Phase 5: Writing (Weeks 9-11, Jun 2-22)

- [ ] Finish Background chapter (currently has placeholder sections)
- [ ] Discussion chapter
- [ ] Conclusion chapter
- [ ] Abstract
- [ ] Polish Introduction

### Phase 6: Review + submission (Weeks 12-13, Jun 23 - Jul 5)

- [ ] Full draft review
- [ ] Revisions and formatting
- [ ] Final submission

---

## Key Risks

| Risk | Mitigation |
|------|-----------|
| LoRA training pipeline issues | Start in Week 3 (not Week 4). Budget 2 weeks. |
| t-bench user simulator needs frontier API key | Sort out API access in Week 2. Can deprioritize if blocked. |
| Writing falls behind | Write methodology NOW, results as experiments complete. Never batch writing to the end. |
| Scope creep (9 configs x 3 models x 2 benchmarks) | Cut additional SLMs and t-bench before cutting BFCL ablation depth. |

## Priority order (if time runs short)

1. **Must have:** Full BFCL ablation (all 9 configs) on Qwen 2.5 7B + frontier baselines + complete thesis
2. **Should have:** t-bench on top 3 configs + 1 additional SLM
3. **Nice to have:** t-bench on all configs + all 3 SLMs

---

## HPC Infrastructure

- **Scheduler:** LSF (bsub), not SLURM
- **GPU queues:** gpua100, gpuv100, gpua10, gpua40, gpul40s
- **Python:** module `python3/3.12.11` (system Python 3.9 too old)
- **CUDA:** module `cuda/12.6.3` (only available on GPU nodes)
- **Setup:** Two-step -- login node (clone repos, basic deps) then GPU node job (vLLM + flash-attn)
- **Scripts:** `scripts/hpc/` -- `run_bfcl.sh` (CD), `run_bfcl_no_guided.sh` (B), `run_bfcl_few_shot.sh` (PE), `run_bfcl_quant.sh` (CD+Q)
- **Environment spec:** `docs/infrastructure/hpc-environment.md`

## Open Questions

- What is the minimum model size that achieves acceptable tool-call accuracy with full optimization?
- Can constrained decoding compensate for a model not fine-tuned on tool-use data?
- ~~Compute resources: what GPU access is available through DTU HPC?~~ Answered: A100, V100, A10, A40, L40S via LSF queues
- LoRA training data: Glaive (single-turn) + small synthetic ReAct traces from frontier API. Budget TBD.
