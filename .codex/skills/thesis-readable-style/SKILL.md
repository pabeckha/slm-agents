---
name: thesis-readable-style
description: Revise, draft, or restructure thesis and academic report prose so it is easy to read and follow, using the clear DTU thesis style modeled on docs/benchmarks/exploring-llm-customization-text-to-code.pdf. Use when Codex is asked to improve thesis writing, make sections clearer, adapt prose to the benchmark thesis style, simplify dense academic text, add signposting, rewrite introductions/methodology/results/conclusion sections, or review whether thesis prose flows logically.
---

# Thesis Readable Style

## Overview

Use this skill to turn dense or fragmented thesis material into clear, plain, easy-to-follow thesis prose. Preserve the user's technical meaning and evidence while adopting the readable structure and approachable tone of the benchmark DTU thesis.

## Workflow

1. Read `references/style-guide.md` before rewriting or drafting substantial thesis text.
2. Identify the section type: introduction, background, methodology, experiment setup, results, discussion, limitations, conclusion, or appendix.
3. Map the user's intended claims before editing:
   - What problem is being addressed?
   - What was done or evaluated?
   - What evidence supports the claim?
   - What trade-off, limitation, or conclusion should the reader remember?
4. Rewrite for readable thesis flow:
   - Start each section with a short orientation paragraph.
   - Move from motivation to concrete method or result.
   - Prefer direct sentences and explicit transitions.
   - Keep technical terms, model names, metrics, and citations intact.
5. Return the revised text first. Add a short note only if important assumptions, missing evidence, or unresolved structure problems remain.

## Style Priorities

- Make the thesis easy to read without making it casual or overly informal.
- Use a calm, explanatory academic register that sounds natural rather than stiff.
- Prefer accessible wording over unnecessarily formal phrasing when both are precise.
- Use "we" for thesis actions when the surrounding document already does so; otherwise match the user's existing authorial voice.
- Prefer "This chapter/section..." signposting when it helps the reader understand the path through the work.
- Explain why a method, metric, or design choice matters before giving details.
- State results plainly before discussing interpretation.
- Keep claims proportional to the evidence. Use "suggests", "indicates", or "may" only when uncertainty is real.

## Editing Rules

- Preserve citations, labels, equations, table numbers, figure numbers, metric names, and numerical results unless the user asks to change them.
- Do not invent references, results, experiments, or claims.
- Do not over-polish into marketing language or dense formal academic language.
- Do not remove limitations; make them clearer and better connected to the thesis claims.
- When source text is incomplete, write a clean version with explicit placeholders such as `[insert result]` rather than fabricating content.

## Reference

Read `references/style-guide.md` for the benchmark-derived style patterns, section templates, and before/after editing checks.
