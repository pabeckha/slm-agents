# Thesis Red-Team Rubric

Use this rubric to look for weaknesses that a friendly editing pass may miss.

## Claim-Evidence Audit

For each major claim, ask:

- What exact evidence supports it?
- Is the evidence direct, or a proxy?
- Is the claim broader than the experiment?
- Is uncertainty quantified where it should be?
- Does another result in the thesis weaken or qualify it?
- Is the same claim phrased consistently in the abstract, introduction, results, discussion, and conclusion?

Common failure modes:

- A headline claim relies on the easiest benchmark category.
- A proxy metric is described as if it were an end-to-end deployment result.
- A limitation appears late but not where the claim first appears.
- A result is statistically significant but practically small, or vice versa.
- A negative result is acknowledged but not allowed to affect the main conclusion.

## Methodology Audit

Check for:

- Missing or weak baselines.
- Controls that change more than one variable.
- Test-set-informed design choices.
- Single-family or single-dataset generalization.
- Cross-harness comparisons that may not be like-for-like.
- Non-executed or simulated components presented as practical validation.
- Ablation ladders where cumulative effects obscure standalone effects.
- Evaluation settings that make the task easier than deployment.

## Statistical Audit

Check for:

- Sample sizes and denominators for every percentage.
- Confidence intervals or uncertainty where comparisons are close.
- Paired vs unpaired test choice.
- Multiple comparisons when many configurations are tested.
- Borderline p-values described too strongly.
- Run-to-run variance compared against reported deltas.
- Claims based on single runs, especially for stochastic benchmarks.

## Technical Correctness Audit

Check for:

- Equations and definitions that are standard but misstated.
- Model, benchmark, and dataset names that are inconsistent.
- Configuration names that drift across chapters.
- Tables whose values disagree with prose.
- Figures whose captions overstate what is shown.
- Pipeline descriptions that do not match the implementation.
- Claims about memory, latency, or hardware that need unit or setup details.

## Related Work And Citation Audit

Check for:

- Citations used for claims they do not actually support.
- Missing comparator papers or benchmark methods.
- Prior work framed as weaker than it is.
- Novelty claims that should be narrowed.
- Leaderboard or documentation dates that need timestamping.

## Practical Relevance Audit

Check for:

- Deployment claims without measured deployment components.
- Cost models that omit router cost, local serving cost, latency, utilization, or maintenance.
- Privacy/offline claims that are plausible but not evaluated.
- Tool-calling accuracy presented as agent completion ability.
- Real-world validation sets that are too small or hand-crafted to carry broad claims.

## Output Quality Rules

- Prefer fewer, sharper findings over a long list of weak objections.
- Quote or reference exact sections when possible.
- State the minimum fix needed: reframe, add caveat, add analysis, verify citation, or run experiment.
- Include "what is already well scoped" so the author does not weaken defensible claims.
- If evidence is missing because the artifact was not available, say what could not be checked.
