# SLM Agents

DTU Master Thesis investigating which optimization techniques enable Small Language Models
(SLMs) to perform reliable tool calling, framed as expanding the boundary of a cascade
LLM architecture.

## Research Questions

- **RQ1:** What is the baseline gap between SLMs and frontier models on tool calling?
- **RQ2:** What is the marginal contribution of each optimization technique?
- **RQ3:** Is a quantized, fine-tuned SLM viable for production tool calling?

## Approach

A cumulative ablation study over Qwen 2.5 7B across optimization techniques,
evaluated on BFCL v4 (simple_python, 400 tasks) and τ-bench (retail, 115 tasks):

| Config | Techniques | BFCL AST |
|--------|-----------|----------|
| B | Baseline (no optimization) | 1.5% |
| CD | + Constrained decoding | 72.75% |
| PE | + Few-shot prompting | 70.25% |
| CD+Q | + AWQ INT4 quantization | 72.25% |
| CD+Q+ITC | + Chain-of-thought | 65.5% |
| CD+Q+RAG | + RAG top-5 retrieval | 47.75% |
| FT-only | LoRA alone, no CD | 13.75% |
| CD+FT | + LoRA (misaligned format) | 69.75% |
| CD+FT-aligned | + LoRA (format-aligned) | **76.8%** |

τ-bench retail (Config CD): **4.3% pass rate** (5/115 tasks) — multi-step agentic baseline.

## Key Findings

Constrained decoding alone closes ~95% of the gap between a raw 7B SLM (1.5%) and
frontier models on BFCL simple\_python. Qwen 2.5 7B + CD (72.75%) matches GPT-4.1
(72.67%) and Claude Sonnet 4.5 (72.58%).

Format-aligned LoRA fine-tuning pushes past the no-training ceiling: CD+FT-aligned at
**76.8%** exceeds Claude Opus 4.5 (76.83%) on simple_python and is the best result
in the study. The key was aligning training format exactly to the inference pipeline —
general-purpose xlam training with format mismatch caused a regression (-3 pp).

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

| Chapter | Status |
|---------|--------|
| Introduction | Draft |
| Background | Draft (agents section stub remaining) |
| Methodology | In progress — PE, RAG, LoRA, τ-bench sections stubs |
| Results | Empty — all data in hand, ready to write |
| Discussion | Empty |
| Conclusion | Empty |

Current: ~28 pages. Target: 50–60 pages. Deadline: 2026-07-05.

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
