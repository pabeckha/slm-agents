# Config CD+FT Results — LoRA Fine-Tuning + Guided Decoding (v1, format-misaligned)

**Date**: 2026-04-24
**Jobs**: bfcl_ft (Apr 22, guided), bfcl_ft_no_guided (Apr 24, unguided)
**Model**: models/merged/Qwen_Qwen2.5-7B-Instruct-merged (LoRA merged, bfloat16)
**Base**: Qwen/Qwen2.5-7B-Instruct + xlam LoRA, merged via merge_lora.py
**Backend**: vLLM 0.8.5, max-model-len 4096
**Benchmark**: BFCL v4 simple_python (400 test cases, AST accuracy)

## Results

| Config | Guided | Accuracy | Correct | Delta vs CD |
|--------|--------|----------|---------|-------------|
| B (no guided, base) | No | 1.5% | 6/400 | -71.25 pp |
| CD (base model) | Yes | 72.75% | 291/400 | baseline |
| **FT-only (LoRA merged, no guided)** | **No** | **13.75%** | **55/400** | -59 pp |
| **CD+FT (LoRA merged + guided)** | **Yes** | **69.75%** | **279/400** | **-3 pp** |

### Key numbers

- CD+FT accuracy: **69.75%** (279/400) — -3 pp regression vs CD baseline
- FT-only accuracy: **13.75%** (55/400) — +12.25 pp over unguided baseline (1.5%)

## Analysis

### CD+FT regresses vs CD (-3 pp)

The most important finding: LoRA fine-tuning on xlam makes the guided model slightly worse, not better. The likely mechanism is a format conflict between training distribution and evaluation setting.

The xlam dataset uses Python call syntax in the assistant turn (`function_name(arg=value, ...)`). After LoRA training, the merged model's weights encode this convention. At inference, constrained decoding overrides the surface format (forcing valid JSON), but the model's argument value predictions are now biased toward the xlam conventions rather than BFCL's. The model is simultaneously fighting two signals — the grammar constraint and the training distribution — and resolves them poorly.

A secondary factor: the LoRA training set includes 52.6% multi-call examples (xlam allows multiple calls per query), while BFCL simple_python is exclusively single-call. The model may have shifted its prior toward generating multi-call patterns in contexts where none are needed.

### FT-only shows meaningful format learning (+12.25 pp)

Without constrained decoding, the merged model produces structurally valid JSON in far more cases than the base model (13.75% vs 1.5%). Fine-tuning teaches the model that tool-calling responses should be structured — this is genuine learning. But 13.75% is still far below the CD baseline (72.75%), meaning format compliance alone is not sufficient: the model still produces malformed or incomplete JSON in the majority of cases without grammar enforcement.

The 59 pp gap between FT-only (13.75%) and CD+FT (69.75%) shows that constrained decoding still does most of the heavy lifting even after fine-tuning.

### Why the thesis target was not reached

The thesis target was ≥85% on BFCL simple_python. CD+FT at 69.75% is -3 pp below the CD baseline rather than +12 pp above it.

Root causes:
1. **Distribution mismatch**: xlam uses Python call syntax; BFCL expects a specific JSON argument format. The model learned the wrong output convention.
2. **No BFCL-aligned training signal**: the LoRA was not trained on BFCL-format (schema, query, JSON) examples. The training distribution does not reward BFCL argument conventions.
3. **Semantic gap persists**: the 27% of failures that remain after CD are value-level errors (wrong defaults, wrong numeric precision, format conventions). xlam examples do not systematically target these specific error types.

## Implications for thesis

This result reframes the Phase 2 narrative. Fine-tuning on a general function-calling dataset (xlam) does not improve over constrained decoding on its own; it produces a regression. The positive contribution of LoRA requires alignment between the training distribution and the evaluation conventions.

This is itself a thesis finding: **general function-calling fine-tuning is not substitutable for task-aligned fine-tuning**. The model learns format from training data, and when the training format differs from the evaluation format, guided decoding cannot fully compensate.

For the cascade architecture framing, this is relevant: if the SLM component is fine-tuned, it must be fine-tuned on data that matches the production tool schema and argument conventions, not on a generic function-calling corpus.

The FT-only result (13.75%) confirms the complementarity of the two techniques: fine-tuning improves unguided format compliance; constrained decoding provides the floor. Neither alone reaches the CD baseline.

## Follow-up ablation

To test whether format mismatch was the primary cause, a format-aligned v2 uses the same xlam data reformatted to match the inference pipeline's exact prompt and output format. See `config-ft-lora-aligned-ablation.md`.

## Result files

| Config | Scores | Run manifest |
|--------|--------|-------------|
| CD+FT | `data/output/bfcl_ft/scores/` | `data/output/bfcl_ft/runs/2026-04-22T12-54-08_*.json` |
| FT-only | `data/output/bfcl_ft_no_guided/scores/` | `data/output/bfcl_ft_no_guided/runs/2026-04-23T23-46-20_*.json` |
