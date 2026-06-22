# Evaluation rubric

A checklist of what to probe per dimension. You won't find every item in every
thesis — use it as a prompt for "did I check this?", not a form to fill. The goal
is to catch the things a hurried reader misses. For each item, the useful output
is a page-cited observation, not a checkmark.

## Methodology & rigor

- **Question–method fit.** Do the chosen methods actually answer the stated
  research questions? A qualitative interview study can't establish a causal
  effect; a benchmark on one dataset can't establish generality.
- **Claims vs. evidence.** Go through the conclusion's claims one by one. For
  each, find the evidence in the body. Flag any claim that outruns its evidence —
  this is the single most common serious thesis flaw.
- **Sample & data.** Sample size and how it was obtained. Selection bias.
  Representativeness. For ML: train/test/val split, leakage, baseline fairness.
- **Confounds & controls.** What else could explain the results? Are alternative
  explanations considered and ruled out?
- **Reproducibility.** Could someone repeat this? Are parameters, prompts, code,
  data, and procedures described well enough? Is code/data shared?
- **Limitations.** Does the author acknowledge the real limitations, or only safe
  ones? Note limitations they *should* have flagged but didn't — that gap is itself
  a finding.
- **Ethics / data handling** where relevant (human subjects, personal data, GDPR).

## Mathematical & technical correctness

- **Formulas & derivations.** Re-derive key steps where feasible. Check units,
  edge cases, and that defined symbols are used consistently.
- **Proofs.** Are stated theorems actually proved? Any gaps, circularities, or
  unjustified "it follows that"? Are assumptions stated?
- **Algorithms & complexity.** Does the pseudocode match the description? Are
  time/space complexity claims correct? Any off-by-one or termination issues?
- **Statistics.** Right test for the data? Assumptions met (normality,
  independence)? Is "significant" backed by an actual test and a sane n? Multiple
  comparisons corrected? Effect sizes, not just p-values? Confidence intervals?
- **Notation hygiene.** Symbols defined before use, consistent throughout, no
  collisions.
- **System / architecture.** Does the described design actually do what's
  claimed? Failure modes, scalability, security where relevant.
- When you can't verify a step (e.g. a cited lemma, a number from a proprietary
  run), say so explicitly and route it to the "verification notes" section.

## Contribution & novelty

- **What's actually new.** State the contribution in one sentence. Is it a new
  method, a new result, a new artefact, a new dataset, or a new synthesis? Or is
  it an application of known methods (which can still be a fine Master's thesis —
  judge against level)?
- **Related-work coverage.** Are the obvious prior works and competing approaches
  present? Anything important missing? Are citations recent enough for a
  fast-moving field?
- **Fair representation.** Are prior/competing approaches described accurately and
  fairly, or strawmanned?
- **Significance.** Would this matter to someone in the field? Is the "so what"
  articulated, or left implicit?
- **Positioning.** Is the contribution clearly delineated from prior work, or
  blurred so you can't tell what the author did vs. what they reused?

## Business & practical relevance

For applied, entrepreneurial, or design-science theses (common in
business-school and CS+Business contexts):

- **Problem validation.** Is there real evidence the problem exists and matters
  to real customers, or just assertion?
- **Market sizing.** TAM/SAM/SOM — are the numbers sourced and the method shown,
  or pulled from the air? Top-down vs. bottom-up; do they reconcile?
- **Unit economics.** Are cost and revenue assumptions realistic? Does the margin
  math actually work? Are key cost drivers (e.g. per-API-call, per-message LLM
  cost) accounted for?
- **Willingness to pay.** How was WTP elicited? Stated-preference surveys are
  weak evidence; what's the basis? Sample and bias.
- **Competition & alternatives.** Are real competitors and the "do nothing"
  alternative considered honestly?
- **Validated vs. speculative.** Is the thesis honest about what's been tested in
  the market vs. what's a hopeful projection? Conflating the two is a major issue.
- **Practical feasibility.** Could this actually be built/operated/sold given the
  constraints described?

## Cross-cutting quality

- **Structure & flow.** Logical chapter progression; does each chapter earn its
  place; clear thread from question to answer.
- **Writing clarity.** Precise, readable, free of filler. Acronyms defined on
  first use.
- **Figures & tables.** Captioned, referenced in text, readable, honest (no
  truncated axes, no cherry-picked windows).
- **Citation hygiene.** Consistent style, no broken/missing refs, claims of fact
  cited.
- **Scope vs. level.** Is the scope appropriate for the degree — neither a
  term-paper nor three PhDs crammed together?
- **Internal consistency.** Numbers in the abstract match the body; the
  conclusion doesn't introduce new claims.
