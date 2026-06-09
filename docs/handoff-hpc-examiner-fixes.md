# Handoff: HPC runs for the examiner-review fixes

Written 2026-06-09. Context: the examiner review
(`thesis/main-examiner-review.md`) surfaced 16 issues, tracked in
`docs/thesis-examiner-issues.md`. All prose, figure, and bibliography fixes
are already applied in the working tree on branch
`thesis/technique-isolation-ablation` (uncommitted), and the thesis compiles
cleanly. Three items need the HPC because the per-case prediction files and
the GPUs live there. Everything below runs from the HPC checkout at
`~/Documents/slm-agents` after pulling this branch.

## Task 1: Config B-template run (closes issue 1 fully)

**Why.** The thesis's 1.5% baseline is a generic integration without Qwen's
native tool-calling chat template. The reframed text currently cites an
external reference point (ToLeaP, 94.50% on an earlier BFCL revision). One
run of the new B-template config replaces that citation with our own
measurement under our own harness, which is a far stronger defense position:

| Config | Prompting | Decoding | Claim it supports |
|---|---|---|---|
| B | generic two-stage | free | model-agnostic floor (1.5%) |
| B-template | native chat template | free | model-specific, high but no guarantee |
| CD | generic two-stage | guided | guaranteed format, model-agnostic |

**What was added.**
- `src/chat_template_backend.py`: renders the prompt client-side with
  `tokenizer.apply_chat_template(..., tools=...)`, sends it to the same vLLM
  completions endpoint, parses the model's `<tool_call>` block (with a
  bare-JSON fallback). Parse failures count as failures, mirroring Config B.
  The `parse_tool_call` and numeric-casting logic match the other backends so
  scoring differences reflect prompting only.
- `src/bfcl_adapter.py`: new `--backend vllm-template` (requires
  `--no-guided`; refuses `--rag/--few-shot/--cot`). Single-call categories
  only (`simple_python`, `multiple`); it has no `process_parallel`.
- `scripts/hpc/run_bfcl_template_baseline.sh`: LSF job, same shape as
  `run_bfcl_no_guided.sh`.

**Run.**
```bash
cd ~/Documents/slm-agents
git fetch && git checkout thesis/technique-isolation-ablation && git pull
bsub < scripts/hpc/run_bfcl_template_baseline.sh
# optional size sweep afterwards:
#   MODEL=Qwen/Qwen2.5-0.5B-Instruct bsub < scripts/hpc/run_bfcl_template_baseline.sh
```
Results land in `data/output/bfcl_template_baseline/` (scores under
`<model>/scores/simple_python_scores.json`). Roughly 30–60 min including
model load. The local parser logic is unit-tested; if many cases fail with
"no <tool_call> block", inspect a few raw outputs before trusting the score
(see Troubleshooting below).

**Then update the thesis** (anchors are grep-able strings):

1. `thesis/chapters/01_introduction.tex`, paragraph starting "The 1.5\%
   figure characterises": replace the ToLeaP sentence with our own number,
   e.g. "Under the same harness with the model's native tool-calling
   template and free generation (Config B-template), the same model reaches
   X.XX\%, confirming that the baseline gap is a property of the generic
   integration." Keep or drop the ToLeaP citation as corroboration.
2. `thesis/chapters/03_methodology.tex`, paragraph starting "Base is
   deliberately model-agnostic": add one sentence reporting the B-template
   number as the measured counterpart.
3. `thesis/chapters/04_results.tex`, Table `tab:baseline-results`: add a
   B-template row between B and CD so the three-point story is visible in
   the results chapter.
4. `thesis/chapters/05_discussion.tex`, threats entry "Baseline
   construction": replace "reports the same model far above the 1.5\%
   measured here" with the measured number.
5. `thesis/chapters/06_conclusion.tex`, RQ1 answer, sentence starting "This
   gap quantifies the cost of a naive generic integration": insert the
   measured number.
6. Interpretation guidance: if B-template lands above CD (likely), the
   honest framing is that constrained decoding's value is the *structural
   guarantee* and model-agnosticism, not raw accuracy superiority over
   native templates. If B-template lands near or below CD, the original
   framing strengthens. Either way the format-vs-semantic finding stands.

## Task 2: McNemar paired tests (closes issue 4)

**Why.** Section 4.4.1 now states that the +4.0 pp CD+FT-aligned gain needs
a paired test; the text awaits the numbers.

**Run** (re-scores stored result files with the same ast_checker):
```bash
# CD vs CD+FT-aligned (7B, simple_python)
uv run --group hpc python scripts/mcnemar_bfcl.py \
    data/output/bfcl/Qwen_Qwen2.5-7B-Instruct/non_live/BFCL_v4_simple_python_result.json \
    data/output/bfcl_ft_aligned/<merged-model-dirname>/non_live/BFCL_v4_simple_python_result.json \
    --category simple_python

# CD+Q vs CD+Q+FT-aligned
uv run --group hpc python scripts/mcnemar_bfcl.py \
    data/output/bfcl_quant/<awq-model-dirname>/non_live/BFCL_v4_simple_python_result.json \
    data/output/bfcl_cdqft_aligned/<awq-ft-model-dirname>/non_live/BFCL_v4_simple_python_result.json \
    --category simple_python
```
Replace `<...-dirname>` with the actual directory names under each output
dir (the model path with `/` replaced by `_`). The script prints both
re-scored accuracies (sanity check: must reproduce 291/400, 307/400,
289/400, 297/400), the discordant counts b and c, and the exact two-sided
p-value.

**Then update the thesis.** In `thesis/chapters/04_results.tex`, find the
sentence "attaching a significance level to this delta requires a paired
comparison (McNemar's test)" and extend the passage with the result, e.g.:
"McNemar's exact test on the per-case predictions gives b = N cases corrected
by fine-tuning against c = M cases broken (p = 0.0XX)." If p < 0.05, the
"only configuration family to exceed the no-training level" claim can be
restated more firmly; if not, keep the current direction-consistency framing
as the primary evidence.

## Task 3 (optional): guided-decoding latency (issue 7 follow-up)

The thesis now says latency was not measured. If you want the stronger
version: rerun B, CD, and CD+Q with `--limit 100`, capture wall time per
request from the adapter logs (each case prints a line; timestamps in the
LSF log suffice), and add a three-row latency table to §4.2.1. Not required
for the claims as currently worded.

## Verification checklist after inserting numbers

- [ ] `latexmk -pdf thesis/main.tex` compiles with no undefined references.
- [ ] Abstract, §1.1, §3.4, Table 4.1, §5.3.1, and RQ1 all quote the same
      B-template number.
- [ ] `docs/thesis-examiner-issues.md`: tick issues 1 and 4, and the McNemar
      entry in the verification queue.
- [ ] Commit on this branch and open a PR (never push to main; no AI
      attribution in commits).

## Troubleshooting

- **`transformers` import error in the eval client:** the hpc dependency
  group includes sentence-transformers, which pulls transformers. If the
  import still fails, add `transformers` to the hpc group in
  `pyproject.toml` and re-run `uv sync --group hpc`.
- **Many "no <tool_call> block" failures in B-template:** print 2–3 raw
  completions (add a temporary `print(raw)` in
  `ChatTemplateBackend.process_raw`). If the model emits tool calls in a
  different wrapper, the regex in `parse_tool_call` is the only thing to
  adjust. If outputs are cut off mid-JSON, raise `max_tokens`.
- **McNemar script accuracies do not reproduce the thesis numbers:** the
  result file does not correspond to the run cited in the thesis; check the
  run manifests in `data/output/*/runs/` for the matching timestamps before
  using the p-value.
