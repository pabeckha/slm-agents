# Config CD+Q+FT — Quantized Format-Aligned LoRA + Guided Decoding

**Date**: 2026-05-10
**Job**: 28395175 on L40S 46GB (gpul40s)
**Model**: `Qwen_Qwen2.5-7B-Instruct-merged-aligned-AWQ` (AWQ INT4 of format-aligned LoRA merged)
**Backend**: `src/vllm_backend.py` (guided_choice + guided_json, quantization=awq_marlin, enforce-eager)
**Benchmark**: BFCL v4 simple_python (400 test cases)
**Configuration**: CD+Q+FT — guided decoding + AWQ INT4 + format-aligned LoRA

## Research question

Does quantizing the format-aligned LoRA-merged model preserve the +4.0 pp gain from CD+FT-aligned (76.75%), or does the AWQ quantization step erode it?

## Result

**AST accuracy: 74.25% (297/400)**

## Comparison

| Config | Model | Guided | Accuracy | Correct | Delta vs CD |
|--------|-------|--------|----------|---------|-------------|
| CD | 7B FP16 | Yes | 72.75% | 291/400 | baseline |
| CD+Q | 7B AWQ INT4 | Yes | 72.25% | 289/400 | -0.5 pp |
| CD+FT (misaligned) | 7B bf16 merged | Yes | 69.75% | 279/400 | -3.0 pp |
| CD+FT-aligned | 7B bf16 merged | Yes | 76.75% | 307/400 | +4.0 pp |
| **CD+Q+FT-aligned** | **7B AWQ INT4 merged** | **Yes** | **74.25%** | **297/400** | **+1.5 pp** |

## Analysis

Quantizing the format-aligned LoRA-merged model costs 2.5 pp compared to the unquantized merged model (76.75% → 74.25%). This is a larger penalty than applying AWQ to the base model (72.75% → 72.25%, -0.5 pp), suggesting that quantization interacts with the LoRA adapter more than with the base weights.

Despite the 2.5 pp cost, the full stack still beats both the CD baseline (+1.5 pp over 72.75%) and the CD+Q baseline (+2.0 pp over 72.25%). The LoRA training signal survives quantization — it is attenuated but not destroyed.

### Memory

The AWQ model occupies approximately the same footprint as CD+Q (~5.2 GiB), fitting comfortably on a 24 GB consumer GPU alongside KV cache. This is the deployment-relevant configuration: fine-tuned capability at INT4 size.

### Failure modes

Not analyzed in detail. Expected to mirror CD+FT-aligned's residual failures (optional parameter handling, enum conventions, string format mismatches) plus potential new errors from quantization noise on fine-tuned weights.

## Interpretation

The 2.5 pp quantization penalty on a LoRA-merged model (vs 0.5 pp on the base model) is worth noting for the thesis. One plausible explanation: AWQ calibration was performed on the merged model using a generic calibration set — the calibration distribution may not represent the function-calling inputs the LoRA was trained on, leading to suboptimal quantization of the fine-tuned weight deltas.

Alternatives not explored:
- Calibrate AWQ on function-calling examples rather than generic text
- Apply GPTQ instead of AWQ (different quantization algorithm)
- Use a higher bit-depth (e.g., INT8) to reduce precision loss

For the thesis narrative, the practical conclusion is: the full CD+Q+FT stack is deployable on consumer hardware at 74.25% — 1.5 pp above the no-training ceiling and within 2.5 pp of the unquantized peak.

## Thesis implications

The CD+Q+FT-aligned configuration closes the research arc: the combined stack of all four techniques (constrained decoding, quantization, LoRA fine-tuning, format alignment) achieves 74.25%, confirming that:

1. The LoRA training signal is robust to AWQ quantization — 2.5 pp loss, not catastrophic degradation
2. The deployment-viable configuration (INT4, consumer GPU) still outperforms the no-training no-quantization CD baseline
3. The best accuracy remains with the unquantized CD+FT-aligned at 76.75% — the cost of INT4 quantization on a fine-tuned model is measurable and non-negligible

## Result files

- Scores: `data/output/bfcl_cdqft_aligned/scores/simple_python_scores.json`
- Run manifest: `data/output/bfcl_cdqft_aligned/runs/`
- Log: `logs/bfcl_cdqft_aligned_28395175.out`
- HPC script: `scripts/hpc/run_bfcl_cdqft_aligned.sh`
