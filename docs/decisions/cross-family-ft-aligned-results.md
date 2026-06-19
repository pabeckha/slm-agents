# Cross-Family CD+FT-aligned, BFCL simple_python (2026-06-18)

## Question

Phase 2 of the cross-family grid (`cross-family-full-grid-plan.md`): does the
CD+FT-aligned finding from the Qwen2.5 size sweep (`config-ft-aligned-size-sweep.md`)
generalise across families? Same pipeline as `cross-family-cd-results.md`
(`run_bfcl_ft_aligned.sh` → merge LoRA → `src.bfcl_adapter`, frozen vLLM stack),
per-family format-aligned LoRA (xlam), changing only the base model. Each model run
twice on `simple_python`: **guided** (the CD+FT-aligned config) and **no-guided**
(free generation, same two-stage `/v1/completions` harness).

## Methodology

- Scripts: `scripts/hpc/run_bfcl_ft_aligned.sh` (guided) and
  `run_bfcl_ft_aligned_no_guided.sh`, each `bsub`-chained behind train→merge→eval→eval→cleanup.
- Category: BFCL v4 `simple_python`, all 400 cases.
- Jobs (latest pipeline, Phi-4-mini): train 28690185, merge 28690186,
  guided eval 28690187, no-guided eval 28690188, cleanup 28690189 — all exit 0,
  no LSF `Exited`/`TERM_*`, all reached `=== Done ===`. Earlier models
  (gemma-1b, Llama-1B, Llama-3B) from the same script across 2026-06-18.
- Numbers read from the `runs/` manifests, not aggregate `scores/` (per
  `results_source_of_truth`).

## Results (simple_python, 400 cases)

| Model | Lab | CD-only (instruct, guided) | CD+FT-aligned (guided) | FT Δ (guided) |
|---|---|---|---|---|
| gemma-3-1b-it | Google | 55.50% | 58.75% (235/400) | +3.25 pp |
| Llama-3.2-1B-Instruct | Meta | 60.50% | 63.00% (252/400) | +2.50 pp |
| Llama-3.2-3B-Instruct | Meta | 62.50% | 75.25% (301/400) | +12.75 pp |
| Phi-4-mini-instruct | Microsoft | 68.25% | 72.25% (289/400) | +4.00 pp |

CD-only values from `cross-family-cd-results.md`. The guided numbers are solid and
match the Qwen size-sweep pattern: FT-aligned helps at every family, non-monotonic
magnitude (Llama-3B gains most, +12.75 pp; the others +2.5–4 pp).

## The no-guided collapse (key finding)

The same FT-aligned checkpoints, evaluated **without** guided decoding, collapse to
near-zero — but the matched non-FT instruct models on the **identical** no-guided
harness do **not**:

| Model | instruct, no-guided | FT-aligned, no-guided | FT effect |
|---|---|---|---|
| gemma-3-1b-it | 156/400 (39.00%) | 15/400 (3.75%) | −35.25 pp |
| Llama-3.2-1B | 165/400 (41.25%) | 12/400 (3.00%) | −38.25 pp |
| Llama-3.2-3B | 233/400 (58.25%) | 9/400 (2.25%) | −56.00 pp |
| Phi-4-mini | 270/400 (67.50%) | **0/400 (0.00%)** | −67.50 pp |

instruct no-guided runs: single clean run each, hardened-parser era (2026-06-13/14).

**Interpretation — FT-induced dependence on the guided scaffold, not a harness floor.**
The discriminator is the non-FT column: free-generation on this two-stage raw-prompt
harness is *not* near-zero for everything — the instruct models free-generate
parseable tool calls at 39–67.5%. Only the format-aligned LoRA versions collapse. So
the aligned FT overfits the model to the constrained output format; remove the
constraint and it breaks.

**Mechanism (Phi-4-mini, job 28690188).** vLLM returned `200 OK` on all 400 requests;
the merged weights are sound (guided run = 289/400 on the same checkpoint). The
failures split into:
- 322/400 — function-name stage succeeded, **argument-extraction stage returned an
  empty string** (`no JSON object in completion: ''`).
- 78/400 — function-name stage itself returned empty (`ERROR:` with nothing after).

The empty-string (`''`) signature is EOS-as-first-token: prompted with `…JSON: `, the
FT-aligned Phi-4-mini emits its end-of-turn token immediately. Phi-4 is the extreme
(exactly 0) because it never emits a stray parseable JSON by chance; the other three
occasionally do (hence 2.25–3.75%).

**Parser-independent.** This is distinct from the no-guided parser drift in
`base_baseline_parser_drift` / `no-guided-parser-fix-results.md`: there the model
emitted non-empty but unparseable prose that a hardened parser later rescued
(MCP 6%→92%). Here the FT-aligned completions are literally empty — no parser can
recover a correct call from `''`. The collapse is a genuine behavioural shift caused
by FT, not a scoring artefact.

## Thesis implications

- The cleanest single illustration of the guided-decoding thesis: on the same merged
  Phi-4-mini weights, CD = 72.25% vs no-guided = 0%. Guided decoding is doing the
  entire job.
- Nuance to state honestly: format-aligned FT and guided decoding are
  **complementary-but-coupled**, not independent. The aligned adapter buys +2.5–12.75 pp
  *given* the guided scaffold, but it makes the model strictly worse than its own
  instruct checkpoint when the scaffold is removed. FT does not produce a model that
  stands alone; it produces one specialised to the constrained protocol.
- Cascade framing: a CD+FT-aligned small tier is only valid inside the guided-decoding
  pipeline. Reported small-tier competence must always be the guided number; the
  no-guided collapse is not a usable fallback.

## Next

Tier-2 categories (multiple / parallel / parallel_multiple) for CD+FT-aligned
cross-family remain, per `cross-family-full-grid-plan.md`. No further simple_python
runs needed — guided + no-guided are complete for all four contrast models.
