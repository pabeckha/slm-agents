# Cross-Family Full-Grid Execution Plan (2026-06-13)

Goal: extend the cross-family contrast set from the targeted CD/simple_python slice
to a **full model × benchmark × technique grid**, matching the Qwen2.5 coverage.
Decision made by the student (override of the deferred design in
`model-selection-rationale.md` §6/§7); cost and deadline risk acknowledged.

## Runnable models

| Model | Guided configs (CD, CD+schema, CD+Q, CD+FT, ITC) | Non-guided configs (B, few-shot-ng, CoT-ng, RAG-ng) | tau-bench |
|---|---|---|---|
| Llama-3.2-1B | ✅ | ✅ | ✅ |
| Llama-3.2-3B | ✅ | ✅ | ✅ |
| gemma-3-1b | ✅ | ✅ | ✅ |
| Phi-4-mini | ✅ | ✅ | ✅ |
| **gemma-3-4b** | ❌ **multimodal — guided decoding not enforced on vLLM 0.8.5** | ✅ (no guided decoding to break) | ✅ |

**gemma-3-4b** is permanently excluded from every guided-decoding config on this
stack (confirmed root cause, see `cross-family-cd-results.md`). It MAY run the
free-generation configs and tau-bench; include it there only, clearly flagged.

## Phases (dependency-ordered; each respects the `uv sync` venv race)

### Phase 1 — inference-only, NO new infra (existing scripts, `$MODEL`/`$CATEGORY`)
- **1a (LAUNCHING NOW): Tier-2 categories.** `run_bfcl_eval.sh` CD on `multiple`,
  `parallel`, `parallel_multiple` for the 4 guided-capable models. 12 jobs, 4
  per-model chains.
- **1b: simple_python ablation configs** for the contrast models, mirroring Qwen:
  - Guided (4 models): `schema_rich`, `itc`, `template_baseline` (B-template),
    `few_shot` (guided), `rag` (guided).
  - Non-guided (4 + gemma-4b = 5 models): `no_guided` (B), `few_shot_no_guided`,
    `cot_no_guided`, `rag_no_guided`.
  - `latency` (4 models).
- **1c: GitHub MCP gaps.** gemma-1b B+CD (job 28648249, submitted). gemma-4b
  **B only** (CD blocked — guided).

### Phase 2 — CD+FT-aligned (needs training, no new data code)
Per model: `train_lora.sh` (FORMAT_VERSION=v2, applies the family's own template) →
`merge_lora.sh` → `run_bfcl_ft_aligned.sh` (guided) + `run_bfcl_ft_aligned_no_guided.sh`.
4 guided models (gemma-4b: only the no-guided arm, if at all). One LSF chain per model.

### Phase 3 — CD+Q and CD+Q+FT (needs AWQ quantization)
- CD+Q: `quantize_lora_merged.py` on each base instruct model → `run_bfcl_quant.sh`
  (CD eval of the AWQ model). 4 models.
- CD+Q+FT-aligned: quantize each Phase-2 merged-aligned model →
  `run_bfcl_cdqft_aligned.sh`. 4 models. Depends on Phase 2.

### Phase 4 — tau-bench
`run_tau_bench.sh` per model (retail env; `appl` env is also unrun for everyone —
decide whether to add it). 4–5 models.

## Tracking
Record every landed run in `cross-family-cd-results.md` (CD/categories) and a new
`cross-family-ablation-results.md` (techniques), applying the §2 validity gate
(served-model line, no 404s, manifest total_count). gemma scores: spot-check the
checker-config note. Estimated total: ~70–90 GPU jobs across the phases.
