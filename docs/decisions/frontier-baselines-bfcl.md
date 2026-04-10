# Frontier Baselines — BFCL v4 Simple Function

**Date**: 2026-04-06
**Source**: BFCL v4 official leaderboard (https://gorilla.cs.berkeley.edu/leaderboard.html)
**Data**: Non-Live Simple AST column from gorilla.cs.berkeley.edu/data_overall.csv
**Accessed**: April 2026

## Decision

Use published BFCL leaderboard scores as frontier baselines rather than running our own evaluation. Rationale:
- Official scores are the canonical reference for this benchmark
- No API key costs
- Ensures comparability with other published results

## Frontier Model Scores (Simple Function AST Accuracy)

| Model | Simple AST | Overall |
|-------|-----------|---------|
| Gemini 3 Pro (Prompt) | 79.58% | 72.51% |
| Claude Opus 4.5 (FC) | 76.83% | 77.47% |
| Grok 4.1 Fast (FC) | 77.58% | 69.57% |
| Gemini 3 Pro (FC) | 75.50% | 68.14% |
| o3 (Prompt) | 74.25% | 63.05% |
| GPT-4.1-mini (FC) | 73.33% | 50.45% |
| GPT-5.2 (FC) | 72.92% | 55.87% |
| GPT-4.1 (FC) | 72.67% | 53.96% |
| Claude Sonnet 4.5 (FC) | 72.58% | 73.24% |
| Claude Haiku 4.5 (FC) | 71.00% | 68.70% |
| o4-mini (FC) | 66.92% | 53.24% |
| GPT-5-mini (FC) | 59.92% | 55.46% |
| GPT-4.1-nano (FC) | 59.92% | 33.05% |

## Our Results

| Config | Simple AST |
|--------|-----------|
| Qwen 2.5 7B + CD | 72.75% |
| Qwen 2.5 7B + PE | 70.25% |
| Qwen 2.5 7B (raw) | 1.50% |

## Key Finding

**Qwen 2.5 7B with constrained decoding (72.75%) matches frontier models on Simple Function:**
- Exceeds GPT-4.1 (72.67%) by 0.08 pp
- Exceeds Claude Sonnet 4.5 (72.58%) by 0.17 pp
- Exceeds Claude Haiku 4.5 (71.00%) by 1.75 pp
- Gap to best (Gemini 3 Pro Prompt, 79.58%): 6.83 pp
- Gap to Claude Opus 4.5 (76.83%): 4.08 pp

This is a strong thesis finding for RQ1: the baseline gap on simple function calling is effectively **zero** against mid-tier frontier models when constrained decoding is applied. The remaining gap to top-tier models (4-7 pp) may be closable with LoRA fine-tuning.

## Implications

### RQ1 (Baseline gap)
- Raw SLM gap: 71-78 pp (1.5% vs 72-80%)
- With constrained decoding: 0-7 pp gap
- Constrained decoding alone closes ~95% of the frontier gap

### RQ3 (Production viability)
- The success criterion of >=85% AST accuracy is NOT met by any model on this leaderboard version
- The top score is 79.58% (Gemini 3 Pro)
- Our 72.75% is competitive but the 85% target may need revision based on the leaderboard ceiling

### Cascade architecture
- On simple function calls, the SLM tier with CD can handle requests at frontier-level quality
- Escalation to frontier models only needed for multi-turn/complex tasks (where overall scores diverge significantly)

## Skepticism: Why This Result May Be Misleading

The claim "a 7B SLM matches GPT-4.1 and Claude Sonnet on function calling" demands scrutiny. Several factors may inflate the apparent parity:

### 1. Simple Function is the easiest category
The simple_python category tests single-turn, single-function calls with one function definition per test case. There is no function selection ambiguity (only one candidate), no multi-turn context, no competing tools. This is the most constrained and least representative scenario for real-world agentic use. Frontier models differentiate on harder categories: their Overall scores (which weight multi-turn 30% and agentic tasks 40%) are much higher than SLMs would achieve.

### 2. Constrained decoding levels the playing field on format
Both our guided decoding and frontier models' native tool-calling APIs guarantee valid JSON and valid function names. On format compliance, everyone scores equally. The only differentiator is argument value accuracy, where a 7B model can be competitive on simple lookups but may fall behind on complex reasoning.

### 3. BFCL v4 scoring is stricter across the board
BFCL v4 (July 2025) introduced stricter evaluation than v2/v3. All models score lower. The 85% target in our success criteria was based on older leaderboard numbers where frontier models scored higher. The current ceiling is ~80%.

### 4. We have not tested harder categories
Our evaluation covers only simple_python. Categories like `multiple_function`, `parallel_function`, `java`, `javascript`, and the live benchmarks would likely show a larger gap. The frontier comparison is only valid for the specific slice we tested.

### 5. Overall scores tell a different story
Claude Opus 4.5 scores 77.47% overall (vs 76.83% on simple), meaning it maintains performance across hard tasks. Our SLM would likely collapse on multi-turn and agentic categories where reasoning depth matters — this is exactly the gap that t-bench evaluation should quantify.

### What this result actually shows
The parity on Simple Function is real but narrow. It demonstrates that **constrained decoding solves the format problem completely**, and that **a 7B model's language understanding is sufficient for straightforward single-function argument extraction**. It does NOT demonstrate that the SLM can replace frontier models for agentic tasks in general. The thesis should present this finding with appropriate caveats and use t-bench and harder BFCL categories to show where the gap re-emerges.

## Note on Leaderboard Version

BFCL v4 (released July 2025) significantly changed the scoring methodology. Simple Function scores are lower across the board compared to BFCL v2/v3. The 85% success criterion in status.md was set based on older leaderboard numbers and may need adjustment.
