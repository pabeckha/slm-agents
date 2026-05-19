# τ-bench Results — Retail Domain, Tool-Calling Strategy

**Date**: 2026-04-23
**Job**: 28258755 (L40S 46GB, gpul40s)
**Model**: Qwen/Qwen2.5-7B-Instruct (FP16, vLLM 0.8.5, hermes tool-call parser)
**User simulator**: Same local vLLM instance
**Benchmark**: τ-bench retail domain, test split (115 tasks)
**Configuration**: tool-calling strategy, temperature 0.0, seed 42, max_concurrency 1

## Results

**Pass rate: 4.3% (5/115) — mean across three runs**

Three full runs of the same configuration were completed (all 115 tasks, temperature 0.0, seed 42). Despite deterministic model temperature, run-to-run variance exists because the user simulator generates stochastic responses.

| Run | Job | Passed | Pass rate |
|-----|-----|--------|-----------|
| 1 | 28258755 | 5/115 | 4.35% |
| 2 | 28263173 | 6/115 | 5.22% |
| 3 | 28263174 | 4/115 | 3.48% |
| **Mean** | | **5/115** | **4.35%** |

Range: 3.5%–5.2%. At n=115 binary tasks the standard error is ~1.9 pp, so ±1 correct task is within noise. A meaningful improvement over this baseline would require ≥3 additional correct tasks (~2.6 pp).

| Metric | Value |
|--------|-------|
| Tasks completed | 115/115 |
| Passed (reward = 1.0) | 4–6 across runs |
| Failed (reward = 0.0) | 109–111 |
| Errors | 0 |
| Reward distribution | Binary: 0.0 or 1.0 only |

## Context

τ-bench is a multi-step agentic benchmark where the model must complete retail service tasks (order exchanges, returns, modifications) by calling tools across multiple turns while maintaining correct state. The user simulator (also Qwen2.5-7B running on the same vLLM) generates realistic customer responses.

A task only passes if the final database state exactly matches the ground truth — partial progress gives reward 0.0. This binary scoring is strict: a task that executes 9 of 10 steps correctly still fails.

### Contrast with BFCL

BFCL simple_python measures single-call accuracy — one prompt, one tool call, one evaluation. τ-bench measures end-to-end agentic success across 5–15 turns with tool feedback loops. The gap is large:

| Benchmark | Setting | Pass rate |
|-----------|---------|-----------|
| BFCL simple_python (CD) | Single call, format constrained | 72.75% |
| τ-bench retail (tool-calling) | Multi-step, no format constraint | **4.3%** |

The 68+ pp gap shows that single-call tool accuracy does not transfer to multi-step agent performance. The failure modes are qualitatively different.

## Failure analysis

Reward is binary (no partial credit in the data), so failure decomposition requires inspecting individual trajectories. Likely failure modes based on the task structure:

- **State drift**: model loses track of which items have been exchanged/returned across turns
- **Premature termination**: model calls `finish` before completing all sub-tasks (multi-item requests are common)
- **Tool parameter errors**: wrong order ID, wrong item ID — errors that constrained decoding does not catch because τ-bench tools accept free-form string IDs
- **Context overflow**: some tasks (e.g., task 0, 1) exceeded the 4096-token context limit in earlier runs; bumped to 8192 for this run

## Implications for thesis

This result is a central thesis finding. The cascade architecture motivation is precisely this gap: a 7B SLM cannot reliably execute multi-step agent tasks even when it can generate individually valid tool calls 72% of the time. This quantifies the boundary that optimization techniques need to push.

τ-bench retail at 4.3% is the **agentic baseline** for Config CD. Subsequent configs (CD+Q, CD+FT) should ideally be evaluated on τ-bench as well to show whether BFCL gains transfer. Given HPC cost, prioritize at least one comparison point (e.g., CD+Q on τ-bench).

## Size sweep — baselines and FT-aligned (2026-05-19)

**Jobs**: 28461727–28461730 (baselines); 28443556, 28443558, 28443559 (FT-aligned)
**All runs**: tool-calling strategy, retail domain, 115 tasks, single run per condition

### Pass rates across sizes and configs

| Size | Baseline (CD) | CD+FT-aligned |
|------|--------------|---------------|
| 0.5B | 3.48% (4/115) | 0.00% (0/115) |
| 1.5B | 1.74% (2/115) | 3.48% (4/115) |
| 3B   | 4.35% (5/115) | 4.35% (5/115) |
| 7B   | 4.35% mean (3 runs) | 3.48% (4/115) |

### Key findings

1. **τ-bench scores are uniformly low across all sizes.** 1.7–4.4% for baselines regardless of model scale. The 0.5B→7B range spans only 2.6 pp. Scale does not solve the multi-step agentic problem.

2. **CD+FT-aligned does not improve τ-bench.** Despite +2–8 pp BFCL gains from FT-aligned, τ-bench pass rates are essentially flat. The format-alignment training helps single-call accuracy but does not transfer to multi-turn task completion.

3. **0.5B-merged-aligned collapses to 0%.** The format-aligned fine-tuning at 0.5B destroys what little agentic capability the baseline had. At this scale the model has too few parameters to absorb the training signal without overfitting on call format at the expense of task reasoning.

4. **Single run per condition; noise is high.** At n=115 binary tasks, one task = 0.87 pp. The differences between 3.48% and 4.35% are within noise (±1.9 pp SE). These numbers establish a floor, not a ranking.

### Interpretation

The BFCL → τ-bench transfer gap persists across all model sizes. A 7B model that calls tools correctly 72–76% of the time on BFCL still solves only 4.4% of multi-step retail tasks. A 0.5B model gets 59% on BFCL simple_python (with FT-aligned) but 0% on τ-bench. The optimization techniques studied in this thesis move the BFCL needle but leave the agentic performance floor essentially unchanged. This is the thesis's core finding on the cascade motivation: the gap is not closed by any single-model technique.

## Infrastructure notes

- vLLM `--tool-call-parser qwen2.5` was removed in recent vLLM versions; replaced with `hermes`
- τ-bench checkpoint path construction used raw `config.user_model` (including `/`), causing `FileNotFoundError` — patched in `vendor/tau-bench/tau_bench/run.py:30`
- Wall time: ~1.75 hours for 115 sequential tasks on L40S
