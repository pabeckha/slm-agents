# Thesis no-guided corrections — scope and remaining prose (Issue #172)

**Date:** 2026-06-18
**Depends on:** `no-guided-parser-fix-results.md` (verified corrected numbers).

## The decision (option A)

Config B's headline **1.50%** and the corrected no-guided **62.00%** are the
same 7B runs under a strict vs. a lenient JSON parser (see the parser-framing
section of `no-guided-parser-fix-results.md`). The chosen reconciliation:

- **Keep 1.50% as the headline**, framed as the strict whole-completion-parse
  floor of a naïve model-agnostic integration. Unchanged: `tab:baseline-results`
  (Table 4.1), intro, abstract, `tab:size-sweep-full` B row (3.50/4.75/2.75/1.50),
  full-ablation B row, frontier table, FT-only baseline reference, conclusion.
- **Switch to the lenient corrected numbers in the technique-isolation arm
  only** (`sec:technique-isolation`), labelled explicitly as a different parser.

Most of issue #172's other listed locations (size-sweep B row, abstract, intro,
FT) are therefore **intentionally left at the strict 1.5%** — they are correct
under the kept headline. Only the isolation section moves.

## Applied in-place (this PR, `04_results.tex`)

- `tab:isolation` (7B): B 1.50→**62.00**, RAG-ng 2.50→**52.00**,
  PE-ng 4.50→**59.00**, ITC-ng 26.25→**56.25**; "Delta vs B" recomputed
  (now negative for the three techniques); CD delta +71.25→**+10.75**.
  Caption now states the parser criterion and the 1.50% vs 62.00% relationship.
- `tab:cd-contribution` (7B): None **+10.75**, Few-shot **+11.25**,
  CoT **+9.25**, Retrieval **−4.25** (was +71.25/+65.75/+39.25/+45.25).
- The two analytical paragraphs were replaced with **factual data-reporting
  stubs**; the prior interpretive prose is preserved as `% TODO(#172)` bullets
  inline for rewrite in the author's voice (see below).

All-size reference tables (not built): `thesis/drafts/isolation-tables-corrected.tex`.

## Remaining prose to rewrite (author's voice — `% TODO(#172)` markers in `04_results.tex`)

The following claims **inverted** and the stubs must be rewritten, not just
renumbered:

1. **"None of the prompt techniques exceeds 27%"** → under the lenient parser the
   base is already 62.00%, and all three techniques sit *below* it
   (PE 59.00, ITC 56.25, RAG 52.00). Adding examples / a reasoning trace /
   retrieved context does not raise format compliance above plain prompting here.
2. **CoT "self-scaffolding / highest unguided technique"** → false; few-shot
   (59.00) now edges out CoT (56.25). Drop the self-scaffolding reading (it was
   an artifact of the buggy parser penalising configs unevenly).
3. **"CD is the dominant contributor (+39 to +66 pp)"** → CD's marginal
   contribution is now modest (+9 to +11 pp at 7B) and **negative for retrieval**
   (RAG-ng 52.00 > CD+Q+RAG 47.75). Reframe CD's value as the *structural format
   guarantee* (recovers the strict 1.50% floor to well-formed output for any
   model/schema) plus a modest margin — not accuracy dominance.

### Cross-reference caution for the rewrite

The thesis will legitimately state two CD-vs-Base gaps: **+71.25 pp** vs the
strict headline Base (1.50%, in the size-sweep / discussion §5) and **+10.75 pp**
vs the lenient isolation Base (62.00%). Make the parser distinction explicit
wherever both could be read together, so they do not look contradictory.

## Verification

- All corrected cells verified against `runs/2026-06-12T*` manifests (above doc).
- `make test`: 92 passed (headline 1.5% / 96.00% / p-values unchanged).
