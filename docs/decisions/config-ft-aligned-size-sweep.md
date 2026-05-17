# CD+FT-aligned Size Sweep — 0.5B / 1.5B / 3B

**Date**: 2026-05-17
**Jobs**: merge_lora_aligned_28439604–06 (May 16); bfcl_ft_aligned_28439693–96 (May 17)
**Benchmark**: BFCL v4 simple_python (400 test cases, AST accuracy)
**Models**: Qwen/Qwen2.5-{0.5B,1.5B,3B}-Instruct LoRA-merged (format-aligned FT, bfloat16); 7B from 2026-04-28
**Infrastructure**: DTU HPC (L40S / A100)

## Results

### CD+FT-aligned accuracy by size

| Size | CD only | CD+FT-aligned | FT delta |
|------|---------|---------------|----------|
| 0.5B | 51.5% | 59.2% (237/400) | +7.7 pp |
| 1.5B | 62.3% | 66.0% (264/400) | +3.7 pp |
| 3B | 64.8% | 66.8% (267/400) | +2.0 pp |
| 7B | 72.75% | 76.75% (307/400) | +4.0 pp |

CD only values from `size-sweep-results.md`.

### Size gap under CD+FT-aligned

| Pair | CD gap | CD+FT-aligned gap |
|------|--------|-------------------|
| 0.5B → 1.5B | +10.8 pp | +6.8 pp |
| 1.5B → 3B | +2.5 pp | +0.8 pp |
| 3B → 7B | +7.95 pp | +9.95 pp |

FT-aligned narrows the 0.5B→1.5B gap slightly but widens the 3B→7B gap by ~2 pp. Fine-tuning does not close the size gap.

## Key findings

1. **FT-aligned helps at every size.** Positive delta at all four points. The benefit is not size-limited.

2. **FT benefit is non-monotonic in size.** Largest at 0.5B (+7.7 pp), shrinks at 1.5B and 3B (+3.7 pp, +2.0 pp), then recovers at 7B (+4.0 pp). The small models have more to gain from format exposure; the 3B model is near a local ceiling where xlam's semantic content adds little; the 7B model has enough capacity to use the training signal more effectively.

3. **3B with FT-aligned does not approach 7B.** 3B+FT-aligned = 66.8%, 7B+FT-aligned = 76.75% — a 10 pp gap. Fine-tuning compresses within-size variance but does not substitute for scale.

4. **The 3B→7B gap grows under FT-aligned (+9.95 pp vs +7.95 pp under CD only).** The 7B benefits more from aligned FT than the 3B, so the gap actually widens. xlam's training data appears to have stronger signal for a model with 7B-scale capacity.

## Cascade implications

For a two-tier cascade with 3B as small tier and 7B as large tier:

- Without FT: 3B handles 64.8%, escalates 35.2%
- With FT: 3B handles 66.8%, escalates 33.2%
- FT provides 2 pp routing improvement at the small tier

The 10 pp quality gap between tiers (66.8% vs 76.75%) means escalated calls still benefit significantly from the 7B. The cascade incentive structure is preserved.

## Result files

| Job | Model | Result dir |
|-----|-------|------------|
| 28439693 | 0.5B merged-aligned | `data/output/bfcl_ft_aligned/_zhome_.../Qwen2.5-0.5B-Instruct-merged-aligned/` |
| 28439694 | 1.5B merged-aligned | `data/output/bfcl_ft_aligned/_zhome_.../Qwen2.5-1.5B-Instruct-merged-aligned/` |
| 28439696 | 3B merged-aligned | `data/output/bfcl_ft_aligned/_zhome_.../Qwen2.5-3B-Instruct-merged-aligned/` |

Scores: `data/output/bfcl_ft_aligned/scores/simple_python_scores.json` (overwritten by last run, 3B; per-model results in individual run dirs)
Merged models: `models/merged/Qwen_Qwen2.5-{0.5B,1.5B,3B}-Instruct-merged-aligned`
