# Technique-isolation (no-CD) size sweep — data is complete, but inclusion is not "free" (#159)

**Date:** 2026-06-20
**Status:** decision doc — surfaces a parser-sensitivity problem before any thesis edit.
**Refs:** #159, `table-fill-verification-2026-06-16.md`, `size-sweep-results.md`,
`base-baseline-parser-drift` memory, thesis Table 4.3 (`sec:technique-isolation`).

## Summary

The technique-isolation arm (each inference-time technique evaluated **without**
constrained decoding) is reported at 7B only in the thesis. Issue #159 asks to extend
it to 0.5B/1.5B/3B and fold the result into Tables 4.3 and 4.4.

The runs already exist on disk for all four sizes (zero new HPC work needed), and the
"3B conflict" previously recorded was a bookkeeping error (a Llama-3.2-3B run misread
as a Qwen re-run; corrected in `table-fill-verification-2026-06-16.md`).

**However, completing the table as written would weaken the thesis, not complete it.**
Under the lenient first-complete-object parser used for the isolation arm, the
smaller-size no-guided numbers are inflated and non-monotonic, and at 3B they invert
the central claim. This is the documented `base-baseline-parser-drift` effect in its
strongest form.

## The full grid (lenient parser, /400, all post-fix Qwen2.5)

| Config | 0.5B | 1.5B | 3B | 7B (in thesis) |
|---|---|---|---|---|
| B (no technique, no CD) | 26.00% (104) | 51.50% (206) | **65.75% (263)** | 62.00% (248) |
| PE-ng (few-shot, no CD) | 25.25% (101) | **53.50% (214)** | 65.25% (261) | 59.00% (236) |
| ITC-ng (CoT, no CD)     | 19.00% (76)  | 44.50% (178) | 58.25% (233) | 56.25% (225) |
| RAG-ng (retrieval, no CD)| 24.75% (99) | 43.25% (173) | 48.50% (194) | 52.00% (208) |
| FT-aligned-ng (no CD)   | 34.75% (139) | 27.50% (110) | 24.25% (97)  | 41.00% (164) |
| CD (guided) reference   | 51.50% (206) | 62.25% (249) | 64.75% (259) | 72.75% (291) |

CD references from `size-sweep-results.md` (FP16 guided). 7B isolation column matches
thesis Table 4.3 exactly (248/236/225/208/164).

## Why this is not "free to include"

### 1. CD's marginal contribution goes negative at 3B (CD − B-ng)

| Size | CD | B-ng (lenient) | CD contribution |
|---|---|---|---|
| 0.5B | 51.50% | 26.00% | **+25.50 pp** |
| 1.5B | 62.25% | 51.50% | +10.75 pp |
| 3B   | 64.75% | 65.75% | **−1.00 pp** |
| 7B   | 72.75% | 62.00% | +10.75 pp |

At 3B the no-technique, no-guided baseline *beats* constrained decoding under the
lenient parser. The same runs under the strict whole-completion parser give 3B B = 2.8%
(`size-sweep-results.md`), i.e. CD contribution +62 pp. **The sign of the headline
result at 3B is a parser-choice artifact.**

### 2. The 3B baseline is implausible on its face

3B B-ng (65.75%) > 7B B-ng (62.00%). A smaller model should not out-parse a larger one
on the same unguided task; this is parser inflation / no-guided run-to-run noise, not a
real capability ordering.

### 3. Two isolation-section claims break below 7B

- "CD alone outweighs every other method combined" — false at 3B (CD −1 pp).
- "none of the three prompt-level techniques exceeds [Config B]" — false at 1.5B,
  where PE-ng (53.50%) > B (51.50%).

Both claims are true at 7B, which is why the 7B-only table is internally consistent.

## Options

1. **Keep deferred (recommended).** Leave Table 4.3/4.4 at 7B; the conclusion already
   frames the smaller-size sweep as deliberate future work (#192). The data and this
   caveat are preserved here. Cost: none. Risk: none.
2. **Include with strict parser across all sizes.** Re-score every isolation run under
   the strict whole-completion parser so the parser is uniform with the headline
   integration floor. This restores monotonicity and a positive, growing CD
   contribution — but it is a re-scoring + re-write of the whole isolation section, and
   the strict floor (~1.5–4.8%) makes the prompt-level technique ordering nearly
   meaningless at small sizes (everything is near zero).
3. **Include lenient numbers as-is.** Not advised — hands an examiner a clean
   parser-sensitivity attack on the isolation framing.

## Recommendation

Option 1. The earlier "data is clean and free, so include it" read was half-right: the
data is free, but it is **not** clean for thesis inclusion. The deferred framing in #192
turns out to be load-bearing — it shields the thesis from the 3B sign-flip. If
size-completeness is wanted later, Option 2 (uniform strict parser) is the only honest
path and is a deliberate section rewrite, not a table fill.
