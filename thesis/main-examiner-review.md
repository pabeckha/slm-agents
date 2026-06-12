# Examiner Review — Agents with Small Language Models

**Author:** Paulo Ricardo Beckhauser de Araujo · **Reviewed:** 2026-06-10 · **Pages:** 57 content + appendices (65 PDF pages total)
**Reviewer note:** AI-assisted examiner review — to be verified and owned by the examiner.

---

## 1. Summary of the thesis

The thesis investigates which optimization techniques make a small language model (0.5B–7B parameters) reliably call tools, with the practical motivation of an SLM tier in a cascade architecture that offloads the majority of requests from a frontier-model API. Three research questions are addressed: (RQ1) the performance gap between unoptimized SLMs and frontier models; (RQ2) the marginal contribution of each technique when applied cumulatively; (RQ3) whether a fully optimized SLM configuration can meet production-viability criteria on consumer hardware. An incremental ablation study evaluates 12+ configurations of Qwen 2.5 (0.5B–7B) on BFCL v4 and τ-bench retail. The central finding is that the unoptimized failure mode is format non-compliance (394/400 failures are malformed JSON, not wrong answers), that constrained decoding eliminates this class structurally and raises accuracy from 1.5% to 72.75%, and that schema-enriched constrained decoding (CD+schema) further raises accuracy to 89.0%, entering the frontier range without modifying model weights.

---

## 2. Overall assessment

This is a methodologically careful, well-scoped MSc thesis with a genuine empirical contribution. The ablation design is appropriate for the questions asked, the claims are consistently backed by evidence, and the limitations section is unusually transparent — the threats-to-validity catalogue (Section 5.3.1) is notably thorough for a thesis at this level. The central finding — that the dominant failure is format compliance, not reasoning, and that schema information loss (rather than model capacity) drives most of the residual after plain CD — is both non-obvious and well validated. Writing is precise and economical; figures are honest and well-captioned.

The main things holding the thesis back from the top band are: (1) the primary evaluation is confined to BFCL simple python, the least demanding of the four BFCL categories, with harder categories covered only partially; (2) the τ-bench evaluation uses the same model as both agent and user simulator, making the absolute pass rate hard to interpret in isolation; (3) the strongest result (CD+schema, 89.0%) is absent from the cost-benefit analysis in Section 5.2, which is the chapter's primary analytical section; (4) one or two bibliography entries appear never to be cited in the text. None of these undermine the core claims, and the first three are acknowledged in the thesis itself.

**Indicative grade band: 10 (B) — very good.** The work fulfils its objectives comprehensively with a few minor to moderate weaknesses. Fixing issue #1 (adding CD+schema to Section 5.2) and #3 (citation hygiene) are the two highest-leverage changes before submission. A frontier-model simulator run on τ-bench would push the agentic evaluation toward 12 territory but requires additional compute that is realistically a future-work item.

---

## 3. Strengths

- **Tight problem framing.** The distinction between format failures and semantic failures (Section 1.2, p. 11) organises the entire evaluation coherently and allows each result to be interpreted unambiguously.
- **Rigorous ablation design.** Twelve configurations on a single 400-case test set, with per-case prediction files enabling paired McNemar tests, gives the comparisons genuine statistical grounding (Sections 4.2–4.4).
- **Honest negative-result reporting.** The CoT flip analysis (Fig. 4.2, p. 33) — 51 losses vs. 24 gains from chain-of-thought — is a model of how to report negative results: not just the net accuracy delta but the per-case directional breakdown with mechanistic explanation.
- **B-template control.** Including the native-template control (96.00%, p. 22) is methodologically important and correctly interpreted: it bounds the integration gap and prevents the 1.5% baseline from being read as a model capability claim.
- **CD+schema result.** The McNemar test on 73 vs. 7 discordant pairs (p < 0.00001, p. 24) is clean and the mechanism — missing schema vocabulary drives most of the residual — is directly validated by the contingency counts, not inferred.
- **Threats-to-validity section** (Section 5.3.1, pp. 51–53) is unusually thorough, covering τ-bench simulator bias, BFCL simple python reliance, benchmark convention mismatch, and the run-to-run spread with explicit quantification (±0.5 pp).
- **Practical deployment guidelines** (Section 6.2, pp. 57–58) are concrete, ordered by implementation cost, and faithfully reflect the evidence.

---

## 4. Evaluation by dimension

### Methodology & rigor

The experimental design is fit for the research questions. The cumulative ablation ladder — adding one technique at a time, with technique isolation runs in both directions (with and without CD, Tables 4.5–4.6) — allows unambiguous marginal attribution. Train/test separation is maintained; the format-mismatch hypothesis for LoRA is confirmed by a controlled replication (v1 vs. v2 adapters, Fig. 4.4, p. 38), which is good experimental practice. Sample size (n=400) is standard for BFCL; the ±4.1–4.4 pp Wilson interval is reported correctly, and borderline comparisons are appropriately hedged.

The main methodological limitation is the single-model-family design (Qwen 2.5 only). Directional findings are consistent across four sizes, which is the correct basis for the stated conclusions, and the limitation is acknowledged (pp. 50–51).

The τ-bench simulator issue is the most significant methodological weakness. Using the same 7B model as both agent and user simulator means simulator errors (misstatements, omissions) deflate pass rates independently of agent capability. The absolute 4.35% figure therefore conflates agent and simulator failures. The thesis correctly does not compare this to published pass rates from frontier simulators, but a stronger statement quantifying the expected simulator contribution to the failure rate — even based on trajectory inspection — would sharpen the finding.

### Technical / mathematical correctness

The attention formula (Eq. 2.1, p. 14) is standard and correct. The McNemar test is the correct choice for paired binary comparisons on shared cases; the exact two-sided variant with stated discordant-pair counts (b=73, c=7; b=45, c=27) is correctly applied and the borderline p=0.044 is honestly labelled "borderline" (p. 38). The Wilson confidence interval is the appropriate choice at n=400 (p. 41).

Memory and latency calculations are internally consistent: AWQ 63.5% memory reduction (14.25 → 5.20 GiB, p. 23), 8× latency gain (6.995 s → 0.878 s, p. 35). The claim that CD+schema introduces no additional latency (0.704 s mean, p. 33) is directly measured and contrasts correctly with the unconstrained baseline. No mathematical errors found.

### Contribution & novelty

The contribution is correctly characterised as applied and empirical rather than a new method. The genuine novelties are: (a) the systematic incremental ablation across 12 configurations on a single model family at four sizes; (b) the format-alignment insight from LoRA — a controlled replication isolating output format as the controlling variable (Section 4.4.1, pp. 37–38); (c) the direct quantification of schema information loss as the dominant residual component after plain CD (CD+schema, Section 4.2.3). These are meaningful contributions for an MSc thesis.

Related-work coverage is adequate. The key prior works — Willard & Louf [30] on FSM-based constrained generation, Gorilla [21] on training-time retrieval, ToolLLM [22] on disambiguation degradation with API count — are all present and accurately described. The Tam et al. [26] connection to the CoT regression (p. 53) is appropriately drawn.

One citation gap: reference [9] (Hinton, Vinyals, Dean — "Distilling the Knowledge in a Neural Network") appears in the bibliography but is not cited in the text. Reference [5] (Dettmers et al. — QLoRA) also appears not to be cited in the main text, though it is directly relevant to Section 2.6 (Parameter-Efficient Fine-Tuning). Both should be either cited in context or removed.

### Business / practical relevance

The cascade framing (Section 2.2.4, p. 16; Section 5.4, pp. 52–53) grounds the evaluation in a concrete deployment scenario. The cost model is transparent: savings expressed as p × c per query, with explicit p values per configuration. The cascade criterion (p ≥ 0.70, ≤24 GiB) is stated in advance (pp. 11–12) and evaluated against specific configurations, not retrofitted. The acknowledgement that p values are upper-bound estimates requiring a semantic router (p. 52) is an important honest caveat.

The cost-benefit discussion is qualitative about break-even query volume (Section 5.4, p. 52). A worked numerical example using order-of-magnitude API token costs and LoRA training compute costs would make the deployment trade-off more actionable, but this is a polish point.

---

## 5. Issues to address

| # | Severity | Area | Location | Issue & why it matters | Suggested fix |
|---|----------|------|----------|------------------------|---------------|
| 1 | **Major** | Contribution | Section 5.2, pp. 48–50 | CD+schema (89.0%, the strongest result and the only configuration to achieve frontier parity without weight modification) is entirely absent from the cost-benefit analysis. Section 5.2 covers CD, quantization, PE, CoT, RAG, and LoRA, but not schema enrichment. Given that CD+schema has zero training cost, no latency overhead (0.704 s mean, below unconstrained baseline), and the highest single-step accuracy gain (+16.25 pp), its cost-benefit ratio is the highest in the evaluation. Omitting it leaves the most important result without an analytical home in the discussion chapter. | Add a dedicated paragraph in Section 5.2 for CD+schema: zero training cost, no extra tokens, no latency overhead, +16.25 pp gain, cost scales with schema richness (benefit proportional to the density of descriptions/enumerations/defaults in the tool schema). Note the practical constraint: requires maintaining enriched prompt templates per tool. |
| 2 | **Major** | Methodology | Section 4.6 / 5.3.1, pp. 43, 51 | The τ-bench user simulator is the same Qwen 2.5 7B model used as the agent. The thesis flags this correctly in Section 5.3.1 but provides no quantitative bound on the simulator contribution to failures. The 4.35% pass rate conflates agent failures and simulator errors. Without at least a trajectory-based estimate of how many failures are simulator-side, the claim "single-call accuracy does not predict multi-turn performance" is well-supported, but the claim about the specific failure taxonomy (state drift, premature termination, etc.) rests on trajectories where some episodes were corrupted by the simulator. | In the submission window, a full frontier-simulator rerun is likely infeasible. At minimum: (1) add to Section 5.3.1 a sentence estimating the magnitude — e.g., "based on trajectory inspection, an estimated X% of failures involved ambiguous or incomplete simulator turns that a frontier simulator would likely have handled correctly"; (2) if any short frontier-simulator run is feasible on HPC, even 20–30 tasks would provide an indicative bound. |
| 3 | **Minor** | Writing / citation | Bibliography, pp. 60–61 | Reference [9] (Hinton et al. — knowledge distillation) appears in the bibliography but is not cited anywhere in the thesis text. Reference [5] (Dettmers et al. — QLoRA) also does not appear to be cited in the text, despite being directly relevant to Section 2.6 and the LoRA experimental section. Uncited bibliography entries are a citation hygiene issue and may raise examiner questions about whether the author has read the cited work. | Search the LaTeX source for `\cite{hinton` and `\cite{dettmers`. For [5]: add a sentence to Section 2.6 comparing QLoRA (quantization-aware fine-tuning) to the LoRA-then-AWQ approach used here, and cite it. For [9]: either add a sentence on distillation as a related but out-of-scope technique in Section 2.6 or Section 6.3 (future work), or remove from the bibliography. Removing [9] will shift subsequent reference numbers — check consistency throughout. |
| 4 | **Minor** | Writing | Title page, p. 3 | ISSN and ISBN fields contain placeholder values (`[0000-0000]`, `[000-00-0000-000-0]`). These will be visible in the submitted PDF. | Remove the placeholder lines or replace with the actual DTU report series identifiers assigned at submission. |
| 5 | **Minor** | Methodology | Section 5.2, p. 52 | The cascade cost-benefit discussion ("at low throughput, CD+Q is preferable; at high throughput, the break-even moves earlier") is qualitative where a worked example would be more useful. A deployment engineer reading the thesis cannot derive the break-even without external numbers. | Add one order-of-magnitude worked example: e.g., if an A100-hour of LoRA training costs ~$3 (DTU HPC approximate rate) and a GPT-4o token call costs $X/M tokens at Y tokens per call, the break-even query count is $3 / (0.02 × $X × Y). Even rough numbers give the reader a calibration point. |
| 6 | **Minor** | Methodology | Table 4.10, p. 43 | τ-bench size sweep reports single runs at 0.5B, 1.5B, 3B; the 7B result is the mean of three runs. The full spread (1.74%–4.35%) is less than two standard errors at n=115, but the table caption only states "other conditions are single runs" without saying the spread is within noise. Readers may incorrectly infer a size trend. | Strengthen the table caption: "The full spread (1.74%–4.35%) is within two standard errors (≈1.9 pp per run at n=115); no ranking between conditions is statistically supported." |

---

## 6. Questions for the defense

1. **The B-template control reaches 96.00% with free generation, but your constrained configurations top out at 89.0% (CD+schema).** You attribute the 7 pp gap to "native template prompt-format advantage and residual scorer artifacts." How much of that gap is scorer artifact vs. genuine model capability? If you replaced your model-agnostic prompt with the native template's system prompt while keeping the FSM constraint, where would accuracy land?

2. **CD+schema (89.0%) without any training beats CD+FT-aligned (76.75%) with fine-tuning on 54,000 examples.** This means adding schema detail to the prompt is worth more than a full LoRA training run. What does this imply about where the model "stores" argument value conventions — in weights vs. context? And does it change when you would recommend investing in fine-tuning at all?

3. **The RAG configuration has 97.2% recall@5 but only 47.75% accuracy — a 49 pp gap caused by candidate disambiguation.** Is there a k=1 result? What does selecting the single top-1 retrieved function produce, and what does it reveal about whether a better retrieval model (not just top-k) could close the gap?

4. **τ-bench retail: 4.35% at 7B with CD, not meaningfully different from 3B or 1.5B.** You attribute this to multi-turn planning failure, but your simulator is the same 7B model used as the agent. Walk through a specific trajectory from your stored runs where you believe the failure is agent-side, and one where you believe it might be simulator-side. How confident are you in the attribution?

5. **Parallel category: 0% across all configurations and sizes.** You diagnose this as a hard architectural boundary — the pipeline emits at most one argument object per distinct function name. What is the minimum pipeline change that would unlock parallel calls? An output schema returning an array of call objects, a loop that iterates over call count, or something else? And can constrained decoding enforce an array output schema with repeated function names?

6. **Your deployment guidelines list schema enrichment as Step 5**, after CD, quantization, cautious prompting, and fine-tuning. But CD+schema has no training cost, no latency overhead, and the highest accuracy of any no-training configuration. Why is it Step 5 rather than Step 1b, applied immediately after constrained decoding?

---

## 7. Verification notes

- **Frontier leaderboard scores** (Table 4.8, p. 41): taken from the BFCL leaderboard, accessed 2026-06-04 and re-verified 2026-06-10 (data last updated 2026-04-12 per the page). The examiner should verify these are current at assessment time and note the cross-harness caveat in Section 4.5.
- **τ-bench absolute pass rates** (4.35%) should not be directly compared to published pass rates from papers that used frontier-model simulators — the simulator difference makes the comparison non-like-for-like.
- **McNemar test values** (b=73, c=7 for CD+schema vs. CD; b=45, c=27 for CD+FT-aligned vs. CD) depend on stored per-case prediction files from the HPC runs. The examiner may wish to request these files or a reproducibility script to confirm the paired comparisons use matched predictions from the same configuration runs.
- **References [5] and [9]**: the examiner should ask the author to confirm which sections cite these works, as they appear potentially uncited in the current text.
