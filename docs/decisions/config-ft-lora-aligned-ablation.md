# Ablation: Format-Aligned LoRA Training (v2)

**Date**: 2026-04-24
**Status**: Complete — results available 2026-04-29
**Hypothesis**: The CD+FT v1 regression (69.75%, -3 pp vs CD) was caused by format mismatch between training data and inference pipeline, not by xlam's semantic content conflicting with BFCL's argument conventions.

## What changed from v1

One function in `scripts/train_lora.py`: `format_xlam_example`.

### v1 (misaligned)

Training example assistant turn:
```
autocomplete_places(q='San', country='US,CA', limit=5)
```

Training example user message:
```
Available functions:
- autocomplete_places(q: string, country: string, limit: integer): Returns a list of places...

User request: Find places starting with San in US or Canada, limit 5
```

System prompt: `"Output only the function call, nothing else."`

### v2 (aligned)

Training example assistant turn:
```json
{"q": "San", "country": "US,CA", "limit": 5}
```

Training example user message (matches `build_args_extraction_prompt` exactly):
```
Function: autocomplete_places(q: string, country: string, limit: integer) -> any
Description: Returns a list of places that match a given prefix...
User request: Find places starting with San in US or Canada, limit 5
Extract the argument values as a JSON object with keys: q (string), country (string), limit (integer).
JSON: 
```

System prompt: `"You are a function-calling assistant. Extract argument values as a JSON object."`

## Three specific mismatches fixed

| # | v1 | v2 |
|---|----|----|
| Output format | Python call: `name(arg=val)` | JSON object: `{"arg": val}` |
| Prompt structure | `Available functions: ...\nUser request:` | `Function: ...\nDescription: ...\nUser request: ...\nExtract ...\nJSON:` |
| System prompt | Hints at function-call syntax | Neutral: "extract as JSON" |

**What is NOT fixed**: the chat-template-vs-raw-completions mismatch — see below.

## Remaining mismatch: chat template vs raw completions

Training uses Qwen's chat template (`apply_chat_template`), so the model sees:

```
<|im_start|>system
You are a function-calling assistant...<|im_end|>
<|im_start|>user
Function: autocomplete_places(q: string, ...) -> any
Description: ...
User request: Find places starting with San...
Extract the argument values as a JSON object with keys: q (string), ...
JSON: <|im_end|>
<|im_start|>assistant
{"q": "San", "country": "US,CA", "limit": 5}<|im_end|>
```

At inference, `vllm_backend.py` uses `client.completions.create` (raw text completion), so the model sees:

```
Function: autocomplete_places(q: string, ...) -> string
Description: ...
User request: Find places starting with San...
Extract the argument values as a JSON object with keys: q (string), ...
JSON: 
```

No `<|im_start|>` / `<|im_end|>` tokens, no system prompt, no role markers. The model was pre-trained on chat-template format and fine-tuned with it — at inference it receives plain text with no framing.

This matters because Qwen's generation behavior is conditioned on those role tokens: the model expects to complete after `<|im_start|>assistant\n`, not after a bare `JSON: `. In practice the content alignment (v2 fix) is the dominant factor, but this residual mismatch could suppress gains.

**Fixing this** would require switching `vllm_backend.py` to `chat.completions.create` and restructuring the prompt builders to return message lists rather than raw strings. That is a meaningful refactor touching `VLLMBackend`, `build_args_extraction_prompt`, and `build_function_selection_prompt`. It is deferred — if CD+FT-aligned still regresses relative to CD, closing this mismatch is the natural next step.

## What the ablation tests

| Outcome | Interpretation |
|---------|----------------|
| CD+FT-aligned > 72.75% | Format fix unlocked improvement; xlam semantic content helps |
| CD+FT-aligned ≈ 72.75% | Format was the problem; xlam content is neutral once format is right |
| CD+FT-aligned > 69.75% but < 72.75% | Format was primary cause of regression; residual semantic mismatch remains |
| CD+FT-aligned ≈ 69.75% | Format alone is not the issue; xlam's argument conventions clash with BFCL regardless |

The no-guided variant (FT-aligned-ng) is expected to show a larger absolute improvement than the guided variant, because:
- Guided decoding already enforces format at inference — the aligned model's improved format compliance is redundant there
- Without guided decoding, the model must produce valid JSON on its own — format training directly helps this path

If FT-aligned-ng >> FT-only v1 (13.75%) but CD+FT-aligned ≈ CD+FT v1 (69.75%), the conclusion is: **format training improves the unguided path substantially but adds nothing under guided decoding** — the two techniques are fully complementary and non-additive when combined.

## Hyperparameters

Same as v1 (controlled ablation, single variable changed):

| Parameter | Value |
|-----------|-------|
| Base model | Qwen/Qwen2.5-7B-Instruct |
| Dataset | Salesforce/xlam-function-calling-60k (54k train, 6k val) |
| Epochs | 2 |
| LoRA rank | 16 |
| dtype | bfloat16 |
| Adapter dir | `models/lora/Qwen_Qwen2.5-7B-Instruct-aligned` |
| Merged model | `models/merged/Qwen_Qwen2.5-7B-Instruct-merged-aligned` |

## HPC job sequence

```sh
# 1. Train
bsub < scripts/hpc/train_lora_aligned.sh

# 2. Merge (run after training completes, on login node)
uv run --group hpc python scripts/merge_lora.py \
    --adapter models/lora/Qwen_Qwen2.5-7B-Instruct-aligned \
    --output models/merged/Qwen_Qwen2.5-7B-Instruct-merged-aligned

# 3. Evaluate
bsub < scripts/hpc/run_bfcl_ft_aligned.sh
bsub < scripts/hpc/run_bfcl_ft_aligned_no_guided.sh
```

## Results

| Config | Guided | Accuracy | Correct | Delta vs CD |
|--------|--------|----------|---------|-------------|
| CD (base) | Yes | 72.75% | 291/400 | baseline |
| CD+FT v1 | Yes | 69.75% | 279/400 | -3 pp |
| **CD+FT-aligned** | **Yes** | **76.75%** | **307/400** | **+4.0 pp** |
| B (base) | No | 1.5% | 6/400 | — |
| FT-only v1 | No | 13.75% | 55/400 | — |
| **FT-aligned-ng** | **No** | **13.25%** | **53/400** | **—** |

Job IDs: merge 28320841, eval 28320861 (guided), eval 28320862 (no-guided). Run date: 2026-04-28.

### Outcome interpretation

CD+FT-aligned at 76.75% lands in the first prediction bucket (> 72.75%): **format fix unlocked improvement and xlam semantic content helps**. The hypothesis is confirmed — the v1 regression was caused by format mismatch, not by xlam's argument conventions conflicting with BFCL.

FT-aligned-ng at 13.25% is slightly below FT-only v1 (13.75%). The aligned training format (JSON args only, no function name in output) removed the function name from the assistant turn entirely. Without guided decoding, the evaluator cannot identify which function was called, so nearly all cases fail with "Function name not found in model output." The original Python-call format (`func(arg=val)`) at least included the function name in the output. This is a side effect of optimizing the training format for the guided path: the args-only JSON format is correct for the args extraction step under constrained decoding, but renders the model useless on the unguided path.

### Key numbers for the thesis

- Format alignment: +7.0 pp over misaligned FT (69.75% → 76.75%)
- CD+FT-aligned vs CD baseline: **+4.0 pp** — fine-tuning with aligned format is the first configuration to beat the no-training ceiling
- Constrained decoding gap remains: 76.75% vs 13.25% (+63.5 pp) — guided generation is still the essential enabler even after format-aligned FT

### Representative failures (CD+FT-aligned, 93/400 remaining)

- Optional parameter not provided and not marked optional
- Type mismatch: inner array element type (e.g., `[1, 3]` where `float[]` expected)
- Invalid enum value: `'dict'` instead of `'dictionary'`, `'km'` instead of `'km/h'`
- String format: `'New York'` instead of `'New York, NY'`

These are the same failure categories as the CD baseline — value-level semantic errors that fine-tuning on xlam did not fix, confirming that xlam's argument conventions partially align with BFCL but do not fully close the semantic gap.

## Thesis implications

The hypothesis is confirmed. The v1 regression was a methodology artifact, not an inherent property of LoRA fine-tuning. The thesis narrative is:

> LoRA fine-tuning on a general function-calling corpus can improve over the constrained decoding baseline, but only when training format is aligned to the inference pipeline. Naively applying a standard function-calling dataset (xlam Python-call format) actively hurts performance (-3 pp). Aligning the training format to the evaluation pipeline converts the regression into a gain (+4.0 pp). This is the first configuration to exceed the no-training ceiling of ~72–73%.

The remaining 23.25% failure rate is driven by value-level semantic errors (wrong default values, unit conventions, string formats) that xlam's training signal does not correct. Closing this gap would require training data whose argument value distributions match BFCL's ground truth labels, or a fundamentally different training strategy.

The FT-aligned-ng result is a caution: format alignment must be designed end-to-end. Optimizing the training format for one inference path (guided, args-only JSON) can break the other path (unguided, where function name must appear in the output).
