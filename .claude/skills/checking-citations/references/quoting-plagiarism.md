# Quoting and Plagiarism-Risk Review

Goal: find passages a plagiarism tool (DTU uses Ouriginal) would flag, and fix
them *before* submission. This is a judgment task over prose; scope it to the
chapters the user names.

This does not run a similarity check against external corpora. It catches the
patterns that produce flags: unattributed verbatim text, under-quoted material,
and over-close paraphrase.

## What to scan for

1. **Verbatim without quotes**: a sentence or clause copied word-for-word from a
   source but not wrapped in quotation marks or a `quote` environment. Even with
   a citation, verbatim text must be quoted.
2. **Direct quote missing page number**: biblatex direct quotes should carry a
   locator, e.g. `\textcite[p.~12]{key}` or `\parencite[p.~12]{key}`. Flag quoted
   text cited without a page/section.
3. **Over-close paraphrase**: same sentence structure and most words as the
   source with only synonyms swapped. Reword into independent phrasing or quote
   it directly.
4. **Definitions and standard phrasings**: boilerplate definitions lifted from a
   paper or Wikipedia. Rephrase in the author's own words.
5. **Self-plagiarism**: text reused from the author's own prior reports/papers
   without attribution. Cite the earlier work.
6. **Figure/table captions and data**: numbers or wording copied from a source
   table without attribution.

## Heuristics

- Sentences of 8+ consecutive words that read markedly different in tone from the
  surrounding prose are candidates for copied text.
- Technical definitions stated with unusual specificity often come verbatim from
  a source.
- A long passage with a single trailing citation may be paraphrasing more than
  one sentence than the citation appears to cover.

## Output

```
[chapter:line] "<short quote>"
  risk: <verbatim-unquoted | quote-no-page | close-paraphrase | self-plagiarism>
  suggest: <quote-and-cite | reword | add-locator | attribute>
```

Propose fixes; do not rewrite the author's prose automatically. For verbatim
text, offer both options: quote-and-cite, or reword into original phrasing.
