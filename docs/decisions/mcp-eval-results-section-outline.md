# Results-section outline — GitHub MCP real-world eval (issue #174)

**Status:** outline for the student to write in own voice (thesis-voice rule). Bullets + validated tables only — no finished prose.
**Source data:** `data/output/github_mcp/*/results.json`, all metrics re-extracted 2026-06-18.
**Placement (student to decide):** the MCP eval is single-call selection from a 21-tool catalog — conceptually closer to the `multiple`/disambiguation work than to multi-turn `\section{Agentic Evaluation}` (tau-bench). Two options:
  - (a) standalone `\section{Real-World Tool Selection}` framed as the production-viability / RQ3 validation — **recommended**, it reads cleanly and isn't shoehorned next to multi-step agentics;
  - (b) `\subsection` under `\section{Agentic Evaluation}` after the tau-bench size sweep.
  Label `\label{sec:github-mcp}` either way.

---

## ⚠️ Framing decision that changes the headline (was a stale assumption in #174)

Issue #174 said "note the B-baseline staleness caveat (original 6% … CD/CDQ unaffected)." That instruction predates the rerun landing. **The rerun inverts the headline, it does not footnote it.**

- Original B run (2026-05-30, old lenient parser): Qwen-7B tool selection = **6%**.
- B rerun (2026-06-13, fixed no-guided parser, PR #163/#167): Qwen-7B tool selection = **92%**.
- **Do NOT print "6% → 96%" as the result.** Lead with the same-parser numbers. The 6% may appear once as a *methods aside* ("an earlier run under a stricter output parser scored 6%, illustrating parser sensitivity"), never as the CD contrast.

**Validations done before trusting the new numbers (both pass):**
1. CD/CDQ_Qwen have **0 parse failures** in 50 cases → the parser fix cannot touch the guided path → Qwen 92→96→98 is one consistent basis even though B is 06-13 and CD/CDQ are 05-31.
2. Cross-family CD<B cells (Llama-3B, gemma) are **real**: B and CD prompts are byte-identical; the CD errors are an interpretable over-constraint pattern (7× `search_issues`, 2× `update_issue`), not a pipeline bug. Valid to report.

**Open cross-chapter consistency flag (student to rule on — entangled with #176, do NOT fix by re-running BFCL):**
MCP baseline B = 92% (new parser) will sit in the same thesis as BFCL baseline B = 1.5% (old parser, `tab:baseline-results` line 17). An examiner will ask why the two baselines use different parsers. Recommended: one methodological sentence acknowledging both baselines are parser-sensitive and that the no-guided parser was hardened mid-project; cite the BFCL parser caveat already in the thesis. **Leave a marked placeholder for this sentence in the draft.**

---

## Outline

### Motivation (1 short para)
- BFCL `simple_python` shows the model one candidate function; tau-bench has a fixed/known catalog. Neither is a real MCP deployment.
- This eval: 21 real GitHub MCP tools, 50 NL prompts, predictions for the 11 read-only tools executed live against the GitHub REST API. Single-domain, hand-crafted → frame as a **targeted real-world validation**, not a BFCL replacement (limitation, state up front).
- Secondary question: does the RAG disambiguation collapse (−24pp from 1→many candidates) reappear at a real 21-tool scale?

### Result 1 — Headline (Qwen-7B, same-parser basis)
- Table `tab:mcp-qwen` below.
- Bullets:
  - **Load-bearing causal line — state it here, where 92% first appears:** B's 92% is the *hardened parser* recovering tool calls from free-form output. B now leans on parser engineering exactly the way BFCL's B-template leans on the native chat template. This is the answer to the examiner's "what does B even measure?" and the setup for the structural-guarantee point. (The 6% old-parser number is a one-clause aside on parser sensitivity, nothing more.)
  - CD adds **+4pp** tool selection over an already-strong B (92→96); arg accuracy flat at 80%.
  - **Quantization is free:** CDQ 98% tool / 80% arg — matches-or-beats CD at ~half the memory and faster load (~6s vs ~24s). Parser-independent (CDQ is 05-31, 0 parse failures). This is the clean win — lead the discussion with it.
  - Live execution 86–93% (HTTP <400) → predictions are real tool calls, not label-matching. The 3 CD exec failures are all `search_issues` HTTP 422 (NL phrase instead of GitHub search syntax) — a model-knowledge limit `guided_json` can't fix (string type only).

### Result 2 — Cross-family (the honest, examiner-proof narrative)
- Table `tab:mcp-cross-family` below (all 06-13, one parser).
- Bullets:
  - CD's accuracy benefit **concentrates on the weakest viable model**: Llama-3.2-1B **+36pp** (46→82).
  - For models that already comply, CD is **marginal or negative**: Phi-4-mini +2, Qwen-7B +4, **Llama-3.2-3B −14** (94→80).
  - gemma-3-1b sits **below the viability floor** — B 36%, CD 38%, arg ~22% — neither helps; too small to use the catalog.
  - **This confirms, not contradicts, the Baseline-section framing** (line 25): CD's value is the *structural guarantee* (valid call every time, any model/schema), not raw accuracy beating a capable model's own template. Mirror of B-template 96% > CD 72.75% in BFCL. Cross-reference `\ref{sec:baseline}` / Discussion.
  - Llama-3B regression mechanism: `guided_choice` over 21 tools shifts the 3B model toward the broad `search_issues` tool where the narrower read tool was correct (7/9 of the new errors). Real disambiguation cost of forcing a choice over a large catalog.

### Disambiguation question (answers the secondary motivation)
- RAG showed −24pp when candidate count grew. Here CD at 21 tools holds 96% on Qwen-7B → the RAG collapse was **retrieval noise, not a general tool-count scaling problem**. But the Llama-3B regression shows large catalogs *do* cost smaller models — nuance, not a flat "scale-free" claim.

### Limitations (tie to threats-to-validity)
- 50 cases, single domain, hand-crafted; write tools scored on selection+args only (not executed).
- Not end-to-end MCP transport — REST translation of `{fn,args}`.
- Baseline parser-sensitivity (the placeholder sentence above).

---

## Tables (numbers validated 2026-06-18, /50 unless noted)

### tab:mcp-qwen — headline, Qwen 2.5 7B
```latex
\begin{table}[ht]
\centering
\caption{GitHub MCP real-world eval, Qwen~2.5 7B-Instruct (50 NL prompts, 21-tool
catalog). All configurations scored under the hardened no-guided parser
(constrained-decoding outputs parse unconditionally; see Section~\ref{...}).}
\label{tab:github-mcp-qwen}
\begin{tabular}{lrrr}
\toprule
Config & Tool selection ($\uparrow$) & Arg accuracy ($\uparrow$) & Exec.\ success (read-only) \\
\midrule
B (baseline)        & 92.0\% (46/50) & 80.0\% (40/50) & 93.3\% (28/30) \\
CD                  & 96.0\% (48/50) & 80.0\% (40/50) & 90.0\% (27/30) \\
CD+Q (AWQ 4-bit)    & 98.0\% (49/50) & 80.0\% (40/50) & 86.2\% (25/29) \\
\bottomrule
\end{tabular}
\end{table}
```

### tab:mcp-cross-family — B vs CD per family (tool selection / arg accuracy)
```latex
\begin{table}[ht]
\centering
\caption{GitHub MCP tool selection and argument accuracy, baseline (B) vs.\
constrained decoding (CD), across model families (50 prompts each, single
parser). CD's benefit concentrates on the weakest viable model; for models
that already comply it is marginal or negative.}
\label{tab:github-mcp-cross-family}
\begin{tabular}{lrrrr}
\toprule
Model & B tool & CD tool & B arg & CD arg \\
\midrule
google/gemma-3-1b-it        & 36\% & 38\% & 24\% & 22\% \\
meta-llama/Llama-3.2-1B     & 46\% & 82\% & 34\% & 56\% \\
meta-llama/Llama-3.2-3B     & 94\% & 80\% & 74\% & 60\% \\
microsoft/Phi-4-mini        & 88\% & 90\% & 78\% & 78\% \\
Qwen/Qwen2.5-7B             & 92\% & 96\% & 80\% & 80\% \\
\bottomrule
\end{tabular}
\end{table}
```

Counts (for footnotes if wanted): gemma-3-1b B18/CD19 tool; Llama-1B B23/CD41; Llama-3B B47/CD40; Phi B44/CD45; Qwen B46/CD48 (all /50).

**Missing cell:** `gemma-3-4b` (job 28647094) produced no output dir on disk — only gemma-3-1b landed. Either re-run it or drop the row; do not leave a blank in the thesis table.

---

## Source provenance
- Qwen B: job rerun 2026-06-13T17:02; CD/CDQ: 2026-05-31 (`docs/decisions/github-mcp-eval-results.md`).
- Cross-family B+CD: 2026-06-13 (`scripts/hpc/run_github_mcp_cross_family.sh`). CD+Q cross-family not run (no per-family AWQ INT4) — omit those cells.
- By-cluster / by-difficulty breakdowns available in each `results.json` (`metrics.by_cluster`, `metrics.by_difficulty`) if a deeper table is wanted.
