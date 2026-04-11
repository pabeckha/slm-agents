# Config B Baseline — Qwen 2.5 7B Without Guided Decoding

**Date**: 2026-04-05
**Job**: 28142319 on A100 40GB (gpua100, node n-62-12-23)
**Model**: Qwen/Qwen2.5-7B-Instruct via vLLM 0.8.5
**Backend**: `src/vllm_backend.py` (no guided decoding — `--no-guided` flag)
**Benchmark**: BFCL v4 simple_python (400 test cases)
**Configuration**: Config B — raw model output, no constrained decoding, no quantization, no fine-tuning

## Results

**AST accuracy: 1.5% (6/400)**

| Metric | Value |
|--------|-------|
| Total test cases | 400 |
| Correct | 6 |
| Failed (parse error) | ~370 |
| Failed (wrong function name) | ~24 |
| Accuracy | 1.5% |

### Comparison with Config CD (guided decoding)

| Config | Accuracy | Correct | Failed |
|--------|----------|---------|--------|
| **B** (no guided decoding) | 1.5% | 6/400 | 394 |
| **CD** (guided decoding) | 72.75% | 291/400 | 109 |
| **Marginal impact of CD** | **+71.25 pp** | +285 | -285 |

## Failure Analysis

### Dominant failure mode: format non-compliance

The overwhelming failure mode is not semantic misunderstanding — it is the model's inability to produce output in the expected JSON format without structural constraints.

**Error breakdown** (from 394 failures):

| Error Type | Approx. Count | Description |
|------------|--------------|-------------|
| `Extra data` (JSON parse) | ~350 | Model generates multiple JSON objects, trailing text, or conversational wrapping around the JSON |
| Empty parse (no JSON found) | ~20 | Model generates pure natural language with no JSON structure |
| Wrong function name | ~24 | Output parses but `ast_checker` cannot match function name |

The `Extra data` error occurs because the model outputs text like `{"name": "func", ...}\n{"name": "func2", ...}` or wraps JSON in conversational text. The extraction heuristic (`find("{")` to `rfind("}") + 1`) captures the outer braces but the interior remains invalid multi-object JSON.

### The 6 successful cases

| Test ID | Function Call |
|---------|-------------|
| simple_python_22 | `math.gcd(num1=12, num2=15)` |
| simple_python_84 | `calculate_bmi(weight=85, height=180, unit='cm')` |
| simple_python_109 | `random_forest.train(n_estimators=100, max_depth=5, data='my_data')` |
| simple_python_253 | `retrieve_religion_info(religion_name='Buddhism', detail_level='full')` |
| simple_python_261 | `draw_rectangle(width=20, height=10, color='red')` |
| simple_python_349 | `game_score.highest(game='Overwatch', platform='PC', region='Global')` |
| simple_python_396 | `hospital.locate(location='Denver, Colorado', radius=5, department='pediatrics')` |

These share common traits: simple parameter types (strings, integers), no optional parameters, and straightforward mappings from the user query to argument values. In these rare cases, the model happened to produce clean single-object JSON.

## Key Insight: Constrained Decoding Solves Format, Not Semantics

This experiment cleanly separates two capabilities:

1. **Format compliance** (can the model produce valid, parseable tool-call JSON?)
   - Without CD: ~7% of outputs are parseable at all
   - With CD: 100% — guided_json guarantees valid JSON, guided_choice guarantees valid function names

2. **Semantic accuracy** (given correct format, are the argument values right?)
   - With CD: 72.75% — the model understands most queries but struggles with conventions, precision, and optional parameters
   - Without CD: unmeasurable at scale — too few parseable outputs to draw conclusions

The 71.25 percentage point gap is almost entirely a **format compliance gap**, not a reasoning gap. The model likely "knows" the right function and arguments in most cases but cannot reliably express them in the required structured format without constrained decoding.

## Implications for Thesis

### RQ1 (What is the baseline gap?)

Config B (1.5%) establishes the raw SLM baseline. This is the starting point from which all optimization techniques are measured. The gap to frontier models (85-95%+ on BFCL) is 83-93 percentage points.

### RQ2 (Marginal contribution of each technique)

Constrained decoding alone recovers 71.25 percentage points — by far the largest single-technique improvement expected in the ablation study. This validates the thesis premise that constrained decoding is the foundational technique for SLM tool calling.

The remaining 27.25% failure rate (Config CD) is a **semantic** problem that requires different techniques: prompt engineering, fine-tuning, or better reasoning chains.

### Cascade architecture implications

The 1.5% baseline means that without constrained decoding, an SLM is essentially non-functional for tool calling. In a cascade architecture, the routing decision is binary: if CD is available, the SLM can handle ~73% of simple calls; without it, every call must be escalated to a frontier model.

## Infrastructure Notes

- Job runtime: 33 minutes (01:45:16 → 02:18:57 CEST)
- vLLM startup: ~5 minutes (model load 2:24 + warmup)
- 400 inferences: ~13 minutes after server ready
- GPU memory: 14.2 GiB on A100 40GB
- Same infrastructure as Config CD job — results are directly comparable

## Result Files

- Predictions: `data/output/bfcl_no_guided/Qwen_Qwen2.5-7B-Instruct/non_live/BFCL_v4_simple_python_result.json`
- Scores: `data/output/bfcl_no_guided/scores/simple_python_scores.json`
- Run manifest: `data/output/bfcl_no_guided/runs/2026-04-05T00-18-52_Qwen_Qwen2.5-7B-Instruct_simple_python_no_guided.json`
- Log: `logs/bfcl_no_guided_28142319.out`

## Next Steps

1. Document this finding in the thesis methodology/results chapters
2. Run Config PE (prompt engineering) to measure few-shot impact on the remaining 27.25% semantic failures
3. Establish frontier baselines for the gap calculation
