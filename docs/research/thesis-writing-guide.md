# Thesis Writing Guide

Reference this while writing. Based on Sune Lehmann's guide + AI detection avoidance.

## Voice Rules

1. **Active voice always.** "I ran the experiment" not "The experiment was conducted". "I chose Qwen 2.5 7B because..." not "Qwen 2.5 7B was selected due to...".

2. **Use "I" throughout.** Single-author thesis — own the work. "I evaluate", "I observe", "I argue".

3. **Vary sentence length.** Mix short punchy sentences with longer explanatory ones. A paragraph with five 20-word sentences reads like a machine wrote it. Break the rhythm.

4. **State things directly.** Don't hedge. "Constrained decoding solves the format problem" not "It is important to note that constrained decoding appears to address the formatting challenge".

5. **Be specific, not generic.** "72.75% accuracy on 400 test cases" not "significant improvement in performance metrics".

## Words and Phrases to AVOID

These are AI-detector red flags:

| Avoid | Use instead |
|-------|-------------|
| furthermore, moreover, additionally | and, also, or just start the sentence |
| it is important to note that | (delete — just say the thing) |
| it is worth mentioning | (delete) |
| delve into | examine, study, test |
| comprehensive | (usually unnecessary — cut it) |
| leverage | use |
| facilitate | enable, allow, help |
| landscape | field, area, space |
| underscore | show, highlight |
| in conclusion | (just start concluding) |
| a myriad of | many, several |
| plays a crucial role | matters, affects |
| in the context of | in, for, when |
| this highlights the fact that | this shows |
| notably | (delete or rephrase) |

## Paragraph Structure

**Don't** write every paragraph as: topic sentence -> support -> support -> support -> conclusion. That's the AI pattern.

**Do** vary structure:
- Sometimes start with the evidence, then the claim
- Sometimes one paragraph is two sentences
- Sometimes a paragraph is a single long argument that builds
- Let transitions happen naturally — you don't need a connector word at every paragraph start

## Lehmann's Rules Applied

### Reproducibility
For every experiment, document:
- Exact model ID (e.g., `Qwen/Qwen2.5-7B-Instruct`)
- Software versions (vLLM 0.8.5, Python 3.12.11, CUDA 12.6.3)
- Hardware (A100 40GB, which HPC queue)
- Hyperparameters (temperature=0, max_tokens=512, gpu_memory_utilization=0.9)
- How to re-run it (the bsub command + script path)

### Justify every choice
Don't just state what you did. Explain why:
- Why Qwen 2.5 7B? (strong instruction following, fits on RTX 4090, official AWQ variant available)
- Why BFCL? (standardised benchmark with AST-level evaluation, widely cited)
- Why cumulative ablation? (isolates marginal impact of each method)
- Why vLLM? (supports guided decoding natively, standard serving layer)

### Figure captions
Bad: "Figure 1: Pipeline overview."
Good: "Figure 1: Two-stage function calling pipeline. Stage 1 selects the function name from candidates using guided_choice. Stage 2 extracts arguments as a JSON object using guided_json. Both stages use vLLM's constrained decoding to guarantee valid output."

### Narrative structure per section
Each section follows: context -> method -> result -> interpretation.
- What question are we answering?
- What did we do?
- What happened?
- What does it mean?

## Checklist Before Submitting a Chapter

- [ ] Read every sentence aloud. Does it sound like you talking?
- [ ] Search for "furthermore", "moreover", "additionally", "it is important" — replace all
- [ ] Check sentence length variance: no five consecutive same-length sentences
- [ ] Every claim has a number or a citation
- [ ] Every design choice has a justification
- [ ] Figures have descriptive captions (not just labels)
- [ ] Used "I" consistently (not "the author" or passive voice)
- [ ] No paragraph starts with a transition word that could be deleted
