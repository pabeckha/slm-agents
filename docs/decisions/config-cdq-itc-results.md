# Config CD+Q+ITC Results — CoT Before Argument Extraction

**Status**: complete
**Date**: 2026-04-11
**Job**: 28187017 on L40S 46GB (gpul40s)
**Model**: `Qwen/Qwen2.5-7B-Instruct-AWQ` via vLLM 0.8.5
**Backend**: `src/vllm_backend.py` (`guided_choice` + free-form reasoning + `guided_json`, `cot=True`)
**Benchmark**: BFCL v4 simple_python (400 test cases)
**Configuration**: Config CD+Q+ITC — AWQ INT4 + guided decoding + CoT reasoning before argument extraction
**Spec**: `config-cdq-itc-spec.md`

## Results

**AST accuracy: 65.5% (262/400) — a substantial negative result, -6.5 pp vs CD+Q.**

### Comparison across configs

| Config | Accuracy | Correct | Model Size | Delta vs CD+Q |
|--------|----------|---------|-----------|---------------|
| B (no guided) | 1.5% | 6/400 | 14.25 GiB | -70.5 pp |
| **CD+Q+ITC (CoT + guided + AWQ INT4)** | **65.5%** | **262/400** | **5.20 GiB** | **-6.5 pp** |
| PE (few-shot + guided) | 70.25% | 281/400 | 14.25 GiB | -1.75 pp |
| CD+Q (guided, AWQ INT4) | 72.0% | 288/400 | 5.20 GiB | baseline |
| CD (guided, full precision) | 72.75% | 291/400 | 14.25 GiB | +0.75 pp |

CD+Q+ITC is **the worst-performing no-training config that uses guided decoding** — worse than PE, worse than CD+Q, and worse than full-precision CD. Cot regressed in both absolute accuracy and relative to every other config evaluated on this benchmark.

### Flip analysis (CD+Q → CD+Q+ITC)

Rescoring both result sets against the BFCL ground truth lets us separate gains (cases CoT recovered) from losses (cases CoT broke).

| Flip | Count |
|---|---|
| CD+Q failure → CD+Q+ITC success (gains) | 24 |
| CD+Q success → CD+Q+ITC failure (losses) | 50 |
| **Net change** | **-26** |

CoT did help on some cases — but it broke **more than twice as many** cases as it fixed. The gains look like the model guessing closer to BFCL's arbitrary optional-parameter defaults (`round=2`, `units='cm'`, `face_value=1000`, `mod=1`). The losses are more systematic.

## The dominant failure pattern

**CoT moves the model *toward* linguistic naturalness and *away from* BFCL's learned-association conventions.**

All 138 CD+Q+ITC failures are value mismatches on parameters the model picked (not missing arguments or wrong function names). 50 of those are cases where CD+Q had already produced BFCL's exact expected value and CoT overrode it with something more "reasonable".

The reasoning traces make the mechanism explicit — CoT does not fail silently, it fails *while arguing for the wrong answer*. Six concrete cases:

### Case studies — CoT broke CD+Q successes

**1. `simple_python_127` — discount rate unit flip**

- User request: ... discount_rate 10% ...
- CD+Q: `discount_rate=0.1` ✓ (matches BFCL)
- CD+Q+ITC: `discount_rate=10.0` ✗
- Reasoning trace excerpt:
  > "The cash flows are in dollars, and the discount rate is in percentage form. Extracted arguments: ... discount_rate = 10"
- The model reasoned itself into saying "percentage form" and wrote `10` where CD+Q's one-shot guided decode had already produced `0.1`.

**2. `simple_python_139` — yield unit flip (opposite direction)**

- User request: ... 5% yearly yield ...
- CD+Q: `yearly_yield=5.0` ✓
- CD+Q+ITC: `yearly_yield=0.05` ✗
- Reasoning trace excerpt:
  > "5% yearly yield should go into yearly_yield ... estimate_mutual_fund_return(0.05, 2000, 3)"
- Opposite direction from case 127: here CoT *decimalized* the percentage. The model has no consistent rule — CoT produces whichever normalization looks natural at the moment.

**3. `simple_python_147` — CoT "helpfully" preserved wording BFCL expected dropped**

- User request: ... last 2 weeks ...
- CD+Q: `duration='2 weeks'` ✓
- CD+Q+ITC: `duration='last 2 weeks'` ✗
- Reasoning trace excerpt:
  > "The duration is given as 'last 2 weeks', which needs to be preserved exactly as a string."
- Ironically, CoT's self-imposed instruction to "preserve exactly as stated" is precisely what broke the test. CD+Q's one-shot extraction dropped "last" and matched BFCL; CoT told itself to keep it.

**4. `simple_python_168` — date format normalization**

- User request: ... lawsuits filed ... January 1, 2021 ...
- CD+Q: `start_date='01/01/2021'` ✓
- CD+Q+ITC: `start_date='2021-01-01'` ✗ (BFCL expected `'01-01-2021'` or `'January 1, 2021'`)
- Reasoning trace excerpt:
  > "start_date: '2021-01-01' (assuming they want lawsuits filed after this date)"
- CoT defaulted to ISO 8601, which is the most defensible date format in isolation but not one of BFCL's accepted forms.

**5. `simple_python_200` — abbreviation expansion**

- User request: ... gas mileage ...
- CD+Q: `fuel_type='gas'` ✓
- CD+Q+ITC: `fuel_type='gasoline'` ✗
- Reasoning trace excerpt:
  > "Gasoline would be the fuel type ... calculate_emissions(12000, 'gasoline', 25.0, 0)"
- CoT expanded the user's abbreviation into its full form, which is the linguistically natural move. BFCL's accepted value was the abbreviation.

**6. `simple_python_203` — optional-default flip**

- CD+Q: `detail=True` ✓
- CD+Q+ITC: `detail=False` ✗
- Reasoning trace excerpt:
  > "There is no indication of needing detailed data, so we can assume 'detail' is False by default."
- The reasoning is plausible in isolation. BFCL's hidden convention for this function happened to be the opposite.

### Pattern summary

Across all six cases (and across most of the 50 losses), the reasoning traces read as competent, confident argument for the wrong answer. CoT is not hallucinating or refusing the task — it is **reasoning toward a linguistically natural, self-consistent interpretation** that does not match the arbitrary convention BFCL's ground truth happens to enforce.

The few-shot experiment (Config PE) showed prompt hints cannot fix learned-association errors. This experiment shows something sharper: **making the model reason explicitly actively hurts on this benchmark**, because reasoning surfaces linguistically-intuitive alternatives that override the quieter pattern-match CD+Q was relying on.

## Why the reasoning step backfires

Three mechanisms observed in the traces:

1. **Drift and over-explanation.** The reasoning prompt asked the model to "think step by step". The model interprets this as licence to produce full implementation sketches, quadratic-formula derivations, and justification paragraphs, all of which consume tokens and attention before the extraction step ever fires.
2. **Self-justification locks in early errors.** Once CoT commits to a value in the reasoning block ("extracted arguments: discount_rate = 10"), the subsequent guided JSON extraction inherits that value. The reasoning text acts as a prompt injection against itself.
3. **Natural-language normalization beats arbitrary conventions.** BFCL ground truths frequently encode one specific, often arbitrary, form ("gas" not "gasoline", "2 weeks" not "last 2 weeks", specific numeric precisions). CoT's default behavior is to produce the form a thoughtful human would write, not the form a specific dataset happens to label correct.

## Infrastructure Notes

- vLLM startup: 333s (first model load on gpul40s)
- Total test run: completed within the 2h wall time; reasoning step roughly doubled per-case latency vs CD+Q
- Reasoning traces: 400 files, saved to `data/output/bfcl_itc/reasoning/` for this analysis
- One observation from the traces: the `stop=["\nJSON:", "\nFunction:"]` safeguard prevented the model from leaking guided output into the reasoning block, but not from drifting into tangents (code blocks, math derivations). Future CoT work should also stop on `"\n\n"` or cap at ~100 tokens instead of 256.

## Implications for Thesis

### RQ2 (Marginal impact of each technique)

| Method | Expected Impact | Actual Impact |
|--------|----------------|---------------|
| Constrained Decoding | High | **+71.25 pp** (B → CD) |
| Quantization (AWQ INT4) | Neutral | -0.75 pp (CD → CD+Q) |
| Prompt Engineering (few-shot) | Medium (+5–10%) | **-2.5 pp** (negative) |
| **Inference-Time Compute (CoT)** | **Medium (+2–5%)** | **-6.5 pp** (strongly negative) |

Two out of two prompt-only interventions have now failed on the argument-extraction failure class, and CoT failed worse than PE. This is not a single noisy result — it is a consistent direction: **prompting interventions that ask the model to think or reference more examples make argument extraction worse on BFCL simple_python**, because the benchmark rewards exact match against arbitrary conventions, not thoughtful reasoning.

### Cumulative no-training chain

The best-performing no-training config is still **Config CD+Q at 72.0%**. Neither PE nor ITC improved on it. The no-training ceiling for Qwen 2.5 7B on BFCL simple_python is therefore approximately 72% — everything above that must come from training.

### The case for LoRA is now strong

Before CD+Q+ITC: one prompt-only technique (PE) failed with -2.5 pp. Could be noise, could be one technique being badly matched.

After CD+Q+ITC: two prompt-only techniques have failed, the second one with a larger negative delta and a clear *mechanistic* explanation (CoT reasons toward linguistic naturalness, BFCL rewards arbitrary conventions). The failure mode is not "the model doesn't know how" — it is "the model's internal priors about value formats do not match BFCL's labels, and prompting moves the model further from BFCL, not closer".

The only intervention remaining on the table that can actually change the model's internal association between a function-schema context and a specific value form is **LoRA fine-tuning** (or full fine-tuning). This is now the critical-path experiment for hitting the spec's 85% target.

### Cascade architecture implications

For a cascade where the SLM handles easy cases and escalates hard ones to a frontier model, CD+Q (72%) is the right SLM operating point. Adding CoT at the SLM tier would *increase* escalation traffic by ~6.5 pp, which is the opposite of what a cascade is supposed to do. CoT at the SLM tier is contraindicated for this benchmark.

### ReAct note

This result only speaks to the CoT variant of ITC on a single-call benchmark. It does not rule out ReAct as a distinct technique on multi-turn benchmarks (τ-bench), where reasoning has something real to consume (tool observations, intermediate state). The negative finding here is specifically: **CoT does not help single-call argument extraction on Qwen 2.5 7B, and in fact hurts it substantially**.

## Result Files

- Predictions: `data/output/bfcl_itc/Qwen_Qwen2.5-7B-Instruct-AWQ/non_live/BFCL_v4_simple_python_result.json`
- Scores: `data/output/bfcl_itc/scores/simple_python_scores.json`
- Reasoning traces (400 files): `data/output/bfcl_itc/reasoning/`
- Run manifest: `data/output/bfcl_itc/runs/2026-04-11T10-38-17_Qwen_Qwen2.5-7B-Instruct-AWQ_simple_python_guided_cot.json`
- Log: `logs/bfcl_itc_28187017.out`

## Next Steps

1. **Config CD+Q+RAG (Issue #7)** — closes the no-training Phase 1 stack. RAG retrieves tool schemas rather than trying to fix value extraction, so it targets a different failure mode and has no reason to inherit CoT's problem.
2. **Phase 2 LoRA (Issues #9, #22)** — the only remaining path to the spec's 85% target. The PE + ITC negative results are the empirical motivation for the entire training phase.
3. **Supervisor discussion (2026-04-13)** — confirm this result is strong enough evidence to commit hard to LoRA; discuss training data sources (Glaive vs BFCL train split vs Claude Opus distillation).
