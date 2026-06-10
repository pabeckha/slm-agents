# Handoff: HPC runs for the examiner-review follow-ups

Updated 2026-06-10. The original version of this document (written 2026-06-09)
defined three tasks after the examiner review; their outcomes are summarised
below, and the remaining work is tracked as GitHub issues #140, #141, and
#142. Everything runs from the HPC checkout at `~/Documents/slm-agents` on a
feature branch (never push to main; open a PR).

## Status of the original tasks

**Task 1 — Config B-template: done, merged (PR #139).** The native-template
control scored 96.00% (384/400) on `simple_python` with zero parse failures.
The number is inserted at all anchors (abstract, §1.1, §3.4, Table 4.1,
§5.3.1, RQ1), and the result forced a narrative correction: the residual
failures of the constrained pipeline are now attributed substantially to
schema information loss (the pipeline's prompts carry only parameter names
and types), not solely to the model's learned value priors. See
`docs/thesis-examiner-issues.md`, issue 1, for the full edit list.

**Task 2 — McNemar paired tests: done, merged (PR #139).** CD vs
CD+FT-aligned: b=45, c=27, p=0.044 (reported as borderline against the
observed run-to-run spread); CD+Q vs CD+Q+FT-aligned: b=46, c=37, p=0.38
(not significant). Two side findings came out of this and are already in the
thesis: the original per-case files behind the recorded 291/289 figures were
overwritten (results are git-ignored), and re-runs over the project period
vary by 1–2 cases out of 400, which falsified the old determinism claim
(§3.2.1, §4.2.1, and §5.3.1 corrected). Details in
`docs/decisions/mcnemar-significance-results.md`.

**Task 3 — latency table: still optional**, now tracked as issue #141.

## Current task: schema-enriched constrained decoding (issue #140)

This is the highest-value remaining experiment. B-template (96.00%) shows the
model resolves most cases when it sees the full schemas; the constrained
pipeline peaks at 76.75% (CD+FT-aligned) while withholding parameter
descriptions, defaults, and enumerations. If enriching the constrained
pipeline's prompt closes most of that 19.25 pp gap, the thesis headline
becomes "near-native accuracy with structural guarantees", and the future-work
paragraph in §6.3 becomes a main result.

### Implementation sketch

1. `src/schema.py`: extend `FunctionParameter` with optional `description`,
   `default`, and `enum` fields (keep `type` required so existing callers are
   unaffected).
2. `src/bfcl_adapter.py` (`bfcl_function_to_function_def`): populate the new
   fields from the BFCL property specs instead of dropping them.
3. `src/prompt.py` (`build_args_extraction_prompt`): when the new data is
   present, render one line per parameter (name, type, description, default,
   allowed values) instead of the current `name (type)` list. Gate it behind
   a flag so existing configs are unchanged.
4. `src/bfcl_adapter.py`: add a CLI flag (e.g. `--schema-rich`) and record it
   in the run manifest; add a job script
   (`scripts/hpc/run_bfcl_schema_rich.sh`, copy of `run_bfcl_eval.sh` with the
   flag and its own output dir).

Two design notes:

- **Prompt-only first.** Do not also add `enum` constraints to the
  `guided_json` schema in the first run; keeping the structural constraint
  identical to CD isolates the information effect. Enum-in-schema is a
  second variant worth running afterwards (it converts enum mismatches from
  semantic failures into structurally impossible outputs).
- **Run CD and CD+schema in the same session.** Result files are overwritten
  per run and accuracies drift 1–2 cases across sessions. Running both
  configs back-to-back gives a valid pair for
  `scripts/mcnemar_bfcl.py`, so the comparison comes with a paired p-value
  computed on files that reproduce each other's session.

### Evaluation and thesis insertion

- 7B `simple_python` first; if the gain is large, sweep 0.5B–3B.
- Insert: new row(s) in the results tables; rework the §5.1 passage that
  currently says carrying schema detail into the pipeline is "the most
  direct unexplored improvement"; update the §6.3 future-work paragraph
  (it becomes a completed experiment); revisit the abstract sentence on the
  residual failure attribution if the gap mostly closes.
- Either outcome is publishable in the thesis: a small gain would instead
  support the learned-value-priors interpretation and should be reported
  just as plainly.

## Optional tasks

- **Issue #141 — latency:** rerun B, CD, CD+Q (and optionally B-template)
  with `--limit 100`, capture per-request wall time, add a small table to
  §4.2.1, drop the "latency was not measured" caveat.
- **Issue #142 — leaderboard check:** look up Qwen2.5-7B-Instruct on the live
  BFCL v4 leaderboard; if present, add the official number to the §4.5
  comparability note; if absent, note that and close.

## Verification checklist for any thesis change

- [ ] `latexmk -pdf thesis/main.tex` compiles with no undefined references.
- [ ] Any new accuracy number is quoted identically everywhere it appears.
- [ ] Update `docs/thesis-examiner-issues.md` and close the GitHub issue.
- [ ] Feature branch, PR, no AI attribution in commits or PR text.
