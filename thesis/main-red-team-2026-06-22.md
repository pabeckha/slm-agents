# Red-Team Report — Agents with Small Language Models

**Reviewed:** 2026-06-22 · **Stance:** adversarial (deliberately one-sided)

**Central claims under attack:**
1. Constrained decoding (CD) recovers **48–71 pp** of BFCL accuracy across 0.5B–7B, lifting a near-zero baseline (1.5–4.75%) to 51.5–72.75% — the foundational contribution (Contribution #1, abstract, RQ1, RQ2, conclusion).
2. Schema-enriched CD (CD+schema, 89.0%) is the strongest no-training result and **enters the lower frontier range** (10.25 pp above GPT-5-mini) on BFCL v4 Python Simple AST.
3. Prompt-level and retrieval additions (PE, CoT, RAG) **reduce** accuracy; RAG by 24.5 pp.
4. An optimized SLM is **cascade-viable** for single-call tool calling (RQ3 = "yes", p ≥ 0.70 on a consumer GPU).

## Headline: where this thesis is most likely to break

The thesis is unusually well-hedged — most obvious attacks are pre-empted in Threats to Validity. The damage is therefore not in the conceded limitations but in the **gap between the concessions and the headline framing**. One attack is Critical: the thesis's most-repeated number — CD recovers ~71 pp from a 1.5% baseline — is a **parser artifact**. By the author's own correction record, the same 7B run scores **62.00%** under the lenient parser used to score every other configuration, so CD's same-parser marginal contribution at 7B is **+10.75 pp, not +71.25 pp**. The 71 pp framing nonetheless leads the abstract, Contribution #1, RQ1, and the conclusion, while the +10.75 pp number appears only in one isolation subsection. Two further Majors (the RAG "−24.5 pp" confound and the RQ3 "yes") follow the same pattern: a careful concession in the body that does not propagate to the abstract/contributions. All three are survivable with reframing, not with new data.

## Attacks (ranked)

### ATTACK 1 — The headline "+48–71 pp from CD" is a cross-parser artifact [Critical]

- **Claim attacked:** "constrained decoding alone recovers 48–71 pp … lifting the near-zero model-agnostic baseline (1.5–4.75%) to 51.50–72.75%" (Contribution #1, `chapters/01_introduction.tex`); abstract "1.5% … 77–96 pp below frontier models"; RQ1/RQ2 in `chapters/06_conclusion.tex`.
- **Why it breaks:** The 1.5% Base and the 72.75% CD are **not scored on a level field**. `docs/decisions/no-guided-thesis-corrections-2026-06-18.md` states it plainly: "Config B's headline **1.50%** and the corrected no-guided **62.00%** are the same 7B runs under a strict vs. a lenient JSON parser." The 1.5% comes from a whole-completion parse that discards a valid leading JSON object the moment any trailing text follows it; the lenient `raw_decode` parser (PR #163) — used to score the no-guided isolation arm and the FT no-CD cells — recovers the same outputs. CD's output is FSM-guaranteed single-object, so its score is parser-invariant. Hold the parser fixed and CD's marginal contribution at 7B is **62.00% → 72.75% = +10.75 pp** (the doc's own `tab:cd-contribution` correction: "+71.25 → **+10.75**"). The headline inflates the contribution roughly **7×** by scoring the baseline more strictly than the treatment.
- **Scope precisely (don't overstate):** The same-parser check exists **only at 7B**. The correction doc deliberately kept the size-sweep B row at strict near-zero values (3.50/4.75/2.75/1.50) and reports the no-guided variants at 7B only. So the cross-size "+48–71 pp" range in Contribution #1 has been honestly checked against the same parser at **exactly one size**, where it collapses to +10.75 pp. The 0.5B/1.5B/3B legs of the range are strict-parser throughout.
- **What would refute this attack:** Same-parser no-guided Base numbers at 0.5B/1.5B/3B showing the gap stays near 48–71 pp; or an argument that the strict parser is the only defensible scoring of a "model-agnostic integration." Neither exists in the record — the project chose the lenient parser as correct everywhere it was applied.
- **Best available defense (the author's strongest, and it is real):** CD's value is the **structural guarantee**, not the accuracy jump. CD takes parseable-output rate from ~62% to **100%** and eliminates the residual ~38% unparseable tail with guarantees that hold for any model and schema; the lenient parser is a post-hoc rescue that a production router cannot rely on. This defends *CD as a technique* — it does **not** defend the *number*. The attack is not "CD doesn't work"; it is "the magnitude in the abstract, Contribution #1, RQ1, and the 77–96 pp frontier gap is a parser artifact."
- **Fix:** Lead with **both** numbers wherever the contribution is stated: strict floor 1.5% (naive integration) **and** same-parser 62.00% (7B), with CD's true same-parser delta +10.75 pp at 7B. Recast Contribution #1 around the **structural guarantee and the eliminated unparseable tail**, not the pp figure. Either re-ground the size sweep under the lenient parser or restrict the "+48–71 pp" range claim to "strict-parser floor; same-parser delta verified only at 7B (+10.75 pp)."

### ATTACK 2 — "RAG reduces accuracy by 24.5 pp" measures oracle removal, not RAG [Major]

- **Claim attacked:** abstract "retrieval-augmented generation reduce accuracy by … 24.5 percentage points relative to the constrained-decoding configuration each extends"; Contribution-level framing of RAG as a clean ablation step.
- **Why it breaks:** `docs/decisions/config-cdqrag-results.md` shows RAG is the **only** configuration that changes the task: every other config is given **1 oracle candidate** function; CD+Q+RAG retrieves **5 candidates** the model must disambiguate. The −24.5 pp (72.0% → 47.8%) therefore measures the cost of **removing the oracle and adding a 5-way selection problem**, not the marginal cost of "adding RAG" to a fixed task. The doc concedes it: "With oracle selection (1 candidate), this problem doesn't exist." Presenting it in the abstract alongside CD/quantization/CoT — all same-task deltas — implies a like-for-like ablation step that it is not.
- **What would refute this attack:** A RAG arm that keeps the oracle single candidate and still drops 24.5 pp (would isolate retrieval overhead from selection difficulty); the record has no such arm.
- **Best available defense:** Open-catalog top-5 selection is the *realistic* tool-calling setting, so the comparison reflects a real deployment cost. Legitimate — but that makes it a **task-difficulty finding** ("SLMs cannot disambiguate semantically similar candidates"), not the marginal effect of a retrieval module, and the abstract should say so.
- **Fix:** Reword to "open-catalog retrieval (5 candidates vs. 1 oracle) drops accuracy 24.5 pp, attributable to candidate disambiguation, not retrieval (recall@5 = 97.2%)." Remove RAG from any sentence that lists it as an additive ablation step on a fixed task. The discussion already does this carefully; align the abstract to it.

### ATTACK 3 — RQ3 "cascade-viable: yes" is met only on criteria that omit the cascade [Major]

- **Claim attacked:** "Under the scope defined … the answer is yes for single-call, schema-constrained tool calling" (RQ3, `chapters/06_conclusion.tex`).
- **Why it breaks:** RQ3's two viability criteria (frontier-parity accuracy + fits a 24 GiB GPU) describe the **SLM in isolation**, not a working cascade. The cascade needs to know *which* outputs to escalate — and the thesis concedes that CD **destroys the only free signal** for this: "after constrained decoding, structural routing signals are unavailable because every output is valid JSON naming a known function. The reported p values are … upper bounds" assuming "an ideal semantic router … not evaluated in this thesis." So the intervention that makes the SLM accurate also removes the cheap way to detect its 27% wrong answers, and the component that would realize p ≥ 0.70 is unbuilt. Answering "yes" lets the abstract's framing ("cascade economics") rest on an unimplemented and arguably harder-after-CD router.
- **What would refute this attack:** A measured router (even a weak token-confidence baseline) showing escalation can recover most of the 27% without escalating most of the 73% correct; not present.
- **Best available defense:** RQ3 is *explicitly* scoped to the two stated criteria, and the cascade router is openly deferred. Defensible on the author's own terms — which is exactly why the attack must be framed as **scope-vs-claim**: meeting "frontier-parity accuracy + fits a GPU" is not what a reader hears in "cascade-viable," and CD makes the routing problem worse, not solved.
- **Fix:** Answer RQ3 as "yes on the two stated criteria; cascade viability proper is not established and is complicated by CD's removal of structural routing signals." Move the p-values' upper-bound caveat out of the body and into the RQ3 answer and the abstract.

### ATTACK 4 — "89% enters the frontier range above GPT-5-mini" is leaderboard-vs-local [Minor / largely conceded]

- **Claim attacked:** CD+schema "places the 7B model inside the frontier range … above GPT-5-mini" (abstract, Contribution #2).
- **Why it breaks:** The frontier scores are taken from the public BFCL leaderboard, not re-run under the local harness, so "10.25 pp above GPT-5-mini" compares a local two-stage pipeline against externally-reported numbers under possibly different prompt/tool-call handling. The 89% itself is also a single run (CD pair = 290/400 in `schema-rich-full-run-results.md`, 291/400 = 72.75% in the thesis — the documented 289–291 noise band).
- **Why it is only Minor:** The author concedes this directly ("indicative because frontier scores are taken from the public leaderboard rather than re-run"), and the +16.25 pp CD→CD+schema delta itself is McNemar p < 0.00001 (73 vs 7 discordant) — robust to run noise. The "teaching-to-the-test" angle (schema enrichment injects enums/defaults) does **not** land: the schema-rich doc shows the residual 44 failures are benchmark value-strictness (`1e-05` vs `0.0001`), not the model being handed answers.
- **Fix:** Downgrade "above GPT-5-mini" to "within the lower frontier band (indicative; leaderboard scores, not re-run locally)" wherever it appears as a ranking rather than a band.

## Attacks the author already defused (do not re-litigate — they are covered)

These are genuinely conceded in Threats to Validity; an examiner who raises them will be answered. Listing them so the report is not mistaken for inflating conceded limitations into findings:

- **τ-bench user simulator** — the simulator is the 7B agent itself, deflating pass rate vs. frontier-simulator setups; bounded at ±0.87 pp over 3 runs; conclusion (single-call gains don't transfer) holds at the upper bound.
- **Single-run, temperature-0 protocol (±0.5 pp)** — conceded; sub-pp orderings (0.5 pp quant penalty, 2.5 pp PE) explicitly flagged as within noise; the load-bearing deltas (CD+schema +16.25 pp, CD structural gain) are robust to it.
- **BFCL convention mismatch** — "gas" vs "gasoline", `1e-05` vs `0.0001` scored wrong; conceded to inflate the 27% residual.
- **Few-shot example design bias** — PE examples authored from test-split errors; conceded as biasing *toward* PE, which still fails (conservative).
- **Single model family** — most directional findings are Qwen-2.5-only; conceded, with CD and FT-aligned cross-family checks as partial external support. (Residual attack: the abstract states size-dependent findings — e.g. "few-shot reverses direction at 7B" — without the family caveat inline; tighten if an examiner presses generality.)

## Bottom line for the defense

Three questions are likely and only the first is dangerous:
1. **"Your 71 pp CD headline — is it 71 or 10.75?"** Dangerous. Pre-empt it: lead with both numbers and recast CD as a guarantee (Attack 1). Do not let the examiner be the one to find the correction doc.
2. **"Did RAG hurt, or did you just take away the oracle?"** Survivable by conceding it's an open-catalog difficulty result (Attack 2).
3. **"Is it cascade-viable if the router isn't built and CD removed the routing signal?"** Survivable by holding to the two stated criteria and conceding the rest (Attack 3).
