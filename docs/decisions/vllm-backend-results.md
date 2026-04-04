# vLLM Backend Results — Qwen 2.5 7B Instruct

**Date**: 2026-04-04
**Job**: 28141866 on A100 40GB (gpua100, node n-62-12-20)
**Model**: Qwen/Qwen2.5-7B-Instruct via vLLM 0.8.5
**Backend**: `src/vllm_backend.py` using `guided_choice` + `guided_json`

## Summary

11/11 test cases correct. 100% function selection accuracy AND 100% argument extraction accuracy. This is a significant improvement over the 0.6B model's 7/11 with the local backend.

## Results

| # | Prompt | Function | Arguments | Correct |
|---|--------|----------|-----------|---------|
| 1 | What is the sum of 2 and 3? | fn_add_numbers | a=2, b=3 | Yes |
| 2 | What is the sum of 265 and 345? | fn_add_numbers | a=265, b=345 | Yes |
| 3 | Greet shrek | fn_greet | name='shrek' | Yes |
| 4 | Greet john | fn_greet | name='john' | Yes |
| 5 | Reverse the string 'hello' | fn_reverse_string | s='hello' | Yes |
| 6 | Reverse the string 'world' | fn_reverse_string | s='world' | Yes |
| 7 | What is the square root of 16? | fn_get_square_root | a=16 | Yes |
| 8 | Calculate the square root of 144 | fn_get_square_root | a=144 | Yes |
| 9 | Replace all numbers in "Hello 34 I'm 233 years old" with NUMBERS | fn_substitute_string_with_regex | source_string="Hello 34 I'm 233 years old", regex='\\d+', replacement='NUMBERS' | Yes |
| 10 | Replace all vowels in 'Programming is fun' with asterisks | fn_substitute_string_with_regex | source_string='Programming is fun', regex='[aeiouAEIOU]', replacement='*' | Yes |
| 11 | Substitute the word 'cat' with 'dog' in 'The cat sat on the mat with another cat' | fn_substitute_string_with_regex | source_string='The cat sat on the mat with another cat', regex='cat', replacement='dog' | Yes |

## Comparison: Qwen3-0.6B (local) vs Qwen2.5-7B (vLLM)

| Test Case | 0.6B Local | 7B vLLM | Issue in 0.6B |
|-----------|-----------|---------|---------------|
| 1–4 (add, greet) | Correct | Correct | — |
| 5 (reverse 'hello') | Wrong | **Correct** | 0.6B computed result ('olleh') instead of passing input |
| 6 (reverse 'world') | Wrong | **Correct** | Same issue + garbled output |
| 7–8 (sqrt) | Correct | Correct | — |
| 9 (regex numbers) | Wrong | **Correct** | 0.6B cannot formulate regex patterns |
| 10 (regex vowels) | Wrong | **Correct** | 0.6B generated 200+ char hallucinated string |
| 11 (substitute cat/dog) | Wrong | **Correct** | 0.6B pre-applied the substitution in source_string |

**Score: 0.6B = 7/11 (64%), 7B = 11/11 (100%)**

## Analysis

### Why 7B succeeds where 0.6B fails

1. **Input vs output confusion resolved**: The 7B model understands that function arguments should be inputs to the function, not computed results. This is a fundamental reasoning capability that emerges with scale.

2. **Regex understanding**: The 7B model correctly formulates `\d+` and `[aeiouAEIOU]` regex patterns. The 0.6B model lacks this domain knowledge.

3. **guided_json constraint**: Extracting all arguments as a single JSON object (rather than one-by-one) gives the model full context about all parameters simultaneously, leading to more coherent argument sets.

### Infrastructure notes

- vLLM startup time: ~5 minutes (model loading 133s + torch.compile 58s + warmup 30s)
- Model memory: 14.2 GiB on A100 40GB
- KV cache: 362,144 tokens capacity, 88x concurrency at 4096 tokens/request
- All 11 test cases completed in ~10 seconds after server ready

## Implications for Thesis

- Confirms that **model scale matters** for argument extraction quality (RQ1 baseline gap)
- The vLLM backend with `guided_json` is ready for BFCL evaluation
- The 7B + guided decoding combination is a strong baseline for the ablation study (RQ2)
- Next step: run BFCL simple_python category on this configuration
