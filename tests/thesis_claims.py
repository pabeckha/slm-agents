"""Registry binding thesis claims to their source-of-truth data files.

This is the "snapshot" that the regression suite checks against. Each entry says:
"the thesis quotes <correct>/<total>, and some result file under <source_glob>
still reproduces that count." When you re-run an experiment (the data changes) or
edit a document (the quoted fraction changes), the tests in
test_thesis_consistency.py fail and tell you which claim drifted.

WHY A GLOB INSTEAD OF ONE FILE
  Most configs were re-run several times, producing many identically-named,
  timestamped files under runs/ (CD+Q alone has nine). Pinning one timestamp is
  both brittle (a fresh re-run adds a new file) and arbitrary. So a claim points
  at a glob and asserts that *at least one* matching file reproduces the count.

WHY NOT THE AGGREGATE scores/ FILES
  Several `scores/simple_python_scores.json` aggregates were overwritten by a
  later or different run and no longer match the thesis (e.g. bfcl_quant/scores
  reports 258/400, but the thesis CD+Q number is 289/400). Always bind to a glob
  whose files actually carry the count the thesis reports — verify with:
       grep -rl '"correct_count": <N>' data/output
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Claim:
    claim_id: str
    # repo-root-relative glob; >=1 matching JSON must carry the expected count
    source_glob: str
    correct: int
    total: int
    # docs/chapters that quote this number; checked for the "<correct>/<total>" string
    cited_in: tuple[str, ...] = field(default_factory=tuple)
    note: str = ""


_RESULTS = "thesis/chapters/04_results.tex"

CLAIMS: list[Claim] = [
    Claim(
        "b_no_guided_simple_python",
        "data/output/bfcl_no_guided/runs/*no_guided.json",
        6, 400,
        ("docs/decisions/config-b-no-guided-baseline.md", _RESULTS),
        "Base, generic prompt, no constrained decoding (1.5%).",
    ),
    Claim(
        "pe_few_shot_simple_python",
        "data/output/bfcl_few_shot/runs/*few_shot.json",
        281, 400,
        ("docs/decisions/config-pe-few-shot-results.md", _RESULTS),
        "Few-shot prompting + guided (70.25%).",
    ),
    Claim(
        "cdq_simple_python_awq",
        "data/output/bfcl_quant/runs/*guided.json",
        289, 400,
        ("docs/decisions/config-cdq-quantization-results.md", _RESULTS),
        "CD+Q (guided, AWQ INT4, 72.25%). The aggregate "
        "bfcl_quant/scores file reports 258/400, a different run — do not bind it.",
    ),
    Claim(
        "cdq_itc_simple_python",
        "data/output/bfcl_itc/runs/*cot.json",
        262, 400,
        ("docs/decisions/config-cdq-itc-results.md",),
        "CD+Q+ITC (in-thought chain), negative result (65.5%). The bfcl_itc/scores "
        "aggregate reports 232/400 — stale; bind to the run file.",
    ),
    Claim(
        "cdqrag_simple_python",
        "data/output/bfcl_rag/runs/*rag*.json",
        191, 400,
        ("docs/decisions/config-cdqrag-results.md",),
        "CD+Q+RAG top-5 (47.75%; doc rounds to 47.8%).",
    ),
    Claim(
        "cdqfta_simple_python",
        "data/output/bfcl_cdqft_aligned/runs/"
        "*7B-Instruct-merged-aligned-AWQ*ft.json",
        297, 400,
        ("docs/decisions/config-cdqfta-results.md",),
        "CD+Q+FT-aligned, 7B (74.25%).",
    ),
    Claim(
        "cd_ft_aligned_simple_python",
        "data/output/bfcl_ft_aligned/"
        "_work3_s242779_models_models_merged_Qwen_Qwen2.5-7B-Instruct-merged-aligned/"
        "scores/simple_python_scores.json",
        307, 400,
        ("docs/decisions/config-ft-lora-aligned-ablation.md",),
        "CD+FT-aligned, 7B (76.75%).",
    ),
    Claim(
        "schema_rich_simple_python",
        "data/output/bfcl_schema_pair/schema_rich/runs/"
        "*Qwen2.5-7B-Instruct_simple_python_guided_schema_rich.json",
        356, 400,
        ("docs/decisions/schema-rich-full-run-results.md",),
        "CD+schema-rich, 7B (89.0%).",
    ),
]


# Known unresolved discrepancies — documented, intentionally NOT asserted so the
# suite stays green. Resolve the data, then promote each to a Claim above.
KNOWN_ISSUES = """
- thesis CD baseline = 291/400 (72.75%) has no backing file in data/output
  (closest live runs are 289 and 290; the results docs note run-to-run drift of
  +/- one case). The mcnemar-significance doc attributes 291 to job 28142188.
  Locate/regenerate that run, then add a Claim.
- data/output/bfcl_quant/scores/simple_python_scores.json = 258/400 does not match
  the CD+Q number (289/400) quoted in the thesis; bfcl_itc/scores = 232/400 does
  not match the ITC number (262/400). The aggregate scores/ files for these
  configs are stale relative to the runs/ files. Decide whether to regenerate them.
- tau-bench retail "5/115" and github-mcp "49/50" are derived numbers (a mean
  across three runs, and a with-retry combined metric) with no single source file,
  so they are not registry claims. Guard them with a dedicated computation test if
  needed.
"""
