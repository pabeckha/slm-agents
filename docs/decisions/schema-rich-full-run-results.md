# Schema-Rich Prompting, Full 400-Case Run + McNemar (2026-06-10)

## Question

Validate Config CD+schema (schema-enriched constrained decoding, PR #145) on
the full BFCL v4 `simple_python` set (400 cases) and test significance of the
delta over plain CD with McNemar's exact test.

## Methodology

- Job 28624501 (`run_bfcl_schema_rich`), Qwen2.5-7B-Instruct, vLLM, guided
  decoding, `schema_rich=true`, sequential, all 400 cases.
- Paired against the stored CD result file
  `data/output/bfcl_schema_pair/cd/.../BFCL_v4_simple_python_result.json`
  (290/400 — one of the known 289–291 run-noise band, see
  `mcnemar-significance-results.md`).
- Manifest: `data/output/bfcl_schema_pair/schema_rich/runs/2026-06-10T13-01-28_*.json`.

## Results

**CD+schema: 356/400 = 89.0%** vs CD 290/400 = 72.5% → **+16.5 pp**.

McNemar paired contingency:

| | count |
|---|---|
| both correct | 283 |
| both wrong | 37 |
| CD wrong, CD+schema correct (b) | 73 |
| CD+schema wrong, CD correct (c) | 7 |

**p < 0.00001** (exact two-sided), net b−c = 66.

Latency (full 400, sequential): mean 0.704s, median 0.650s, p95 1.086s —
essentially identical to plain CD (0.878s mean on the 100-case latency run),
so the schema enrichment costs nothing at inference time.

## Analysis

- Unlike the FT-aligned deltas (p = 0.044 and 0.380, fragile to run noise),
  this effect is unambiguous: 73 vs 7 discordant pairs cannot be produced by
  the ±1–2 case run-to-run variance documented earlier.
- Remaining 44 failures are dominated by ground-truth value strictness
  (e.g. `1e-05` vs `0.0001`, `'Los Angeles'` vs `'Los Angeles, CA'`,
  unit/enum mismatches), not structural or schema errors — i.e. close to the
  ceiling this scorer allows without value-level disambiguation in prompts.
- 89.0% closes most of the gap to the frontier baselines recorded in
  `frontier-baselines-bfcl.md`.

## Thesis implication

CD+schema is the strongest single technique measured so far on this category
(+16.5 pp over CD, p < 1e-5) and can be stated as statistically significant
without the hedging required for the FT-aligned deltas. Headline numbers for
the thesis: 290/400 → 356/400, b = 73, c = 7, McNemar exact p < 0.00001,
no latency cost.
