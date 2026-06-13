# Pyramid Principle & MECE

## The Pyramid Principle (Barbara Minto)

Structure every deck top-down:
1. **Answer first** — state the conclusion before the evidence (inductive)
2. **Grouped support** — group supporting arguments into 3 (±1) buckets
3. **Each bucket** — supported by its own evidence layer below

```
Conclusion (slide 1 or title slide subtitle)
├── Argument A (slide 2 title)
│   ├── Evidence A1
│   └── Evidence A2
├── Argument B (slide 3 title)
└── Argument C (slide 4 title)
```

## MECE

Groups must be **Mutually Exclusive** (no overlap) and **Collectively Exhaustive** (nothing missing).

Test: can any item appear in two groups? → not ME. Is there an obvious category missing? → not CE.

Common MECE frameworks:
- By time: past / present / future
- By geography: region A / region B / ...
- By segment: user type A / B / C
- By issue: problem / cause / solution

## Horizontal Logic

Reading only the titles across slides in a section, they must form a logical argument — each title either continues a sequence or adds a parallel point.

Bad sequence:
- "Model accuracy results"
- "Quantization overview"
- "LoRA improved accuracy"

Good sequence (parallel, each proves one sub-claim):
- "Constrained decoding raises accuracy by 71 pp"
- "Quantization adds no accuracy cost"
- "Format-aligned LoRA is the only technique that surpasses the CD baseline"

## Vertical Logic

Within each slide, every bullet / data point must directly support the title claim. If a bullet would be equally true under a different title, cut it.
