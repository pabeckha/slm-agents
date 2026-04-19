# Config CD+Q+ITC Spec — Chain-of-Thought Before Argument Extraction

**Status**: pre-run spec (2026-04-11)
**Config**: CD+Q+ITC (CoT variant for BFCL simple_python)
**Baseline to beat**: Config CD+Q — 72.0% AST accuracy (288/400)
**Benchmark**: BFCL v4 simple_python, 400 test cases
**Model**: `Qwen/Qwen2.5-7B-Instruct-AWQ` via vLLM 0.8.5

---

## Scope note — why ReAct is not tested on BFCL simple_python

ITC is an umbrella label that covers two distinct techniques in the experiment-spec: chain-of-thought (CoT) and ReAct. They are not interchangeable.

**CoT** is a single reasoning pass before a decision: Thought → Action.

**ReAct** is an iterative loop: Thought → Action → **Observation** → Thought → Action → … until done. The distinguishing feature is reasoning *over the result of a tool call*.

On BFCL simple_python, ReAct structurally collapses to CoT:

1. Each test case provides exactly one function and one user query.
2. BFCL does not execute the function — it only compares the emitted call against a reference structurally (AST accuracy).
3. There is no multi-step goal, no observation, and no second turn for reasoning to consume.

A "ReAct run" on simple_python would therefore be exactly one Thought, then one Action, then stop — which is indistinguishable from CoT on a single tool call. There is no distinct experiment to run, so the ITC config on this benchmark is implemented as CoT-before-extraction.

Where ReAct is a distinct technique and should be evaluated separately:

- **τ-bench** — multi-turn, tools actually execute, multi-step goals. This is the benchmark `experiment-spec.md` already earmarks for ReAct. Tracked in Issue #4.
- **Other BFCL categories** — `multi_turn`, `parallel_multiple`, `multiple` — not on the current Phase 1 implementation path, but candidates for a later ReAct evaluation if τ-bench slips.

The ReAct variant of Config ITC will run when one of those benchmarks is online. Until then, "Config CD+Q+ITC" in Phase 1 refers specifically to the CoT variant on simple_python.

---

## Hypothesis

Config CD failures cluster into two classes (established in `config-pe-few-shot-results.md`):

1. **Reasoning-visible errors** — the model could have gotten the right answer if forced to externalize its thinking before committing to structured output. E.g. numeric precision (9.8 vs 9.81), Python syntax (`x**2` vs `x^2`), nested types ([1,3] vs [1.0,3.0]).
2. **Learned-association errors** — no amount of reasoning fixes them because the error is in the model's prior. E.g. unit abbreviation preferences ("km/h" vs "kilometers per hour"), location format conventions ("New York, NY"), and optional-parameter defaults (`root_type=''` vs `'all'`).

**H1** — CoT improves class (1) by making value selection explicit before extraction.
**H2** — CoT does not help class (2), for the same structural reason few-shot didn't (Config PE).
**H3** — Net effect: small positive (+1 to +4 pp) if H1 dominates, small negative (-1 to -3 pp, prompt-length dilution) if H2 dominates.

Either outcome is a publishable data point. A negative result here is the third piece of evidence (alongside PE) that prompting alone cannot fix argument-extraction errors, further motivating LoRA in Phase 2.

---

## Technical design

### Pipeline shape

Current CD+Q pipeline (`src/vllm_backend.py`):

```
prompt
  ├─ _select_function  → guided_choice → fn_name
  └─ _extract_args     → guided_json   → args dict
```

Proposed CD+Q+ITC pipeline:

```
prompt
  ├─ _select_function  → guided_choice → fn_name                          (unchanged)
  ├─ _reason_about_args → free generation → reasoning text (new)
  └─ _extract_args     → guided_json, with reasoning text in context → args dict
```

Key properties:
- **Guided decoding still wraps the final extraction.** CoT runs in free mode before it; the final `guided_json` call still constrains the output structure. Format validity is preserved.
- **Reasoning is ephemeral.** The reasoning text is used as context for extraction, then discarded. Not stored in the `FunctionCall` object.
- **One additional inference call per test case.** ~2x latency on the extraction path, still cheaper than any training approach.

### Prompt shape for the reasoning step

The reasoning prompt targets the failure modes from Config CD:

```
Function: {signature}
Description: {description}
User request: {query}

Before extracting the arguments, think step by step about:
- Which exact values from the user's request should go into each argument?
- Are there any numeric precisions, units, or string formats that must be preserved exactly as stated?
- What are reasonable defaults for any optional arguments not mentioned?

Reasoning:
```

The model completes the "Reasoning:" block in free mode (no guided decoding), with `max_tokens=256`, `temperature=0`. The resulting text is injected into the argument-extraction prompt as additional context immediately before the `JSON: ` completion anchor.

### Stopping / output hygiene

- Cap reasoning at 256 tokens and also at the first occurrence of `"\nJSON:"` or `"\nFunction:"` to prevent the model from hallucinating a structured answer during the free-gen step.
- If the model leaks a `{...}` block in the reasoning, do not parse it — always pass through to the guided extraction step.

---

## Implementation plan

Four files touched. Roughly 80–120 lines added.

| File | Change |
|---|---|
| `src/prompt.py` | Add `build_reasoning_prompt(func, query)` and a variant of `build_args_extraction_prompt` that accepts an optional `reasoning: str` and injects it between the user request and the `JSON: ` anchor. |
| `src/vllm_backend.py` | Add `cot: bool = False` constructor flag. Add `_reason_about_args(prompt, func) -> str` method. In `_extract_args`, when `cot=True`, call `_reason_about_args` first and pass the result into the extraction prompt builder. |
| `src/bfcl_adapter.py` | Add `--cot` CLI flag that forwards to `VLLMBackend(cot=True)`. Extend the run manifest writer to record `cot: true/false`. |
| `scripts/hpc/run_bfcl_itc.sh` | New HPC job script. Mirrors `run_bfcl_quant.sh` but passes `--cot` and writes to `data/output/bfcl_itc/`. |

Unchanged:
- `src/decoder.py`, `src/schema.py`, `src/pipeline.py` — the pipeline shape is backward compatible; `cot=False` is the default and preserves current CD+Q behavior exactly.
- Existing run scripts for B, CD, CD+Q, PE — untouched.

### Mutual exclusion with PE

`cot=True` and `few_shot=True` are mutually exclusive for this config (we want to isolate CoT's effect, not stack it with few-shot). The CLI should error if both flags are passed. An orthogonal combination experiment can come later if either is individually interesting.

---

## How to run

```sh
bsub < scripts/hpc/run_bfcl_itc.sh
```

Expected wall time: ~50 min (roughly 2× Config CD+Q due to the extra reasoning call; one-shot CoT is fast on AWQ INT4).

Outputs:
- Predictions: `data/output/bfcl_itc/Qwen_Qwen2.5-7B-Instruct-AWQ/non_live/BFCL_v4_simple_python_result.json`
- Scores: `data/output/bfcl_itc/scores/simple_python_scores.json`
- Run manifest: `data/output/bfcl_itc/runs/<timestamp>_..._guided_cot.json`
- Reasoning traces: `data/output/bfcl_itc/reasoning/<test_id>.txt` (new — for failure analysis)

The reasoning traces are saved specifically so the failure analysis in the results doc can quote concrete examples of where CoT helped or hurt.

---

## Analysis plan (for the results doc)

Once the job finishes, the results doc (`config-cdq-itc-results.md`) should report:

1. **Headline accuracy** — AST accuracy, correct count, delta vs CD+Q.
2. **Failure-class breakdown** — Use the same categories as Config PE: wrong optional default, nested type mismatch, numeric precision, string format, location format. Tabulate how each class moved vs CD+Q. This tests H1 vs H2 directly.
3. **Case studies** — 3 examples where CoT flipped a CD+Q failure to success, 3 where CoT flipped a CD+Q success to failure. Quote the reasoning text for each.
4. **Latency** — mean and p95 wall time per test case vs CD+Q. Document the throughput cost of the reasoning step.
5. **Prompt-length sanity check** — Compare mean total prompt tokens vs CD+Q and PE. If CD+Q+ITC regresses like PE did, we want to know whether it's CoT itself or just prompt length inflation.
6. **Thesis implications** — Update the RQ2 impact table. If CoT is net negative, write the explicit conclusion that prompting-only interventions have now failed twice on this failure-mode class, and LoRA is the remaining path for argument-extraction accuracy.

---

## Related

- Baseline: `config-cdq-quantization-results.md` (72.0%)
- Upstream comparison: `bfcl-simple-python-baseline.md` (Config CD, 72.75%)
- Negative precedent: `config-pe-few-shot-results.md` (Config PE, 70.25%)
- Planning: `docs/planning/experiment-spec.md` § Methods → Inference-Time Compute
- Issue: #23
