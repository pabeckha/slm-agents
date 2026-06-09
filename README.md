# SLM Agents

DTU Master Thesis investigating which optimization techniques enable Small Language Models
(SLMs) to perform reliable tool calling, framed as expanding the boundary of a cascade
LLM architecture.

## Research Questions

- **RQ1:** What is the baseline gap between SLMs and frontier models on tool calling?
- **RQ2:** What is the marginal contribution of each optimization technique?
- **RQ3:** Is a quantized, fine-tuned SLM viable for production tool calling?

## Approach

A cumulative ablation study on Qwen 2.5 7B across optimization techniques,
evaluated on BFCL v4 (simple_python, 400 tasks) and τ-bench (retail, 115 tasks).
The 7B table below is the primary result; the key configurations were also run
as a model-size sweep across the full Qwen 2.5 family (0.5B, 1.5B, 3B, 7B).

| Config | Techniques | BFCL AST (7B) |
|--------|-----------|----------|
| B | Baseline (no optimization) | 1.5% |
| CD | + Constrained decoding | 72.75% |
| PE | + Few-shot prompting | 70.25% |
| CD+Q | + AWQ INT4 quantization | 72.25% |
| CD+Q+ITC | + Chain-of-thought | 65.5% |
| CD+Q+RAG | + RAG top-5 retrieval | 47.75% |
| FT-only | LoRA alone, no CD | 13.75% |
| FT-aligned-ng | Format-aligned LoRA, no CD | 13.25% |
| CD+FT | + LoRA (misaligned format) | 69.75% |
| CD+FT-aligned | + LoRA (format-aligned) | **76.75%** |
| CD+Q+FT-aligned | + LoRA (format-aligned) + AWQ INT4 | 74.25% |

τ-bench retail (Config CD): **4.35% pass rate** (mean of 3 runs × 115 tasks) — multi-step agentic baseline.

### Model-size sweep (BFCL simple_python)

The same family was evaluated at four sizes. The unoptimized baseline stays at
1.5–4.75% across all four with no consistent trend, while constrained decoding
lifts every size and scales with model size:

| Size | + Constrained decoding (CD) |
|------|------------------------------|
| 0.5B | 51.5% |
| 1.5B | 62.25% |
| 3B   | 64.75% |
| 7B   | 72.75% |

A τ-bench size sweep and a multi-category BFCL sweep (multiple / parallel /
parallel_multiple) were also run; see [docs/decisions/size-sweep-results.md](docs/decisions/size-sweep-results.md).

## Key Findings

Constrained decoding alone closes ~95% of the gap between a raw 7B SLM (1.5%) and
frontier models on BFCL simple\_python. Qwen 2.5 7B + CD (72.75%) matches GPT-4.1
(72.67%) and Claude Sonnet 4.5 (72.58%).

Format-aligned LoRA fine-tuning pushes past the no-training ceiling: CD+FT-aligned at
**76.75%** comes within 0.08 pp of Claude Opus 4.5 (76.83%) on simple_python and is
the best result in the study. The key was aligning training format exactly to the
inference pipeline — general-purpose xlam training with format mismatch caused a
regression (-3 pp).

## Project Structure

```
src/                  # Constrained decoding pipeline (vLLM backend, prompts, schema)
scripts/              # HPC job scripts, evaluation scripts, LoRA training
data/                 # Input datasets and output results
docs/                 # Decisions, research, planning, meeting notes
thesis/               # LaTeX thesis document (main.tex)
project_plan/         # Formal project plan and bibliography
```

## Thesis Progress

All chapters complete; all experiments done.

| Chapter | Status |
|---------|--------|
| Introduction | Complete |
| Background | Complete |
| Methodology | Complete |
| Results | Complete — all 11 configs, size sweep, τ-bench, multi-category BFCL |
| Discussion | Complete |
| Conclusion | Complete |
| Appendices | Complete — AI disclosure, hyperparameters, full results |

Current: 58 pages (target 40–60, excl. preface and appendix). Deadline: 2026-07-05.
Build verified clean: no undefined references or citations.

## Running Experiments

All experiments run on DTU HPC (`gbar.dtu.dk`) via LSF. Submit jobs from the login node:

```bash
bsub < scripts/hpc/run_bfcl.sh               # Config CD
bsub < scripts/hpc/run_bfcl_quant.sh         # Config CD+Q
bsub < scripts/hpc/run_bfcl_few_shot.sh      # Config PE
bsub < scripts/hpc/run_bfcl_rag.sh           # Config CD+Q+RAG
bsub < scripts/hpc/train_lora_aligned.sh     # LoRA training (format-aligned)
bsub < scripts/hpc/run_bfcl_ft_aligned.sh    # Config CD+FT-aligned
bsub < scripts/hpc/run_tau_bench.sh          # τ-bench retail
```

Monitor jobs:

```bash
bstat
bjobs
tail -f logs/<jobid>.out
```

## Setup

```bash
uv sync --group hpc
```

Requires `HF_TOKEN` for model downloads and `HF_HOME` pointing to scratch storage on HPC.

## Supervisor

Nicki Skafte Detlefsen (DTU) — meetings tracked in `docs/supervision/`
