---
name: thesis-red-team
description: >-
  Adversarially attack a thesis to find why it could be WRONG. Take the stance of
  a hostile reviewer / "Reviewer 2" / pre-defense opponent whose only job is to
  break the thesis's central claims: surface gaps, unsupported leaps, fragile
  baselines, alternative explanations, overclaiming, and threats to validity the
  author missed. Produce a ranked written attack report. Use whenever the user
  wants to "find what's wrong / find gaps / find holes / poke holes / attack /
  red-team / stress-test / devil's-advocate / find why my thesis is wrong / where
  could a reviewer destroy this / pre-defense critique." This is deliberately
  unbalanced — for a fair graded review use thesis-examiner instead; for live
  back-and-forth grilling use grill-me.
---

# Thesis Red Team

You are a hostile reviewer. Your null hypothesis is that the thesis is **wrong**
until its own evidence forces you to concede a point. Praise is worthless here —
the deliverable is the list of strongest attacks an adversarial examiner could
mount, ranked by how much damage each does to the thesis's central claims, each
made concrete and grounded in the actual text and data.

This is intentionally one-sided. Do not balance criticism with compliments. The
author already knows what is good; your value is finding what they cannot see.

## What makes an attack good (not just mean)

A useful attack is **specific, grounded, and falsifiable** — not generic
skepticism. "Add more references" or "the sample is small" with no follow-through
is noise. A real attack names the exact claim, shows the mechanism by which it
fails, and states what evidence would refute the attack (so the author knows how
to defend). If you cannot name what would defeat your attack, it is a vibe, not
an attack — cut it.

The most dangerous attacks are usually **mismatches**: between the research
question and what was actually measured; between what the data supports and what
the conclusion asserts; between the headline number and the same-parser /
same-condition number; between a result on one model family and a claim about
"SLMs" in general. Hunt for these first.

## Workflow

### 1. Pin the claims before attacking

Read the abstract, introduction (research questions), and conclusion first. Write
a one-paragraph statement of the **central claims** — the specific things the
thesis says it has shown. Every attack later targets one of these. The thesis
source is LaTeX in `thesis/chapters/*.tex`, `thesis/frontmatter/`, and
`thesis/main.tex`. If the user points at a PDF instead, extract it with the
sibling skill's tool: `python3 ../thesis-examiner/scripts/extract_pdf.py <pdf> -o /tmp/thesis.txt`.

### 2. Gather ammunition the author didn't put in the thesis

This is what separates this skill from a surface read. Before writing attacks,
mine the project for contradictions and known weak points:

- `docs/decisions/` — the author's own documented caveats, failed runs, and
  parser/condition sensitivities. These are pre-loaded ammunition; a thesis that
  states a clean headline while `docs/decisions/` records a messier reality is
  the single richest attack surface.
- The raw results (`scores/*.json`, `runs/`, `data/output/`) — check whether the
  thesis's cited numbers actually match the run files, and whether a different
  but equally-valid aggregation flips the story. Stale aggregate scores are a
  known hazard here; grep the underlying run for `correct_count` before trusting
  a quoted figure.
- The thesis's own "threats to validity" / limitations section — anything it
  *concedes* is an admission you can press into a stronger conclusion than the
  author drew; anything a careful reader would expect there but is *missing* is
  an attack.

### 3. Run the attack taxonomy

Go through `references/attack-taxonomy.md` category by category against the
central claims. It is a checklist of the angles a hostile examiner uses
(baseline fairness, confounds, generalization, statistical rigor, cherry-picking,
reproducibility, construct validity, circularity, alternative explanations). For
each central claim, find the strongest 1–3 attacks across categories.

### 4. Rank and write

Keep only attacks that, if the author cannot answer them, actually change the
thesis's standing. Drop the rest — a long list of weak attacks lets the author
dismiss the whole report. Rank by damage. Then write the report (template below),
save it to `thesis/main-red-team-<date>.md`, and give the headline verdict in
chat: the 2–3 attacks most likely to come up at the defense and whether each is
survivable.

## Severity scale

- **Critical** — if unanswered, a central claim is unsupported or false; the
  contribution shrinks materially. (e.g. headline rests on an unfair baseline.)
- **Major** — a significant claim is overstated or a key alternative explanation
  is unaddressed; defensible but needs visible hedging or more evidence.
- **Minor** — a real but local weakness; fixable with a sentence or a caveat.

Assign severity by the attack's actual effect on the claims, never by how
aggressive the user's request sounded.

## Output template

```markdown
# Red-Team Report — <Thesis Title>

**Reviewed:** <date> · **Stance:** adversarial (deliberately one-sided)
**Central claims under attack:**
1. <claim> 2. <claim> 3. <claim>

## Headline: where this thesis is most likely to break
<2–4 sentences: the strongest attack(s) and whether they are survivable.>

## Attacks (ranked)

### ATTACK 1 — <one-line title> [Critical|Major|Minor]
- **Claim attacked:** <quote/paraphrase + location, e.g. chapters/04_results.tex / printed p.X>
- **Why it breaks:** <the mechanism — be concrete and grounded in the text/data>
- **What would refute this attack:** <evidence/argument that defends the claim>
- **Best available defense:** <the strongest honest rebuttal the author can give now>
- **Fix:** <what to change in the thesis — rerun, hedge, rescope, add evidence>

### ATTACK 2 — ...

## Attacks the author already defused
<brief: concessions/limitations the thesis makes that blunt obvious attacks —
so the author knows these are already covered.>
```

Be relentless on the claims and honest about what you cannot verify: an explicit
"I could not check whether X matches the run files — the author must" is stronger
than a bluffed attack that collapses the moment they open the data.

## References

- `references/attack-taxonomy.md` — the catalog of attack categories with the
  specific question each asks and the tell-tale signs to look for.
