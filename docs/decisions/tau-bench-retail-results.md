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

## Infrastructure notes

- vLLM `--tool-call-parser qwen2.5` was removed in recent vLLM versions; replaced with `hermes`
- τ-bench checkpoint path construction used raw `config.user_model` (including `/`), causing `FileNotFoundError` — patched in `vendor/tau-bench/tau_bench/run.py:30`
- Wall time: ~1.75 hours for 115 sequential tasks on L40S
