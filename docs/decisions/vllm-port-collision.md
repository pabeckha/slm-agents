# vLLM Port Collision Across Concurrent HPC Jobs (2026-06-12)

## Question

The B-template 1.5B run (job 28626696, issue #157) scored exactly 0/400
while 0.5B scored 78.0% and 3B 95.0%. Was this a real result or a pipeline
artifact?

## Root cause

Every HPC job script started its vLLM server on hard-coded port 8000 and
health-checked `localhost:8000`. LSF can place several single-GPU jobs on
the same node. When that happens, the second job's server fails to bind
the port, but the health check passes against the **first** job's server,
and the evaluation runs against whatever model that server is serving.

For job 28626696 (1.5B B-template, node n-62-13-18), all 400 requests
404'd with "The model `Qwen/Qwen2.5-1.5B-Instruct` does not exist" because
the answering server (job 28626690's) was serving 0.5B. The adapter
recorded each as a failure, producing the 0/400.

## Blast radius

A sweep of `logs/*.out` for the 404 signature shows this was systemic, not
a one-off:

- `bfcl_template_baseline` 1.5B (28626696): 400/400 — invalid, rerun needed.
- `bfcl_schema_rich` 1.5B (28626697): 800 404s — invalid.
- `bfcl_ft_aligned_no_guided` (28626695): 400 404s — already on the
  parser-fix rerun list.
- May runs with the same signature: `bfcl_no_guided` 7B ×3 (28337927/30/32),
  AWQ runs on 2026-05-03 (bfcl_eval/no_guided/quant 28341819–24), parts of
  the τ-bench May runs (28443556/58/59, 28461727–30). Several of these were
  already superseded; any that feed thesis tables must be checked against
  their job logs before use.
- Partial contamination (a few 404s at job start/end, e.g. 28626700 RAG
  1.5B with 2): a handful of cases scored as failures that never reached
  the model.

## Fix

PR #167: in all 22 vLLM-backed scripts,

1. `VLLM_PORT=$((10000 + ${LSB_JOBID:-$$} % 20000))` — port derived from
   the job id, so co-located jobs cannot collide;
2. after the health check, query `/v1/models` and abort unless the served
   model id equals the model the script asked vLLM to load.

The second check turns any future cross-talk into a loud early failure
instead of a silent 0% run.

## Decision

- Treat any run whose job log contains the `does not exist` 404 signature
  as invalid, regardless of its manifest accuracy.
- Reruns submitted 2026-06-12 with the fixed scripts (jobs 28640860–72):
  Config B at all four sizes, few-shot/CoT/RAG no-guided at 0.5B/1.5B,
  FT-aligned no-guided 0.5B, FT no-guided 7B, B-template 1.5B.
- Before any thesis table is finalized, cross-check each contributing run's
  job log for this signature (in addition to the no-guided parser issue in
  `no-guided-parser-fix-results.md`).
