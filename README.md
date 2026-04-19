# SLM Agents

DTU Master Thesis investigating which optimization techniques enable Small Language Models
(SLMs) to perform reliable tool calling, framed as expanding the boundary of a cascade
LLM architecture.

## Research Questions

- **RQ1:** What is the baseline gap between SLMs and frontier models on tool calling?
- **RQ2:** What is the marginal contribution of each optimization technique?
- **RQ3:** Is a quantized, fine-tuned SLM viable for production tool calling?

## Approach

A cumulative ablation study over Qwen 2.5 (0.5B, 1.5B, 3B, 7B) across five techniques,
evaluated on BFCL v4 and tau-bench:

| Config | Techniques | Status |
|--------|-----------|--------|
| Config B | Baseline (no optimization) | Done — 1.5% AST accuracy |
| Config CD | + Constrained decoding | Done — 72.75% AST accuracy |
| Config PE | + Few-shot prompting | Done — 70.25% AST accuracy |
| Config CD+Q | + AWQ INT4 quantization | Done — 72.0% AST accuracy |
| Config CD+Q+RAG | + Retrieval-augmented generation | Done |
| Config CD+Q+FT | + LoRA fine-tuning | Running on HPC |

## Key Finding (so far)

Constrained decoding alone closes ~95% of the gap between a raw 7B SLM (1.5%) and
frontier models on BFCL simple\_python. Qwen 2.5 7B + CD (72.75%) matches GPT-4.1
(72.67%) and Claude Sonnet 4.5 (72.58%) on this category.

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
| Background | Draft |
| Methodology | In progress (28 pages total so far) |
| Results | Empty — pending experiment completion |
| Discussion | Empty |
| Conclusion | Empty |

## Running Experiments

All experiments run on DTU HPC (`gbar.dtu.dk`) via LSF. Submit jobs from the login node:

```bash
bsub < scripts/hpc/run_bfcl.sh         # Config CD
bsub < scripts/hpc/run_bfcl_quant.sh   # Config CD+Q
bsub < scripts/hpc/run_bfcl_few_shot.sh # Config PE
bsub < scripts/hpc/run_bfcl_rag.sh     # Config CD+Q+RAG
bsub < scripts/hpc/train_lora.sh        # LoRA training
bsub < scripts/hpc/run_bfcl_ft.sh      # Config CD+Q+FT
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

Niklas Skafte (DTU) — meetings tracked in `docs/meetings/`
