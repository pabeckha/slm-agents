# Citation audit & bibliography hygiene (Issue #179)

**Date:** 2026-06-18
**Scope:** Pre-submission integrity pass on thesis citations before the Ouriginal
plagiarism check. Covers the four layers of the `checking-citations` skill:
(1) integrity, (2) `.bib` hygiene, (3) claim/source grounding, (4) self-plagiarism.

## Methodology

- **Layer 1 (deterministic integrity):** ran
  `.claude/skills/checking-citations/scripts/check_citations.py --tex-dir thesis`.
- **Layer 3 (grounding):** fetched the actual sources for the two load-bearing,
  literature-backed quantitative claims flagged in the issue (SLM size definition
  and the frontier/BFCL comparison) and matched the cited number/range against the
  retrieved paper, rather than trusting recall. Both cited papers are 2025
  (post knowledge-cutoff), so web verification was mandatory.
- **Layer 4 (self-plagiarism):** compared `thesis/bibliography.bib` cite keys and
  thesis prose against the student's own `project_plan/` (`main.tex`, `bibliography.bib`)
  for shared keys and verbatim passage overlap.
- The student's *own* experimental figures (1.5% Config-B baseline, 96.00%/384-400
  B-template) are **out of scope** here — they belong to the data-consistency path
  (`runs/` + `make test`), not the citation audit.

## Findings

### Verified (issue's named must-check claims)

| Claim (location) | Cite key | Source | Result |
|---|---|---|---|
| SLM ≈ "1 to 12 billion parameters" (`01_introduction.tex:9`) | `sharma2025slmagents` (arXiv 2510.03847) | "Small language models (SLMs; 1-12B params, sometimes up to 20B)" | **Match** |
| "94.50% … same model … official BFCL harness, earlier revision" (`01_introduction.tex:43`) | `chen2025toleap` (arXiv 2505.11833) | ToLeaP Table 6, Qwen2.5-7B-Instruct, *simple (non-live)* = 94.50 | **Match** |

- **Layer 1:** clean — 34 keys cited / 34 entries; no undefined, duplicate, unused,
  or malformed entries.
- **Existence:** both 2025 sources fetched and confirmed real (correct titles/authors).

### Fixed (this audit)

- **`01_introduction.tex:7`** — the motivation sentence attributed
  "*most* individual tool calls are mechanically simple" to `sharma2025slmagents`.
  The survey supports the schema-/API-constrained framing but does **not** state a
  quantitative "most." Reworded to "*a large fraction of* individual tool calls are
  mechanically simple … the schema- and API-constrained regime where SLMs are most
  competitive", so the citation carries only the claim the source actually makes;
  the framing remains the author's own argument.

### Self-plagiarism vs `project_plan/`

- **No shared cite keys** between `project_plan/bibliography.bib` and
  `thesis/bibliography.bib`. A few of the *same papers* appear under different keys
  (LoRA, knowledge distillation) — not a concern.
- **No verbatim prose overlap.** Only generic field terminology recurs
  ("malformed structured outputs", "privacy-sensitive", "structured output
  generation"); the thesis motivation/background is independently rewritten and
  more developed. Low Ouriginal risk.

### Considered, not changed

- **`.bib` style inconsistency:** 2 entries (`sharma2025slmagents`, `taubench2024`)
  use `@misc` + `eprint`/`archivePrefix` (the more correct arXiv form); the other
  arXiv papers use `@article` + `journal = {arXiv preprint arXiv:…}`. Both render
  under biblatex. Left as-is: "normalizing" would mean degrading the two correct
  entries to the looser style for no bibliographic gain.

## Outcome

No must-fix integrity or mis-citation defects. One minor claim/source overstatement
corrected. Self-plagiarism risk low. Bibliography ready for the Ouriginal pass.
