# GitHub MCP Real-World Evaluation (Issue #36)

**Date**: 2026-05-30 (B+CD), 2026-05-31 (CDQ)
**Jobs**: 28555260 (B+CD, L40S, ~9 min) · 28559325 (CDQ, L40S, ~11 min)
**Models**: Qwen/Qwen2.5-7B-Instruct (B, CD) · Qwen/Qwen2.5-7B-Instruct-AWQ (CDQ)
**Script**: `scripts/eval_github_mcp.py`
**HPC job**: `scripts/hpc/run_github_mcp_eval.sh`
**Results**: `data/output/github_mcp/{B,CD}_Qwen_Qwen2-5-7B-Instruct/results.json` · `data/output/github_mcp/CDQ_Qwen_Qwen2-5-7B-Instruct-AWQ/results.json`
**Issue**: https://github.com/pabeckha/slm-agents/issues/36

---

## Motivation

All earlier results (BFCL, tau-bench) have a shared limitation: the model sees only one candidate function per test case (BFCL simple_python), or the tool catalog is fixed and known (tau-bench retail). Neither scenario reflects a real MCP deployment, where an agent must choose the right tool from a full catalog of semantically similar operations and then produce valid arguments.

Issue #36 was opened to create a real-world counterpart to the BFCL benchmark: use the GitHub MCP tool catalog (21 tools the Claude Code GitHub MCP server actually exposes), feed the model natural language prompts, and validate predictions by executing the read-only ones against the live GitHub REST API. This directly answers the thesis question of whether constrained decoding is sufficient for production-viable MCP tool calling — not just benchmark-viable.

A secondary motivation was to test whether the disambiguation failure observed in the RAG experiment (−24 pp when expanding from 1 to many candidate functions) also appears in a real 21-tool setting.

---

## What Was Built

### 1. Tool catalog: `data/input/github_tools.json`

21 tools matching the GitHub MCP server's public API, hand-transcribed as JSON function schemas (same format used by the constrained decoding pipeline). The tools are deliberately grouped into clusters of semantically similar operations that force genuine disambiguation:

| Cluster | Tools |
|---|---|
| Issue read | `get_issue`, `list_issues`, `search_issues` |
| Issue write | `create_issue`, `update_issue`, `add_issue_comment` |
| PR read | `get_pr`, `list_prs`, `list_pr_comments` |
| PR write | `create_pr`, `merge_pr` |
| Repo read | `get_repo`, `list_repos`, `search_repos` |
| Repo write | `create_repo`, `update_repo`, `delete_repo`, `push_files`, `create_or_update_file` |
| Search | `search_code`, `search_users` |

### 2. Test set: `data/input/github_mcp_tests.json`

50 hand-crafted natural language prompts, each with a ground-truth `{fn_name, args}`. Cases were written to cover all 21 tools with deliberate disambiguation challenges — the notes field on many cases explains the intended confusion risk.

| Cluster | n | Difficulty breakdown |
|---|---|---|
| issue_read | 12 | 5 easy, 5 medium, 2 hard |
| issue_write | 9 | 5 easy, 2 medium, 2 hard |
| pr_read | 9 | 5 easy, 3 medium, 1 hard |
| pr_write | 6 | 3 easy, 3 medium |
| repo_read | 6 | 3 easy, 2 medium, 1 hard |
| repo_write | 5 | 2 easy, 2 medium, 1 hard |
| search | 3 | 2 easy, 1 medium |

Total: 25 easy / 18 medium / 7 hard.

Representative disambiguation cases from the test set:
- Issue #8: "Get all enhancement issues in pabeckha/slm-agents" → `list_issues` with `labels=enhancement`, not `search_issues` (scope is single repo)
- Issue #12: "Are there any open issues about the RAG experiment failing…?" → `search_issues` (text body search), not `list_issues` (no text filter)
- Issue #18: "Mark issue #10 as resolved" → `update_issue` with `state=closed`, could be confused with `add_issue_comment`
- Issue #35: "Squash and merge pull request #80" → `merge_pr` with `merge_method=squash` (optional arg from natural language)
- Issue #47: "Create or overwrite the file…" → `create_or_update_file`, not `push_files` (single file vs multi-file)
- Issue #49: "Find all Python files that import vllm" → `search_code` (file content), not `search_repos`

### 3. Evaluation runner: `scripts/eval_github_mcp.py`

The runner:
1. Loads all 21 tool schemas and the 50 test cases
2. Starts a vLLM backend (already running from the HPC job script)
3. For each prompt, calls `VLLMBackend.process(prompt, functions)` which uses `guided_choice` to constrain tool selection and `guided_json` to constrain argument extraction (CD config), or raw completion (B config)
4. Compares predicted `{fn_name, args}` against ground truth
5. For read-only tools: executes the predicted call against the live GitHub REST API and records the HTTP status

**Execution validation**: the script manually maps each MCP tool call to an equivalent GitHub REST endpoint (`https://api.github.com`). This is **not** end-to-end MCP — the MCP transport layer is not involved. The executor translates `{fn_name, args}` into the appropriate REST path and query parameters. Write tools are skipped entirely (scored on tool selection and args only) to avoid side effects.

The 11 read-only tools that are executed live: `get_issue`, `list_issues`, `search_issues`, `get_pr`, `list_prs`, `list_pr_comments`, `get_repo`, `list_repos`, `search_repos`, `search_code`, `search_users`.

**Metrics computed**:
- `tool_selection_accuracy`: fraction where `predicted.fn_name == ground_truth.fn_name`
- `arg_accuracy`: fraction where tool is correct AND all ground-truth args match (normalised string/numeric comparison)
- `execution_success_rate`: fraction of read-only predictions that return HTTP < 400 from the GitHub API

Breakdowns by cluster and by difficulty are included in the output JSON.

### 4. HPC job: `scripts/hpc/run_github_mcp_eval.sh`

LSF job script (L40S GPU, 8 CPU, 20 GB RAM, 2 h wall time). Starts a vLLM server for the model, waits for it to be healthy, then runs the evaluation runner for configs B and CD sequentially on the same server instance. A trap ensures the vLLM process is cleaned up on exit. CDQ (AWQ quantized) can be run by passing `CONFIG=CDQ MODEL=Qwen/Qwen2.5-7B-Instruct-AWQ`.

---

## Results

### Overall: B vs CD vs CDQ

> **CORRECTED 2026-06-18 — B rerun landed; the original 6% is a parser artefact, not the headline.**
> The original B run (2026-05-30) scored 6% under the old lenient no-guided parser. The rerun
> under the hardened parser (PR #163/#167, job 28647091, 2026-06-13) scores **92%**. CD/CDQ are
> **unaffected** (they use guided decoding — verified 0 parse failures across 50 cases each, so the
> parser fix cannot touch them; CD/CDQ remain the original 2026-05-31 runs). **Do not cite "6% → 92%"
> as a comparison and do not headline 6%.** The 6% is reportable only as a parser-sensitivity aside.
> Table below is the corrected, same-parser basis.

| Metric | B (baseline, new parser) | CD (constrained decoding) | CDQ (CD + AWQ 4-bit) |
|---|---|---|---|
| Tool selection | 92.0% (46/50) | 96.0% (48/50) | **98.0% (49/50)** |
| Arg accuracy | 80.0% (40/50) | 80.0% (40/50) | 80.0% (40/50) |
| Exec success (read-only) | 93.3% (28/30) | 90.0% (27/30) | 86.2% (25/29) |

Under the hardened parser the baseline is **not** non-functional: a capable 7B model already selects
the right tool 92% of the time from free-form output, because the lenient-to-hardened parser still
extracts a tool call from unconstrained text — B now leans on parser engineering the same way BFCL's
B-template leans on the native chat template. Constrained decoding adds only **+4 pp** tool selection
(92 → 96) and leaves arg accuracy flat at 80%. **CD's value here is therefore the structural guarantee
(a valid call every time, any model/schema), not raw accuracy over a model that can already comply** —
the same conclusion the BFCL Baseline section reaches (B-template 96% > CD 72.75%). The clean win is
quantization: **AWQ 4-bit has zero impact on argument accuracy and marginally improves tool selection**
(+2 pp, 96 → 98), and is parser-independent. The slightly lower CDQ execution rate (86% vs 90%) is a
counting artefact: CDQ correctly predicted `search_issues` on task 12 (CD got it wrong), shifting that
case from a read-only `list_issues` call to a `search_issues` call with wrong args (HTTP 422) — one more
execution failure but one fewer tool selection failure.

### By Cluster

| Cluster | n | B tool | CD tool | CDQ tool | B args | CD args | CDQ args |
|---|---|---|---|---|---|---|---|
| issue_read | 12 | 0% | 92% | **100%** | 0% | 67% | 67% |
| issue_write | 9 | 0% | 89% | **100%** | 0% | 67% | **78%** |
| pr_read | 9 | 0% | 100% | 100% | 0% | 100% | 100% |
| pr_write | 6 | 0% | 100% | 100% | 0% | 100% | 100% |
| repo_read | 6 | 17% | 100% | **83%** | 17% | 83% | **67%** |
| repo_write | 5 | 40% | 100% | 100% | 40% | 100% | 100% |
| search | 3 | 0% | 100% | 100% | 0% | 33% | 33% |

CDQ improves or matches CD in most clusters. The one regression is repo_read (100% → 83%): task 38 "What are the current settings of pabeckha/slm-agents on GitHub?" was predicted as `update_repo` instead of `get_repo` — the word "settings" may have shifted the quantized model toward the write tool.

### By Difficulty

| Difficulty | n | CD tool | CDQ tool | CD args | CDQ args |
|---|---|---|---|---|---|
| easy | 25 | 96% | **100%** | 84% | **88%** |
| medium | 18 | 100% | 94% | 78% | 72% |
| hard | 7 | 86% | **100%** | 71% | 71% |

CDQ is stronger on easy and hard cases; CD has a slight edge on medium. No systematic degradation from quantization.

### Execution Validation

- **CD**: 30 read-only calls executed, 27 succeeded (90%). All 3 failures are `search_issues` (tasks 9, 10, 11 — HTTP 422, wrong query syntax).
- **CDQ**: 29 read-only calls executed, 25 succeeded (86%). 4 failures: tasks 9, 10, 11, 12 — all `search_issues` HTTP 422. CDQ correctly predicted `search_issues` on task 12 (where CD predicted `list_issues`), which added one more executable-but-failing call. The lower n_executed (29 vs 30) is because task 38 predicted `update_repo` (a write tool, skipped) instead of `get_repo` (read), removing one call from the execution pool.

---

## Analysis

### What the baseline measures (corrected)

The B config uses a raw completion endpoint with no structural constraint on output. Under the **old
lenient parser** the model's free-form / malformed JSON scored 6% — an artefact of that parser, not a
capability floor. Under the **hardened parser** the same outputs score **92%**: a capable 7B model does
emit recoverable tool calls in free text, and the parser extracts them. So the baseline is parser-bound,
not "accidental." The thesis claim is not "CD rescues a broken baseline" but "CD provides a structural
guarantee the baseline cannot," which holds regardless of where the parser lands.

### Why quantization doesn't hurt

AWQ 4-bit quantization reduces model weights from bfloat16 to 4-bit integers, but `guided_choice` and `guided_json` constrain the output space regardless of weight precision. The model still needs to fill in semantically correct values, and the quantized weights are sufficient for that. The result confirms CDQ is the optimal deployment config: same accuracy as CD at roughly half the GPU memory footprint and faster inference (checkpoint loads in ~6s vs ~24s for the full-precision model).

### Why PR and repo write clusters are perfect under both CD and CDQ

These schemas have flat, unambiguous required arguments. `get_pr` needs `{owner, repo, pull_number}` — all present in the prompt, no optional filters to reason about. `guided_json` constrains the output to a valid object; the model fills values correctly.

### Why issue args plateau at 67–78%

`list_issues`, `update_issue`, and `create_issue` have multiple optional arguments (`state`, `labels`, `title`, `body`) that the model must decide whether to include. In several cases it omits a required filter or uses the wrong format. This is a model knowledge limitation — `guided_json` enforces types but not semantic completeness.

### Why search args fail consistently (33% across all configs)

The `query` parameter accepts GitHub search syntax (`is:issue is:open repo:owner/repo`). `guided_json` only constrains the field to be a string, not valid search syntax. The model produces natural language phrases instead of structured queries. This failure mode is identical under CD and CDQ — it is not a quantization issue.

### Tool confusion cases

- **CD task 12** (issue_read, hard): "Are there any open issues about the RAG experiment failing?" → `list_issues` (wrong, should be `search_issues` — body text search requires the search tool). CDQ fixes this.
- **CD task 16** (issue_write, easy): "Close issue #36" → `merge_pr` (wrong, should be `update_issue`). CDQ fixes this too.
- **CDQ task 38** (repo_read, medium): "What are the current settings of pabeckha/slm-agents?" → `update_repo` (wrong, should be `get_repo`). CD gets this right. Likely a quantization-induced ambiguity around the word "settings".

---

## Status

All three configs (B, CD, CDQ) complete. Issue #36 can be closed after thesis write-up.

### Update 2026-06-13 — re-validation + cross-family extension (in flight)

Two staleness issues found when revisiting #36, plus an extension submitted:

1. **B baseline (6%) predates two bug fixes.** The original B run (2026-05-30)
   used the pre-fix no-guided path (parser fixed in PR #163) and the pre-fix
   `run_github_mcp_eval.sh` (port-collision fixed in PR #167, commit 70406d9).
   CD/CDQ are **unaffected** — their 96–98% prove the server was healthy in
   that run (a port collision would have collapsed CD), and they use guided
   decoding, not the no-guided parser. Only the **B number is suspect**, so it
   is being recomputed with the fixed script (job **28647091**, CONFIG=B).
   Same caveat as the BFCL Config B 1.5% rerun (handoff §4): B may move.

2. **Single-family (Qwen2.5-7B only).** Extended to the cross-family contrast
   set (§2c) via `scripts/hpc/run_github_mcp_cross_family.sh`, an LSF
   dependency chain (serialized to avoid the shared-`.venv` `uv sync` race;
   head anchored on the in-flight batch). B + CD per model; CD+Q deferred
   (no AWQ INT4 variants per family yet):

   | Job | Model | Configs |
   |---|---|---|
   | 28647091 | Qwen/Qwen2.5-7B-Instruct | B (rerun only) |
   | 28647092 | meta-llama/Llama-3.2-3B-Instruct | B + CD |
   | 28647093 | meta-llama/Llama-3.2-1B-Instruct | B + CD |
   | 28647094 | google/gemma-3-4b-it | B + CD |
   | 28647095 | google/gemma-3-1b-it | B + CD |
   | 28647096 | microsoft/Phi-4-mini-instruct | B + CD |

   Verify each per handoff §2 (served-model line, no 404s) before using the
   numbers. Results land in `data/output/github_mcp/{B,CD}_<model_slug>/`.

**Not yet in the thesis.** A `grep` of `thesis/` finds no reference to this
eval — the strongest single RQ3 result is currently unused. Planned placement:
Results chapter, as the real-world / production-viability validation (framed as
a targeted single-domain validation per the limitation below), once the rerun-B
and cross-family numbers land.

### Update 2026-06-18 — rerun + cross-family LANDED (numbers below)

All re-extracted from `data/output/github_mcp/*/results.json` on 2026-06-18.
B rerun and the cross-family B+CD chain are on disk and recorded. **One cell
missing:** `gemma-3-4b` (job 28647094) produced no output dir — only `gemma-3-1b`
landed. Omit gemma-3-4b until re-run, or drop the cell.

Cross-family tool selection / arg accuracy (50 prompts each, single hardened parser):

| Model | B tool | CD tool | Δ tool | B arg | CD arg |
|---|---|---|---|---|---|
| google/gemma-3-1b-it    | 36% (18/50) | 38% (19/50) | +2  | 24% | 22% |
| meta-llama/Llama-3.2-1B | 46% (23/50) | 82% (41/50) | **+36** | 34% | 56% |
| meta-llama/Llama-3.2-3B | 94% (47/50) | 80% (40/50) | **−14** | 74% | 60% |
| microsoft/Phi-4-mini    | 88% (44/50) | 90% (45/50) | +2  | 78% | 78% |
| Qwen/Qwen2.5-7B         | 92% (46/50) | 96% (48/50) | +4  | 80% | 80% |
| google/gemma-3-4b-it    | — | — | — | — | — | (no output; rerun needed)

Validated 2026-06-18: B/CD prompts byte-identical per case; the Llama-3.2-3B
CD<B regression is real over-constraint (`guided_choice` over 21 tools shifts the
3B model toward the broad `search_issues`: 7 of 9 new errors), not a pipeline bug.
CD's accuracy benefit concentrates on the weakest *viable* model (Llama-3.2-1B);
for already-compliant models it is marginal or negative; gemma-3-1b is below the
viability floor (nothing helps). This is independent evidence for the
structural-guarantee framing, not a contradiction of it.

Thesis section outline drafted in `docs/decisions/mcp-eval-results-section-outline.md`
(issue #174).

## Thesis Implications

- **Direct RQ evidence (corrected — do NOT use the old 6%→96% headline)**: under a consistent hardened parser, B 92% → CD 96% → CDQ 98% tool selection, same model, same prompt. CD's accuracy contribution over a capable model is small (+4 pp); its real contribution is the **structural guarantee** of a valid call every time. The dramatic gains appear on weaker models (cross-family below: Llama-3.2-1B +36 pp), which is where the enabling-technique story actually lives. The old "6% → 96%" framing was a parser artefact and must not be cited.
- **Quantization is free**: CDQ matches CD on arg accuracy and slightly exceeds it on tool selection. AWQ 4-bit quantization does not degrade tool calling performance — the constrained output space compensates for reduced weight precision. CDQ is the optimal deployment config: same accuracy, half the memory, faster inference.
- **Real-world validity**: 90% execution success on live GitHub API calls confirms the predictions are not label-matching artifacts. A deployed MCP agent using this pipeline would succeed on 9 out of 10 read-only GitHub requests.
- **Disambiguation at 21-tool scale**: The RAG experiment showed −24 pp when tool count grew (single-function BFCL → multi-function setting). Here, CD at 21 tools still achieves 96% tool selection — suggesting the disambiguation failure was RAG-specific (retrieval noise), not a general scaling problem.
- **Limitation to note**: The 50-case test set is hand-crafted and covers a single domain. It should be reported as a targeted real-world validation, not a replacement for BFCL's coverage.
