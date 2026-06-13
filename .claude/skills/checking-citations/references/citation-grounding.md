# Citation Grounding (anti-hallucination)

Goal: verify, against the **actually retrieved source**, that (a) each cited
paper really exists and (b) the source supports the claim made at the cite site.
The point is to ground judgments in fetched text, not the model's memory.

This is web-abstract-level by default: it confirms existence, topic, and
headline findings. It cannot confirm a specific number buried in a results table
from an abstract alone — flag those as "needs full text" rather than guessing.

## Step 1: extract resolvable identifiers

```bash
python3 .claude/skills/checking-citations/scripts/extract_sources.py --tex-dir thesis
```

Outputs JSON per cited key with a `resolve` field:

- `arxiv` → `fetch` is an arXiv abstract URL. Most reliable.
- `url` → `fetch` is the entry's URL.
- `title` → use `query` with academic search.
- `MISSING` → no `.bib` entry (already a hard error from check_citations.py).

Filter to the chapter under review using each record's `cited_in` list.

## Step 2: retrieve the real source

Per record, in this order:

1. `resolve == "arxiv"`: WebFetch the `fetch` URL. Extract the **title, authors,
   and abstract** from the page.
2. `resolve == "url"`: WebFetch the `fetch` URL. Extract title + the relevant
   passage.
3. `resolve == "title"`: search for the paper (consensus `search`, or WebSearch).
   Take the top result whose title and authors match the `.bib`.

Batch consensus searches at most 3 at a time. If a fetch fails or rate-limits,
mark the record `unverified` and move on; do not invent content.

## Step 3: existence check (catch fabricated references)

Compare the retrieved title/authors/year to the `.bib` entry:

- **No source found** for a plausible-looking entry → flag `possibly-fabricated`.
  AI-assisted bibliographies sometimes invent realistic-looking references.
- **Retrieved title or authors differ materially** from the `.bib` → flag
  `metadata-mismatch` (wrong key, or wrong paper attached to the key).
- Match → record a one-line source summary from the abstract.

## Step 4: grounding check (claim vs source)

For each `\cite` site of the key in the target chapter:

1. Identify the specific claim the citation supports.
2. Compare it to the retrieved abstract/passage summary.
3. Classify:
   - `supported` — abstract clearly backs the claim.
   - `plausible-needs-fulltext` — consistent with the abstract, but the specific
     detail (a number, an ablation) is not in the abstract. Note that the PDF is
     needed to confirm.
   - `unsupported` — the source is about something else, or contradicts the claim.
   - `overstated` — source supports a weaker version than the prose states.

## Output

```
[key] resolve=<arxiv|url|title>  existence=<ok|possibly-fabricated|metadata-mismatch>
  source: "<retrieved title>" — <1-line summary of abstract>
  claims:
    [chapter:line] "<claim quote>" → <supported|plausible-needs-fulltext|unsupported|overstated>
       note: <why / what to fix>
```

Report `unsupported`, `overstated`, `possibly-fabricated`, and
`metadata-mismatch` as must-fix. Always state when a verdict is abstract-only so
the user knows what still needs the full PDF. Never claim a number is verified
unless it appeared in retrieved text.
