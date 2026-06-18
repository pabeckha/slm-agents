# Consistency sweep: 1–12B SLM definition + title/scope framing (Issue #178)

**Date:** 2026-06-18
**Scope:** Consistency sweeps owed after the title/scope change
("Evaluating Optimization Techniques for Reliable Tool Calling") and the
number corrections (handoff §5.4). Three checkboxes from #178.

## Methodology

- **SLM size alignment:** grepped the whole thesis for stray "10B" / "under 10" /
  "sub-10" and aligned to the 1–12B SLM definition, which is what the cited
  survey states (`sharma2025slmagents`, arXiv 2510.03847: *"Small language models
  (SLMs; 1-12B params, sometimes up to 20B)"*; confirmed in the #179 citation audit).
- **Framing scan:** read abstract, the three RQs, and the Contributions list for
  "reasoning" / "optimize" framing that over-promises against the trimmed title;
  confirmed nothing leads with reasoning as a co-equal contribution.
- **Regression check:** ran `make test` (thesis-consistency suite).

## Changes

| Location | Before | After |
|---|---|---|
| `02_background.tex:54` | "SLMs, typically under 10B parameters~\cite{sharma2025slmagents}" | "SLMs, commonly taken to span roughly 1 to 12 billion parameters~\cite{sharma2025slmagents}" (matches `01_introduction.tex:9` + source) |
| `02_background.tex:324` | "Qwen 2.5 7B … strongest open-weight models for tool use at sub-10B parameter scales" | "Qwen 2.5 7B … strongest open-weight SLMs for tool use" (drop competing boundary; use defined term) |
| `05_discussion.tex:518` | "Qwen 2.5 … strongest sub-10B models for tool use" | "Qwen 2.5 … strongest open-weight SLMs for tool use" |
| `01_introduction.tex:174` | "…marginal contribution to tool-calling accuracy and reasoning quality." | "…marginal contribution to tool-calling accuracy." (over-promise trim; consistent with intro:111 narrow reasoning scope and the tool-calling-only Contributions) |

## Framing — assessed clean (no change needed)

- **Abstract:** explicitly frames the gap as "a format compliance gap, not a
  reasoning gap"; reasoning appears only as the CoT technique being evaluated.
- **RQs (RQ1–RQ3):** all scoped to tool calling / optimization techniques /
  production viability.
- **Contributions (4 items):** all report tool-calling / BFCL accuracy; none lead
  with reasoning.
- **`01_introduction.tex:111`:** already de-scopes reasoning explicitly
  ("tool calling is evaluated directly … reasoning is operationalised narrowly").

## Outcome

- No residual stray "10B" / "sub-10" or "reasoning quality" in the thesis.
- `make test`: **91 passed** (96.00% / 1.5% / p-values reproduce; no regression).
  Tier-2 data layer skips in CI as expected (data/output gitignored).
