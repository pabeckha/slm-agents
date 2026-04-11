# Config PE Results — Few-Shot Prompting + Guided Decoding

**Date**: 2026-04-06
**Job**: 28148815 on A100 40GB
**Model**: Qwen/Qwen2.5-7B-Instruct via vLLM 0.8.5
**Backend**: `src/vllm_backend.py` (guided_choice + guided_json + few-shot examples)
**Benchmark**: BFCL v4 simple_python (400 test cases)
**Configuration**: Config PE — guided decoding with 3 few-shot examples prepended to argument extraction prompts

## Results

**AST accuracy: 70.25% (281/400)**

### Comparison across configs

| Config | Accuracy | Correct | Delta vs CD |
|--------|----------|---------|-------------|
| B (no guided) | 1.5% | 6/400 | -71.25 pp |
| **PE (few-shot + guided)** | **70.25%** | **281/400** | **-2.5 pp** |
| CD (guided only) | 72.75% | 291/400 | baseline |

**Few-shot prompting decreased accuracy by 2.5 percentage points.** The examples did not help and slightly hurt performance.

## Few-Shot Examples Used

Three examples were prepended to the argument extraction prompt, targeting known Config CD failure modes:

1. **Numeric precision** — `9.81` (exact), not `9.8` (rounded)
2. **String format with location qualifier** — `"San Francisco, CA"` (with state)
3. **Python expression syntax** — `x**2` (Python), not `x^2` (math notation)

## Failure Analysis

The same failure categories from Config CD persist at similar or higher rates:

| Failure | Config CD | Config PE | Example |
|---------|-----------|-----------|---------|
| Wrong optional default | Present | Present | `root_type=''` expected `'all'` |
| Nested type mismatch | Present | Present | `[1, 3]` expected `[1.0, 3.0]` |
| Numeric precision | Present | Present | `9.8` expected `9.81` |
| String format | Present | Present | `"kilometers per hour"` expected `"km/h"` |
| Location format | Present | Present | `"New York"` expected `"New York, NY"` |

The few-shot examples demonstrated the correct conventions, but the model did not generalize from them. The 10 additional cases lost (compared to CD) suggest the longer prompt context slightly degraded performance on borderline cases.

## Why Few-Shot Failed

1. **Domain mismatch**: The few-shot examples use different functions than the test cases. The model doesn't transfer conventions like "use exact numeric values" from one function to another.

2. **Prompt length penalty**: Adding ~300 tokens of examples to every prompt increases context length without proportional benefit. For a 7B model, this extra noise may dilute attention on the actual task.

3. **Fundamental representation issue**: The failures (9.8 vs 9.81, "km/h" vs "kilometers per hour") reflect the model's internal representation of concepts, not a formatting gap that examples can bridge. The model genuinely associates "acceleration due to gravity" with 9.8, not 9.81.

## Implications for Thesis

### RQ2 (Marginal impact of each technique)

| Method | Expected Impact | Actual Impact |
|--------|----------------|---------------|
| Prompt Engineering (few-shot) | Medium (+5-10%) | **-2.5%** (negative) |

This is a **negative result but a valuable finding**:
- Prompt engineering is the cheapest intervention, and it doesn't work for this failure mode class
- The argument extraction errors are not about format awareness — they are about the model's learned associations
- This strengthens the case for **LoRA fine-tuning**: the model needs to learn BFCL-specific value conventions through training, not prompting
- Few-shot examples can teach format but cannot override learned numeric constants or string preferences

### Cascade architecture implications

In a cascade architecture, prompt engineering does not expand the SLM's capability boundary. The same ~27% of cases that fail with guided decoding alone continue to fail with few-shot prompting. These cases must still escalate to a frontier model unless the SLM is fine-tuned.

## Infrastructure Notes

- Job runtime: similar to Config CD (~25 minutes)
- No additional VRAM overhead from few-shot (text-only, no model changes)

## Result Files

- Predictions: `data/output/bfcl_few_shot/Qwen_Qwen2.5-7B-Instruct/non_live/BFCL_v4_simple_python_result.json`
- Scores: `data/output/bfcl_few_shot/scores/simple_python_scores.json`
- Run manifest: `data/output/bfcl_few_shot/runs/2026-04-06T09-37-13_Qwen_Qwen2.5-7B-Instruct_simple_python_guided_few_shot.json`
- Log: `logs/bfcl_few_shot_28148815.out`

## Next Steps

1. LoRA fine-tuning (Config FT, CD+FT) — the most promising path to fix argument extraction errors
2. Frontier baselines — establish the ceiling for comparison
3. Quantization (Config CD+Q) — verify no accuracy degradation from INT4
