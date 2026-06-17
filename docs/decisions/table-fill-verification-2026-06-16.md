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

## #159 — technique isolation, no-guided (simple_python, /400) ⚠️ 3B CONFLICT

0.5B / 1.5B / 7B each have a single canonical post-parser-fix run (verified):

| Config | 0.5B | 1.5B | 7B |
|---|---|---|---|
| B (no_guided)   | 26.00% (104) | 51.50% (206) | 62.00% (248) |
| few-shot-ng     | 25.25% (101) | 53.50% (214) | 59.00% (236) |
| cot-ng          | 19.00% (76)  | 44.50% (178) | 56.25% (225) |
| rag-ng          | 24.75% (99)  | 43.25% (173) | 52.00% (208) |
| ft-aligned-ng   | 34.75% (139) | 27.50% (110) | 41.00% (164) |

**3B is unresolved — two post-fix runs per config disagree by ~30 cases:**

| Config | 06-12 run (handoff/draft cite) | 06-13/14 re-run ("latest") |
|---|---|---|
| B-ng        | 263/400 = 65.75% (06-12T23:35) | 233/400 = 58.25% (06-13T22:36) |
| few-shot-ng | 261/400 = 65.25% (06-12T20:01) | 223/400 = 55.75% (06-13T23:15) |
| cot-ng      | 233/400 = 58.25% (06-12T20:26) | 224/400 = 56.00% (06-14T00:51) |
| rag-ng      | 194/400 = 48.50% (06-12T20:17) | 198/400 = 49.50% (06-14T02:39) |
| ft-aligned-ng | 97/400 = 24.25% (06-12T21:02) | 9/400 = 2.25% (06-14T08:12, FAILED — ignore) |

Both 06-12 and 06-13/14 runs are post the 2026-06-12 ~18:56 parser fix, so this is
**not** a pre/post-parser split — it is the no-guided run-to-run drift documented in
`base-baseline-parser-drift` / `no-guided-parser-fix-results.md`. Needs a decision on
which 3B run is canonical (and ideally a why — a ~7 pp swing on 400 cases is large)
before the #159 3B row can be filled. The handoff #159 table and
`thesis/drafts/isolation-tables-corrected.tex` currently use the 06-12 values.
