# .bib Hygiene

Goal: normalize `bibliography.bib` so entries are consistent, complete, and
render correctly under biblatex. Apply only to entries the checker flags or that
the user points at. Propose changes; let the user confirm before editing.

## Field completeness

Per entry type, ensure the required fields (the checker enforces these):

- `@article`: author, title, journal, year (+ volume, number, pages, doi)
- `@inproceedings`: author, title, booktitle, year (+ pages, publisher, doi)
- `@book`: author, title, publisher, year (+ edition, isbn)
- `@phdthesis` / `@mastersthesis`: author, title, school, year
- `@techreport`: author, title, institution, year (+ number)
- `@online` / `@misc`: title (+ author, year/date, url, urldate)

For `@online` and web sources, include `url` and `urldate` so the reference is
verifiable and dated.

## Consistency rules

- **Author format**: use `Last, First and Last, First`. Do not mix `First Last`
  and `Last, First` across entries. Keep full names or initials consistently.
- **Title capitalization**: biblatex lowercases titles by style. Protect proper
  nouns and acronyms with braces: `{LoRA}`, `{T}ransformer`, `{GPT}-4`.
- **Year vs date**: prefer a 4-digit `year`. If using `date`, keep it ISO
  (`YYYY` or `YYYY-MM-DD`); do not set both inconsistently.
- **DOIs**: add `doi` where available; drop the `http://doi.org/` prefix and keep
  the bare DOI. Avoid duplicate `url` + `doi` pointing at the same target.
- **Venue fields**: conference papers use `booktitle` (not `journal`); journal
  papers use `journal` (not `booktitle`).
- **arXiv preprints**: `@misc` or `@online` with `eprint`, `eprinttype = {arXiv}`,
  and `eprintclass`. If later published, cite the published version instead.

## Duplicates and keys

- Merge entries that describe the same work under one key.
- Keep citation keys in a consistent scheme (e.g. `authorYEARword`). Do not
  rename keys without updating every `\cite` in the `.tex` files.

## Verification after edits

Re-run the checker and rebuild to confirm no regressions:

```bash
python3 .claude/skills/checking-citations/scripts/check_citations.py --tex-dir thesis
cd thesis && latexmk -pdf -interaction=nonstopmode main.tex   # or the project build
```

Check `main.blg` (biber/bibtex log) for warnings about missing fields or empty
entries after the build.
