# Examiner Review — Agents with Small Language Models

**Author:** Paulo Beckhauser · **Reviewed:** 2026-06-20 · **Pages:** 72 (PDF)
**Reviewer note:** AI-assisted examiner review — to be verified and owned by the examiner.

## 1. Summary of the thesis

The thesis asks which inference- and training-time optimization techniques let a
small language model (SLM, 0.5B–7B) call tools reliably enough to serve as the
local tier of a cascade architecture. It answers three research questions (§1.3):
**RQ1** the unoptimized SLM-vs-frontier gap; **RQ2** the marginal contribution of
each technique (constrained decoding, schema enrichment, few-shot, chain-of-thought,
RAG, AWQ quantization, LoRA fine-tuning) applied cumulatively; **RQ3** whether a
fully optimized config is production-viable on consumer hardware. A two-stage
constrained-decoding pipeline is built and twelve configurations are evaluated over
Qwen 2.5 (four sizes) on BFCL v4 (`simple_python` plus the harder `multiple`/
`parallel`/`parallel_multiple` categories), on τ-bench retail, and on a small
GitHub-MCP real-world set, with comparison to frontier leaderboard scores. The
central claim: constrained decoding converts tool calling from a *format-compliance*
problem (fixable structurally at inference time) into a *semantic argument-value*
problem, of which the dominant remaining component is schema information discarded
by a generic prompt — recovered by schema-enriched CD (89.0%, the strongest
no-training result).

## 2. Overall assessment

This is a strong, carefully executed empirical thesis. What carries it is scientific
discipline: the central format-vs-semantic distinction is genuinely illuminating and
is backed at every turn (394/400 baseline failures are structural); the **B-template
control** (§4.1) is excellent hygiene that stops the dramatic "1.5%→89%" arc from
becoming an overclaim, by showing the same model already reaches 96% under its native
template; and the **negative results are reported plainly** (few-shot −2.5 pp, CoT
−6.75 pp, RAG −24.5 pp) rather than buried. Statistical handling is above the bar for
a Master's: paired McNemar tests with b/c counts, a documented ±0.5 pp run-to-run
spread, and honest labelling of a borderline result (p=0.044) and a non-significant
one (p=0.38). The `parallel` 0%→79% diagnosis — recognising a pipeline artefact and
fixing the schema rather than blaming model capacity — is a highlight of intellectual
honesty.

What holds it back is breadth and the gap between framing and delivery. The headline
"frontier parity" rests on `simple_python`, the *least* demanding BFCL category
(single-turn, single-candidate, no selection ambiguity); the thesis says so, but the
strongest claim leans on the easiest task. The **cascade architecture** is the
motivating frame and the source of the practical-impact chapter, yet it is never
built or measured — the economic results (p≈0.72–0.77, break-even N≈15,000) are
extrapolations resting on an explicitly unbuilt semantic router. And the titular word
"agents" is, on the thesis's own evidence, where the approach *fails*: τ-bench retail
sits at 4.35%, barely above noise. None of these is an unsupported claim — each is
carefully scoped and acknowledged — so there is no Critical defect; they are real but
non-fatal weaknesses, mostly converted into stated limitations.

**Indicative grade band (written report only, advisory): 10 (B)**, with a credible
reach to **12 (A)** on a strong defense. What would move it up: demonstrating any
part of the cascade end-to-end, or making the harder BFCL categories (not
`simple_python`) carry a headline claim. What would pull it toward 7: if the defense
revealed the few-shot/PE design or the frontier cross-harness comparison to be less
controlled than the text presents.

## 3. Strengths

- **The organizing distinction is real and well-evidenced** (§1.2, §6.1): format
  failures (structural, fixable by CD) vs semantic failures (value conventions,
  not). The 394/400-structural baseline breakdown anchors it concretely.
- **B-template control** (§4.1, §3.6): prompting the same model through its native
  tool-calling template reaches 96.0%, reframing the 1.5% baseline as the cost of a
  *generic integration*, not a capability deficit. This is the single best
  methodological decision in the thesis and it recurs consistently.
- **Schema-enrichment result** (§4.2.3): CD+schema 89.0% (+16.25 pp, McNemar
  p<0.00001, b=73/c=7) localizes the residual to missing schema detail rather than
  model priors — the most novel and most defensible finding.
- **Honest negative results** (§4.2, §4.3) with mechanism analysis (the CoT
  flip-analysis table; the RAG disambiguation breakdown showing recall@5=97.2% yet
  −24.5 pp).
- **Statistical care** (§3.3, §4.4, §5.3.1): run-to-run spread quantified and used to
  temper borderline claims; paired tests where the design is paired; Wilson CIs in
  the frontier comparison.
- **Reproducibility**: pipeline, prompts, guided-decoding schemas, HPC scripts, and
  training scripts in a public repo (§3.1.2); hardware/software stack pinned.
- **Format-alignment finding** (§2.7.1, §4.3.2): two adapters, identical
  hyperparameters/loss, differing 7.0 pp purely by output-format match — a clean
  extension of Gorilla's data-relevance insight to format alignment.

## 4. Evaluation by dimension

**Methodology & rigor.** Design fits the questions for RQ1/RQ2; the cumulative
ladder plus the no-guided isolation arm cleanly separates each technique's standalone
effect from CD's contribution. The main soft spot is generality: the primary metric
is one BFCL category on one model family, and the constrained-decoding advantage is
explicitly contingent on oracle function provision (§5.3.1). The PE few-shot examples
are hand-authored from failure *classes* identified by inspecting the 109 test-split
errors (§3.6/§4.2.2) — the thesis flags this, but it means the technique's design is
informed by the evaluation split, a mild contamination worth stating even more
plainly. RQ3's cascade economics are extrapolated, not measured (§5.4).

**Technical/mathematical correctness.** The standard formulas (scaled-dot-product
attention §2.1.1; LoRA W+AB §2.6.1) are correct and used consistently. The statistics
are sound: McNemar is the right test for paired binary outcomes, and significance is
neither overclaimed nor inflated — the thesis explicitly downgrades p=0.044 to
"borderline" against the run-to-run spread and calls p=0.38 not significant. I could
not independently verify the 94.50% figure attributed to ToLeaP (chen2025toleap),
which is a per-model number from that paper's tables — see §7.

**Contribution & novelty.** Incremental but solid for the level. The synthesis — a
single controlled cumulative ablation spanning CD, schema enrichment, quantization,
prompting, RAG, and format-aligned LoRA across four sizes — is the claimed gap (per
the sharma2025 survey) and is delivered. The schema-enrichment localization and the
format-alignment result are the two findings most likely to interest the field.
Related-work coverage is appropriate and fairly represented.

**Business/practical relevance.** The Step 1–5 deployment decision ladder (§6.2) and
the break-even model (§5.4) are genuinely useful and honestly labelled as upper-bound.
One tension deserves attention: §5.4 concedes that for a single frozen model the
native template (96%) supersedes every constrained configuration "on accuracy
grounds" — an intellectually honest admission that also partly undercuts the thesis's
own recommended path, and the strongest single thread an examiner will pull.

## 5. Issues to address

| # | Severity | Area | Location | Issue & why it matters | Suggested fix |
|---|----------|------|----------|------------------------|---------------|
| 1 | Major | Methodology | §4.6, §5.2 / abstract | Headline "frontier-range" parity rests on `simple_python`, the easiest category; the harder categories (where `parallel` only works after a schema fix and `parallel_multiple` tops out ~72.5%) tell a more sobering story. The claim is scoped, but the abstract/intro emphasis can read as stronger than the evidence base. | Add one sentence in the abstract and §6.1 explicitly subordinating the 89% claim to the single-candidate setting; let a harder-category number share the headline. |
| 2 | Major | Methodology / Business | §5.4, RQ3 | The cascade is the motivating architecture but is never built; p-values and break-even N assume an ideal semantic router that §5.4 itself says is not evaluated. The practical chapter's quantitative claims are extrapolations. | Reframe §5.4 results as projections with the router assumption stated up front in the section lead, not only mid-section; or add even a toy routing experiment. |
| 3 | Major | Contribution | Title / §5.5, §6.3 | The title promises "Agents," but multi-step agentic performance (τ-bench 4.35%) is where the approach fails. Honestly scoped, but a reader expecting agents finds single-call tool calling. | Either soften the title's scope or foreground early (abstract + §1.1) that the contribution is the single-call tier of an agentic stack, not end-to-end agency. |
| 4 | Major | Methodology | §3.6, §4.2.2 | PE few-shot examples are designed from failure classes identified on the evaluation test split; this couples technique design to the test set. Flagged, but under-emphasized given PE is one of RQ2's techniques. | State the contamination plainly as a threat to the PE result specifically, and note a held-out dev split would be the correct design. |
| 5 | Minor | Methodology | §4.7 | The GitHub-MCP section (50 hand-crafted prompts, single domain, write tools not executed) is thin and reads as a late addition; it now connects to intro/conclusion but carries little evidential weight. | Keep, but label it explicitly as an exploratory probe and avoid letting it bear any generalization claim. |
| 6 | Minor | Methodology | §3.5.2, §4.5.1 | τ-bench uses a 7B user simulator (not the reference frontier simulator) and single runs at non-7B sizes; absolute pass rates are weak. The *qualitative* conclusion survives (the gap is ~68 pp), but the numbers are noisy. | Already well-handled in §5.3.1; consider moving that caveat nearer the first τ-bench number. |
| 7 | Minor | Technical / Citation | §4.1, §4.6 | The "94.50%" corroborating figure (chen2025toleap) and the `snell2024scaling` cite used for *cascade architectures* (§2.2.4) should be checked — Snell is a test-time-compute paper, not a cascade reference. | Verify the 94.50% against ToLeaP's tables; add a dedicated cascade citation or soften the attribution. |
| 8 | Minor | Writing | §6.1 | The RQ2 answer was a single ~60-line paragraph (now split); confirm the split reads cleanly and that the MCP prose and condensed intro paragraph match your voice. | Author voice pass (in progress). |

## 6. Questions for the defense

1. §5.4 states that for a single frozen model the native template (96%) beats every
   constrained configuration on accuracy. Why, then, is constrained decoding the
   recommended deployment path rather than the native template — and in which concrete
   deployment does the structural guarantee actually pay for the accuracy it costs?
2. Your strongest result (CD+schema, 89%) is on the single-candidate category. How much
   of it survives when function selection is non-trivial — and what is the honest
   headline number for a realistic multi-candidate deployment?
3. The cascade economics (break-even N≈15,000) assume an ideal semantic router that you
   did not build. After CD removes all structural routing signals, what evidence do you
   have that such a router is achievable at the accuracy your p-values assume?
4. τ-bench is 4.35% — effectively a failure at the agentic task your title names. What,
   specifically, in your results predicts that any of the techniques studied would move
   that number, given they did not?
5. The few-shot examples were designed from errors observed on the test split. How do
   you bound the effect of that on the PE result, and would PE still be negative on a
   clean held-out set?

## 7. Verification notes

- **94.50% (ToLeaP / chen2025toleap):** a per-model BFCL number from that paper's
  tables; I verified the citation exists and is on-topic but not the figure itself.
  The examiner/author should confirm it against the source before relying on it.
- **Frontier leaderboard scores** (§4.6) are cross-harness, not re-run locally; the
  thesis acknowledges this and the B-template control bounds the comparability concern,
  but the exact frontier numbers depend on the leaderboard snapshot dated in the text.
- **MCP table figures** (§4.7) were validated against an internal results doc per the
  source notes; `make test` passes on the encoded claims, but the prose numbers I drafted
  should be cross-read against `docs/decisions/mcp-eval-results-section-outline.md`.
