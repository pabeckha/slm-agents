---
theme: ./theme
layout: cover
title: Agents with Small Language Models
info: DTU Master Thesis · Defense
author: Paulo Beckhauser
date: 2026
exportFilename: defense-paulo-beckhauser
---

# Agents with Small Language Models

Optimization Techniques for Reliable Reasoning and Tool Calling

<div class="meta">

**Paulo Beckhauser** · s242779 · Supervisor: Nicki Skafte · DTU Compute

</div>

<!--
20-25 min, roughly one minute per slide.

Opening: "Thank you all for being here. My thesis asks whether a small language model, the kind that runs on a single consumer GPU, can call tools reliably enough to replace an expensive frontier API for most requests. I tested seven optimization techniques across four model sizes to find out. The model size is not a footnote in this talk, it is the axis I will keep returning to."

Keep background short. Spend the time on results and discussion.
-->

---

# Small models are cheap, but they cannot call tools out of the box

**Why frontier models are a problem at scale**
- Expensive per token, external API dependency, no data control

**Why small models are attractive**
- Run locally on consumer hardware at fixed cost, independent of query volume
- This thesis: Qwen 2.5 at **0.5B, 1.5B, 3B, and 7B**

**The deployment context: cascade architecture**
- SLM handles the majority of requests; frontier model escalates only when the SLM cannot
- If the SLM handles 75% of requests → 75% of per-query API cost disappears

**The research question**
- How far can we push the fraction the SLM handles — and how small can that SLM be?

<!--
The only motivation slide, deliberately. The advisor said not to dwell on motivation and background.

Frame the size axis up front: the interesting question for a thesis titled "Small Language Models" is not just "can a 7B do it" but "how small can you go before it breaks." Every results slide answers that for one technique.

Honest scoping to state: I evaluate the SLM tier in isolation. I do not build the router or the escalation logic. BFCL accuracy is my proxy for the fraction of requests the small model could handle.
-->

---

# The failure is not knowledge, it is format, at every size

Qwen 2.5, no optimization. Query: *"What is the sum of 265 and 345?"* Tool: `add(a, b)`.

Expected: `{"name": "add", "arguments": {"a": 265, "b": 345}}`. The model produces:

> *"The sum of 265 and 345 is 610. You can calculate this using the add function with parameters a=265 and b=345."*

Right tool, right arguments, wrapped in prose that does not parse.

| Unoptimized | 0.5B | 1.5B | 3B | 7B |
|-------------|------|------|----|----|
| Accuracy | 3.5% | 4.75% | 2.75% | 1.5% |

**Near-zero at every size.** A 14x difference in parameters does not help. Format non-compliance is not a capacity problem.

**Control: the same 7B with its native tool-calling template, free generation, no optimization, reaches 96.00%.** The gap is integration, not capability. The 1.5% is the floor for a generic, model-agnostic integration.

<!--
This slide motivates everything, and the size row is the point: scaling the model 14x does nothing. The base model fails the same way at 0.5B and 7B. So format compliance is not something you buy with parameters.

The B-template control is essential honesty here and the censor will know it: Qwen ships a native tool-calling template, and prompted that way the model scores 96% with zero optimization. So I am NOT claiming the model is broken. I am measuring what a generic integration achieves without model-specific prompting, and what each technique adds on top of that floor. The value of constrained decoding is the structural guarantee that holds for any model and any schema.

The handful of correct outputs at each size are semantically right and happen to be well-formed by chance. The non-monotonic ordering (3B below 1.5B) is noise at this accuracy floor, not a real trend. Say that if asked.

This sets up the whole thesis split: format failures (size-independent, fixable with constraints) vs semantic failures (size-dependent, addressed by training and by restoring schema detail).
-->

---

# Three research questions

<div class="text-left max-w-4xl">

**RQ1.** What is the performance gap between unoptimized small models (**0.5B to 7B**) and frontier models on tool-calling benchmarks?

**RQ2.** What is the marginal contribution of each optimization technique (constrained decoding, prompt engineering, RAG, quantization, LoRA) when applied cumulatively, **and how does each interact with model size**?

**RQ3.** Can a fully optimized small model reach production-viable accuracy on consumer hardware, **and how small can it be**?

</div>

<div class="mt-8 opacity-70">

The size dimension runs through all three: RQ1 spans the range, RQ2 measures each technique at every size, RQ3 asks where the floor is.

</div>

<!--
The spine of the talk. Everything maps back to one of these.

The size-sweep is Contribution 3 in the thesis and it is woven into all three questions, not isolated. That is why the results section presents each technique across all four sizes.
-->

---

# Method: a cost-ordered ladder, run at every size

**Models.** Qwen 2.5 Instruct at 0.5B, 1.5B, 3B, 7B. **One family, four sizes, so size effects are clean.**

**Benchmarks.**
- BFCL v4 `simple_python`: 400 single-function calls. Format and argument correctness of one call.
- τ-bench retail: 115 multi-turn tasks. End-to-end completion across 5 to 15 turns.

**The ladder.** Techniques ordered by implementation cost. No-training first (constrained decoding, prompting, RAG, quantization), training-based LoRA last. **Every rung is evaluated at all four sizes**: 7 configurations times 4 sizes on BFCL, plus two controls (B-template with the native template, and each technique run without CD).

<!--
Why one family: holding the architecture and training recipe fixed across four sizes is what lets me attribute differences to scale rather than to model design. Single family is also a stated limitation, I will get to it.

Why a ladder: a deployment team adopts these in order of cost. Each rung answers "what do I get if I add the next cheapest thing, at the size I can afford to run."

All BFCL runs use temperature 0. Within one session, repeated runs are identical (six-run check). But re-runs months apart drift by 1 to 2 cases out of 400, about half a percentage point, so I treat any single accuracy figure as carrying that much run-to-run uncertainty. Do NOT claim full determinism if asked; the thesis states the spread explicitly.
-->

---
layout: section
---

# Results

## Seven techniques, four sizes, one question: what does scale change?

<!--
Transition: "I will walk each technique across all four sizes. For every one, the interesting question is the same: does it help the small models, the large ones, all of them, or none?"
-->

---

# Constrained decoding: mask the vocabulary to valid-prefix tokens

<small class="opacity-50">Technique 1 of 7</small>

At every generation step the token logits are masked so only tokens consistent with a valid function call survive. The model never sees an option that breaks the structure.

- **Function name:** only tokens that prefix a known function name are unmasked. The model cannot hallucinate a function that does not exist.
- **Arguments:** the mask is type-specific. Digits for int and float, `true`/`false` for bool, free text for strings.

Building `add(a=265, b=345)`: after `add`, only `(` survives; for an int argument, only digits survive.

**The model never had to know the output format. It only had to pick reasonable values inside a structure we enforce.** Benchmark results use vLLM's guided decoding (logit masks compiled from the schema); a from-scratch decoder was also built for the local prototype.

<!--
Be precise here, because the thesis says the BFCL results are produced via vLLM's guided_choice and guided_json (Willard and Louf's FSM approach). I implemented my own decoder for the local llm_sdk backend, which is real engineering work and fine to mention, but the reported numbers come from the vLLM pipeline. Do not say the results come from a from-scratch decoder.

Five steps if asked: run the model, get logits; set everything to minus infinity; unmask only valid-prefix tokens; argmax over survivors; append and repeat.

The conceptual punchline, repeated next slide: structural errors become impossible, semantic errors remain possible. That is the heart of the thesis, and it is what makes the size story legible: CD removes the size-independent failure (format) and exposes the size-dependent one (values).
-->

---

# Constrained decoding lifts every size, and the gain grows with scale

<small class="opacity-50">Technique 1 of 7</small>

| Size | Base | CD | Gain |
|------|------|-----|------|
| 0.5B | 3.5% | **51.5%** | +48.0 pp |
| 1.5B | 4.75% | **62.25%** | +57.5 pp |
| 3B | 2.75% | **64.75%** | +62.0 pp |
| 7B | 1.5% | **72.75%** | +71.25 pp |

CD shifts the **entire curve up** without changing its shape. The remaining failures are now structurally valid but semantically wrong: format is solved, **argument-value accuracy is what scales**.

**The 0.5B model alone reaches 51.5% with zero training — 27.25 pp below GPT-5-mini (78.75%), but recall that CD is the floor, and fine-tuning adds a further 7.75 pp at 0.5B.** CD becomes the baseline for every later experiment.

<!--
Most important conceptual slide. Two messages.

One: CD reframes the problem. Every remaining failure is semantic. Format compliance is gone. The question changes from "can the model produce valid output" to "can it produce the right values," and that second question is the one that scales with size.

Two, the small-model headline: you do not need 7B. A 0.5B model, which fits in a fraction of a gigabyte, gets to 51.5% with nothing but constrained decoding. That is the genuine "small language model" result and the intro of the thesis leads with it.

Why the gain grows with size: larger models have better latent value priors, so once you remove the format barrier, more of that latent capability shows through.
-->

---

# Quantization: the cost shrinks as the model grows

<small class="opacity-50">Technique 2 of 7</small>

Weights compressed FP16 to INT4 with Activation-aware Weight Quantization (AWQ). The CD mask and prompt are unchanged.

| Size | CD | CD + Quant | Penalty |
|------|-----|-----------|---------|
| 0.5B | 51.5% | 47.75% | −3.75 pp |
| 1.5B | 62.25% | 60.5% | −1.75 pp |
| 3B | 64.75% | 64.5% | −0.25 pp |
| 7B | 72.75% | 72.25% | −0.5 pp |

**Negligible at 3B and above, within run-to-run variance. Meaningful only at 0.5B**, where there is less parameter redundancy to absorb rounding error. At 7B: memory drops 63.5% (14.25 to 5.20 GiB), startup 83.5% (212 to 35 s).

<!--
The size story here is clean: quantization is free where you have parameters to spare and costs a few points where you do not. So the safe operating point is 3B and up.

This makes the RQ3 "consumer hardware" claim concrete: the 7B at INT4 is 5.20 GiB, fits an RTX 4090 with room for the KV cache. Even the 0.5B and 1.5B quantized models run on far weaker hardware.

The tradeoff: at 0.5B you pay 3.75 pp for 4x memory savings, still acceptable if memory is the binding constraint.
-->

---

# Few-shot prompting: helps small models, reverses on the 7B

<small class="opacity-50">Technique 3 of 7</small>

Three solved examples prepended to the prompt before each query.

| Size | CD | CD + few-shot | Δ |
|------|-----|--------------|---|
| 0.5B | 51.5% | 53.5% | **+2.0 pp** |
| 1.5B | 62.25% | 64.75% | **+2.5 pp** |
| 3B | 64.75% | 67.0% | **+2.25 pp** |
| 7B | 72.75% | 70.25% | **−2.5 pp** |

**The direction of effect depends on scale.** At small sizes the examples act as format anchors and help. At 7B they add roughly 300 context tokens that compete for attention, and CD already solved the format the examples were teaching.

**Practical consequence: the best no-training config is size-dependent.** Few-shot at 3B and below, CD alone at 7B.

<!--
This is the cleanest size-interaction result in the thesis, and it is exactly the kind of finding you only see by sweeping sizes. If I had tested 7B alone I would have concluded "few-shot hurts." If I had tested 0.5B alone I would have concluded "few-shot helps." Both are wrong as general statements. The truth is it reverses.

Mechanism: few-shot teaches format and value style. Small models still need that hint. The 7B does not, so the examples are pure context noise.
-->

---

# Chain-of-thought: a constant penalty at every size

<small class="opacity-50">Technique 4 of 7</small>

The model thinks step by step before the call. CD constrains the final call, but the reasoning has already steered the values.

| Size | CD+Q | CD+Q+CoT | Δ |
|------|------|----------|---|
| 0.5B | 47.75% | 42.0% | −5.75 pp |
| 1.5B | 60.5% | 54.75% | −5.75 pp |
| 3B | 64.5% | 58.0% | −6.5 pp |
| 7B | 72.25% | 65.5% | −6.75 pp |

Roughly **−6 pp at every size.** Example flips: `discount_rate=0.1` becomes `10.0` (*"it is a percentage"*), `'gas'` becomes `'gasoline'`, `'01/01/2021'` becomes `'2021-01-01'` (*"ISO format"*).

Reasoning activates world knowledge that overrides the literal value the user wrote. **This is not a capability small models lack and large ones exploit: the mechanism operates at every scale.**

<!--
The size story: unlike few-shot, CoT hurts uniformly. The penalty is flat across the range. So this is not "small models are too weak to reason," it is "explicit reasoning points compute at the wrong subproblem regardless of size."

The flips are intuitive: when the model thinks, it normalizes. It knows discount rates are percentages, dates should be ISO, gas is short for gasoline. So it converts. The benchmark wants the literal query value.

Connects to Wei et al: CoT helps multi-step arithmetic and symbolic decomposition. Argument extraction is value recall, not that kind of reasoning.
-->

---

# RAG: hurts every size, and disambiguation never scales

<small class="opacity-50">Technique 5 of 7</small>

The five most similar function schemas are retrieved and injected alongside the real target schema.

| Size | CD+Q | CD+Q+RAG | Δ |
|------|------|----------|---|
| 0.5B | 47.75% | 26.0% | −21.75 pp |
| 1.5B | 60.5% | 34.75% | −25.75 pp |
| 3B | 64.5% | 48.25% | −16.25 pp |
| 7B | 72.25% | 47.75% | −24.5 pp |

The largest drops of any technique, and **retrieval recall@5 is 97.2%**: the right schema is almost always retrieved. The bottleneck is **disambiguation**, picking the target out of similar-but-wrong neighbours.

**Critically, this does not improve with scale.** The 7B is no better than the 1.5B at distinguishing semantically similar functions.

<!--
The counterintuitive result: retrieval works (97.2% recall), but feeding the model near-miss schemas confuses it. "Similar" and "correct" are nearly identical here, so the distractors are maximally adversarial.

The size message is the important one for the scaling thesis: disambiguation is a capability that does NOT come with parameters. A bigger model does not rescue you. That is why the fix is architectural (re-ranking, or training-time retrieval like Gorilla), not "use a larger model."

66% of RAG failures produce the identical answer as the non-RAG run, so retrieval mostly adds overhead.
-->

---

# LoRA: format alignment between training and inference is everything

<small class="opacity-50">Technique 6 of 7</small>

A LoRA adapter trained on a function-calling corpus. Two variants, same data, same hyperparameters, **differing only in output format**.

| Training label for *"GCD of 12 and 15"* | Format |
|---|---|
| `{"name": "math.gcd", "arguments": {"num1": 12, "num2": 15}}` | misaligned (JSON not used at inference) |
| `math.gcd(num1=12, num2=15)` | aligned (matches what CD emits) |

A model trained on misaligned labels **fights** CD at inference. Aligned labels **reinforce** it. The two adapters differ by **7 pp** on the benchmark, from format alignment alone.

<!--
The finding I am proudest of, because it turned a failure into a confirmed hypothesis.

The first LoRA run regressed 3 pp under CD. Rather than concluding "fine-tuning does not help," I diagnosed it: the xlam training data encodes calls as Python syntax, my pipeline expects a JSON argument object. Format mismatch. I reformatted the labels to match inference exactly and re-ran. That one change moved the result 7 pp.

Generalizes Gorilla: they showed content relevance matters in training data. I show output-format compatibility matters just as much.
-->

---

# Format-aligned LoRA improves every size, most of all the smallest

<small class="opacity-50">Technique 6 of 7</small>

| Size | CD | CD + LoRA (aligned) | Δ |
|------|-----|--------------------|---|
| 0.5B | 51.5% | **59.25%** | **+7.75 pp** |
| 1.5B | 62.25% | 66.0% | +3.75 pp |
| 3B | 64.75% | 66.75% | +2.0 pp |
| 7B | 72.75% | **76.75%** | +4.0 pp |

The only technique that beats CD, **and it beats it at every size.** The gain is largest at 0.5B (+7.75 pp): fine-tuning helps most where base capability is lowest.

LoRA *without* CD reaches only 13.75% at 7B: **constrained decoding remains the dominant contributor even after fine-tuning.**

<small class="opacity-50">Paired McNemar test at 7B: 45 cases corrected vs 27 broken, p = 0.044, borderline against the run-to-run spread. The consistent positive direction across all four sizes is the stronger evidence.</small>

<!--
Two messages. One: this is the only technique that pushes past the CD ceiling, and it does so at all four sizes, which is what makes it a real recommendation rather than a 7B-specific trick.

Two, the small-model angle: the biggest absolute gain is at 0.5B. Fine-tuning is most valuable exactly where you are most parameter-starved. That is good news for tiny deployments.

The 63 pp gap between LoRA-only (13.75%) and CD+LoRA (76.75%) is the cleanest proof that CD does the heavy lifting; fine-tuning refines on top.
-->

---

# Schema enrichment: recover the detail the generic prompt discards

<small class="opacity-50">Technique 7 of 7</small>

The generic CD prompt carries only parameter names and types. Descriptions, defaults, and enumerations are dropped. The model never sees that `fuel_type` accepts `enum: ["gas", "electric", "hybrid"]`, or that `discount_rate` expects a fraction, not a percentage.

**Schema enrichment:** inject parameter descriptions and enum values directly into the guided prompt while keeping the FSM mask in place. The model sees the full value vocabulary; the mask still guarantees structural validity.

Two failure modes addressed simultaneously:
- **Value disambiguation:** enum options eliminate guessing between synonyms.
- **Unit and format hints:** descriptions resolve `0.1` vs `10.0` and `"gas"` vs `"gasoline"`.

The mask and the enriched prompt operate independently: richer context guides value selection; the structural guarantee is unchanged. No training, no architectural change.

<!--
This technique targets the single largest diagnosed failure mode after plain CD: the model lacks the expected value vocabulary. The limitation slide (up next) says the 19 pp residual is largely this information loss. This is the direct fix.

Mechanically it is the simplest technique in the ladder — just a richer prompt — but it requires knowing what the schema detail is and where to put it in the constrained prompt without breaking the FSM.

Key framing for the defense: the thesis identified this gap in the limitations section and then closed it in the same work. That is a clean arc.
-->

---

# Schema-enriched CD: 89.0% at 7B, +16.5 pp, p < 0.00001

<small class="opacity-50">Technique 7 of 7</small>

| Config | Accuracy | vs plain CD |
|--------|----------|-------------|
| CD (7B) | 72.5% | baseline |
| **CD + schema (7B)** | **89.0%** | **+16.5 pp** |

McNemar paired contingency: b = 73 (CD wrong, CD+schema correct), c = 7 (reversed), **p < 0.00001**.

Latency: mean 0.704 s vs CD 0.878 s — schema enrichment costs nothing at inference time.

**Remaining 44 failures are value-strictness artifacts** (`"Los Angeles"` vs `"Los Angeles, CA"`, `1e-05` vs `0.0001`) — not structural or schema errors. The model sees the right vocabulary and uses it; the scorer penalises literal mismatches.

<!--
The strongest single result in the thesis, and the only one that requires no hedging. 73 vs 7 discordant pairs cannot be produced by the ±1–2 case run-to-run variance documented elsewhere. Unlike LoRA (p = 0.044, borderline), this is unambiguous.

The latency note matters: a larger prompt could plausibly slow inference. It does not — the mean is slightly lower than plain CD because the model commits to a correct value faster and terminates earlier.

Residual failure characterisation: 44 remaining failures are scorer strictness, not model capability gaps. The model is close to the ceiling this benchmark allows without value-level disambiguation in the ground truth. The gap to B-template (96%) has narrowed from 23 pp to 7 pp; that 7 pp is largely the scorer, not the model.
-->

---

# The full picture: seven techniques across four sizes

| Config | 0.5B | 1.5B | 3B | 7B |
|--------|------|------|----|----|
| Base | 3.5% | 4.75% | 2.75% | 1.5% |
| Constrained decoding (CD) | 51.5% | 62.25% | 64.75% | 72.75% |
| CD + Quantization | 47.75% | 60.5% | 64.5% | 72.25% |
| CD + Few-shot | 53.5% | 64.75% | 67.0% | 70.25% |
| CD + Chain-of-thought | 42.0% | 54.75% | 58.0% | 65.5% |
| CD + RAG | 26.0% | 34.75% | 48.25% | 47.75% |
| CD + LoRA (aligned) | 59.25% | 66.0% | 66.75% | 76.75% |
| **CD + Schema** | — | — | — | **89.0%** |

CD dominates at every size. Quantization is near-free above 1.5B. Prompting and RAG mostly hurt. Format-aligned LoRA beats CD across sizes. **Schema enrichment adds +16.5 pp at 7B (over the paired CD baseline) with no training cost and no latency overhead.**

<small class="opacity-50">This matrix is the size sweep, so every row above Base includes CD. CD+schema was evaluated at 7B only. Each technique was *also* run alone, without CD, at 7B to isolate its own contribution. Those numbers are on the next slide.</small>

<!--
The synthesis slide. Pause here and let them read the matrix.

The story in one breath: constrained decoding does almost everything at every size; quantization is free where parameters are plentiful; few-shot helps the small and hurts the large; CoT and RAG hurt across the board; only fine-tuning on correctly-formatted examples pushes past CD, and it does so everywhere.

This matrix IS the size-sweep contribution. It is the densest slide; do not read every cell, point at the bold bottom row and the columns.

The matrix shows every technique on top of CD. The next slide shows the complement: each technique run alone without CD, at 7B, which is how I isolated each one's own contribution. Together they answer RQ2 from both directions.
-->

---

# Run alone, without CD, almost nothing works

<small class="opacity-50">Each technique in isolation. Qwen 2.5 7B, BFCL `simple_python`.</small>

| Technique alone (no CD) | Accuracy | vs Base |
|--------------------------|----------|---------|
| Base | 1.5% | baseline |
| Few-shot | 4.5% | +3.0 pp |
| RAG | 2.5% | +1.0 pp |
| LoRA (format-aligned) | 13.25% | +11.75 pp |
| Chain-of-thought | **26.2%** | +24.7 pp |
| **Constrained decoding** | **72.75%** | **+71.25 pp** |

No prompt technique alone clears 27%. **CD alone outweighs every other method combined.** CoT is the best non-CD technique (26.2%): step-by-step reasoning incidentally scaffolds more structured output, but it still trails CD by 46 pp.

<small class="opacity-50">7B isolation study (thesis Section 4.2.5, Tables 4.3 and 4.4).</small>

<!--
This slide is the direct answer to "what is each technique worth on its own," which is the heart of RQ2 and exactly the isolation a censor wants to see.

The story: format compliance dominates so completely that running a method alone barely moves the needle. Few-shot (+3) and RAG (+1) are essentially noise. The one surprise is CoT at 26.2%: thinking step by step before answering accidentally produces more consistently formatted JSON, a self-scaffolding effect. But even that is 46 pp below CD alone.

This reframes the whole ablation: it is not that the other techniques are bad, it is that CD solves the problem that dominates, and once you measure each one alone you see just how much of the accuracy is pure format compliance.

Decomposition I can offer verbally if pushed: adding CD on top of each technique recovers +65.75 pp (few-shot), +45.25 pp (RAG), +39.3 pp (CoT). CD's marginal contribution is smallest on top of CoT, because CoT already supplied partial format scaffolding.

This is in the thesis: Section 4.2.5 (Technique Isolation Without Constrained Decoding), Table 4.3 (isolation accuracies) and Table 4.4 (CD contribution decomposition). The three prompt-level no-CD runs are framed there as supplementary controls, separate from the eleven-config ladder, run to isolate CD's marginal contribution.
-->

---

# Latency: constrained decoding is 8× faster, not slower

<small class="opacity-50">Qwen 2.5 7B · BFCL simple_python · first 100 cases · sequential · single A100-class GPU · vLLM backend</small>

| Config | Mean (s) | Median (s) | p95 (s) | Accuracy |
|--------|----------|------------|---------|----------|
| B (no CD) | 6.995 | 6.929 | 11.922 | 1% |
| CD | 0.878 | 0.847 | 1.375 | 65% |
| CD + Q (AWQ) | 0.661 | 0.623 | 1.006 | 63% |

CD terminates at the closing brace of a valid call. The unconstrained model rambles — explanations, markdown, trailing text — generating far more tokens per call. **The 8× latency win is a consequence of the accuracy fix, not a separate optimisation.**

AWQ stacks a further **~25% reduction** on top of CD (0.661 s vs 0.878 s mean, p95 1.006 s vs 1.375 s).

<!--
Reverses the intuitive assumption: constrained decoding sounds like it could add overhead (maintaining the FSM mask at each step). In practice it is massively faster because it terminates early. The unconstrained model's 6.995 s mean is almost entirely prose generation.

B at 1% accuracy in this run: the "Extra data" JSON parse failures already documented elsewhere — the model emits a valid call and then keeps generating. CD stops it.

The 65% vs 72.75% gap between this 100-case latency run and the full 400-case CD result: the first 100 cases skew math-heavy and enum-heavy; the accuracy floor is lower there.

The practical payoff: the deployment narrative is not "CD trades latency for accuracy." It is "CD gives you both — accuracy goes up, latency goes down, and memory is cut by quantization."
-->

---

# Where each size lands against the frontier

| Model | Accuracy |
|-------|----------|
| Claude Sonnet 4.5 | 97.75% |
| **Qwen 2.5 7B B-template (control)** | **96.00%** |
| Gemini 3 Pro | 94.75% |
| GPT-4.1 | 91.00% |
| **Qwen 2.5 7B + CD + Schema** | **89.0%** |
| GPT-5-mini | 78.75% |
| **Qwen 2.5 7B + CD + LoRA** | **76.75%** |
| **Qwen 2.5 7B + CD** | **72.75%** |
| **Qwen 2.5 3B + CD** | **64.75%** |
| **Qwen 2.5 1.5B + CD** | **62.25%** |
| **Qwen 2.5 0.5B + CD** | **51.5%** |

With schema enrichment the 7B reaches **89.0%, 10.25 pp above GPT-5-mini and 2 pp below GPT-4.1**. Without training, CD+LoRA (76.75%) is just below GPT-5-mini. The **B-template control (96.00%) sits inside the flagship band**, showing the gap is integration quality, not model capability.

<small>BFCL v4 leaderboard, Python Simple AST category (same 400 test cases as this evaluation), snapshot 2026-06-04. Cross-harness comparisons are indicative only: B-template (96.00%) locally matches the flagship frontier band, confirming the category is commensurable. **Answers RQ1 and RQ3.**</small>

<!--
This is the answer to RQ1 and RQ3, and the size axis makes it far more interesting than a single 7B number. I am placing every SLM size in the frontier ranking, so the audience sees the whole spectrum: 0.5B far below frontier, 7B with CD+schema entering the frontier range above GPT-5-mini and just below GPT-4.1.

Honest framing: frontier models use native function-calling APIs that enforce structure the same way CD does, so the fair comparison is at the CD level. The raw 78 pp unoptimized gap at 7B collapses to about 6 pp with CD, to near-parity with GPT-5-mini after LoRA, and to above GPT-5-mini with CD+schema.

The comparability caveat is load-bearing now: my own B-template control scores 96.00% locally, inside the flagship band (Gemini 3 Pro 94.75%, Claude Sonnet 4.5 97.75%). That confirms the local evaluation and leaderboard are commensurable on this category. I present these as indicative placement; the internally valid comparisons are between my own configurations under one harness.

Threats to validity if pressed: frontier scores are from the public leaderboard, not re-run under my harness, so I claim indicative placement, not a definitive ranking.
-->

---

# Beyond simple calls: fine-tuning helps small sizes, saturates at 7B

<small class="opacity-50">BFCL `multiple` category: choose one function from several, then call it</small>

| Size | CD | CD + LoRA (aligned) | Δ |
|------|-----|--------------------|---|
| 0.5B | 42.0% | 55.5% | +13.5 pp |
| 1.5B | 53.5% | 61.0% | +7.5 pp |
| 3B | 62.0% | 60.5% | −1.5 pp |
| 7B | 70.5% | 70.5% | 0.0 pp |

The pattern mirrors `simple_python`: fine-tuning helps most where capacity is lowest, then **vanishes at 7B where CD alone already saturates the category**.

But `parallel` (two simultaneous calls to the same function) yields **0% at every size**: the pipeline emits at most one call per distinct function, so same-function parallel calls are structurally impossible. An architectural ceiling, not a tuning gap.

<!--
Extends the size story to a harder category. Same shape: fine-tuning is a small-model booster, the 7B with CD alone already maxes it out.

Be precise on the parallel mechanism, because parallel_multiple DOES produce multi-call responses (up to 4 calls, 38.5% at 7B). The pipeline selects a set of distinct function names and runs one deterministic argument extraction per name. Distinct functions: multiple calls possible. Same function twice: impossible, because the second extraction would produce the identical argument object. So 0% on parallel is by design at every size; no scale or training fixes it. Future work.
-->

---

# The central finding: single-call accuracy collapses on real agentic tasks, at every size

BFCL measures one call. τ-bench measures a whole task: 5 to 15 turns, passing only if the final database state exactly matches ground truth.

| Size | BFCL simple (CD) | τ-bench retail (CD) |
|------|------------------|---------------------|
| 0.5B | 51.5% | 3.48% |
| 1.5B | 62.25% | 1.74% |
| 3B | 64.75% | 4.35% |
| 7B | 72.75% | 4.35% |

A **68 pp gap at 7B**, and **no scale trend** in the agentic column: every size sits on the same floor (1.74% to 4.35%). The failure is not formatting (CD handles that) but multi-turn planning and error recovery.

**This quantifies exactly where the cascade boundary sits.**

<small class="opacity-50">The user simulator is also Qwen 7B; the reference setup uses a frontier simulator, so these pass rates are conservative and not comparable to published numbers.</small>

<!--
The most important honest result in the thesis. Do not bury it.

State the simulator confound before anyone asks: the user simulator is the same 7B model, where the reference tau-bench setup uses a frontier model. A weak simulator deflates pass rates independently of agent capability, so the absolute floor is conservative and comparisons to published frontier pass rates are not like-for-like. Quantitative bound: three independent runs at identical agent settings (temp 0.0, seed 42) produced 3.48%, 4.35%, and 5.22%. Because the agent is deterministic, the 1.74 pp spread is attributable entirely to stochastic simulator turns, bounding the observed simulator-noise contribution at ±0.87 pp. The qualitative finding (single-call gains do not transfer to multi-turn) survives: even at the 5.22% upper bound the gap to 72.75% BFCL CD exceeds 67 pp. It would be easy to stop at "small models match frontier on single calls" and tell a triumphant story. The truth is more interesting: parity on single calls, collapse on multi-step agency.

The size column is the key addition here: the agentic floor is flat across 0.5B to 7B. So this is a capability boundary, not a tuning or scale problem within the small range. It is the single best argument for the cascade: the SLM handles the simple bulk, the frontier model handles genuine multi-step agency.

This is the slide an examiner will probe. Lean into it.
-->

---
layout: section
---

# Discussion & Conclusions

<!--
Transition: "So what does a deployment team do with this, and what does it mean for how small you can go?"
-->

---

# A cost-ordered decision ladder, and the right size for each step

1. **Benchmark the native template first, then apply constrained decoding.** A model that ships a tool-calling template gives 96% for free, but with no validity guarantee and tied to that model. CD adds the structural guarantee for any model and any schema; the 0.5B alone reaches 51.5% with it.
2. **Quantize above 1.5B for free efficiency.** 63.5% less memory, 83.5% faster startup, under 0.5 pp cost at 3B and 7B. At 0.5B the cost is 3.75 pp, a real tradeoff.
3. **Match prompting to size, or skip it.** Few-shot helps at 3B and below, hurts at 7B. Chain-of-thought and RAG hurt everywhere. After CD the residual failures are semantic.
4. **Fine-tune for the ceiling, especially when small.** Format-aligned LoRA is the only technique above CD, and its gain is largest at 0.5B. The binding constraint is format alignment between training and inference.

**Cascade economics:** an SLM handling fraction *p* saves *p · c* per query. CD+Q gives p≈0.72, CD+LoRA gives p≈0.77, all on one GPU.

<!--
The practical payoff of RQ2 and RQ3. The new twist versus a 7B-only talk: the recommendation is size-aware. The cheapest viable size depends on your accuracy target, and the best technique stack changes with size (quantize freely at 7B but not 0.5B; few-shot only below 7B).

On cascade economics: p values are upper bounds. After CD every output is valid JSON naming a real function, so I have lost the structural signal a router would use to escalate. Reaching p near the measured accuracy needs a semantic router, which I did not build. State this plainly.
-->

---

# Limitations, stated honestly

- **Schema detail gap: addressed.** The generic CD prompt withheld descriptions, defaults, and enumerations. CD+schema injects them and recovers 89.0% at 7B, narrowing the gap to B-template from 23 pp to 7 pp. The remaining 7 pp is largely value-strictness scorer artifacts, not model failures.
- **One benchmark category.** Primary results are BFCL `simple_python`: single turn, single candidate, one call. The CD advantage depends on the correct function being the only candidate.
- **Partial generalization.** CD+LoRA reaches 70.5% on `multiple` at 7B, but **0% on `parallel` at every size**: at most one call per distinct function, an architectural ceiling.
- **One model family.** All results use Qwen 2.5. The size-dependent findings are consistent within it but may not transfer to Llama or Phi, which have different training regimes.
- **Cascade not built; simulator confound.** Router and escalation are future work; *p* values are accuracy-based estimates. The τ-bench simulator is also a 7B model, so agentic pass rates are conservative.
- **Benchmark conventions.** `"gas"` vs `"gasoline"` scores wrong though both are valid. The 27% residual may overstate real-world error.

<!--
Showing I know exactly where the work stops is worth as much as the results.

The single-family caveat is sharper now because the whole talk leans on size effects. I should be explicit: the SHAPES I report (CD gain grows with size, few-shot reverses, quantization penalty shrinks, fine-tuning helps small most) are observed within Qwen 2.5. Whether they hold for other families is genuinely open. I do not overclaim.

The parallel 0% is the cleanest limitation: structurally impossible in this architecture, 0% by design at every size.
-->

---

# Conclusion

**RQ1.** The unoptimized gap is enormous (1.5 to 4.75% vs ~79%) but it measures the **generic integration, not the model**: the native-template control reaches 96%. The gap is almost entirely **format**, and **flat across size**. CD closes it at every scale with structural guarantees.

**RQ2.** CD dominates (+48 to +71 pp, growing with size). Quantization is near-free above 1.5B. Few-shot reverses with scale; CoT and RAG hurt at every size; format-aligned LoRA beats CD across all sizes; **schema enrichment adds +16.5 pp at 7B over the paired CD baseline (p < 0.00001) with no training and no latency cost.**

**RQ3.** Yes. The 7B with CD+schema reaches **89.0%, 10.25 pp above GPT-5-mini and 2 pp below GPT-4.1**. Without training, CD+LoRA (76.75%) is just below GPT-5-mini (78.75%). Schema enrichment enters the frontier range without modifying model weights.

<div class="mt-6 font-semibold">

The thread: constrained decoding converts tool calling from a **format** problem (size-independent, guaranteed at inference) into a **semantic** problem, whose residual is schema detail the generic prompt withholds — and restoring that detail with schema enrichment closes most of the remaining gap.

</div>

<!--
The one sentence I want the room to keep is the bold line: CD turns a size-independent format problem into a size-dependent semantic problem. That single reframing explains every result in the talk, including why some techniques scale and others do not.

Then the practical headline: across the whole small range, constrained decoding plus optional fine-tuning makes these models competitive on single-call tool use, but real multi-step agency stays out of reach, which is exactly why the cascade makes sense.
-->

---

# Future work

- **Multi-step reliability is the main open problem.** The τ-bench floor (under 5% at every size) is about planning and error recovery, not formatting. Process reward models, observation-grounded reasoning, and fine-tuning on multi-turn trajectories are the next steps.
- **Other model families.** Confirm whether the size-dependent patterns hold beyond Qwen 2.5 (Llama 3.2, Phi-4).
- **Domain-matched training data.** Generate LoRA examples from the deployment's own tool schemas to remove the format-mismatch confound.
- **A real cascade router.** Semantic confidence scoring to decide when to escalate, since structural signals vanish after CD.
- **Parallel call emission.** Extend the architecture to a JSON array of calls or a multi-step loop, unlocking the `parallel` categories.

<!--
Each item maps to a specific limitation, which shows the future work is grounded, not generic.

The one I would do next: the semantic router, because it turns measured accuracy into actual cascade savings and is a tractable extension. A close second is repeating the sweep on a second model family to test whether the size patterns generalize, since that is the biggest threat to the scaling claims.
-->

---
layout: statement
---

# Thank you

<div class="opacity-70 text-xl mt-4">

Questions and discussion

</div>

<!--
Hand over for questions. Stay relaxed: this is a discussion, not a test. I know this project better than anyone in the room.

Likely questions:
- "Your own control scores 96% with no optimization at all. Why does your pipeline exist?" The research question is about which techniques contribute what, measured from a model-agnostic floor. The native template gives no validity guarantee and ties you to one model family. The gap between the generic pipeline and the native template turned out to be largely schema information loss — and schema enrichment closes most of it (89.0% vs 96.00%). That diagnosis and fix is itself a contribution.
- "Your best result is 89%. Why is there still a 7 pp gap to your own 96% control?" The remaining failures are predominantly scorer-strictness artifacts: `"Los Angeles"` vs `"Los Angeles, CA"`, `1e-05` vs `0.0001`. The model selects the right value vocabulary; the benchmark penalises literal mismatches. True capability is close to the template ceiling.
- "Why only Qwen 2.5?" Compute budget and clean size comparison; stated as a limitation; four sizes in one family is what makes the scaling analysis valid.
- "Why present all four sizes?" Because the thesis is about small models and the size interactions ARE findings: few-shot reverses, quantization penalty shrinks, fine-tuning helps small most, disambiguation never scales. A single size would hide all of that.
- "Isn't CD just doing what the benchmark wants?" CD enforces structure exactly like frontier function-calling APIs, so the comparison is fair at the CD level. It does not touch values.
- "Is the LoRA gain statistically significant?" McNemar on the paired predictions gives p = 0.044 at 7B, borderline against the run-to-run spread; the quantized-stack gain is not significant (p = 0.38). The stronger evidence is the consistent positive direction at all four sizes. I report it exactly that way. The CD+schema gain is unambiguous: p < 0.00001, 73 vs 7 discordant pairs.
- "Why is tau-bench so low at every size, did something break?" No. The bottleneck is multi-turn planning, which none of my single-call techniques target, and it does not improve across the small range. The simulator is also a 7B model, so the absolute floor is conservative. Quantitative bound: three deterministic-agent runs gave 3.48%–5.22%; the 1.74 pp spread is pure simulator noise (±0.87 pp). The qualitative finding stands even at the 5.22% upper bound — the BFCL-to-τ-bench gap exceeds 67 pp.
- "How small can you really go?" 0.5B with CD reaches 51.5% on single calls — 27.25 pp below GPT-5-mini (78.75%), but +7.75 pp with format-aligned LoRA (59.25%). For multi-step agency, no size in this range is sufficient, which is what the cascade is for.
- "Does constrained decoding add latency?" The opposite: CD is 8× faster than unconstrained (0.878 s vs 6.995 s mean) because it terminates at the closing brace instead of generating prose. AWQ adds a further 25% reduction to 0.661 s.
-->
