# Technique Isolation Ablation — PE / CoT / RAG without Constrained Decoding

**Date**: 2026-05-17
**Jobs**: bfcl_few_shot_no_guided_28439608, bfcl_cot_no_guided_28439609, bfcl_rag_no_guided_28439610
**Benchmark**: BFCL v4 simple_python (400 test cases, AST accuracy)
**Model**: Qwen/Qwen2.5-7B-Instruct (FP16, no quantization)
**Infrastructure**: DTU HPC (A100)
**Purpose**: Isolate CD's contribution — run each prompt-level technique alone, without constrained decoding

## Results

| Config | Guided | Accuracy | Correct | Delta vs B |
|--------|--------|----------|---------|------------|
| B (baseline) | No | 1.5% | 6/400 | — |
| PE-ng (few-shot, no CD) | No | 4.5% | 18/400 | +3.0 pp |
| CoT-ng (ITC, no CD) | No | 26.2% | 105/400 | +24.7 pp |
| RAG-ng (no CD) | No | 2.5% | 10/400 | +1.0 pp |
| FT-aligned-ng | No | 13.25% | 53/400 | +11.75 pp |

### Comparison: same technique with vs without CD

| Technique | Without CD | With CD | CD contribution |
|-----------|-----------|---------|-----------------|
| CD alone | — | 72.75% | +71.25 pp |
| Few-shot (PE) | 4.5% | 70.25% | +65.75 pp |
| CoT (ITC) | 26.2% | 65.5% | +39.3 pp |
| RAG | 2.5% | 47.75% | +45.25 pp |

## Key findings

1. **CD is the dominant contributor in every config.** Without CD, only CoT (26.2%) and FT-aligned-ng (13.25%) reach double digits; all other prompt techniques stay at ≤4.5%. The format compliance problem swamps everything else.

2. **CoT without CD reaches 26.2% — highest of any unguided technique.** CoT's chain-of-thought reasoning incidentally helps the model produce structured output. Step-by-step thinking before the output acts as self-scaffolding that produces more consistently formatted JSON. Among the prompt-level techniques isolated here (PE, CoT, RAG), CoT is the only one with more than marginal improvement over B; FT-aligned-ng (+11.75 pp) also clears this bar but via training, not prompting.

3. **CoT's relationship with CD reverses.** Under CD, CoT hurts (-7.25 pp vs CD+Q baseline). Without CD, CoT is the best prompt technique (+24.7 pp over B). The mechanism: CD already guarantees format, so CoT's format benefit is redundant and its reasoning introduces value-level errors. Without CD, CoT's format benefit is the primary signal and it matters.

4. **Few-shot (PE) without CD: minimal effect (+3.0 pp).** In-context examples provide weak format guidance compared to CoT's explicit reasoning. The three examples are too few to reliably induce correct JSON structure.

5. **RAG without CD: +1.0 pp, essentially noise.** Surfacing 5 candidate functions to a model that cannot reliably produce structured output adds nothing. The format failure is so dominant that the retrieval signal cannot reach the output.

6. **CD's contribution is smallest in the CoT config (39.3 pp vs 65–71 pp for others).** CoT already provides partial format scaffolding without CD; adding CD recovers less absolute ground. But the combined result (65.5%) is still lower than CD alone (72.75%) because CoT's reasoning produces value-level errors that CD cannot fix.

## Interpretation for thesis (RQ1)

This ablation cleanly quantifies CD's marginal contribution in isolation. The 71.25 pp gap documented in Config B (1.5% → 72.75%) is confirmed as an almost pure format compliance gap. The only exception is CoT: even without CD it reaches 26.2%, suggesting CoT provides about 25 pp of "implicit" format benefit. Adding CD on top of CoT recovers 39.3 pp more, putting CD+Q+CoT at 65.5%. The total 7B-CoT-with-CD benefit (65.5% vs 1.5% baseline) is 64 pp, compared to 71.25 pp for CD alone — meaning CoT actually costs ~7 pp of CD's effectiveness while providing 25 pp in the unguided setting.

## Result files

| Config | Result dir |
|--------|------------|
| PE-ng | `data/output/bfcl_few_shot_no_guided/Qwen_Qwen2.5-7B-Instruct/` |
| CoT-ng | `data/output/bfcl_cot_no_guided/Qwen_Qwen2.5-7B-Instruct/` |
| RAG-ng | `data/output/bfcl_rag_no_guided/Qwen_Qwen2.5-7B-Instruct/` |

Scores: `data/output/bfcl_{few_shot,cot,rag}_no_guided/scores/simple_python_scores.json`
Logs: `logs/bfcl_{few_shot,cot,rag}_no_guided_2843960{8,9,10}.out`
