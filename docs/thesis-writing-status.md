# Thesis Writing Status

**Date**: 2026-06-09
**Current page count**: 58 pages
**Target**: 40--60 pages (excl. preface and appendix)

## Chapter Status

| Chapter | Lines | Status |
|---------|-------|--------|
| Abstract | — | Written — up to date with all results |
| Ch.1 Introduction | 160 | Complete — motivation, motivating example, final numbers, cascade framing, RQs, contributions |
| Ch.2 Background | 461 | Complete — constrained decoding, quantization, LoRA, RAG, BFCL, τ-bench |
| Ch.3 Methodology | 382 | Complete — all 7 rungs of evaluation ladder, pipeline description |
| Ch.4 Results | 765 | Complete — all 11 configs, size sweep, τ-bench, multi-category BFCL (multiple/parallel/parallel_multiple), frontier comparison, capability decomposition |
| Ch.5 Discussion | 407 | Complete — scaling analysis, cost-benefit, limitations, practical implications, Relation to Prior Work |
| Ch.6 Conclusion | 188 | Complete — RQ answers, deployment guidelines, future work |
| App. A AI Disclosure | — | Written (Vancouver Convention, DTU guidelines) |
| App. B Hyperparameters | — | Written |
| App. C Full Results | — | Written |

## All Experiments Complete

| Config | Result |
|--------|--------|
| B (baseline) | 1.5% AST |
| CD | 72.75% AST |
| PE | 70.25% AST |
| CD+Q | 72.25% AST |
| CD+Q+ITC | 65.5% AST |
| CD+Q+RAG | 47.75% AST |
| CD+FT | 69.75% AST |
| FT-only | 13.75% AST |
| FT-aligned-ng | 13.25% AST |
| CD+FT-aligned | **76.75% AST** ← best |
| CD+Q+FT-aligned | 74.25% AST |
| τ-bench CD (retail, 7B) | 4.35% pass rate |
| Model-size sweep | Done — see `size-sweep-results.md` |
| τ-bench size sweep | Done — see `tau-bench-retail-results.md` |
| BFCL multiple/parallel/parallel_multiple | Done — CD 38.5% on parallel_multiple; FT-aligned 70.5% on multiple, 0% on parallel |

No pending HPC jobs.

## Remaining Work

### Done (pre-submission polish)
- [x] **#56** — Full read-through: figures, cross-references, bibliography, config label consistency (closed; merged in #134). Build is clean: 58 pages, no undefined references or citations, no float warnings.
- [x] **#108–#128** — Thesis review issues (21) closed; merged in #130, #133.

No open issues remain.

### Out of scope / dropped
- #36 — Real-world MCP evaluation: not done, out of scope for this submission

## What Was Completed Since Last Status (2026-04-26 → 2026-05-25)

- Figures: bar chart (all 11 configs), frontier comparison, CoT flip, RAG breakdown, LoRA training loss, memory vs. accuracy scatter — all added
- CD+Q+FT-aligned section (was stubbed, now written with 74.25% result)
- τ-bench size sweep section (Ch.4.6.1)
- Multi-category BFCL section (Ch.4.8: multiple/parallel/parallel_multiple)
- Discussion Ch.5: Relation to Prior Work section added
- Introduction: sharpened with final numbers in first section
- Conclusion: expanded Future Work with concrete directions and 4-rung decision ladder
- Page count grew from 36 → 56 pages (+20 pp)
