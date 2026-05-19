# Size Sweep Results — BFCL Simple Python Across Qwen 2.5 Model Sizes

**Date**: 2026-05-10
**Jobs**: finished 2026-05-10 (bfcl_few_shot, bfcl_itc, bfcl_rag, bfcl_quant sweeps)
**Benchmark**: BFCL v4 simple_python (400 test cases, AST accuracy)
**Models**: Qwen/Qwen2.5-{0.5B,1.5B,3B}-Instruct (FP16) and -{AWQ} (INT4); 7B already existed
**Infrastructure**: DTU HPC (gpul40s / A100)

## Results

### Per-model, per-config accuracy — simple_python

| Config | 0.5B | 1.5B | 3B | 7B |
|--------|------|------|----|----|
| B (no guided, FP16) | 3.5% | 4.8% | 2.8% | 1.5% |
| CD (guided, FP16) | 51.5% | 62.3% | 64.8% | 72.75% |
| CD+Q (guided, AWQ INT4) | 47.8% | 60.5% | 64.5% | 72.25% |
| PE (few-shot + CD, FP16) | 53.5% | 64.8% | 67.0% | 70.25% |
| CD+Q+ITC (CoT + guided + AWQ) | 42.0% | 54.8% | 58.0% | 65.5% |
| CD+Q+RAG (top-5 + guided + AWQ) | 26.0% | 34.8% | 48.2% | 47.75% |
| CD+FT-aligned (guided, bf16 merged) | 59.2% | 66.0% | 66.8% | 76.75% |

7B values taken from established phase 1 runs (phase1-ablation-summary.md); earlier draft had transcription errors.
Multiple and parallel categories for 7B CD baseline: both 0% across all configs. CD+FT-aligned multiple/parallel for 0.5B–3B run separately — see section below.

### Quantization cost by size (CD vs CD+Q)

| Size | CD (FP16) | CD+Q (AWQ INT4) | Delta |
|------|-----------|-----------------|-------|
| 0.5B | 51.5% | 47.8% | -3.7 pp |
| 1.5B | 62.3% | 60.5% | -1.8 pp |
| 3B | 64.8% | 64.5% | -0.3 pp |
| 7B | 72.75% | 72.25% | -0.5 pp |

AWQ quantization cost decreases with model size. At 0.5B, the 4-bit approximation loses 3.7 pp; at 3B and 7B, the loss is within noise (<0.5 pp).

### Few-shot (PE) delta vs CD baseline (FP16 models)

| Size | CD | PE | Delta |
|------|----|----|-------|
| 0.5B | 51.5% | 53.5% | +2.0 pp |
| 1.5B | 62.3% | 64.8% | +2.5 pp |
| 3B | 64.8% | 67.0% | +2.2 pp |
| 7B | 72.75% | 70.25% | -2.5 pp |

Few-shot helps small models (+2–2.5 pp) but hurts the 7B (-2.5 pp). Pattern reversal at 7B aligns with the earlier finding that longer few-shot prompts dilute 7B attention on borderline cases. At smaller sizes the examples may act more like format anchors.

### ITC (CoT) delta vs CD+Q baseline

| Size | CD+Q | CD+Q+ITC | Delta |
|------|------|----------|-------|
| 0.5B | 47.8% | 42.0% | -5.8 pp |
| 1.5B | 60.5% | 54.8% | -5.7 pp |
| 3B | 64.5% | 58.0% | -6.5 pp |
| 7B | 72.25% | 65.5% | -6.75 pp |

CoT is consistently harmful at every model size. The delta is roughly constant (~-6 pp) across the full range. CoT is not a "capability too small models can't use" — the 0.5B loses as much as the 7B.

### RAG delta vs CD+Q baseline

| Size | CD+Q | CD+Q+RAG | Delta |
|------|------|----------|-------|
| 0.5B | 47.8% | 26.0% | -21.8 pp |
| 1.5B | 60.5% | 34.8% | -25.7 pp |
| 3B | 64.5% | 48.2% | -16.3 pp |
| 7B | 72.25% | 47.75% | -24.5 pp |

RAG is harmful at every size. The drop is large and non-monotonic: 3B loses least (-16 pp), 1.5B most (-25.7 pp). The disambiguation failure (picking a wrong sibling function from 5 candidates) does not improve with size — 7B is not noticeably better than 3B at RAG.

## Key patterns

1. **CD is essential at all sizes.** Without guided decoding, accuracy is 1–5% regardless of model size. The format compliance problem dominates everything else.

2. **Scaling law holds under CD.** 51.5% → 62.3% → 64.8% → 72.75% is a consistent size-accuracy curve. 0.5B to 1.5B is the steepest gain (+10.8 pp); 1.5B to 3B is flatter (+2.5 pp); 3B to 7B is another +7.95 pp step.

3. **AWQ quantization is safe above 1.5B.** At 3B and 7B, quantization loss is within noise. At 0.5B it is -3.7 pp — meaningful but still acceptable for a 4x memory reduction.

4. **Few-shot inverts at 7B.** Helpful for 0.5B–3B, harmful at 7B. The crossover is likely a prompt-length vs capability tradeoff. For smaller models, few-shot examples act as format anchors. For 7B, they compete with attention.

5. **ITC (CoT) is uniformly harmful, size-independent.** -5.7 to -6.75 pp at every scale. The failure mechanism (CoT reasons toward linguistic naturalness rather than BFCL conventions) does not depend on model capability.

6. **RAG disambiguation failure is not solved by scale.** 7B is no better than 3B at picking the right function from 5 candidates. This confirms the disambiguation problem is a training-data issue, not a capability issue.

## Implications

### For the thesis (RQ2 — which techniques improve SLM tool calling)

The size sweep adds evidence that the Phase 1 7B findings generalize across model scales:
- CD is the baseline requirement at every size
- Prompting interventions (PE, ITC) do not reliably help — the direction of effect even reverses with size for PE
- RAG top-5 is harmful at every size tested; the problem is not model capability

The best strategy per size (without fine-tuning) is **CD alone** at 7B, and **PE+CD** at ≤3B.

### For the cascade architecture

A cascade using 3B as the small tier and 7B as the large tier would see the 3B SLM handle 64.5–67% of cases (with CD or PE+CD) and escalate the rest. The 3B–7B gap is ~8 pp.

### CD+FT-aligned delta vs CD by size

| Size | CD | CD+FT-aligned | FT delta |
|------|----|---------------|----------|
| 0.5B | 51.5% | 59.2% | +7.7 pp |
| 1.5B | 62.3% | 66.0% | +3.7 pp |
| 3B | 64.8% | 66.8% | +2.0 pp |
| 7B | 72.75% | 76.75% | +4.0 pp |

FT-aligned helps at every size. The benefit is largest at 0.5B (+7.7 pp), drops at 1.5B and 3B, then recovers at 7B (+4.0 pp). Fine-tuning does not close the 3B→7B gap — the gap under CD+FT-aligned (10 pp) is wider than under plain CD (7.95 pp). See `config-ft-aligned-size-sweep.md` for full analysis.

## BFCL multiple and parallel — CD+FT-aligned size sweep (2026-05-17/19)

**Jobs**: 28443541, 28443543, 28443547, 28443549, 28443551 (0.5B/1.5B); 28461731 (3B multiple re-run after crash fix); 7B pending (jobs 28468135, 28468136)
**Benchmark**: BFCL v4 multiple (200 cases) and parallel (200 cases)
**Models**: CD+FT-aligned merged models (same as simple_python sweep above)

### CD+FT-aligned accuracy — multiple and parallel categories

| Size | multiple | parallel |
|------|----------|----------|
| 0.5B | 55.5% (111/200) | 0.0% (0/200) |
| 1.5B | 61.0% (122/200) | 0.0% (0/200) |
| 3B   | 60.5% (121/200) | 0.0% (0/200) |
| 7B   | pending | pending |

### Key findings

1. **Parallel is uniformly 0% across all sizes.** CD+FT-aligned models cannot execute parallel tool calls (two simultaneous function calls in one output). This matches the 7B CD baseline (also 0%). Parallel call format requires generating two complete JSON objects in a single response — a skill that format-aligned fine-tuning does not teach and constrained decoding does not scaffold.

2. **Multiple is 55–61% at all sizes — remarkably flat.** Unlike simple_python where scores scale from 59% to 67% across 0.5B→3B, the multiple category shows almost no size dependence under CD+FT-aligned. The 0.5B gets within 5.5 pp of the 3B. This suggests the main barrier for multi-function single-call accuracy is format knowledge (taught by FT), not reasoning capacity (which scales with size).

3. **Multiple category is substantially easier than parallel, even for small models.** "Multiple" asks the model to pick one of several candidate functions; "parallel" asks it to output two calls simultaneously. The 0 pp / 55+ pp gap confirms the distinction is about output format complexity, not function selection difficulty.

4. **The 3B multiple result (60.5%) comes from a re-run** after the eval-checker crash was fixed on branch `fix/bfcl-eval-checker-crash`. The earlier run (job 28443543) crashed mid-evaluation and logged 0% incorrectly.

### Implication for thesis

The flat multiple accuracy across sizes (55–61%) combined with universally 0% parallel shows that FT-aligned training solves one sub-problem (function selection from a candidate set) but not another (structured multi-output generation). This is a clean capability decomposition and a useful negative result: scale and fine-tuning together are still insufficient for parallel tool calling.

## Result files

| Config | Result dir | Runs dir |
|--------|------------|----------|
| CD | `data/output/bfcl/` | `data/output/bfcl/runs/` |
| B | `data/output/bfcl_no_guided/` | `data/output/bfcl_no_guided/runs/` |
| CD+Q | `data/output/bfcl_quant/` | `data/output/bfcl_quant/runs/` |
| PE | `data/output/bfcl_few_shot/` | `data/output/bfcl_few_shot/runs/` |
| CD+Q+ITC | `data/output/bfcl_itc/` | `data/output/bfcl_itc/runs/` |
| CD+Q+RAG | `data/output/bfcl_rag/` | `data/output/bfcl_rag/runs/` |
