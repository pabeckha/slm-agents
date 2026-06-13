---
name: checking-citations
description: Audit citation integrity, claim/source matching, quoting/plagiarism risk, and .bib hygiene in a LaTeX/biblatex thesis. Use when the user asks to verify citations, check references, find undefined or unused \cite keys, validate the bibliography, check for mis-citations or self-plagiarism, or prepare a thesis for a plagiarism tool such as Ouriginal.
---

# Checking Citations

Audit a LaTeX/biblatex thesis for citation problems across four layers. Run the
deterministic checks first (they are fast and objective), then do the
judgment-based reviews only on the sections the user cares about.

This skill does **not** replace a plagiarism service (DTU uses Ouriginal). It
catches the issues that cause plagiarism flags and reference errors *before*
submission.

## Workflow

Copy this checklist and check items off as you go:

```
- [ ] 1. Integrity + hygiene: run check_citations.py, report and fix findings
- [ ] 2. Bib hygiene: apply references/bib-hygiene.md to flagged entries
- [ ] 3. Claim/source match: spot-check per references/claim-source-match.md
- [ ] 4. Grounding: verify against fetched sources per references/citation-grounding.md
- [ ] 5. Quoting/plagiarism: scan per references/quoting-plagiarism.md
- [ ] 6. Summarize findings by severity; confirm fixes with the user
```

Run only the layers the user requested. Layers 1–2 are mechanical; layers 3–4
require reading prose and judgment, so scope them to specific chapters unless
the user asks for the whole document.

## 1. Citation integrity + bib hygiene (deterministic)

Run the checker from the repo root:

```bash
python3 .claude/skills/checking-citations/scripts/check_citations.py --tex-dir thesis
```

It reports four categories and exits non-zero on hard errors:

- **Undefined citations** (hard error): a `\cite` key with no `.bib` entry. Fix
  by correcting the key or adding the entry.
- **Duplicate keys** (hard error): same key defined twice in `.bib`. Merge them.
- **Unused entries** (warning): in `.bib` but never cited. Either cite or delete.
  Entries pulled in only by `\nocite{*}` show here; that is expected.
- **Malformed entries** (warning): missing required fields for the entry type, or
  a non-4-digit year.

No third-party packages required. The script handles `\cite`, `\citep`,
`\citet`, `\parencite`, `\textcite`, `\autocite`, etc., strips `%` comments, and
ignores the `\nocite{*}` wildcard.

For deeper `.bib` normalization (author formatting, DOIs, capitalization,
journal vs. booktitle), see [references/bib-hygiene.md](references/bib-hygiene.md).

## 2. Claim/source match (judgment)

Verify that each cited source plausibly supports the claim it is attached to.
This catches wrong-paper citations, citations of survey papers for primary
results, and overstated claims. See
[references/claim-source-match.md](references/claim-source-match.md) for the
review procedure and what to flag.

## 3. Citation grounding (anti-hallucination, web)

Verify against the **actually retrieved source** that each cited paper exists and
supports its claim, instead of trusting the model's memory. Extract identifiers
with `scripts/extract_sources.py`, fetch each source (arXiv abstract, URL, or
academic search), then compare. This catches fabricated references and
mis-attributed papers. Abstract-level by default: confirms existence and
headline claims, not numbers buried in tables. See
[references/citation-grounding.md](references/citation-grounding.md).

## 4. Quoting and plagiarism risk (judgment)

Find passages that a plagiarism tool would flag: long verbatim quotes without
quotation marks, direct quotes missing page numbers, and paraphrases that stay
too close to the source. See
[references/quoting-plagiarism.md](references/quoting-plagiarism.md).

## Reporting

Group findings by severity:

- **Must fix**: undefined citations, duplicate keys, unquoted verbatim text,
  mis-citations.
- **Should fix**: malformed `.bib` entries, missing page numbers, unused entries.
- **Consider**: hygiene/style normalization.

Show the user the list before editing files. Do not silently rewrite `.bib`
entries or prose; propose changes and let the user confirm, since wording and
citation choices are theirs.
