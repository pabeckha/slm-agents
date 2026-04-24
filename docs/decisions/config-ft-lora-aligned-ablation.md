# Ablation: Format-Aligned LoRA Training (v2)

**Date**: 2026-04-24
**Status**: Pending — training not yet submitted
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

**What is NOT fixed**: the chat-template-vs-raw-completions mismatch. Training still uses Qwen's chat template (`<|im_start|>system...`), while inference uses raw `completions.create` with plain text. The content inside the turns now matches; the framing tokens still differ. Addressing this would require changing the inference backend to use `chat.completions.create`, which is a larger refactor.

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

## Results (pending)

| Config | Guided | Accuracy | Delta vs CD |
|--------|--------|----------|-------------|
| CD (base) | Yes | 72.75% | baseline |
| CD+FT v1 | Yes | 69.75% | -3 pp |
| **CD+FT-aligned** | **Yes** | **TBD** | **TBD** |
| B (base) | No | 1.5% | — |
| FT-only v1 | No | 13.75% | — |
| **FT-aligned-ng** | **No** | **TBD** | **TBD** |

## Thesis implications

This ablation directly addresses a key methodological question: *does LoRA fine-tuning on a general function-calling corpus improve tool-calling accuracy when training format is aligned to evaluation format?*

The v1 result (-3 pp) could not answer this question because format mismatch confounded the comparison. The v2 result isolates the effect of the training data's semantic content independently of format.

If the hypothesis is confirmed (v2 > v1), the thesis narrative becomes:
> LoRA fine-tuning can improve over the CD baseline, but only when training format matches the inference pipeline. General-purpose function-calling datasets require careful format alignment before fine-tuning; naively applying a standard function-calling dataset with the wrong output convention actively hurts performance.

If the hypothesis is refuted (v2 ≈ v1), the narrative becomes:
> The xlam dataset's argument conventions are too distant from BFCL's ground truth for fine-tuning to help, regardless of format. BFCL-specific training data or stronger alignment between training corpus and target schema conventions would be required to improve over the CD baseline.
