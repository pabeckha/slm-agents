---
name: thesis-red-team
description: Critique a thesis, dissertation, academic report, thesis PDF, LaTeX source, examiner review, or research writeup as an adversarial reviewer. Use when Codex should find gaps, overclaims, weak evidence, methodological flaws, statistical issues, citation problems, internal inconsistencies, missing limitations, defense risks, or potential errors before submission or defense.
---

# Thesis Red Team

## Overview

Use this skill to stress-test a thesis as a critical examiner would. The goal is not to polish prose, but to find what could be wrong, overstated, under-supported, inconsistent, or vulnerable in a defense.

## Required Reading

Before producing the critique, read `references/red-team-rubric.md`. If the target is a PDF and editable source exists nearby, inspect the source files too so comments can point to stable files and sections.

## Workflow

1. Identify the artifact and scope:
   - PDF, LaTeX source, chapter, abstract, review note, or whole thesis.
   - Submission stage: early draft, pre-defense, final polish, or examiner preparation when known.
2. Map the thesis claims before criticizing:
   - Main research questions and contributions.
   - Strongest empirical claims and headline numbers.
   - Scope boundaries and limitations.
   - Evidence used for each claim.
3. Attack the argument from multiple angles:
   - Methodology and experimental design.
   - Technical and mathematical correctness.
   - Statistical validity and uncertainty.
   - Benchmark and dataset fit.
   - Baselines, controls, and comparability.
   - Citation accuracy and related-work framing.
   - Practical or business relevance.
   - Internal consistency between abstract, introduction, results, discussion, and conclusion.
4. Separate real issues from preference:
   - Mark severity as Critical, Major, Minor, or Question.
   - Explain why each issue matters for grading, validity, or defense.
   - Give a concrete fix or mitigation.
5. Preserve academic ownership:
   - Do not invent results, citations, or experiments.
   - Do not add AI attribution.
   - Do not soften serious issues to be polite.
   - Do not overstate criticism when the text already scopes the claim correctly.

## Output Format

Lead with findings, ordered by severity. Use this structure unless the user asks for a different format:

```markdown
# Red-Team Thesis Review

## Executive Risk Summary
[Short paragraph: strongest claim, largest vulnerability, likely defense pressure point.]

## Findings
| # | Severity | Area | Location | Issue | Why it matters | Suggested fix |
|---|----------|------|----------|-------|----------------|---------------|

## Potential Errors To Verify
[Specific numbers, citations, equations, tables, or claims that need checking.]

## Defense Questions
[Hard questions an examiner might ask.]

## What Is Already Well Scoped
[Claims that are defensible as written, to avoid unnecessary rewrites.]
```

## Severity Guide

- Critical: Could invalidate a central claim, cause a failed defense question, or require new experiments or major rewriting.
- Major: Weakens a core contribution, headline claim, methodology, or comparison, but can be fixed by reframing, extra analysis, or clearer limitations.
- Minor: Local ambiguity, missing caveat, weak wording, citation hygiene, or presentation issue.
- Question: Something the author should be ready to answer, but not necessarily a flaw.

## Thesis-Specific Priorities

For the SLM agents thesis in this repository, pay special attention to:

- Whether claims about "agents" are actually supported by single-call tool-calling evidence.
- Whether "frontier range" or "parity" claims are limited to BFCL v4 Python Simple AST / `simple_python` and do not imply broader agent reliability.
- Whether cascade economics are clearly presented as projections when no router is implemented.
- Whether BFCL, tau-bench, GitHub MCP, and extended BFCL categories are weighted proportionally to their evidence strength.
- Whether negative results are interpreted honestly instead of hidden behind the strongest no-training result.
- Whether the B-template control undercuts or reframes the contribution of model-agnostic constrained decoding.

## Interaction With Other Skills

Use this skill instead of `thesis-readable-style` when the user asks for criticism, gaps, errors, examiner pressure, red-team review, defense risks, or overclaim detection. Use `thesis-readable-style` only after the critique when rewriting fixes. Use `thesis-examiner` when the user wants a full examiner-style evaluation or indicative grade.
