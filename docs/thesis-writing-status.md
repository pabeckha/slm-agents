# Thesis Writing Status

**Date**: 2026-04-26
**Current page count**: 36 pages
**Target**: 60--100 pages (DTU MSc standard)

## Chapter Status

| Chapter | Status | Notes |
|---------|--------|-------|
| Abstract | Written | Needs update when aligned FT + tau-bench results in |
| Ch.1 Introduction | Written | Thin (~2 pp), see gaps below |
| Ch.2 Background | Written | Thin (~4 pp related work), see gaps below |
| Ch.3 Methodology | Complete | All sections written |
| Ch.4 Results | Mostly complete | Aligned FT rows pending HPC jobs 28270250/28270251 |
| Ch.5 Discussion | Complete | Could go deeper on related work connections |
| Ch.6 Conclusion | Complete | |
| App. A AI Disclosure | Written | |
| App. B Hyperparameters | Written | |
| App. C Full Results | Written | Add aligned FT rows when available |

## Gaps by Priority

### Priority 1 — Figures (no figures exist yet, biggest single gap)

Every result comparison is currently prose + table only. Adding figures would
add 8--15 pages and make the thesis significantly clearer.

Figures to create:
- [ ] Bar chart: all 8 configs on BFCL simple_python (accuracy)
- [ ] Frontier comparison bar chart (SLM configs vs GPT-4.1, Claude, Gemini)
- [ ] CoT flip analysis: 24 gains vs 50 losses (stacked bar or sankey)
- [ ] RAG failure breakdown: 66% identical / 32% wrong function / 2% wrong params
- [ ] LoRA training loss curve (train + val loss vs epoch)
- [ ] Memory vs accuracy scatter (B, CD, CD+Q, FT configs)
- [ ] Evaluation pipeline diagram (two-stage: selection → extraction)

### Priority 2 — Background / Related Work expansion

Currently ~4 pages total. Target: 15--25 pages.

Topics to expand:
- [ ] Function calling benchmarks in depth (BFCL categories, tau-bench design)
- [ ] SLM survey: what Qwen 2.5, Phi-4, Llama 3.2 achieve on tool use
- [ ] Constrained decoding literature beyond Willard & Louf (Outlines, LMQL, vLLM)
- [ ] Prior LoRA fine-tuning for tool use (ToolLLM, Gorilla, xLAM paper)
- [ ] Cascade / mixture-of-experts LLM routing prior work

### Priority 3 — Pending experimental results

- [ ] Aligned FT ablation results (HPC jobs 28270250, 28270251 -- PEND as of 2026-04-26)
  - Add CD+FT-aligned and FT-aligned-ng rows to Ch.4 Combined Configurations
  - Add one paragraph to Ch.5 Discussion
  - Update abstract and conclusion when final numbers are in
- [ ] tau-bench retail results -- ongoing
  - New section in Ch.4 Results
  - New subsection in Ch.5 Discussion
- [ ] BFCL harder categories (multiple_function, parallel_function) -- not yet run
- [ ] Real-world MCP evaluation: GitHub 21-tool catalog, real execution (Issue #36)

### Priority 4 — Introduction expansion

Currently ~2 pages. Could expand:
- [ ] Concrete motivating example: show an actual SLM failure on a tool-calling query
- [ ] Clearer framing of the cascade architecture hypothesis
- [ ] More specific contributions (tie each to a result number)

### Priority 5 — Discussion depth

- [ ] Connect CoT finding to Wei et al. 2022 and Snell et al. 2024
- [ ] Connect RAG disambiguation finding to prior SLM tool-selection work
- [ ] Deeper cascade architecture section: routing heuristics, cost model

## Citation Fixes Applied

- `lin2023awq` → `lin2024awq` (fixed in Introduction)
- `yao2024taubench` → `taubench2024` (fixed in Introduction)
- `zhang2024xlam` added to bibliography (xLAM paper, arXiv 2409.03215)
