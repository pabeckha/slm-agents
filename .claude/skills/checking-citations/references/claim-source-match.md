# Claim/Source Match Review

Goal: confirm each cited source actually supports the claim it is attached to.
This is a judgment task. Scope it to the chapters the user names rather than the
whole thesis at once.

## Procedure

For each citation in the target section:

1. Read the sentence containing the `\cite` and identify the **specific claim**
   it supports (a number, a method, a finding, a definition).
2. Read the matching `.bib` entry. Note the source type (primary paper, survey,
   blog, docs) and what it is actually about (from title/abstract/notes).
3. Judge whether the source type and topic fit the claim.

If the source text is not available locally, judge from the entry metadata and
flag anything that needs the user to open the PDF.

## What to flag

- **Wrong-paper citation**: claim is about method X but the cited paper is about
  method Y (e.g. citing the LoRA paper for a quantization result).
- **Survey cited for a primary result**: a specific empirical number attributed
  to a survey/review rather than the originating paper. Prefer the primary source.
- **Overstated claim**: prose says "proves" / "always" / "state of the art" but
  the source supports a weaker or narrower statement.
- **Citation-needed**: a factual or quantitative claim with no citation at all,
  especially in Background and Discussion.
- **Stale attribution**: "recent" or "current best" claims tied to an old source.
- **Self-citation drift**: the thesis's own earlier numbers cited to an external
  paper, or vice versa.

## Output

List each flag as:

```
[chapter:line] claim "<short quote>"
  cited: <bibkey> (<entry type>, <what it is about>)
  issue: <wrong-paper | survey-for-primary | overstated | citation-needed | ...>
  suggest: <fix>
```

Do not edit prose automatically. Propose the change and let the user decide,
since the underlying claim may need rewording, not just a citation swap.
