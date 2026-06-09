# McNemar's Exact Test on the FT-Aligned Deltas (2026-06-09)

## Question

Attach a significance level to the two paired 7B deltas in thesis Section 4.4.1:

1. CD vs CD+FT-aligned (thesis headline: 291/400 → 307/400, +4.0 pp)
2. CD+Q vs CD+Q+FT-aligned (thesis headline: 289/400 → 297/400, +2.0 pp)

McNemar's exact test needs the paired per-case predictions, re-scored from the
stored result files with `scripts/mcnemar_bfcl.py` (commit `006d2be`, which
fixed a `nan`/`inf` decode bug that had silently corrupted an earlier attempt).

## Provenance issue found along the way

The re-scored A-side accuracies do **not** match the thesis headlines, and the
cause is run-to-run variance plus file overwriting — not the decode bug
(decode is clean, zero failures):

- **CD 291/400** comes from the original baseline run (job 28142188, see
  `bfcl-simple-python-baseline.md`). That run predates the `runs/` manifests.
  The four manifests since (2026-05-03) score 290, 290, 290, 289. The stored
  per-case file is the latest run (289/400).
- **CD+Q 289/400** was reproduced by ~9 April runs, but the four most recent
  runs (2026-04-23 onward) and the stored file score 288/400 (the variance was
  already noted in `config-cdq-quantization-results.md`).
- Result files in `data/output/.../non_live/` are git-ignored and overwritten
  on every run, so the per-case data behind the exact thesis headline numbers
  is unrecoverable. Only summary manifests survive per run.
- Both **B-side files reproduce the thesis numbers exactly** (307/400 and
  297/400), so those are the original runs.

Run-to-run spread on the A-sides is 289–291 (CD) and 288–289 (CD+Q): ±1–2
cases, i.e. ±0.25–0.5 pp, consistent with the noise note from April.

## Results (on the stored paired files, clean decode)

### Comparison 1: CD (289/400) vs CD+FT-aligned (307/400)

| | count |
|---|---|
| both correct | 262 |
| both wrong | 66 |
| A wrong, B correct (b) | 45 |
| B wrong, A correct (c) | 27 |

**p = 0.044** (exact two-sided).

### Comparison 2: CD+Q (288/400) vs CD+Q+FT-aligned (297/400)

| | count |
|---|---|
| both correct | 251 |
| both wrong | 66 |
| A wrong, B correct (b) | 46 |
| B wrong, A correct (c) | 37 |

**p = 0.380** (exact two-sided).

## Interpretation

- Comparison 1 reaches p < 0.05, but only barely, and only on the one
  surviving CD run (the 289 one). Had the surviving file been one of the
  290/291 runs, the test would likely land at p ≈ 0.06–0.10. The significance
  claim is therefore fragile to run noise and should not be stated as a
  headline result.
- Comparison 2 is clearly not significant: the +2.0 pp quantized delta is
  well within what discordant-pair noise produces (46 vs 37).

## Thesis implication

Use the conservative framing for both deltas: report b, c, and p, state that
the single-category delta does not robustly reach significance on its own
(borderline for comparison 1, clearly not for comparison 2), and rest the
evidence for the format-alignment effect on its consistent positive direction
across all four model sizes. Do **not** insert "confirming the improvement is
statistically significant."

If the McNemar numbers are quoted alongside accuracies, quote the accuracies
of the actual paired files (289 and 288), footnoting the run-to-run spread,
rather than mixing the test with the headline 291/289 figures from
non-surviving runs.
