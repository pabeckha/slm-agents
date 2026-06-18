# No-Guided JSON Parser Fix + Corrected Ablation Results (2026-06-12)

## Question

The few-shot no-guided 3B run (job 28626704) scored exactly 0/400, below both
smaller models (0.5B: 5.3%, 1.5B: 16.3%). Was this a real result or a
pipeline artifact?

## Root cause

All 400 cases failed with `json.loads` "Extra data" errors. The no-guided
argument-extraction path in `src/vllm_backend.py` sliced the completion from
the first `{` to the **last** `}` before parsing. Without guided decoding the
model often keeps generating after its answer (continuing the few-shot
pattern with more example blocks, or emitting a second JSON object), so the
slice spanned multiple JSON objects and parsing failed even when the first
object — the actual answer — was valid.

This affected every no-guided run to varying degrees, not just few-shot 3B:
RAG no-guided 3B had 321/400 "Extra data" failures, CoT no-guided 3B ~170,
FT-aligned no-guided runs dozens each. The scores measured the parser, not
the model.

## Fix

PR #163 (merged, `86bb5bf`): use `json.JSONDecoder().raw_decode()` starting
at the first `{` to parse the first complete JSON object and ignore trailing
text. Genuinely malformed JSON still raises and counts as a failure, so the
ablation still measures the model's ability to emit valid output — it just no
longer penalizes a valid object followed by trailing text.

## Methodology

- Jobs 28638056–59 and 28638553–557 (`run_bfcl_{few_shot,cot,rag,ft_aligned}_no_guided`),
  vLLM on L40S, no guided decoding, BFCL v4 `simple_python`, 400 cases each.
- Identical configs to the contaminated runs; only the parsing changed.
- Submission gotcha found along the way: `MODEL=x bsub < script` does NOT
  propagate the variable on DTU LSF (the first rerun batch silently ran the
  7B default). Use `bsub -env "all, MODEL=..."`.

## Results (old → corrected, % of 400)

| Config (no guided) | Old | Corrected | Δ |
|---|---|---|---|
| Few-shot, 3B | 0.0 | **65.3** | +65.3 |
| Few-shot, 7B | 4.5 | **59.0** | +54.5 |
| CoT, 3B | 14.3 | **58.3** | +44.0 |
| CoT, 7B | 26.3 | **56.3** | +30.0 |
| RAG, 3B | 2.3 | **48.5** | +46.2 |
| RAG, 7B | 2.5 | **52.0** | +49.5 |
| FT-aligned, 1.5B | 21.5 | **27.5** | +6.0 |
| FT-aligned, 3B | 4.0 | **24.3** | +20.3 |
| FT-aligned, 7B | 13.3 | **41.0** | +27.7 |

Run manifests: `data/output/bfcl_*_no_guided/runs/2026-06-12T*` (old
manifests retained alongside).

## Analysis

- The parser bug was the dominant failure mode in the prompting-based
  no-guided ablations. Corrected, the no-guided configs score 24–65% rather
  than 0–26%; the remaining failures are genuine (function-selection misses
  and truly malformed JSON).
- Ordering now looks sane: few-shot 3B (65.3%) > 1.5B (16.3%, still on old
  parser) and accuracy generally scales with model size within a config.
- FT-aligned no-guided improved least — consistent with the format-aligned
  LoRA already producing cleaner, single-object output (less trailing text
  for the bug to trip on), though its absolute scores remain low.

## Thesis implications

- **All previously reported no-guided numbers are biased downward** and
  understate the no-CD baseline, which *overstates* the contribution of
  constrained decoding. Any CD-vs-no-CD deltas in the thesis must use the
  corrected numbers.
- The qualitative conclusion survives — guided decoding still adds a large
  reliability margin (e.g. few-shot guided runs sit well above 65%) — but
  the gap is much smaller than the contaminated runs suggested.
- Still contaminated and pending rerun before any thesis table is final:
  0.5B/1.5B for few-shot/CoT/RAG no-guided, Config B (`bfcl_no_guided`) at
  all sizes, FT no-guided 7B (`bfcl_ft_no_guided`), and FT-aligned 0.5B.

## Decision

Treat all pre-2026-06-12 no-guided results as invalid. Re-run the remaining
contaminated configs with the fixed parser before updating thesis tables.

## Update 2026-06-18 — all sizes landed and verified (issue #172)

The remaining contaminated configs were re-run. Complete corrected no-guided
table, **verified against `data/output/*_no_guided/runs/2026-06-12T*` manifests**
(`correct_count / 400`), latest post-fix run per cell:

| Config (no guided) | 0.5B | 1.5B | 3B | 7B |
|---|---|---|---|---|
| Config B (`bfcl_no_guided`) | 104 = 26.00% | 206 = 51.50% | 263 = 65.75% | 248 = 62.00% |
| Few-shot (PE-ng) | 101 = 25.25% | 214 = 53.50% | 261 = 65.25% | 236 = 59.00% |
| CoT (ITC-ng) | 76 = 19.00% | 178 = 44.50% | 233 = 58.25% | 225 = 56.25% |
| RAG-ng | 99 = 24.75% | 173 = 43.25% | 194 = 48.50% | 208 = 52.00% |
| FT-aligned-ng | 139 = 34.75% | 110 = 27.50% | 97 = 24.25% | 164 = 41.00% |
| FT-only-ng (`bfcl_ft_no_guided`) | — | — | — | 212 = 53.00% |

CD contribution (with-CD minus no-CD, pp), using the corrected no-CD column:

| Technique | 0.5B | 1.5B | 3B | 7B |
|---|---|---|---|---|
| None (CD alone) | +25.50 | +10.75 | −1.00 | +10.75 |
| Few-shot | +28.25 | +11.25 | +1.75 | +11.25 |
| Chain-of-thought | +23.00 | +10.25 | −0.25 | +9.25 |
| Retrieval | +1.25 | −8.50 | −0.25 | −4.25 |
| Format-aligned LoRA | +24.50 | +38.50 | +42.50 | +35.75 |

### Strict vs. lenient parser (important framing)

The 1.50%% headline baseline and the 62.00%% corrected Config B are **the same
7B runs under two parsing criteria**, not a bug vs. a fix:

- **Strict** — `json.loads` on the *whole* completion (the naïve model-agnostic
  integration). The model emits a valid first object then trailing text, so the
  whole string fails to parse → 1.50%% (6/400). This is a legitimate strict
  floor and is **kept as the thesis headline** (`tab:baseline-results`, intro,
  abstract).
- **Lenient** — `raw_decode` of the *first* complete object (PR #163). Used in
  the **technique-isolation arm only**, so techniques are compared fairly rather
  than by how little trailing text they emit → Config B 62.00%%.

The genuinely-buggy parser was the *old lenient* one (first-`{` to last-`}`),
which spanned multiple objects and scored the isolation configs at 0–26%% when
their true lenient scores are 52–62%%. See
`docs/decisions/no-guided-thesis-corrections-2026-06-18.md` for the thesis edit
scope (option A) and the remaining prose-rewrite items.
