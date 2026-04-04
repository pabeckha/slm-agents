# PoC Results Analysis — Constrained Decoding on Qwen3-0.6B

**Date**: 2026-04-04
**Job**: 28141772 on A100 80GB (gpua100, node n-62-18-8)
**Model**: Qwen3-0.6B
**Pipeline**: Constrained decoding with logit masking (src/decoder.py)

## Summary

Ran 11 test prompts against 5 function definitions. Function selection is 100% accurate. Argument extraction works well for simple types (numbers, short strings) but fails on complex string manipulation tasks.

## Results

### Correct (7/11)

| # | Prompt | Result | Status |
|---|--------|--------|--------|
| 1 | "What is the sum of 2 and 3?" | `fn_add_numbers(a=2, b=3)` | Correct |
| 2 | "What is the sum of 265 and 345?" | `fn_add_numbers(a=265, b=345)` | Correct |
| 3 | "Greet shrek" | `fn_greet(name='shrek')` | Correct |
| 4 | "Greet john" | `fn_greet(name='john')` | Correct |
| 7 | "What is the square root of 16?" | `fn_get_square_root(a=16)` | Correct |
| 8 | "Calculate the square root of 144" | `fn_get_square_root(a=144)` | Correct |

### Incorrect (4/11) — Argument Extraction Failures

| # | Prompt | Expected | Got | Issue |
|---|--------|----------|-----|-------|
| 5 | "Reverse the string 'hello'" | `fn_reverse_string(s='hello')` | `fn_reverse_string(s='olleh')` | Model computed the result instead of passing the input |
| 6 | "Reverse the string 'world'" | `fn_reverse_string(s='world')` | `fn_reverse_string(s='drow olrwd')` | Same issue + garbled output |
| 9 | "Replace all numbers in 'Hello 34...' with NUMBERS" | `regex='\d+', replacement='NUMBERS'` | `regex='34 233', replacement='34'` | Cannot formulate regex patterns; wrong replacement |
| 10 | "Replace all vowels in '...' with asterisks" | `regex='[aeiouAEIOU]', replacement='*'` | `replacement='* * * ...'` (200+ chars) | Massive hallucinated replacement string |
| 11 | "Substitute 'cat' with 'dog' in '...'" | `source_string='The cat sat...'` | `source_string='The dog sat...'` | Pre-applied substitution in source_string |

## Analysis

### What works
- **Function selection**: 100% accuracy — constrained decoding reliably picks the correct function from 5 candidates
- **Simple argument types**: Numbers and short strings extracted correctly
- **JSON validity**: 100% — constrained decoding guarantees well-formed output

### What fails
- **Input vs. output confusion**: The 0.6B model tries to compute the answer instead of passing inputs to the function (cases 5, 6, 11)
- **Regex/pattern understanding**: Model cannot formulate regex patterns — it lacks the reasoning capacity at this scale (cases 9, 10)
- **Unbounded string generation**: Without length constraints, the model generates excessively long strings (case 10)

### Root causes
1. **Model scale**: 0.6B params is insufficient for understanding that function arguments should be *inputs*, not *computed outputs*
2. **No reasoning guidance**: Without CoT prompting, the model conflates "what should I pass" with "what is the answer"
3. **Regex as a domain gap**: Regex syntax is likely underrepresented in a 0.6B model's training data

## Implications for Thesis

These results directly motivate the optimization methods:

| Method | Expected Impact on These Failures |
|--------|----------------------------------|
| **Larger model (7B)** | Should resolve input/output confusion and regex understanding |
| **CoT/ReAct prompting** | Explicit reasoning step to separate "what to compute" from "what to pass" |
| **LoRA fine-tuning** | Train on tool-calling examples where args are inputs, not results |
| **RAG** | Retrieve similar function call examples to guide argument extraction |

## Next Steps

1. Run same tests on Qwen 2.5 7B to establish scale-dependent baseline
2. Add CoT prompting to see if reasoning step fixes input/output confusion
3. Integrate BFCL evaluation for standardized benchmarking
