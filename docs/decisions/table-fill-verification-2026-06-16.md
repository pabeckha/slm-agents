# Source-of-truth verification for thesis table fills (#157/#158/#159)

**Date:** 2026-06-16. Numbers below were read from the per-config `runs/*.json`
manifests (`correct_count`/`total_count`), NOT from aggregate `scores/*.json`
(which are stale). Several "latest" runs are **failed re-runs** that must be ignored
— noted per cell.

## #157 — B-template control (`bfcl_template_baseline`, simple_python, /400) ✅ verified

| Size | Correct | Acc | Source run |
|---|---|---|---|
| 0.5B | 312/400 | 78.00% | 2026-06-11T08:04 |
| 1.5B | 339/400 | 84.75% | 2026-06-12T23:53 |
| 3B   | 380/400 | 95.00% | 2026-06-11T18:02 — **NOT** the 2026-06-14T03:19 run (0/400, failed) |
| 7B   | 384/400 | 96.00% | 2026-06-09T20:28 |

## #158 — CD vs CD+schema (`bfcl_schema_pair/{cd,schema_rich}`, /400) ✅ verified

Paired runs (same job runs both arms). NB the #158 "CD" column comes from
`schema_pair/cd`, which differs slightly from the standalone `bfcl/` dir
(e.g. 3B: paired CD 259/400 = 64.75% vs standalone 250/400 = 62.50%) — cite the
paired value for the schema delta.

| Size | CD | CD+schema | Δ pp |
|---|---|---|---|
| 0.5B | 51.50% (206) | 74.25% (297) | +22.75 |
| 1.5B | 62.25% (249) | 84.00% (336) | +21.75 |
| 3B   | 64.75% (259) | 88.00% (352) | +23.25 |
| 7B   | 72.50% (290) | 89.00% (356) | +16.50 |

## #159 — technique isolation, no-guided (simple_python, /400) ✅ all four sizes verified (correction 2026-06-20)

**CORRECTION (2026-06-20):** the "3B CONFLICT" recorded here on 06-16 was a
**bookkeeping error, not a real conflict**. The "06-13/14 re-run" column below was
actually **Llama-3.2-3B** runs, not a Qwen2.5-3B re-run — the cited timestamps
(06-13T22:36, 06-13T23:15, 06-14T00:51, 06-14T02:39, 06-14T08:12) all resolve to
`meta-llama_Llama-3.2-3B-Instruct` files, and their counts (233/223/224/198/9)
match the Llama 3B runs exactly. There is **one** canonical post-fix
Qwen2.5-3B run per config (all 06-12 evening, all post the ~18:56 parser fix), so
nothing needs reconciling. The "9/400 FAILED" ft-aligned that motivated the freeze
is the **Llama** run, not Qwen.

Canonical Qwen2.5 no-guided isolation grid (lenient first-complete-object parser,
all post-fix, /400; 7B column matches thesis Table 4.3):

| Config | 0.5B | 1.5B | 3B | 7B |
|---|---|---|---|---|
| B (no_guided)   | 26.00% (104) | 51.50% (206) | 65.75% (263) | 62.00% (248) |
| few-shot-ng     | 25.25% (101) | 53.50% (214) | 65.25% (261) | 59.00% (236) |
| cot-ng          | 19.00% (76)  | 44.50% (178) | 58.25% (233) | 56.25% (225) |
| rag-ng          | 24.75% (99)  | 43.25% (173) | 48.50% (194) | 52.00% (208) |
| ft-aligned-ng   | 34.75% (139) | 27.50% (110) | 24.25% (97)  | 41.00% (164) |

⚠️ **Do not treat the smaller-size rows as drop-in thesis material.** Under the
lenient parser these no-guided numbers are inflated and non-monotonic: 3B B-ng
(65.75%) exceeds 7B B-ng (62.00%) — implausible — and at 3B it also exceeds the
guided CD reference (64.75%), making CD's marginal contribution **−1.0 pp** at 3B,
versus **+62 pp** for the same runs under the strict whole-completion parser (3B
strict B = 2.8%, see `size-sweep-results.md`). PE-ng at 1.5B (53.50%) also exceeds
B (51.50%). The isolation section's claims ("CD alone outweighs every method
combined"; "none of the prompt-level techniques exceeds B") hold at 7B but **break
at 3B/1.5B under the lenient parser**. This is the `base-baseline-parser-drift`
effect in its strongest form — the *sign* of CD's contribution at 3B is a
parser-choice artifact. Full analysis: `isolation-size-complete-analysis.md`.
