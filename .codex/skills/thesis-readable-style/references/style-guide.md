# Benchmark-Derived Thesis Style Guide

This guide distills the writing style of `docs/benchmarks/exploring-llm-customization-text-to-code.pdf` into reusable rules. Use it to draft or revise thesis prose so it is clear, direct, and easy to follow.

## Core Style

- Use plain thesis prose: formal enough for academic work, but approachable and not stiff.
- Prefer concrete verbs: "evaluate", "compare", "measure", "adapt", "show", "discuss".
- Prefer natural phrasing over overly formal alternatives: use "use" instead of "utilize", "show" instead of "demonstrate" when the simpler word fits, and "because" instead of "due to the fact that".
- Keep paragraphs focused on one job: motivation, setup, method, result, interpretation, or transition.
- Use short orientation paragraphs at the start of chapters and major sections.
- Make the reader's path explicit with sentences such as "In this chapter, we...", "We first...", "Following this...", and "Finally...".
- Use lists for research questions, contributions, evaluation criteria, tools, and benchmark subsets.
- Treat trade-offs as central: performance, cost, complexity, data requirements, resource constraints, and practicality.

## Common Section Patterns

### Introduction

Use a funnel structure:

1. Start with a broad practical problem.
2. Narrow to the technical challenge.
3. Explain why existing general approaches are insufficient.
4. State the thesis goal.
5. List research questions or contributions.
6. End with a brief chapter roadmap.

Good introduction sentences are direct and explanatory:

- "To tackle this problem, the goal of this thesis is to..."
- "We aim to analyze these approaches not only in terms of accuracy, but also..."
- "This thesis begins with..., followed by..."

### Background

Introduce concepts only to the depth needed for later chapters. Use short lead-ins before technical details:

- "In this chapter, we introduce the fundamental concepts underlying..."
- "We briefly outline how this architecture works because..."
- "In the following subsections, we present..."

When explaining a technical concept, use this order:

1. Definition.
2. Why it matters for the thesis.
3. Key variants or mechanisms.
4. Any formula, figure, or example.
5. Link back to later use.

### Methodology

Make the experimental pipeline easy to reconstruct. State what is designed, what is measured, and why.

Use paragraphs that answer:

- What is being built or evaluated?
- Which models, datasets, benchmarks, and metrics are involved?
- What comparison is being made?
- Which constraints affect the design?

Prefer explicit transitions between choices:

- "For this reason, in this work..."
- "This dual perspective allows us to..."
- "The main difference is..."

### Results

Begin with the comparison purpose before table details:

- "In this chapter, we present a detailed comparison..."
- "We begin by establishing a baseline..."
- "Following the baseline, we analyze..."

Write results in three layers:

1. State the observed result.
2. Compare it to the baseline or alternative.
3. Explain the likely reason or implication, without overstating causality.

Use cautious interpretation when evidence is indirect:

- "One possible reason is..."
- "This could be explained by..."
- "These results suggest..."

### Limitations And Future Work

Be direct and specific. Tie limitations to actual constraints rather than generic disclaimers.

Good limitation patterns:

- "In terms of models used for this research, we were constrained by..."
- "Although X could have been an option, Y did not allow for its implementation."
- "For that reason, we were not able to..."

Good future work patterns:

- "Future work can expand on these results in several directions."
- "One promising line is..."
- "Another direction could be..."

## Sentence-Level Rules

- Prefer one main idea per sentence.
- Use "while" and "whereas" for clear contrasts, especially in trade-off discussions.
- Avoid long chains of nouns. Replace "benchmark-based performance metric comparison procedure" with "comparison of benchmark-based metrics".
- Avoid vague intensifiers such as "very", "extremely", "highly", unless quantified.
- Avoid rhetorical or promotional phrasing.
- Avoid inflated academic phrasing that makes simple ideas harder to read.
- Keep definitions compact, then move to why they matter.

## Paragraph Checks

Before returning rewritten text, check that each paragraph passes these tests:

- The first sentence tells the reader what the paragraph is about.
- The paragraph has one main claim.
- Technical detail supports the claim rather than interrupting it.
- Any result or limitation is connected to the thesis question.
- The final sentence either completes the point or transitions naturally to the next one.

## Output Behavior

When revising text:

- Return polished thesis prose, not a list of editing advice, unless the user asks for critique.
- Preserve the user's section headings when possible.
- If the prose needs a stronger structure, add concise headings that match thesis conventions.
- If the input is bullet notes, convert them into connected academic paragraphs.
- If a section is missing evidence, keep the prose readable but mark missing specifics with placeholders.
