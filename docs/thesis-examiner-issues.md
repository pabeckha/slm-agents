# Examiner review issue tracker

Source: `thesis/main-examiner-review.md` (AI-assisted examiner review, 2026-06-09).
Status legend: [ ] open · [~] partially fixed (needs HPC data or author decision) · [x] fixed in working tree (2026-06-09).

## Critical

- [x] **1. Baseline fairness (RQ1 framing).** Reframed everywhere: the abstract,
  §1.1, §3.4, the §5.3.1 threats (new "Baseline construction" entry), and the RQ1
  answer now present 1.5% as the floor of a minimal model-agnostic integration.
  B-template run completed 2026-06-09: 96.00% (384/400) on simple_python with
  the native chat template and free decoding, zero parse failures. All five
  anchor passages plus the abstract now quote the measured 96.00% (ToLeaP
  94.50% kept in §1.1 as corroboration), and Table 4.1 gained a B-template row.
  Since B-template lands above CD, the framing is that constrained decoding's
  value is the structural guarantee and model-agnosticism, not raw accuracy
  superiority over the native template. Follow-on edits drawn from the code
  inspection (`FunctionParameter` stores only the type; prompts omit parameter
  descriptions, defaults, and enums): the residual-failure interpretation in
  §4.1/§5.1/§5.2, the abstract, and RQ2 now attribute much of the post-CD
  residual to this schema information loss rather than solely to learned value
  priors; the threats entry was extended; §4.5 gained a comparability caveat
  (B-template at 96% exceeds every v4 leaderboard frontier score, so
  cross-harness comparisons are indicative only); Step 1 of the deployment
  guidelines now says to benchmark the native template first; future work
  gained the schema-enriched CD prompt experiment.
- [x] **2. Parallel-category contradiction.** Root cause identified in
  `src/vllm_backend.py:process_parallel`: the parallel stage selects a set of
  distinct function names and runs one deterministic argument extraction per name,
  so at most one call per distinct function is possible. Methodology now documents
  the parallel selection stage; §4.8.2 explains the 0% mechanistically; the §5.3
  "one function name and one argument object per inference call" claim is replaced
  with the accurate per-distinct-function formulation that is consistent with the
  1–4 call distributions on parallel multiple.

## Major

- [x] **3. Figure 4.3 wrong denominator.** Figure regenerated as an outcome
  breakdown over all 400 cases (264 identical to CD+Q / 128 wrong function / 8
  wrong arguments); §4.2.4 prose now also decomposes the 209 incorrect cases
  (128 + 8 + 73 shared failures); caption fixed; §5.2 "66% of RAG failures"
  corrected to "66% of all test cases".
- [x] **4. No paired significance test.** McNemar's exact test run on the
  stored paired prediction files (2026-06-09, see
  `docs/decisions/mcnemar-significance-results.md`): CD vs CD+FT-aligned gives
  b=45, c=27, p=0.044 (borderline; the paired CD file scores 289/400 while
  recorded CD runs spread 289–291); CD+Q vs CD+Q+FT-aligned gives b=46, c=37,
  p=0.38 (not significant). §4.4.1 and §4.4.2 now report both tests with the
  conservative framing; the abstract and RQ2 hedge the quantized-retention
  claim. **Follow-on finding:** the reruns showed ±1–2 case variance across the
  project period, contradicting the original "identical re-runs" determinism
  claim; §3.2.1, §4.2.1, and the §5.3.1 single-run-protocol threat were
  corrected to state the ±0.5 pp run-to-run spread.
- [x] **5. τ-bench simulator confound.** Documented in §3.2.2 (departure from the
  reference setup), §4.6 (pass rate is a conservative estimate; comparisons not
  like-for-like), and a new "τ-bench user simulator" threat in §5.3.1.
- [x] **6. "Production-viable" defined.** Explicit two-part criterion added after
  the RQ list in §1.3 (accuracy ≥ lowest frontier score in the comparison set;
  fits a 24 GiB consumer GPU; scoped to single-call with escalation assumed).
  RQ3 in the conclusion and the abstract now answer against that criterion.
- [~] **7. "No additional inference cost" removed.** Abstract, §5.2, and the RQ2
  answer now say "no training, no extra parameters, no additional generated
  tokens" and explicitly state that guided decoding overhead is nonzero and
  latency was not measured.
  *Remaining (optional, HPC):* measure tokens/s for B vs CD vs CD+Q and add a
  small latency table.
- [x] **8. Mixed baselines and PE provenance.** Abstract deltas now quoted against
  the configuration each technique extends (2.5 / 6.75 / 24.5 pp); §5.2 and §5.5
  RAG drops unified at −24.5 pp vs CD+Q; §3.1.1 prose and Figure 3.1 redrawn so PE
  branches from CD at full precision (orange node, "+few-shot" arrow).

## Minor

- [x] **9. Fig 4.5 eleven bars.** CD+Q+FT-aligned (74.25%) bar added in
  `scripts/figures/plot_bfcl_results.py`; figure regenerated; verified in PDF.
- [x] **10. Duplicate paragraph in §4.6.1** deleted.
- [x] **11. Overstated selection claim** rephrased in §4.1: single-candidate
  selection cannot fail; multiple category cited as the real selection evidence.
- [x] **12. Rounding/precision drift.** §5.1.1 now uses exact values
  (3.75/1.75/0.25/0.50 pp) and "bfloat16 baseline"; conclusion RQ3 says bfloat16;
  RAG drop unified.
- [x] **13. Related work added.** Tam et al. 2024 (format restrictions vs
  reasoning) and XGrammar in §2.3.2 and §5.5; APIGen credited as the source of
  xlam-function-calling-60k in §2.8.2. All arXiv IDs verified
  (2408.02442, 2411.15100, 2406.18518, 2505.11833).
- [x] **14. Bibliography hygiene.** ICMJE entry cleaned (garbled note and bogus
  co-authors removed); prior-work citations removed from the own-result sentences
  in the RQ2 answer; ToLeaP entry added. Outlines remains credited to Willard and
  Louf (the library's original authors), which is defensible.
- [x] **15. "Reliable Reasoning" scope** addressed in §1.2: reasoning is
  operationalised narrowly (function selection, argument construction, one
  multi-step benchmark); general reasoning benchmarks declared out of scope.
- [x] **16. Code availability** footnote added in §3.1.2
  (github.com/pabeckha/slm-agents).

## Verification queue

- [x] Reference [20] (Sharma & Mehta 2025, arXiv:2510.03847) confirmed to exist.
- [x] Official-harness reference point found and cited (ToLeaP Table 6:
  Qwen2.5-7B-Instruct 94.50% non-live simple AST).
- [x] Leaderboard snapshot dates unified to 2026-06-04 (footnotes in §4.5 and
  Fig 4.6 caption; matches bib urldate).
- [x] Config B-template run on HPC (issue 1): 96.00% (384/400), run
  2026-06-09T20-28-36, `data/output/bfcl_template_baseline/`.
- [x] McNemar discordant counts from HPC result files (issue 4) — done
  2026-06-09; the original per-case files behind the exact 291/289 figures were
  overwritten, so the tests use the surviving paired files (CD at 289/400).
- [x] BFCL v4 leaderboard check (issue 1, GitHub issue #142) — done 2026-06-10
  with a major finding: no Qwen2.5-7B-Instruct entry exists, but the frontier
  scores previously quoted in Table 4.6 were the leaderboard's "Simple AST"
  column, an unweighted mean over Python (400), Java (100), and JavaScript (50)
  sub-categories. The correct same-category comparator is "Python Simple AST"
  (present only in `data_non_live.csv`, not in the page UI): Sonnet 4.5 97.75%,
  Opus 4.5 96.50%, Haiku 4.5 95.00%, Gemini 3 Pro 94.75%, GPT-4.1 91.00%,
  GPT-4.1-mini 91.00%, GPT-5-mini 78.75%. All frontier-parity claims were
  corrected (abstract, §1.1, §1.3, §1.4, Table 4.6, Figs 4.1/4.5/4.6, §4.5,
  §4.7, §5.1, §5.4, §6.1, §6.2); RQ3 now uses a split criterion (frontier
  parity: not met; cascade viability at p >= 0.70: met by four configurations).
  The B-template control (96.00%) falls inside the flagship band
  (94.75–97.75%), resolving the earlier cross-harness anomaly.
- [ ] Optional: guided decoding latency measurements (issue 7) — Task 3,
  tracked as GitHub issue #141.
- [ ] Follow-up experiment: schema-enriched constrained decoding (carry full
  parameter descriptions/defaults/enums into the guided prompt) — tracked as
  GitHub issue #140; highest-value remaining experiment.

## Build status

`latexmk -pdf main.tex` compiles cleanly (64 PDF pages); no undefined references
or citations; figures regenerated via `scripts/figures/plot_bfcl_results.py`.
