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
| B (no guided, FP16) | 3.5% | 4.8% | 2.8% | 1.8% |
| CD (guided, FP16) | 51.5% | 62.3% | 64.8% | 72.2% |
| CD+Q (guided, AWQ INT4) | 47.8% | 60.5% | 64.5% | 72.0% |
| PE (few-shot + CD, FP16) | 53.5% | 64.8% | 67.0% | 70.2% |
| CD+Q+ITC (CoT + guided + AWQ) | 42.0% | 54.8% | 58.0% | 65.5% |
| CD+Q+RAG (top-5 + guided + AWQ) | 26.0% | 34.8% | 48.2% | 47.8% |

7B values confirmed consistent with earlier single-model runs.
Multiple and parallel categories were only run for 7B (both 0% across all configs — not size-dependent).

### Quantization cost by size (CD vs CD+Q)

| Size | CD (FP16) | CD+Q (AWQ INT4) | Delta |
|------|-----------|-----------------|-------|
| 0.5B | 51.5% | 47.8% | -3.7 pp |
| 1.5B | 62.3% | 60.5% | -1.8 pp |
| 3B | 64.8% | 64.5% | -0.3 pp |
| 7B | 72.2% | 72.0% | -0.2 pp |

AWQ quantization cost decreases with model size. At 0.5B, the 4-bit approximation loses 3.7 pp; at 3B and 7B, the loss is within noise (<0.5 pp).

### Few-shot (PE) delta vs CD baseline (FP16 models)

| Size | CD | PE | Delta |
|------|----|----|-------|
| 0.5B | 51.5% | 53.5% | +2.0 pp |
| 1.5B | 62.3% | 64.8% | +2.5 pp |
| 3B | 64.8% | 67.0% | +2.2 pp |
| 7B | 72.2% | 70.2% | -2.0 pp |

Few-shot helps small models (+2–2.5 pp) but hurts the 7B (-2 pp). Pattern reversal at 7B aligns with the earlier finding that longer few-shot prompts dilute 7B attention on borderline cases. At smaller sizes the examples may act more like format anchors.

### ITC (CoT) delta vs CD+Q baseline

| Size | CD+Q | CD+Q+ITC | Delta |
|------|------|----------|-------|
| 0.5B | 47.8% | 42.0% | -5.8 pp |
| 1.5B | 60.5% | 54.8% | -5.7 pp |
| 3B | 64.5% | 58.0% | -6.5 pp |
| 7B | 72.0% | 65.5% | -6.5 pp |

CoT is consistently harmful at every model size. The delta is roughly constant (~-6 pp) across the full range. CoT is not a "capability too small models can't use" — the 0.5B loses as much as the 7B.

### RAG delta vs CD+Q baseline

| Size | CD+Q | CD+Q+RAG | Delta |
|------|------|----------|-------|
| 0.5B | 47.8% | 26.0% | -21.8 pp |
| 1.5B | 60.5% | 34.8% | -25.7 pp |
| 3B | 64.5% | 48.2% | -16.3 pp |
| 7B | 72.0% | 47.8% | -24.2 pp |

RAG is harmful at every size. The drop is large and non-monotonic: 3B loses least (-16 pp), 1.5B most (-25.7 pp). The disambiguation failure (picking a wrong sibling function from 5 candidates) does not improve with size — 7B is not noticeably better than 3B at RAG.

## Key patterns

1. **CD is essential at all sizes.** Without guided decoding, accuracy is 1–5% regardless of model size. The format compliance problem dominates everything else.

2. **Scaling law holds under CD.** 51.5% → 62.3% → 64.8% → 72.2% is a consistent size-accuracy curve. 0.5B to 1.5B is the steepest gain (+10.8 pp); 1.5B to 3B is flatter (+2.5 pp); 3B to 7B is another +7.4 pp step.

3. **AWQ quantization is safe above 1.5B.** At 3B and 7B, quantization loss is within noise. At 0.5B it is -3.7 pp — meaningful but still acceptable for a 4x memory reduction.

4. **Few-shot inverts at 7B.** Helpful for 0.5B–3B, harmful at 7B. The crossover is likely a prompt-length vs capability tradeoff. For smaller models, few-shot examples act as format anchors. For 7B, they compete with attention.

5. **ITC (CoT) is uniformly harmful, size-independent.** -5.7 to -6.5 pp at every scale. The failure mechanism (CoT reasons toward linguistic naturalness rather than BFCL conventions) does not depend on model capability.

6. **RAG disambiguation failure is not solved by scale.** 7B is no better than 3B at picking the right function from 5 candidates. This confirms the disambiguation problem is a training-data issue, not a capability issue.

## Implications

### For the thesis (RQ2 — which techniques improve SLM tool calling)

The size sweep adds evidence that the Phase 1 7B findings generalize across model scales:
- CD is the baseline requirement at every size
- Prompting interventions (PE, ITC) do not reliably help — the direction of effect even reverses with size for PE
- RAG top-5 is harmful at every size tested; the problem is not model capability

The best strategy per size (without fine-tuning) is **CD alone** at 7B, and **PE+CD** at ≤3B.

### For the cascade architecture

A cascade using 3B as the small tier and 7B as the large tier would see the 3B SLM handle 64.5–67% of cases (with CD or PE+CD) and escalate the rest. The 3B–7B gap is ~7–8 pp.

### LoRA size sweep

The same 0.5B/1.5B/3B models should be run through CD+FT-aligned to establish whether LoRA training can close or narrow the size gap. If 3B+FT-aligned approaches 7B+FT-aligned (76.75%), the cascade can run at 3B with minimal quality loss.

## Result files

| Config | Result dir | Runs dir |
|--------|------------|----------|
| CD | `data/output/bfcl/` | `data/output/bfcl/runs/` |
| B | `data/output/bfcl_no_guided/` | `data/output/bfcl_no_guided/runs/` |
| CD+Q | `data/output/bfcl_quant/` | `data/output/bfcl_quant/runs/` |
| PE | `data/output/bfcl_few_shot/` | `data/output/bfcl_few_shot/runs/` |
| CD+Q+ITC | `data/output/bfcl_itc/` | `data/output/bfcl_itc/runs/` |
| CD+Q+RAG | `data/output/bfcl_rag/` | `data/output/bfcl_rag/runs/` |
