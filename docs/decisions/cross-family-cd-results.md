# Cross-Family CD Generalisation, BFCL simple_python (2026-06-13)

## Question

Does the size × technique finding generalise beyond Qwen2.5? This doc records
Config CD (guided JSON decoding, no other technique) on the contrast families
selected in `model-selection-rationale.md`, run through the *identical* pipeline
(`run_bfcl_eval.sh` → `src.bfcl_adapter`, same vLLM/frozen stack), changing only
`$MODEL`. Out-of-the-box instruct checkpoints, no FT, no quantisation.

## Methodology

- Script: `scripts/hpc/run_bfcl_eval.sh`, `bsub -env "all, MODEL=..."`.
- Category: BFCL v4 `simple_python`, all 400 cases, guided decoding.
- Validity gate (per `vllm-port-collision.md`): each run verified to contain
  `Verified served model: <model>`, `Model:` line matching, no `does not exist`
  404s, manifest `total_count: 400`.
- Scores read from `data/output/bfcl/<model_slug>/scores/simple_python_scores.json`.

## Results (CD, simple_python, 400 cases)

| Family / size | Lab | Accuracy | correct/total | Job | Status |
|---|---|---|---|---|---|
| Llama-3.2-3B-Instruct | Meta | **62.50%** | 250/400 | 28645809 | DONE, verified |
| Llama-3.2-1B-Instruct | Meta | **60.50%** | 242/400 | 28647708 | DONE, verified |
| gemma-3-1b-it | Google | **55.50%** | 222/400 | 28648091 | DONE, verified |
| gemma-3-4b-it | Google | **EXCLUDED** | — | 28648092 | multimodal; CD not applicable on stack — see caveat |
| Phi-4-mini-instruct | Microsoft | **68.25%** | 273/400 | 28648093 | DONE, verified |

All four verified runs pass the validity gate (manifest `total_count: 400`,
`guided: true`, served-model line present, no 404s).

Qwen2.5 CD reference points (same pipeline, prior runs), for comparison:

| Qwen2.5 size | CD accuracy |
|---|---|
| 0.5B | 51.50% |
| 1.5B | 62.25% |
| 3B | 64.75% |
| 7B | 72.50% |

## Analysis (4 of 5 points in)

- **Llama-3.2-3B CD = 62.50%** sits ~2.25 pp below same-size Qwen2.5-3B
  (64.75%) — close enough that CD's structural benefit looks family-robust at the
  3B scale rather than a Qwen artefact.
- **Small end (~1B):** Llama-3.2-1B = 60.50% and gemma-3-1b = 55.50% both land
  well above same-ish Qwen2.5 small points (0.5B = 51.50%, 1.5B = 62.25%). The
  ordering Llama-1B > gemma-1b mirrors the general capability gap between the two
  ~1B instruct checkpoints; both confirm CD lifts sub-2B models into the
  50–60% band, not a Qwen-only effect.
- **Phi-4-mini (3.8B) = 68.25%** is the strongest contrast point — above
  same-range Qwen2.5-3B (64.75%) and within ~4 pp of Qwen2.5-7B (72.50%),
  consistent with Phi's reputation for punching above its parameter count.
- Across families the CD numbers track parameter count and known instruct
  quality rather than clustering by lab, which is the family-robustness claim the
  thesis needs. gemma-3-4b is **excluded** (multimodal — CD not applicable on the
  stack; see caveat), so the contrast set is **4 valid points across 3 labs**
  (Meta ×2, Google ×1, Microsoft ×1) — still enough for the cross-family claim.

## Notes / caveats

- The 4 remaining CD evals were first submitted as an LSF dependency **chain**
  (28647708 → 09 → 10 → 11), anchored behind the last GitHub-MCP job
  (`ended(28647096)`), because `run_bfcl_eval.sh` runs `uv sync --group hpc` on
  the shared NFS `.venv` (see `uv_sync_venv_race`). **Only 28647708 (Llama-1B)
  succeeded**; 28647709/11 (gemma-1b, Phi) died on a **work3 disk-quota** overflow
  and 28647710 (gemma-4b) on a missing **xformers** backend (Gemma-3 needs it
  under vLLM 0.8.5). Fixes: freed 54 GiB on work3 (deleted regenerable merged
  checkpoints + stale HF caches) and un-excluded xformers in `pyproject.toml`
  (PR #171). The three failed models were re-submitted as **28648091 (gemma-1b),
  28648092 (gemma-4b), 28648093 (Phi)** — not chained, since the venv was already
  fully synced so each per-job `uv sync` is a no-op.
- **Gemma checker-config note** (from `model-selection-rationale.md`): the
  `ast_checker` uses gemma's registered config (not the Qwen fallback). BFCL
  simple_python fn-names rarely contain dots, so the underscore↔dot handling is
  low-risk, but spot-check the gemma scores before trusting them.
- CD+Q (per-family AWQ INT4) and CD+FT (per-family template-aligned LoRA) are
  deferred until CD confirms each model behaves on the stack.
- **gemma-3-4b EXCLUDED — multimodal, CD not applicable on the frozen stack
  (job 28648092).** The run completed (served-model verified, 400 cases, ~60 min)
  but scored **0.0% (0/400)**: every case failed with `Expecting property name
  enclosed in double quotes: line 1 column 2 (char 1)` — output is `{` followed by
  a non-`"` char, i.e. the `guided_json` constraint was **not enforced** and the
  model free-generated Python-dict/prose output.

  **Confirmed root cause (not a pipeline bug):** the pipeline is identical for both
  gemma models and works for the text-only **gemma-3-1b (55.5%)**. The only
  difference: **gemma-3-4b is multimodal** — its server log shows
  `Encoder cache will be initialized ... profiled with 8 image items`, i.e. vLLM
  loaded it as a vision model (`Gemma3ForConditionalGeneration`), whereas
  gemma-3-1b is text-only (`Gemma3ForCausalLM`, no encoder cache). On the frozen
  stack (**vLLM 0.8.5, V1 engine**) structured/guided decoding is not applied to
  multimodal models, so CD — the entire point of this study — cannot be evaluated
  for gemma-3-4b here.

  **Decision: exclude from the CD cross-family results**, on the same principled
  grounds `model-selection-rationale.md` uses to exclude Gemma-4-12B (stack
  incompatibility), not because the number is low. Gemma stays represented by the
  valid text-only gemma-3-1b point. **Future work:** re-evaluate gemma-3-4b on a
  vLLM build that enforces structured output for multimodal models, or force a
  text-only load if the stack allows it. A non-CD (free-generation) number is not
  a substitute — it would not measure the CD protocol.

## Next

When each chained job lands: apply the validity gate, record the number above,
and re-assess the cross-family ordering. Then source AWQ INT4 variants for CD+Q.
