# Thesis Status

**Last updated:** 2026-06-09
**Deadline:** 2026-07-05
**State:** All experiments complete; thesis written (58 pages); all GitHub issues closed.

## Research Question

> Which combination of constrained decoding, fine-tuning, and inference optimizations closes the gap between SLMs and large frontier models on agentic benchmarks, while running locally on consumer hardware?

---

## Models

| Model | Size | Role |
|-------|------|------|
| **Qwen 2.5 7B (FP16 + AWQ INT4)** | 7B | Primary — all configs |
| Qwen 2.5 3B / 1.5B / 0.5B | 0.5B–3B | Model-size sweep — done |

Phi-4 Mini, Llama 3.2, Qwen3-0.6B dropped. Narrowed to the Qwen 2.5 family only.

---

## Experiment Configs — BFCL simple_python (400 tasks, AST accuracy)

| Config | Accuracy | Notes |
|--------|----------|-------|
| B (no guided decoding) | 1.5% (6/400) | Raw model cannot produce valid JSON |
| CD (constrained decoding) | 72.75% (291/400) | Guided decoding alone — the enabler |
| PE (few-shot + CD) | 70.25% (281/400) | −2.5 pp vs CD |
| CD+Q (CD + AWQ INT4) | 72.25% (289/400) | −0.5 pp vs CD; 63.5% less VRAM |
| CD+Q+ITC (CD+Q + CoT) | 65.5% (262/400) | −7.25 pp vs CD — strongly negative |
| CD+Q+RAG (CD+Q + RAG top-5) | 47.75% (191/400) | −25 pp vs CD — disambiguation failure |
| FT-only (LoRA, no CD/Q) | 13.75% (55/400) | LoRA alone insufficient without CD |
| FT-aligned-ng (format-aligned, no CD) | 13.25% (53/400) | Aligned format breaks unguided eval |
| CD+FT (CD + LoRA, misaligned) | 69.75% (279/400) | −3 pp vs CD — format mismatch |
| **CD+FT-aligned (CD + format-aligned LoRA)** | **76.75% (307/400)** | **Best result — beats no-training ceiling** |
| CD+Q+FT-aligned (CD + AWQ INT4 + format-aligned LoRA) | 74.25% (297/400) | Fine-tuned capability retained at INT4 |

Full ablation summary: `docs/decisions/phase1-ablation-summary.md`

Also complete: model-size sweep (0.5B–7B), τ-bench size sweep, and the multi-category
BFCL sweep (multiple / parallel / parallel_multiple).

---

## Headline findings

- **No-training ceiling confirmed at CD ~72.75%.** Three prompt-only techniques all regressed vs CD (PE −2.5 pp, CoT −7.25 pp, RAG −25 pp).
- **Constrained decoding is the essential enabler** (+71.25 pp over raw baseline). Without it the model is non-functional.
- **AWQ quantization is essentially free** (−0.5 pp, 63.5% less VRAM; 5.2 GiB fits an RTX 4090).
- **Format-aligned LoRA breaks the ceiling**: CD+FT-aligned at **76.75%** is +4.0 pp over CD and within 0.08 pp of Claude Opus 4.5 (76.83%).
- **τ-bench reveals the agentic gap**: despite 72.75% single-call accuracy, multi-step pass rate is only 4.35% — the cascade architecture motivation in one number.

---

## Agentic Benchmark (τ-bench)

- 3 full runs × 115 retail tasks, Config CD (tool-calling strategy, temperature 0.0, seed 42)
- **Pass rate: 4.35%** (mean across 3 runs)
- User simulator: same local vLLM instance (Qwen 2.5 7B), not gpt-4o-mini
- Failure analysis: `docs/decisions/tau-bench-retail-results.md`

---

## Frontier Baselines

BFCL v4 leaderboard (accessed 2026-06-04):

| Model | simple_python |
|-------|--------------|
| Gemini 3 Pro | 79.58% |
| Claude Opus 4.5 | 76.83% |
| **Qwen 2.5 7B + CD+FT-aligned** | **76.75%** |
| **Qwen 2.5 7B + CD** | **72.75%** |
| GPT-4.1 | 72.67% |
| Claude Sonnet 4.5 | 72.58% |
| Claude Haiku 4.5 | 71.00% |

With constrained decoding alone the 7B model matches GPT-4.1 and Sonnet; with
format-aligned LoRA it reaches Opus-level accuracy on simple_python.

---

## Thesis Document

| Chapter | Status |
|---------|--------|
| Abstract | Complete |
| 1. Introduction | Complete |
| 2. Background | Complete |
| 3. Methodology | Complete |
| 4. Results | Complete — all 11 configs, size sweep, τ-bench, multi-category BFCL |
| 5. Discussion | Complete |
| 6. Conclusion | Complete |
| Appendices (AI disclosure, hyperparameters, full results) | Complete |

58 pages (target 40–60, excl. preface and appendix). `latexmk` builds clean: no
undefined references or citations, no float warnings.

---

## GitHub Issues

All issues closed. Final pre-submission cycle:

| # | Title | Status |
|---|-------|--------|
| #56 | Pre-submission polish (figures, cross-refs, bibliography) | Closed (#134) |
| #108–#128 | Thesis review issues (21) | Closed (#130, #133) |

Out of scope / dropped: #36 (real-world MCP evaluation).

---

## HPC Infrastructure

- **Scheduler:** LSF (`bsub`)
- **Primary queue:** `gpul40s` (L40S 46GB) — less congested than gpua100
- **Python:** `python3/3.12.11` | **CUDA:** `cuda/12.6.3`
- **Key scripts:** `scripts/hpc/` — all configs have dedicated job scripts
- **Sweep script:** `scripts/hpc/run_bfcl_sweep.sh` — matrix across models/configs/categories

## Supervisor

Nicki Skafte Detlefsen (DTU) — meetings tracked in `docs/supervision/`.
