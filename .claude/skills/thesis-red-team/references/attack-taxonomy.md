# Attack Taxonomy

Run each category against every central claim. For each, the **question** is what
a hostile examiner asks; the **tells** are signs the thesis is vulnerable. Find
the strongest 1–3 attacks per claim, then rank globally by damage.

## 1. Baseline fairness
**Question:** Is the comparison rigged in the proposed method's favour?
**Tells:** baseline and method evaluated under different parsers, prompts,
decoding settings, or post-processing; a "naive" baseline no serious user would
run; headline improvement (e.g. "6%→96%") that shrinks under a like-for-like
condition; best-of-N for the method vs single-shot for the baseline; baseline
hyperparameters left untuned while the method's are swept.
**Attack form:** "Under your own same-parser / same-condition setting the gap is
X, not the headline Y — the headline measures the parser, not the method."

## 2. Confounds & uncontrolled variables
**Question:** Does the claimed cause actually explain the effect?
**Tells:** the intervention changes more than one thing at once (decoding +
fine-tuning + prompt); improvements that track model size, data volume, or
compute rather than the named technique; no ablation isolating the mechanism.
**Attack form:** "Your gain is confounded with <X>; you have not shown the
technique, rather than <X>, caused it."

## 3. Generalization / external validity
**Question:** Does the conclusion hold beyond what was tested?
**Tells:** claims about "SLMs" from one model family; one benchmark, one domain,
one tool schema; train/test from the same distribution; cherry-picked model
sizes; cross-family results quietly excluded from a "general" claim.
**Attack form:** "You tested <narrow set> and concluded <broad claim>. On a
second family/benchmark the result could reverse — and you have a documented case
where conditions flip the outcome."

## 4. Statistical rigor
**Question:** Are the differences real or noise?
**Tells:** no variance, no seeds, single run; no confidence intervals or
significance test; tiny eval set; "improves" on differences within run-to-run
noise; multiple comparisons without correction; mean reported where the
distribution is bimodal.
**Attack form:** "With n=<small> and no CI, the <X-point> difference is within
noise; you have not shown it is significant."

## 5. Cherry-picking & selective reporting
**Question:** What was left out?
**Tells:** numbers in the thesis that don't match the run files; a metric that
appears in one table and silently changes definition in another; the best
checkpoint/seed reported as if typical; failure cases relegated to a footnote or
omitted; aggregate scores that disagree with the underlying per-run data.
**Attack form:** "Run file <path> shows <N>, the thesis cites <M>; the favourable
number is not the one in your data."

## 6. Construct validity (are you measuring what you claim?)
**Question:** Does the metric capture the real goal?
**Tells:** "tool-calling reliability" reduced to exact-string match; accuracy that
rewards format compliance over correct behaviour; a benchmark whose pass criterion
the method optimizes directly (teaching to the test); success defined so the
method cannot fail.
**Attack form:** "Your metric measures <format/proxy>, not <the capability you
claim>; a model could score high while failing the real task."

## 7. Circularity & scaffold dependence
**Question:** Does the result depend on the very thing being evaluated?
**Tells:** a method that only works with its own scaffold and collapses without it
(e.g. fine-tuned models that drop to ~0% without guided decoding); evaluation that
assumes the conclusion; "guided" numbers presented as the model's intrinsic
ability.
**Attack form:** "Remove the scaffold and the capability vanishes — you have
measured the scaffold, not the model; the intrinsic claim is unsupported."

## 8. Alternative explanations
**Question:** What simpler story explains the data?
**Tells:** no consideration of a rival hypothesis; effect attributable to prompt
formatting, memorization/contamination, or a quirk of one model; "because of our
technique" where "because of more tokens / a better prompt" also fits.
**Attack form:** "<Simpler cause> predicts the same result; you have not ruled it
out, so the technique is not the established explanation."

## 9. Reproducibility & evidence trail
**Question:** Could anyone reproduce this, and does the evidence exist?
**Tells:** undocumented hyperparameters, versions, seeds, prompts; results that
can't be traced to a committed run; "data available on request"; numbers with no
provenance.
**Attack form:** "Claim <X> has no reproducible trail; an examiner cannot verify
it and neither can you."

## 10. Scope vs claim (the framing attack)
**Question:** Does the thesis deliver what its title/abstract/RQ promise?
**Tells:** abstract claims more than results show; research question asks one
thing, evaluation answers a narrower thing; "enables SLMs to reliably call tools"
where results show reliability only under specific, fragile conditions;
contribution restated as bigger in the conclusion than in the results.
**Attack form:** "Your RQ asks <A>; your evidence answers <a⊂A>; the gap between
them is the part you have not earned."

## 11. Related work & novelty
**Question:** Is the contribution actually new, and fairly positioned?
**Tells:** a known prior method not cited or mischaracterized as weaker than it is;
"first to" claims that a quick search defeats; the delta over prior work too thin
to carry a thesis.
**Attack form:** "<Prior work> already does <X>; your contribution over it is
<thin/unstated>."

## How to weaponize the project's own record

The richest attacks come from comparing the thesis's clean narrative against the
messier reality in `docs/decisions/` and the raw `runs/` / `scores/` files. A
documented caveat the author chose not to surface in the thesis is the strongest
possible attack: it is grounded, it is in their own words, and it cannot be waved
away. Always diff the headline against the evidence trail before finalizing.
