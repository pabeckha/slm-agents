# Thesis update: `parallel` 0% is correct for the OLD design; a later extension lifts it

**Date:** 2026-06-16. **Status:** numbers pending (re-run chains 28671150–28671160
plain-CD and 28671185–28671200 CD+FT-aligned). These are *bullets for the student
to write from* — not finished prose.

## What is actually true (read methodology §387–401 first)

The thesis methodology **deliberately documents** the parallel selection stage: the
model emits a `{"calls": [...]}` object whose array length equals the number of
*distinct* candidate function names, and each name then goes through one deterministic
argument extraction. The stated rationale: at temperature 0, two calls to the same
function would get identical argument objects, so emitting one per distinct name is by
design. Every BFCL `parallel` case has exactly one distinct function, so the pipeline
emits one call → 0%.

So the original 0% is **a correct, methodologically valid result for the architecture
as evaluated** — not a measurement bug and not an "artifact" to retract. The code
(`maxItems = number of distinct candidates`) matches the documented design.

What changed: commit `2faa0df` ("joint guided multi-call generation",
`_build_parallel_calls_schema`) **extends the architecture** to generate a JSON array
of complete call objects jointly, so the same function can repeat with distinct args.
That is exactly the remedy the discussion already named as the requirement. Post-fix
(plain CD, Qwen, 200 cases): `parallel` 0.5/1.5/3/7B = **9.5 / 64.0 / 74.5 / 79.0%**;
7B `parallel_multiple` **38.5% → 72.5%**.

## Framing decision: extension, not retraction

**Do not call the old result wrong, and do not "retract" §5.3.** The honest framing:

1. The original single-extraction design genuinely cannot produce same-function
   parallel calls — a true, documented limitation of *that* architecture. Keep it.
2. §5.3's analytical core stays correct: the 0% was **structural**, not a soft limit
   that more training/scale would close. Keep that sentence verbatim.
3. The new contribution: implementing the schema the discussion named as the
   requirement (array of complete call objects, joint generation) extends the pipeline
   and lifts `parallel` to a normal size gradient.

Guardrails:
- The discussion *named* this remedy as future work; the new work *implements* it.
  Phrase it that way. Do **not** claim the analysis "predicted a fix to a bug" — it
  was a documented design choice, not a defect, so that phrasing would be spin an
  examiner reading the commit would catch.
- Do **not** over-correct into "parallel is solved": 0.5B is still ~9.5%. It remains
  a hard, size-sensitive category.

## Locations to edit (after the re-runs land)

- **`03_methodology.tex:387–401`** — keep the description of the old stage, but add
  that an extended joint-multi-call schema is evaluated (so methodology and results
  agree). Decide whether the old stage is "the baseline pipeline" and the extension a
  named variant.
- **`04_results.tex:997–1001`** — drop "since `parallel` already establishes [the
  ceiling], the size sweep was not extended to `parallel_multiple`." Now run at all
  four sizes; extend `tab:bfcl-parallel-multiple` to a size sweep.
- **`04_results.tex:1005–1015` (`tab:bfcl-parallel-multiple`)** — replace 7B-only
  CD/CD+FT-aligned with the post-extension size sweep.
- **`04_results.tex:1029–1035`** — the "`parallel_multiple` 38.5% > `parallel` 0.0%
  because same-function prompts collapse to one call" contrast was a property of the
  old design; replace with the post-extension comparison.
- **`04_results.tex:1037–1045` (Capability Decomposition)** — "Parallel calling of
  the same function is not achieved at any size" was true for the old pipeline only;
  reframe as: achievable under the extended schema, accuracy then follows size.
- **`05_discussion.tex:243–269`** — keep "not a soft limitation" + the named remedy;
  cut the permanent "ceiling … is therefore 0%" phrasing; state the extension was
  implemented and the size gradient confirms the limitation was the schema, not scale.
- **Search intro/conclusion** for `parallel` 0 / `ceiling` / `structural` echoes.

## Numbers still pending (fill when chains land; apply the §2 validity gate)

- Plain CD `parallel`: contrast families (Llama-1B, gemma-1b, Phi); Qwen done.
- Plain CD `parallel_multiple`: Qwen 0.5/1.5/3B + all four contrast families.
- CD+FT-aligned `parallel` and `parallel_multiple`: all four Qwen sizes.
- **Verify gemma-3-1b**: 0% pre-fix; confirm the post-fix run clears the validity gate
  *and* shows a non-degenerate call-count distribution (gemma is the one model where
  0% could be genuine collapse, not only the design limit).

## Note on the student's `cross-family-cd-results.md` (uncommitted)

That doc's Tier-2 section currently labels `parallel` 0% an "INVALID artifact /
PIPELINE ARTIFACT, NOT a capability result." Per the methodology check above that is
too strong — soften to the "correct-for-the-old-design, superseded by an extension"
framing before committing, to stay consistent with this note.
