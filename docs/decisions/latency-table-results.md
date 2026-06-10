# Per-Call Latency: B vs CD vs CD+Q (2026-06-10)

## Question

Measure single-call latency for the thesis latency table: does constrained
decoding cost or save time, and what does AWQ quantization add on top?

## Methodology

- Job 28624134 (`scripts/hpc/run_bfcl_latency.sh`), single GPU, vLLM server,
  sequential requests (`parallel=False`) so each timing is a clean per-call
  latency.
- BFCL v4 `simple_python`, first 100 cases (latency-focused subset, not the
  full 400 used for the accuracy headlines).
- Three configs, same prompt/dataset:
  - **B**: Qwen2.5-7B-Instruct, no guided decoding
  - **CD**: Qwen2.5-7B-Instruct, guided (constrained) decoding
  - **CD+Q**: Qwen2.5-7B-Instruct-AWQ, guided decoding
- Manifests in `data/output/bfcl_latency/{b,cd,cdq}/runs/`.

## Results

| Config | mean (s) | median (s) | p95 (s) | total (s) | accuracy (n=100) |
|---|---|---|---|---|---|
| B (no CD) | 6.995 | 6.929 | 11.922 | 699.5 | 1% |
| CD | 0.878 | 0.847 | 1.375 | 87.8 | 65% |
| CD+Q (AWQ) | 0.661 | 0.623 | 1.006 | 66.1 | 63% |

- **CD is ~8× faster than the unconstrained baseline** (0.878s vs 6.995s
  mean). Constrained decoding terminates generation at the closing brace of a
  valid JSON call; the unconstrained model rambles (explanations, markdown,
  trailing text), generating far more tokens per call.
- **AWQ cuts another ~25%** on top of CD (0.661s vs 0.878s mean, p95 1.006s
  vs 1.375s).
- Config B's 1% accuracy is the strict-JSON parse artifact already known from
  the ablation work: outputs fail with "Extra data" JSON errors because the
  model appends prose after (or instead of) the call. It is the same failure
  mode that motivates CD, now with the latency cost quantified too.
- CD 65/100 and CD+Q 63/100 on the first-100 subset are consistent with the
  ~72% full-400 numbers (the first 100 cases skew math-heavy with enum-style
  ground truths; see failure list — mostly "Expected one of [...]" value
  mismatches, not structural errors).

## Thesis implication

The latency table for the methodology/results chapter can state: constrained
decoding is not a latency tax but a ~8× latency win at 7B, because it
eliminates free-form rambling; quantization stacks a further ~25% reduction.
Quote mean/median/p95 from the manifests above and note n=100, sequential,
single A100-class GPU, vLLM backend.
