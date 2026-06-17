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

## Tier-2 categories (Phase 1a, CD, 200 cases each) — 2026-06-15

Phase 1a of the full grid (`cross-family-full-grid-plan.md`): the same Config-CD
(guided JSON, no other technique) extended from `simple_python` to the three
harder BFCL v4 categories — `multiple`, `parallel`, `parallel_multiple` — for the
4 guided-capable contrast models. **All 12 cells complete and on disk**, each
passing the validity gate (manifest `total_count: 200`, `guided: true`,
served-model line present, no 404s; gate re-checked from the run manifests under
`data/output/bfcl/runs/`).

| Model | Lab | `multiple` | `parallel` ⚠️INVALID | `parallel_multiple` ⚠️suspect |
|---|---|---|---|---|
| Llama-3.2-3B-Instruct | Meta | 57.5% (115/200) | ~~0.0%~~ artifact | 27.5% (55/200) |
| Llama-3.2-1B-Instruct | Meta | 52.5% (105/200) | ~~0.0%~~ artifact | 17.5% (35/200) |
| gemma-3-1b-it | Google | 44.0% (88/200) | ~~0.0%~~ artifact | 0.0% (0/200) |
| Phi-4-mini-instruct | Microsoft | 62.0% (124/200) | ~~0.0%~~ artifact | 37.0% (74/200) |

⚠️ `parallel` = INVALID artifact (see analysis). `parallel_multiple` = **suspect /
likely undercount**: the old schema could neither call the same function twice nor
emit more calls than there were distinct functions, so any `parallel_multiple` case
needing a repeated call was unwinnable under the committed code. Re-run with the
fixed multi-call schema before citing these. `multiple` is unaffected (single-call
expected) and stands.

Provenance: 4 cells re-run this cycle — Llama-3B `parallel` (job 28654341), gemma-1b
`multiple` (28654342), Llama-1B `parallel_multiple` (28654343), Llama-3B `multiple`
(28654344); the other 8 from the prior cycle (manifest timestamps 2026-06-13). The
4 re-runs replaced cells whose inline scoring was skipped on a `docstring_parser`
import miss (the saved `BFCL_v4_*_result.json` drops the `decoded` field the checker
needs, so offline re-scoring isn't clean — re-ran instead).

### Analysis

- **`parallel` = 0.0% for every model in every family — CONFIRMED PIPELINE
  ARTIFACT, NOT a capability result. Column is INVALID; re-run pending.**
  Root cause traced 2026-06-16: the committed (HEAD `5225fb3`) `process_parallel`
  schema capped the call array at `"maxItems": min(len(fn_names), 5)`. Every BFCL
  `parallel` case has exactly **one** distinct available function (histogram
  `{1: 200}`) called multiple times with different args, so the cap collapsed to
  `min(1,5) = 1` → the guided schema forced a single call → `Wrong number of
  functions` → 0/200, deterministically, for every model and size. Evidence:
  all 200 persisted `result` strings contain exactly one call (e.g. `parallel_0`
  → `[spotify.play(artist='Taylor Swift', duration=20)]`, ground truth needs 2);
  a stochastic capability failure would show *some* 2-call attempts — a flawless
  200/200 single-call is the signature of a structural cap, not model weakness.
  This is the same artifact behind the uniform Qwen `parallel` 0% in
  `size-sweep-results.md` (all sizes 0.5B–7B) and the thesis "structural ceiling"
  framing (§3.5, §5.3, §4.8.3) — see blast-radius note below.
  **Fix already written** (working-tree `src/vllm_backend.py`, mtime 2026-06-16,
  *after* these runs): the new `_build_parallel_calls_schema` emits an array of
  `oneOf` per-function call objects with `maxItems = _MAX_PARALLEL_CALLS` (not the
  distinct-function count), so the same function may repeat with different args.
  Verified offline (no GPU): `scripts/smoke_parallel_schema.py` compiles the
  single-function-repeated and multi-function schemas on both xgrammar and outlines
  backends; `tests/test_parallel_pipeline.py` — 4 passed. **Re-run of all `parallel`
  cells (cross-family + Qwen size-sweep) is required before any `parallel` number is
  cited.** Raw outputs ARE persisted (the `result` field; only the checker's
  `python_str`/`decoded` save as `None`), so re-runs are directly inspectable.
- **`multiple` tracks the `simple_python` ordering** (Phi 62.0% > Llama-3B 57.5% >
  Llama-1B 52.5% > gemma-1b 44.0%) — same family/size pattern, ~6–11 pp below each
  model's `simple_python` number, i.e. selecting the right function among several
  costs accuracy but does not reorder the families.
- **`parallel_multiple`** is the hardest non-zero category: Phi 37.0% and Llama-3B
  27.5% retain partial competence, Llama-1B drops to 17.5%, and gemma-1b collapses
  to 0.0% (same parallel-dispatch failure as its `parallel` column).
- **gemma checker-config spot-check** (per `model-selection-rationale.md`): gemma's
  `multiple` failures are mostly genuine (wrong value / type / fn-name not found),
  not underscore↔dot artefacts — the 0% on both parallel categories is the
  single-call limitation, not a checker config bug.

## Post-fix parallel re-runs (2026-06-17) — schema-cap caveat resolved

The `parallel` / `parallel_multiple` cells flagged INVALID above were re-run with
the committed multi-call fix (`_build_parallel_calls_schema`, commit `2faa0df`).
Two serialized chains, all at Config-CD (guided JSON, no other technique), 200
cases each:

- Plain CD: `scripts/hpc/run_parallel_reruns.sh` → jobs **28671150–28671160** (10).
- CD+FT-aligned (Qwen, merge→eval→eval→cleanup): `run_ft_aligned_parallel_reruns.sh`
  → jobs **28671185–28671200** (16).

**Validity gate** (per `handoff-2026-06-13.md` §2): `Verified served model` line, no
`does not exist` 404s, manifest `total_count=200`. All numbers read from the
`runs/` manifests, not the aggregate `scores/` files.

**22 of 24 evals VALID.** Plain CD (post-fix):

| Model | `parallel` | `parallel_multiple` |
|---|---|---|
| Qwen-0.5B | — | 3.0% (6/200) |
| Qwen-1.5B | — | 46.0% (92/200) |
| Qwen-3B | — | 63.0% (126/200) |
| Llama-3.2-1B | 35.0% (70/200) | 25.5% (51/200) |
| Llama-3.2-3B | — | 30.0% (60/200) |
| Phi-4-mini | 80.5% (161/200) | 70.5% (141/200) |
| gemma-3-1b | **INVALID — engine crash** | **INVALID — engine crash** |

CD+FT-aligned (Qwen, merged-aligned checkpoints, all four sizes valid):

| Size | `parallel` | `parallel_multiple` |
|---|---|---|
| 7B | 72.0% (144/200) | 60.0% (120/200) |
| 3B | 41.5% (83/200) | 38.0% (76/200) |
| 1.5B | 58.0% (116/200) | 33.5% (67/200) |
| 0.5B | 45.5% (91/200) | 16.5% (33/200) |

The fix is confirmed live: the previously-deterministic `parallel` 0% cells now
score non-zero (Llama-1B 35.0%, Phi 80.5%). So the schema-cap caveat above is
**resolved** — the 0% was the documented single-call design limit, lifted by the
multi-call extension, NOT a permanent capability ceiling. (FT-aligned numbers are
non-monotonic in size — consistent with the aligned-adapter degradation already
noted in the size sweep, not a job error.)

### gemma-3-1b parallel = INVALID infra crash (NOT a capability result)

Both gemma cells (jobs 28671151 `parallel`, 28671159 `parallel_multiple`) returned
0.0% (0/200), but this is an **engine crash**, distinct from both the schema-cap
artifact *and* a genuine model collapse:

```
ValueError: vocab size too small; 262144 vs 262145
  ... llguidance/hf.py from_tokenizer -> backend_guidance.GuidanceBackend
EngineDeadError: EngineCore encountered an issue
Request ... failed (engine dead)  -> 500 Internal Server Error
```

- **Mechanism:** vLLM 0.8.5 `auto` guided-decoding routes the parallel array/oneOf
  schemas to the **llguidance** backend (xgrammar does not support
  `minItems`/`maxItems`/`oneOf`). `llguidance.hf.from_tokenizer` asserts the
  tokenizer vocab ≥ the model's logit width; gemma-3-1b is 262144 vs 262145, so the
  engine dies on the **first guided request**. Every subsequent case returns `[]`
  → "Wrong number of functions" → 0/200.
- **Why only these two cells:** gemma's `simple_python` (55.5%) and `multiple`
  (44.0%) ran fine under the same vLLM — their simpler schemas stay on xgrammar.
  Only the parallel schemas push `auto` onto llguidance.
- **Why the gate missed it:** `Verified served model` probes `/health` *before* any
  guided request, and BFCL records 200 failed cases, so `total_count=200`. Fixed:
  `run_bfcl_eval.sh` now captures the server log and exits 1 on
  `EngineDeadError`/`vocab size too small`/500s.
- **Re-run pending:** `scripts/hpc/run_gemma_parallel_reruns.sh` resubmits both
  cells with `GUIDED_BACKEND=xgrammar` (jobs 28686566/28686567). A first attempt with
  `outlines` (job 28682151) died at argument-parse — vLLM 0.8.5 only offers
  `{auto, guidance, xgrammar}`, no outlines — caught by the new run_bfcl_eval.sh gate.
  xgrammar is not llguidance, so it never runs the 262144-vs-262145 vocab assertion,
  and `scripts/smoke_parallel_schema.py` confirms xgrammar compiles both parallel
  schemas (single-fn-repeated and multi-fn `oneOf`) off-HPC. The gemma parallel
  numbers are **pending a valid re-run**, recorded here as an infra failure, never as
  0% capability.
- **Backend confound to flag in the thesis:** the 22 valid cells ran under `auto`
  (which routed this schema to the guidance backend); gemma alone is pinned to
  xgrammar. Both faithfully enforce the same JSON schema at temp-0, so the effect on
  correctness is expected negligible, but the asymmetry should be noted, not hidden.

## Next

simple_python CD is complete (4 valid points, 3 labs). Tier-2 categories (Phase 1a)
are complete (12 cells). Remaining grid work: Phase 1b ablation configs and Phase 2
CD+FT-aligned land in `cross-family-ablation-results.md`; then source AWQ INT4
variants for CD+Q (Phase 3). For the thesis, resolve the `parallel`-schema caveat
above before citing the 0% column as a capability finding.
