# Phase 1 Ablation Summary — Qwen 2.5 7B on BFCL Simple Python

**Date compiled**: 2026-04-24; last updated 2026-05-10 (size sweep 0.5B/1.5B/3B added)
**Benchmark**: BFCL v4 simple_python (400 test cases, AST accuracy)
**Model family**: Qwen/Qwen2.5-7B-Instruct (FP16), Qwen/Qwen2.5-7B-Instruct-AWQ (INT4), and LoRA merged (bfloat16)
**Infrastructure**: DTU HPC (A100 40GB, L40S 46GB)

> **Size sweep across 0.5B–7B**: see `size-sweep-results.md` for per-size accuracy on all Phase 1 configs. Key finding: CD is essential at every size; AWQ penalty decreases with size; PE helps ≤3B but hurts 7B; ITC and RAG are harmful at every size.

## Results

| Config | Description | Model | Accuracy | Correct | Delta vs CD |
|--------|-------------|-------|----------|---------|-------------|
| B | No constrained decoding | 7B FP16 | 1.5% | 6/400 | -71.25 pp |
| PE | Constrained decoding + few-shot (3 examples) | 7B FP16 | 70.25% | 281/400 | -2.5 pp |
| CD | Constrained decoding only | 7B FP16 | **72.75%** | 291/400 | baseline |
| CD+Q | Constrained decoding + AWQ INT4 | 7B INT4 | 72.25% | 289/400 | -0.5 pp |
| CD+Q+ITC | CD+Q + chain-of-thought reasoning | 7B INT4 | 65.5% | 262/400 | -7.25 pp |
| CD+Q+RAG | CD+Q + FAISS top-5 tool retrieval | 7B INT4 | 47.75% | 191/400 | -25 pp |
| FT-only | LoRA merged, no constrained decoding | 7B bf16 | 13.75% | 55/400 | -59 pp |
| CD+FT | Constrained decoding + LoRA merged (misaligned) | 7B bf16 | 69.75% | 279/400 | -3 pp |
| FT-aligned-ng | Format-aligned LoRA, no constrained decoding | 7B bf16 | 13.25% | 53/400 | -59.5 pp |
| **CD+FT-aligned** | **Constrained decoding + format-aligned LoRA** | **7B bf16** | **76.75%** | **307/400** | **+4.0 pp** |
| CD+Q+FT-aligned | CD + AWQ INT4 + format-aligned LoRA | 7B INT4 merged | 74.25% | 297/400 | +1.5 pp |

## Key findings

### 1. Constrained decoding is the essential enabler (+71.25 pp)

Without guided decoding, 98.5% of outputs fail. The dominant failure mode is malformed JSON — the model produces multiple JSON objects, wraps output in conversational text, or generates pure natural language. Only 6/400 responses happened to produce parseable, valid single-object JSON.

With constrained decoding (`guided_choice` for function selection, `guided_json` for argument extraction), every response is structurally valid. The 71.25 pp gap is almost entirely a format compliance gap, not a reasoning gap.

### 2. AWQ quantization is essentially neutral (-0.5 pp)

INT4 AWQ reduces model memory from 14.25 GiB to 5.20 GiB (63.5% reduction) with only 0.5 pp accuracy loss. This falls within run-to-run noise. The failure distribution does not change — no new error modes introduced.

This validates using CD+Q as the base configuration for all subsequent Phase 2 (LoRA) experiments.

### 3. Prompt-only interventions cannot close the semantic gap

Both PE and ITC were designed to help with the 27.25% of failures that remain after constrained decoding. Both made things worse:

- **PE (few-shot, -2.5 pp)**: Three in-context examples apparently introduce formatting conflicts with the constrained grammar or shift the model toward the examples' conventions rather than the test case's.
- **ITC/CoT (-7.25 pp)**: Chain-of-thought reasoning is strongly counterproductive. The model reasons toward linguistically natural value forms (`"gasoline"`, `"last 2 weeks"`, ISO 8601 dates) that override the arbitrary conventions BFCL's ground truth encodes. CoT broke 50 cases that CD+Q had correct, while fixing only 24. The failure traces are explicit: the model argues confidently for wrong answers.

### 4. RAG at top-5 halves accuracy (-25 pp)

RAG recall@5 is 97.2% — the retriever nearly always surfaces the correct function among 5 candidates. The problem is that the model cannot reliably disambiguate between semantically similar candidates (e.g., `calculate_triangle_area` vs `calculate_area` vs `calc_area_triangle`). It picks a plausible-sounding sibling function 32% of the time. With oracle selection (1 candidate per test case), this problem doesn't exist.

RAG as currently implemented is not viable for this setting. If used in a real pipeline, it would need top-1 retrieval, re-ranking, or a training signal to teach disambiguation.

## The no-training ceiling

The best no-training configuration is **CD at 72.75%** (or CD+Q at 72.25%, which is equivalent within noise). No prompting strategy improved on the plain constrained decoding baseline. The no-training ceiling for Qwen 2.5 7B on BFCL simple_python is approximately 72–73%.

The remaining 27–28% failure rate is a semantic problem: the model consistently picks wrong default values for optional parameters, uses incorrect numeric precision (9.8 vs 9.81), uses full words instead of abbreviations, and fails on string format conventions. These are learned-association problems that prompting cannot fix — the model's internal priors about value formats do not match BFCL's ground truth labels.

## LoRA fine-tuning results (Phase 2 + format-aligned ablation)

Initial LoRA training (CD+FT, misaligned format) produced a -3 pp regression to 69.75%. Fixing the training format to match the inference pipeline reversed this into a **+4.0 pp gain** — CD+FT-aligned at **76.75%** is the first configuration to beat the no-training ceiling.

The format mismatch in v1: xlam trained the model to produce Python call syntax (`func(arg=val)`), while the inference pipeline sends a bare prompt expecting JSON. Rewriting `format_xlam_example` to match `build_args_extraction_prompt` exactly (JSON-only output, same prompt structure, same system prompt) fixed this.

FT-aligned-ng (no guided decoding, format-aligned) reached **13.25%** — slightly below the misaligned FT-only (13.75%). Format alignment optimized for the guided path (JSON args only, no function name in output), which breaks the unguided evaluator that must identify the function name from the raw output. This is a design tradeoff: aligning the training format to one inference mode can degrade the other.

The remaining 23.25% failure rate under CD+FT-aligned mirrors the CD baseline's failure taxonomy — optional parameter handling, type precision, enum value conventions, string format — errors that xlam's training signal does not correct. The training data's argument value distributions do not match BFCL's ground truth labels closely enough to close the semantic gap.

**Phase 2 conclusion**: format alignment is the critical variable. General-purpose function-calling fine-tuning requires the training format to match the inference pipeline exactly; the semantic content of xlam provides a modest positive signal once format interference is removed.

See `config-ft-lora-results.md` for the v1 analysis and `config-ft-lora-aligned-ablation.md` for the format-aligned ablation.

## Full stack: CD+Q+FT-aligned (Phase 3)

Applying AWQ INT4 quantization to the format-aligned LoRA merged model gives **74.25% (297/400)** — 2.5 pp below the unquantized CD+FT-aligned peak but 1.5 pp above the no-training CD baseline and 2.0 pp above CD+Q. The full combined stack (all four techniques) is deployment-viable at ~5.2 GiB and still outperforms the no-training ceiling.

The quantization penalty on a fine-tuned model (-2.5 pp) is larger than on the base model (-0.5 pp), suggesting AWQ calibration on generic text suboptimally quantizes the fine-tuned weight deltas. The training signal survives quantization but is attenuated.

See `config-cdqfta-results.md` for the full analysis.

## Result files

| Config | Scores | Run manifest |
|--------|--------|-------------|
| B | `data/output/bfcl_no_guided/scores/simple_python_scores.json` | `data/output/bfcl_no_guided/runs/` |
| PE | `data/output/bfcl_few_shot/scores/simple_python_scores.json` | `data/output/bfcl_few_shot/runs/` |
| CD | `data/output/bfcl/scores/simple_python_scores.json` | — |
| CD+Q | `data/output/bfcl_quant/scores/simple_python_scores.json` | `data/output/bfcl_quant/runs/` |
| CD+Q+ITC | `data/output/bfcl_itc/scores/simple_python_scores.json` | `data/output/bfcl_itc/runs/` |
| CD+Q+RAG | `data/output/bfcl_rag/scores/simple_python_scores.json` | `data/output/bfcl_rag/runs/` |
| FT-only | `data/output/bfcl_ft_no_guided/scores/` | `data/output/bfcl_ft_no_guided/runs/` |
| CD+FT | `data/output/bfcl_ft/scores/` | `data/output/bfcl_ft/runs/` |
| FT-aligned-ng | `data/output/bfcl_ft_aligned_no_guided/scores/` | `data/output/bfcl_ft_aligned_no_guided/runs/` |
| CD+FT-aligned | `data/output/bfcl_ft_aligned/scores/` | `data/output/bfcl_ft_aligned/runs/` |
| CD+Q+FT-aligned | `data/output/bfcl_cdqft_aligned/scores/` | `data/output/bfcl_cdqft_aligned/runs/` |

## Detailed per-config docs

- `config-b-no-guided-baseline.md` — failure analysis, 6 successful cases
- `bfcl-simple-python-baseline.md` — CD baseline, failure taxonomy
- `config-pe-few-shot-results.md` — few-shot setup and failure analysis
- `config-cdq-quantization-results.md` — AWQ memory/accuracy tradeoff
- `config-cdq-itc-results.md` — CoT case studies, flip analysis
- `config-cdqrag-results.md` — RAG recall@5, disambiguation failure analysis
- `config-ft-lora-results.md` — LoRA fine-tuning, format mismatch analysis
- `config-ft-lora-aligned-ablation.md` — format-aligned LoRA ablation, outcome interpretation
- `config-cdqfta-results.md` — full stack CD+Q+FT-aligned, quantization cost on fine-tuned model
- `size-sweep-results.md` — 0.5B/1.5B/3B/7B sweep across all Phase 1 configs
