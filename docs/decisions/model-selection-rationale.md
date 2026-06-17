# Model Selection Rationale — Primary Family and Cross-Family Validation

**Date**: 2026-06-13
**Status**: decision record
**Scope**: justifies (a) the choice of Qwen2.5 as the primary model family for the
size × technique sweep, and (b) the choice of contrast families used to test whether
the findings generalise beyond a single lineage.

## 1. Selection framework

The thesis studies *optimization techniques* (constrained decoding, quantization,
LoRA, RAG) *as a function of model scale*. The model family is therefore an
experimental instrument, not an object of interest in itself. A defensible choice
must satisfy, in priority order:

1. **Size-ladder granularity in the small range.** Multiple sizes sharing one
   architecture so that "technique × scale" is a controlled sweep rather than a set
   of unrelated points.
2. **Lineage independence** (for any *second* family). A different lab, pretraining
   corpus and tokenizer. The more independent the contrast family, the stronger the
   external-validity claim.
3. **Compatibility with the frozen evaluation stack.** vLLM `0.8.5`,
   transformers `>=4.40,<4.52`, the BFCL backend and guided-decoding path that
   produced every Qwen result. Non-negotiable (see §5).
4. **Tool-calling pedigree.** Native function-calling chat template and benchmark
   standing — tempered by the fact that constrained decoding reduces reliance on the
   native template (see §4).
5. **License.** A permissive license eases redistribution and reproduction.

## 2. Why Qwen2.5 is the primary family

| Criterion | Qwen2.5 |
|---|---|
| Size ladder | **0.5 / 1.5 / 3 / 7B**, one architecture — four points below 7B |
| Tool-calling | Native FC template; top open small-model function-calling |
| License | Apache 2.0 |
| Stack | First-class vLLM 0.8.5 + guided decoding; xLAM FT-data compatible |

The decisive factor is the **size ladder**. No competing family offers four
distinct sizes below 7B under a single architecture:

- Llama 3.2 — only 1B and 3B in the small range (8B is a different generation).
- Gemma 3 — 1B then jumps to 4B, 12B, 27B.
- Phi — effectively one small size (mini ≈ 3.8B).
- SmolLM2/3 — 135M / 360M / 1.7B / 3B (no 7B-class point).

The size sweep that underpins the thesis is only possible because Qwen supplies that
granularity. Apache 2.0, native tool-calling and frozen-stack support make it the
natural backbone. **Lead with the size-ladder argument when defending this choice.**

## 3. Contrast families for generalisation

A reviewer will ask whether conclusions resting on a single lineage (Qwen) hold
elsewhere. To answer this, the core comparisons are replicated on **three
independent families**, each size-matched to Qwen's small range and runnable under
the CD protocol on the frozen stack (one selected checkpoint, gemma-3-4b, was later
excluded — multimodal, see §5a):

| Family | Lab | Small sizes (≈ Qwen match) | Lineage vs Qwen | Tool-calling | License | Frozen stack |
|---|---|---|---|---|---|---|
| **Llama 3.2** | Meta | 1B (≈1.5B), 3B (≈3B) | **Maximal** — canonical "other" to Qwen | Native, strong | Llama Community | ✅ |
| **Gemma 3** | Google | 1B (≈1.5B); 4B excluded* | High | Improved instruct | Gemma (custom) | ✅ 1B only (4B multimodal — see §5) |
| **Phi-4-mini** | Microsoft | 3.8B (≈3B) | High (synthetic-heavy data) | Native FC | **MIT** | ✅ |

Together with Qwen (Alibaba) this spans **four labs and four independent pretraining
pipelines** — a substantially stronger generalisation claim than a single contrast.

Ordering of evidentiary value:

1. **Llama 3.2** — the primary contrast. Meta-Llama vs Alibaba-Qwen is the standard
   cross-family axis in the literature, the comparison a reader most expects, and the
   most legible "does this generalise?" test. Size-matches Qwen's 1.5B/3B points
   cleanly.
2. **Gemma 3** — a second independent lab (Google). Only the text-only **1B** is
   usable on the frozen stack; the 4B is multimodal and its CD run was invalid (see
   §5), so Gemma contributes a single ~1B point.
3. **Phi-4-mini** — a third lab (Microsoft) with a distinct, synthetic-heavy training
   recipe and the cleanest license (MIT). Single size point, so it contributes a
   point comparison rather than a sweep.

## 4. Why "native tool-calling" is weighted lightly

The CD configurations use constrained decoding (guided / xgrammar), which forces
schema-valid output **regardless of the model's native chat template**. Under CD the
deciding factors are base capability and the model's behaviour under the grammar
constraint, not whether it ships a function-calling template. This is why criteria 2
(lineage independence) and 1/3 (size match, stack) dominate the contrast-family
choice, and why Gemma 3 — whose tool-calling is less first-class than Llama's —
remains a valid choice for the CD/CD+Q arms.

## 5. Excluded Gemma variants

### 5a. Gemma-3-4B — multimodal, CD not enforceable on the frozen stack

Selected as the ≈3B Gemma point, but its CD run (job 28648092, 2026-06-13) scored
**0.0% (0/400)**: every case produced output that the `guided_json` constraint failed
to shape (parse error at char 1 on all 400). **Confirmed cause:** gemma-3-4b is
**multimodal** — vLLM loads it as a vision model (`Gemma3ForConditionalGeneration`;
the server log initialises an image encoder cache), whereas the text-only gemma-3-1b
(`Gemma3ForCausalLM`) ran the *identical* pipeline and scored 55.5%. On the frozen
stack (**vLLM 0.8.5, V1 engine**) structured/guided decoding is not applied to
multimodal models, so the CD protocol — the whole point of the study — cannot be
evaluated for gemma-3-4b here. This is a stack limitation, not the model's tool-calling
ability and not a pipeline bug.

**Excluded** on the same principled basis as Gemma 4 below (stack incompatibility),
not because the number is low. Gemma stays represented by the valid text-only
gemma-3-1b point. **Future work:** re-evaluate gemma-3-4b on a vLLM build that enforces
structured output for multimodal models (or a forced text-only load). A free-generation
number is not a substitute — it would not measure CD. Full record:
`cross-family-cd-results.md`.

### 5b. Why Gemma 4 is excluded

Gemma 4 (released 2026-06-03; `Gemma4UnifiedForConditionalGeneration`,
`model_type: gemma4_unified`) is the newest option but is **incompatible with the
frozen stack**:

- Requires **transformers `5.10.0.dev0`** (a 5.x dev build) per its own
  `config.json`; the frozen stack pins transformers `<4.52`.
- Encoder-free 12B support landed only in a vLLM **nightly** (PR #44429), not in any
  stable release; the frozen stack pins vLLM `0.8.5`.

Running Gemma 4 would force a nightly vLLM + an unstable transformers major version.
Beyond the stability risk near the deadline, it introduces a **toolchain confound**:
every Qwen result was produced on vLLM 0.8.5 / transformers 4.x, so a Gemma-4 result
on a different stack would conflate "model family" with "toolchain version" — the
exact variable a cross-family comparison must hold fixed. Gemma 4 is recorded as
**future work**: re-running the full matrix on a refreshed, re-validated stack.

## 6. Reproducibility protocol — mirror the Qwen pipeline exactly

The cross-family runs preserve the Qwen experimental structure so that **model family
is the only variable that changes**:

- **Frozen environment.** vLLM `0.8.5`, transformers `>=4.40,<4.52`, pinned in
  `uv.lock`. The lockfile is the reproducibility record and is **not modified** for
  this work.
- **Same scripts, parameterised by `$MODEL`.** Contrast runs reuse the existing
  `scripts/hpc/run_bfcl.sh` (and the FT / quant scripts) unchanged — same BFCL
  version, same guided-decoding backend, same eval categories — differing only in the
  `MODEL` value. The Qwen-specific `download_model.sh` is left untouched; a separate
  parameterised downloader is added for the gated contrast repos.
- **bsub env passing.** Per the known DTU LSF quirk, `MODEL` is passed via
  `bsub -env "all, MODEL=..."` and the `Model:` line in the job log is verified
  before trusting results.
- **One caveat — FT-aligned cannot be byte-identical.** The xLAM LoRA data is
  rendered against Qwen's chat template. For CD+FT on a contrast family the *same*
  pipeline (`prepare_lora_data.py` → `train_lora.py` → `merge_lora.py`) is re-run with
  the family's own template. CD and CD+Q require no such change. FT is deferred until
  CD/CD+Q confirm each contrast model behaves on the stack.

## 7. Decision

- **Primary:** Qwen2.5 (0.5/1.5/3/7B) — justified by its unmatched small-size ladder.
- **Contrast families:** Llama 3.2 (1B, 3B), Gemma 3 (**1B only**), Phi-4-mini (3.8B)
  — three independent labs, size-matched, frozen-stack-compatible. Four valid CD
  points after the gemma-3-4b exclusion.
- **Configs replicated:** CD and CD+Q first (out-of-the-box); CD+FT after smoke
  tests, using per-family template-aligned LoRA data.
- **Excluded:** Gemma 4 — stack-incompatible (§5b); **gemma-3-4b** — multimodal, CD
  not enforceable on vLLM 0.8.5 (§5a). Both future work.
