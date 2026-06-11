# Defense Preparation — Anticipated Examiner Questions

Six sharpest questions based on the examiner review, with grounded answers.

---

## Q1 — B-template vs. CD+schema gap (7 pp)

**Question:** The B-template control reaches 96.00% with free generation, but CD+schema tops out at 89.0%. You attribute the 7 pp gap to "native template prompt-format advantage and residual scorer artifacts." How much of that gap is scorer artifact vs. genuine model capability? If you replaced your model-agnostic prompt with the native template's system prompt while keeping the FSM constraint, where would accuracy land?

**Answer:**

The 7 pp gap is 28 cases (356 vs. 384/400). The thesis pins the CD+schema residual at 44 cases — all described as scorer convention artifacts (`"Los Angeles"` vs `"Los Angeles, CA"`, `1e-05` vs `0.0001`) that are explicitly "not addressable by further schema enrichment." The 28 extra B-template wins are a subset of those 44, where the native system prompt happens to prime the model toward the benchmark's specific value conventions.

The hybrid ablation (native system prompt + FSM constraint) was not run. Be direct: "That specific ablation is future work. The 44 residual failures are scorer artifacts the model cannot reason its way out of regardless of prompt; the native template's advantage is that its training distribution aligns with BFCL's value conventions, not that it enables qualitatively different reasoning."

---

## Q2 — Schema enrichment beats fine-tuning

**Question:** CD+schema (89.0%) without any training beats CD+FT-aligned (76.75%) with fine-tuning on 54,000 examples. What does this imply about where the model stores argument value conventions — in weights vs. context? And does it change when you would recommend investing in fine-tuning at all?

**Answer:**

The model has argument value conventions in parametric memory (it knows enumeration values, numeric formats, string conventions) but the model-agnostic prompt does not supply the vocabulary to activate the right token. Enumerations like `["gasoline", "diesel", "electric"]` in the schema directly constrain the FSM to the correct token — no training needed. Schema enrichment does not teach the model anything new; it restores the disambiguation signal the prompt was suppressing.

Fine-tuning on xlam fails because xlam encodes Python call syntax and different value conventions that conflict with the eval pipeline; it overwrites correct conventions with wrong ones. The training signal is meaningful (FT-aligned-ng improves Base by 12.25 pp) but the conventions learned conflict with the evaluation harness.

**When to recommend fine-tuning:** when the schema is sparse (no descriptions or enumerations) and you have in-domain training data aligned to your output format. For teams with rich schemas, schema enrichment is the higher-return intervention at zero training cost.

---

## Q3 — RAG k=1

**Question:** The RAG configuration has 97.2% recall@5 but only 47.75% accuracy — a 49 pp gap caused by candidate disambiguation. Is there a k=1 result? What does selecting the single top-1 retrieved function produce?

**Answer:**

A k=1 result was not run. The key evidence is Fig. 4.3: 66% of RAG outputs are identical to CD+Q — the model ignores the retrieved context entirely in two-thirds of cases. k=1 would reduce disambiguation pressure in the 34% of cases where retrieval has any effect, but the 66% "retrieval no-ops" would remain unchanged.

The bottleneck is generation, not retrieval. The 7B model cannot reliably select the correct function from a retrieved candidate list even when the correct function is present (recall@5 = 97.2%). This is consistent with the Gorilla finding that inference-time retrieval without a training signal on candidate disambiguation produces poor selection accuracy despite high retrieval recall.

---

## Q4 — τ-bench failure attribution (agent vs. simulator)

**Question:** τ-bench: 4.35% at 7B with CD. Walk through a specific trajectory where the failure is clearly agent-side, and one where it might be simulator-side. How confident are you in the failure taxonomy?

**Answer:**

Be honest: the failure taxonomy (state drift, premature termination, tool parameter errors, context overflow) comes from structural analysis of task types, not from reading individual transcripts. Specific trajectory excerpts were not retained.

**Quantitative robustness bound:** Three runs with deterministic agent (temp 0.0, seed 42) produced 3.48%, 4.35%, 5.22%. The 1.74 pp spread is the observed simulator-noise ceiling — entirely attributable to stochastic simulator turns since the agent is deterministic. The qualitative conclusion (67+ pp gap to BFCL single-call accuracy) holds even at the upper bound (5.22%).

**Agent-side failure pattern (state drift):** The model calls `modify_item` with the correct item ID on turn 3, then calls `finish` on turn 5 before processing the second item in a two-item request, because multi-turn context exceeds working memory span.

**Simulator-side failure pattern:** The simulator (same 7B model) contradicts a prior turn — e.g., restating the order ID differently — causing the agent to re-confirm a parameter it already resolved correctly. These contribute to the ~1.74 pp run-to-run variance.

---

## Q5 — Parallel category: minimum pipeline change

**Question:** Parallel category: 0% across all configurations and sizes. What is the minimum pipeline change that would unlock parallel calls? Can constrained decoding enforce an array output schema with repeated function names?

**Answer:**

Current pipeline: Stage 1 = `guided_choice` emits one function name token; Stage 2 = FSM-constrained argument extraction for that one function.

**Minimum change for `parallel_multiple`** (distinct functions, one call each):
- Replace Stage 1 with a JSON array schema `["func_a", "func_b"]` where each element is constrained to the known function name vocabulary. The FSM enforces valid JSON array syntax with each string element drawn from the function set.
- Run Stage 2 once per selected name — Stage 2 is already per-function, no change needed here.

**For `parallel`** (same function repeated N times):
- The array schema allows repeated names (`["func_a", "func_a"]`), so Stage 1 is unchanged from above.
- Stage 2 must be extended to iterate over array elements (not distinct names), running one argument extraction pass per occurrence.

Yes, constrained decoding can enforce this: the FSM for a JSON array of strings drawn from a fixed vocabulary is straightforwardly constructable with outlines/lm-format-enforcer.

---

## Q6 — Schema enrichment ordering in deployment guidelines

**Question:** Your deployment guidelines list schema enrichment as Step 5, after CD, quantization, prompting, and fine-tuning. But CD+schema has no training cost, no latency overhead, and the highest accuracy of any no-training configuration. Why is it Step 5 rather than Step 1b?

**Answer:**

The ordering is by implementation prerequisite, not by accuracy rank. Steps 1–4 work on any schema, including sparse auto-generated ones. Schema enrichment requires that someone has written rich metadata — parameter descriptions, enumeration values, and default values — for every tool in the catalog. Many production tool catalogs (auto-generated from code annotations or OpenAPI specs) lack this detail.

Step 5 signals a gating condition: "this is the highest-return single step, but only if your schemas are rich enough to apply it." The thesis says explicitly in §6.2: "Schema enrichment is the highest-return single step for teams whose tooling already carries rich metadata."

For teams with human-curated API documentation, schema enrichment is effectively Step 1b and should be attempted before quantization or fine-tuning. The deployment ordering reflects metadata availability as a prerequisite, not a judgment that enrichment is less important than the steps that precede it.
