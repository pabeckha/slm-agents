# BFCL Simple Python Baseline — Qwen 2.5 7B + vLLM Guided Decoding

**Date**: 2026-04-04
**Job**: 28142002 on A100 40GB (gpua100, node n-62-12-20)
**Model**: Qwen/Qwen2.5-7B-Instruct via vLLM 0.8.5
**Backend**: `src/vllm_backend.py` (guided_choice for function selection, guided_json for argument extraction)
**Benchmark**: BFCL v4 simple_python (400 test cases)
**Configuration**: CD+Q baseline (constrained decoding via vLLM guided decoding, no quantization applied yet, no fine-tuning)

## Results

**Preliminary AST accuracy: ~70.8% (283/400)**

Note: This is from a manual checker. The official BFCL `ast_checker` may score slightly higher due to more lenient string matching and type coercion.

### Function selection accuracy: ~100%

All 400 test cases selected the correct function name. Zero function selection errors observed in the failure analysis. Constrained decoding (`guided_choice`) guarantees the model picks from the available function names.

### Argument extraction accuracy: ~70.8%

117 out of 400 cases had at least one incorrect argument value.

## Failure Analysis

### Failure categories (from sample of 117 failures)

| Category | Example | Count (est.) | Root Cause |
|----------|---------|-------------|------------|
| Math expression format | `x^2` instead of `x**2` | ~15-20 | Model uses mathematical notation, not Python syntax |
| Imprecise constants | `9.8` instead of `9.81` | ~10-15 | Model rounds or uses approximate values |
| String format mismatch | `"kilometers/hour"` vs `"km/h"` | ~15-20 | Model uses full words instead of abbreviations |
| Location format | `"New York"` vs `"New York, NY"` | ~5-10 | Missing state/qualifier |
| Optional param wrong default | Fills value when empty string expected | ~20-30 | All params marked required in guided_json |
| Numeric precision | `8987551792.3` vs `8990000000.0` | ~5-10 | Model uses exact vs rounded values |

### Key observations

1. **Function selection is solved** by guided_choice — 100% accuracy on the selection step.
2. **Argument extraction is the bottleneck** — all failures are in argument values.
3. **Format/convention mismatches dominate** — the model understands what to extract but expresses it differently than the ground truth expects (e.g., `x^2` vs `x**2`).
4. **Optional parameters are problematic** — our schema marks all params as required, forcing the model to fill them even when empty string is the correct answer.

## Comparison to Success Criteria

| Criterion | Target | Current | Gap |
|-----------|--------|---------|-----|
| BFCL Simple AST accuracy | ≥85% | ~70.8% | ~14.2 points |

## Implications for Thesis (RQ1, RQ2)

### RQ1 (Baseline gap)
- Qwen 2.5 7B with basic constrained decoding achieves ~70.8% on BFCL simple_python
- Frontier models (GPT-4, Claude) score 85-95%+ on this benchmark
- **Gap to close: ~15-25 points** depending on the frontier baseline

### RQ2 (Marginal impact of each technique)
The failure patterns suggest which methods will help most:

| Method | Expected Impact | Why |
|--------|----------------|-----|
| **Better prompting / few-shot** | Medium | Could fix format conventions (x^2 → x**2) with examples |
| **LoRA fine-tuning** | High | Train on correct BFCL-style outputs; learn expected formats |
| **Optional param handling** | Medium | Fix schema to only require `required` params, not all |
| **RAG** | Low for this benchmark | BFCL already provides all function schemas in context |

### Immediate fix: optional parameters
Many failures come from optional params being filled incorrectly. Updating `bfcl_adapter.py` to only mark `required` params in the JSON schema (and omit optional ones) could recover 5-10% accuracy.

## Infrastructure Notes

- vLLM startup time on A100 40GB: ~5 minutes (model load 2:40 + torch.compile ~1:00 + warmup ~0:30)
- 400 test cases completed in ~15 minutes after server ready
- Total job time: ~25 minutes
- Result files written to: `data/output/bfcl/Qwen_Qwen2.5-7B-Instruct/non_live/`

## Experiment 2: Optional Parameters Fix (job 28142027)

**Change**: Updated `FunctionDef` to carry `required` field from BFCL schemas. `_build_args_json_schema` now only marks required params as required in the JSON schema, while optional params remain in `properties` but are not forced.

**Result**: 70.8% (283/400) — **no change**.

**Why no improvement**: The model still fills optional parameters even when not required by the JSON schema. `guided_json` with `additionalProperties: false` includes all `properties` in the output — the model just isn't forced to fill them but chooses to anyway. The failures are value mismatches, not missing params.

**Conclusion**: The optional params fix is architecturally correct but doesn't impact accuracy. The remaining failures are about the model's understanding of expected values, not about schema enforcement.

## Next Steps

1. Fix optional parameter handling in `bfcl_adapter.py` — only include `required` params in JSON schema
2. Get official BFCL `ast_checker` score (job 28142010 pending)
3. Run with few-shot prompting to fix format issues
4. Establish frontier baseline (Claude Sonnet on same test set)
5. Run LoRA fine-tuning experiment
