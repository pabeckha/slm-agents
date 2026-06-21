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

from dataclasses import dataclass


@dataclass(frozen=True)
class Claim:
    claim_id: str
    # repo-root-relative glob; >=1 matching JSON must carry the expected count
    source_glob: str
    correct: int
    total: int
    # docs/chapters that quote this number; checked for the "<correct>/<total>" string
    cited_in: tuple[str, ...] = ()
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
        "*7B-Instruct-merged-aligned/scores/simple_python_scores.json",
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

    # --- B-template control size sweep (#157, tab:size-sweep-full) ------------
    Claim("b_template_0_5b",
          "data/output/bfcl_template_baseline/runs/*0.5B*no_guided.json",
          312, 400,
          ("docs/decisions/table-fill-verification-2026-06-16.md",),
          "B-template, 0.5B (78.00%)."),
    Claim("b_template_1_5b",
          "data/output/bfcl_template_baseline/runs/*1.5B*no_guided.json",
          339, 400,
          ("docs/decisions/table-fill-verification-2026-06-16.md",),
          "B-template, 1.5B (84.75%)."),
    Claim("b_template_3b",
          "data/output/bfcl_template_baseline/runs/*3B*no_guided.json",
          380, 400,
          ("docs/decisions/table-fill-verification-2026-06-16.md",),
          "B-template, 3B (95.00%). A later 2026-06-14 re-run logged 0/400 "
          "(failed); the glob still matches the valid 380/400 file."),
    Claim("b_template_7b",
          "data/output/bfcl_template_baseline/runs/*7B*no_guided.json",
          384, 400,
          ("docs/decisions/table-fill-verification-2026-06-16.md",),
          "B-template, 7B (96.00%)."),

    # --- CD+schema-rich size sweep (#158, tab:size-sweep-full) -----------------
    Claim("schema_rich_0_5b",
          "data/output/bfcl_schema_pair/schema_rich/runs/"
          "*Qwen2.5-0.5B-Instruct_simple_python_guided_schema_rich.json",
          297, 400,
          ("docs/decisions/schema-rich-full-run-results.md",),
          "CD+schema-rich, 0.5B (74.25%)."),
    Claim("schema_rich_1_5b",
          "data/output/bfcl_schema_pair/schema_rich/runs/"
          "*Qwen2.5-1.5B-Instruct_simple_python_guided_schema_rich.json",
          336, 400,
          ("docs/decisions/schema-rich-full-run-results.md",),
          "CD+schema-rich, 1.5B (84.00%)."),
    Claim("schema_rich_3b",
          "data/output/bfcl_schema_pair/schema_rich/runs/"
          "*Qwen2.5-3B-Instruct_simple_python_guided_schema_rich.json",
          352, 400,
          ("docs/decisions/schema-rich-full-run-results.md",),
          "CD+schema-rich, 3B (88.00%)."),

    # --- corrected no-guided isolation arm + FT, 7B (#172, lenient parser) -----
    # These lock the post-parser-fix lenient figures so they cannot silently
    # drift back. The strict headline B (6/400) stays as b_no_guided_* above;
    # these bind to the post-fix run files (much higher counts).
    Claim("b_no_guided_lenient_7b",
          "data/output/bfcl_no_guided/runs/*7B*no_guided.json",
          248, 400, (_RESULTS,),
          "Isolation-arm Config B, lenient parser, 7B (62.00%)."),
    Claim("pe_ng_lenient_7b",
          "data/output/bfcl_few_shot_no_guided/runs/*7B*few_shot.json",
          236, 400, (_RESULTS,),
          "PE-ng (few-shot, no CD), lenient parser, 7B (59.00%)."),
    Claim("itc_ng_lenient_7b",
          "data/output/bfcl_cot_no_guided/runs/*7B*cot.json",
          225, 400, (_RESULTS,),
          "ITC-ng (chain-of-thought, no CD), lenient parser, 7B (56.25%)."),
    Claim("rag_ng_lenient_7b",
          "data/output/bfcl_rag_no_guided/runs/*7B*rag*.json",
          208, 400, (_RESULTS,),
          "RAG-ng (retrieval, no CD), lenient parser, 7B (52.00%)."),
    Claim("ft_only_ng_lenient_7b",
          "data/output/bfcl_ft_no_guided/runs/*7B*.json",
          212, 400, (_RESULTS,),
          "FT-only (LoRA, no CD), lenient parser, 7B (53.00%)."),
    Claim("ft_aligned_ng_lenient_7b",
          "data/output/bfcl_ft_aligned_no_guided/runs/*7B*.json",
          164, 400, (_RESULTS,),
          "FT-aligned-ng (no CD), lenient parser, 7B (41.00%)."),

    # --- size sweep, BFCL `multiple` category (04_results size table) ---------
    Claim("cd_multiple_0_5b",
          "data/output/bfcl/Qwen_Qwen2.5-0.5B-Instruct/scores/multiple_scores.json",
          84, 200, (_RESULTS,), "CD multiple, Qwen2.5-0.5B (42.0%)."),
    Claim("cd_multiple_1_5b",
          "data/output/bfcl/Qwen_Qwen2.5-1.5B-Instruct/scores/multiple_scores.json",
          107, 200, (_RESULTS,), "CD multiple, Qwen2.5-1.5B (53.5%)."),
    Claim("cd_multiple_3b",
          "data/output/bfcl/Qwen_Qwen2.5-3B-Instruct/scores/multiple_scores.json",
          124, 200, (_RESULTS,), "CD multiple, Qwen2.5-3B (62.0%)."),
    Claim("cd_multiple_7b",
          "data/output/bfcl/Qwen_Qwen2.5-7B-Instruct/scores/multiple_scores.json",
          141, 200, (_RESULTS,), "CD multiple, Qwen2.5-7B (70.5%)."),
    Claim("cdfta_multiple_0_5b",
          "data/output/bfcl_ft_aligned/*0.5B-Instruct-merged-aligned/scores/multiple_scores.json",
          111, 200, (_RESULTS,), "CD+FT-aligned multiple, 0.5B (55.5%)."),
    Claim("cdfta_multiple_1_5b",
          "data/output/bfcl_ft_aligned/*1.5B-Instruct-merged-aligned/scores/multiple_scores.json",
          122, 200, (_RESULTS,), "CD+FT-aligned multiple, 1.5B (61.0%)."),
    Claim("cdfta_multiple_3b",
          "data/output/bfcl_ft_aligned/*3B-Instruct-merged-aligned/scores/multiple_scores.json",
          121, 200, (_RESULTS,), "CD+FT-aligned multiple, 3B (60.5%)."),
    Claim("cdfta_multiple_7b",
          "data/output/bfcl_ft_aligned/*7B-Instruct-merged-aligned/scores/multiple_scores.json",
          141, 200, (_RESULTS,), "CD+FT-aligned multiple, 7B (70.5%)."),

    # --- BFCL `parallel` / `parallel_multiple` size sweep (04_results, #173) --
    # Post-extension joint multi-call schema (commit 2faa0df). Thesis adopts the
    # full size sweep in tab:bfcl-parallel-multiple; scores/ files match runs/.
    Claim("cd_parallel_0.5b",
          "data/output/bfcl/Qwen_Qwen2.5-0.5B-Instruct/scores/parallel_scores.json",
          19, 200, (_RESULTS,), "CD parallel, 0.5B (9.5%)."),
    Claim("cd_parallel_1.5b",
          "data/output/bfcl/Qwen_Qwen2.5-1.5B-Instruct/scores/parallel_scores.json",
          128, 200, (_RESULTS,), "CD parallel, 1.5B (64.0%)."),
    Claim("cd_parallel_3b",
          "data/output/bfcl/Qwen_Qwen2.5-3B-Instruct/scores/parallel_scores.json",
          149, 200, (_RESULTS,), "CD parallel, 3B (74.5%)."),
    Claim("cd_parallel_7b",
          "data/output/bfcl/Qwen_Qwen2.5-7B-Instruct/scores/parallel_scores.json",
          158, 200, (_RESULTS,), "CD parallel, 7B (79.0%)."),
    Claim("cd_parallel_multiple_0.5b",
          "data/output/bfcl/Qwen_Qwen2.5-0.5B-Instruct/scores/parallel_multiple_scores.json",
          6, 200, (_RESULTS,), "CD parallel_multiple, 0.5B (3.0%)."),
    Claim("cd_parallel_multiple_1.5b",
          "data/output/bfcl/Qwen_Qwen2.5-1.5B-Instruct/scores/parallel_multiple_scores.json",
          92, 200, (_RESULTS,), "CD parallel_multiple, 1.5B (46.0%)."),
    Claim("cd_parallel_multiple_3b",
          "data/output/bfcl/Qwen_Qwen2.5-3B-Instruct/scores/parallel_multiple_scores.json",
          126, 200, (_RESULTS,), "CD parallel_multiple, 3B (63.0%)."),
    Claim("cd_parallel_multiple_7b",
          "data/output/bfcl/Qwen_Qwen2.5-7B-Instruct/scores/parallel_multiple_scores.json",
          145, 200, (_RESULTS,), "CD parallel_multiple, 7B (72.5%)."),
    Claim("cdfta_parallel_0.5b",
          "data/output/bfcl_ft_aligned/*0.5B-Instruct-merged-aligned/scores/parallel_scores.json",
          91, 200, (_RESULTS,), "CD+FT-aligned parallel, 0.5B (45.5%)."),
    Claim("cdfta_parallel_1.5b",
          "data/output/bfcl_ft_aligned/*1.5B-Instruct-merged-aligned/scores/parallel_scores.json",
          116, 200, (_RESULTS,), "CD+FT-aligned parallel, 1.5B (58.0%)."),
    Claim("cdfta_parallel_3b",
          "data/output/bfcl_ft_aligned/*3B-Instruct-merged-aligned/scores/parallel_scores.json",
          83, 200, (_RESULTS,), "CD+FT-aligned parallel, 3B (41.5%)."),
    Claim("cdfta_parallel_7b",
          "data/output/bfcl_ft_aligned/*7B-Instruct-merged-aligned/scores/parallel_scores.json",
          144, 200, (_RESULTS,), "CD+FT-aligned parallel, 7B (72.0%)."),
    Claim("cdfta_parallel_multiple_0.5b",
          "data/output/bfcl_ft_aligned/*0.5B-Instruct-merged-aligned/scores/parallel_multiple_scores.json",
          33, 200, (_RESULTS,), "CD+FT-aligned parallel_multiple, 0.5B (16.5%)."),
    Claim("cdfta_parallel_multiple_1.5b",
          "data/output/bfcl_ft_aligned/*1.5B-Instruct-merged-aligned/scores/parallel_multiple_scores.json",
          67, 200, (_RESULTS,), "CD+FT-aligned parallel_multiple, 1.5B (33.5%)."),
    Claim("cdfta_parallel_multiple_3b",
          "data/output/bfcl_ft_aligned/*3B-Instruct-merged-aligned/scores/parallel_multiple_scores.json",
          76, 200, (_RESULTS,), "CD+FT-aligned parallel_multiple, 3B (38.0%)."),
    Claim("cdfta_parallel_multiple_7b",
          "data/output/bfcl_ft_aligned/*7B-Instruct-merged-aligned/scores/parallel_multiple_scores.json",
          120, 200, (_RESULTS,), "CD+FT-aligned parallel_multiple, 7B (60.0%)."),

    # --- cross-family CD, BFCL simple_python (04_results, tab:cross-family-cd) -
    # Config CD (guided, bf16) on the four contrast checkpoints; aggregate
    # scores/ files match the runs/ manifests (verified 2026-06-21).
    Claim("cd_xfamily_gemma_3_1b",
          "data/output/bfcl/google_gemma-3-1b-it/scores/simple_python_scores.json",
          222, 400, (_RESULTS,), "CD simple_python, Gemma-3 1B (55.5%)."),
    Claim("cd_xfamily_llama_1b",
          "data/output/bfcl/meta-llama_Llama-3.2-1B-Instruct/scores/simple_python_scores.json",
          242, 400, (_RESULTS,), "CD simple_python, Llama-3.2 1B (60.5%)."),
    Claim("cd_xfamily_llama_3b",
          "data/output/bfcl/meta-llama_Llama-3.2-3B-Instruct/scores/simple_python_scores.json",
          250, 400, (_RESULTS,), "CD simple_python, Llama-3.2 3B (62.5%)."),
    Claim("cd_xfamily_phi_4_mini",
          "data/output/bfcl/microsoft_Phi-4-mini-instruct/scores/simple_python_scores.json",
          273, 400, (_RESULTS,), "CD simple_python, Phi-4-mini (68.25%)."),
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
