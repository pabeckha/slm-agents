---
theme: ./theme
layout: cover
title: Agents with Small Language Models
info: DTU Master Thesis · Supervisor Meeting
author: Paulo Beckhauser
date: 2026-03-16
exportFilename: meeting-nick-16-march-2026
---

# Agents with Small Language Models

DTU Master Thesis · Supervisor Meeting

<div class="meta">

**Paulo Beckhauser** · s242779 · Supervisor: Nick · March 16, 2026

</div>

---
layout: section
---

# Context

## The core architecture challenge

---

# The challenge

- **SLMs struggle with agentic tasks.** Out of the box, small models fail at the core capabilities an agent needs: reasoning, tool use, and structured output.

- **Reasoning correctly.** The model must decompose tasks, decide when to call a tool vs. respond directly, and chain multi-step reasoning without hallucinating intermediate steps.

- **Calling the correct tools.** Select the right tool from a schema, produce valid arguments, and handle the result, all within constrained compute and latency budgets.


<img src="/tool-calling-challenge.png" class="diagram" />

<style>
.default-body {
  display: flex !important;
  flex-direction: column !important;
}
.default-body > * {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.default-body h1 {
  flex: 0 !important;
  margin-bottom: 0 !important;
}
.default-body ul {
  flex: 1;
  padding: 0;
  padding-top: 1.5rem;
  margin: 0;
}
.default-body li {
  font-size: 0.78rem !important;
  margin-bottom: 0.8rem !important;
  line-height: 1.35 !important;
}
.diagram {
  width: 200%;
  margin-top: 2rem;
  object-fit: contain;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}
</style>

---
layout: statement
---

# Research Question

Which combination of *optimization techniques* enables a *small language model* to reason effectively and call the correct tools?


---

# Evaluation Metrics

| Category | Metric | Description |
|----------|--------|-------------|
| Tool Calling | **Tool Selection Accuracy** | Correct tool picked |
| | **Argument Accuracy** | Correct types and values |
| | **JSON Validity Rate** | Valid structured JSON output |
| | **Hallucination Rate** | Hallucinated names, extra/wrong fields |
| Reasoning | **Task Decomposition Accuracy** | All sub-tasks identified |
| | **End-to-End Task Success** | Full pipeline produces correct result |
| [BFCL](https://gorilla.cs.berkeley.edu/leaderboard.html) | **AST Accuracy** | Function call AST matches expected |
| | **Exec Accuracy** | Executed call produces correct result |

---
layout: section
---

# Methods

## Implementation Order

---

# Implementation Order

**Priority logic:** no-training methods first (cheapest, fastest), then training-required. Each method evaluated individually, and potentially in combination if time allows.

| # | Method | Status | Notes |
|---|--------|--------|-------|
| 0 | **Baseline Definition** | <span class="done">Done</span> | Reference point. Unconstrained Qwen 2.5 3B |
| 1 | **Constrained Decoding** | <span class="next">In progress</span> | Ensures valid output structure. Foundation for all others. |
| 2 | **Prompt Engineering / Few-shot** | <span class="badge-muted">To-do</span> | Zero cost. Establishes what prompting alone can do. |
| 3 | **Inference-Time Compute** | <span class="badge-muted">To-do</span> | No training. CoT/ReAct improves reasoning. |
| 4 | **RAG** | <span class="badge-muted">To-do</span> | No training. Retrieves schemas, reduces hallucination. |
| 5 | **LoRA / PEFT** | <span class="badge-muted">To-do</span> | Training required. Teaches tool-use directly. High impact. |
| 6 | **Knowledge Distillation** | <span class="badge-muted">To-do</span> | Training required. Builds on LoRA pipeline. Needs API budget. |
| — | ~~Quantization~~ | <span class="risky">Discarded</span> | Efficiency only. Doesn't improve reasoning or tool calling. |
| — | ~~Pruning~~ | <span class="risky">Discarded</span> | Efficiency only. Likely degrades instruction-following. |

---
layout: section
---

# Progress

## Overall Status

---

# Overall Status

- ✅ **Project plan submitted.** Motivation, background, research question and Gantt chart delivered.
- ✅ **Literature reviewed.** Constrained decoding, LoRA/PEFT, quantization, pruning, knowledge distillation, RAG.
- 🔄 **Constrained decoding in progress.** PoC built on Qwen 2.5 3B. Running full BFCL evaluation.

```mermaid {scale: 0.42}
gantt
    dateFormat  YYYY-MM-DD
    tickInterval 1month
    axisFormat  %b %Y

    section Done
    Literature search              :done, lit, 2026-01-05, 4w
    Baseline definition            :done, base, 2026-02-02, 2w
    Constrained decoding PoC       :done, cdpoc, 2026-01-19, 4w
    Hand-in project plan           :milestone, done, 2026-02-09, 0d

    section In Progress
    Constrained decoding (BFCL)    :active, cd, 2026-02-20, 3w

    section No Training
    Prompt engineering / Few-shot   :pe, after cd, 2w
    Inference-time compute (CoT)    :itc, after pe, 2w
    RAG                             :rag, after itc, 2w

    section Training Required
    LoRA / PEFT                     :lora, after rag, 3w
    Knowledge distillation          :kd, after lora, 3w

    section Writing
    Report writing                  :write, 2026-02-15, 2026-07-05
    Hand-in thesis (Jul 5)          :milestone, crit, 2026-07-05, 0d
```

---
layout: section
---

# Questions

## Technical & Operational discussion

---

# Technical discussion


- ❓ **Pareto approach to methods.** Instead of going deep on one method, evaluate each for improvement potential and invest time where the marginal gain is highest. Does this approach make sense for a thesis?
<br/> A:

- ❓ **Do we always need an LLM?** For some tasks (e.g., deterministic routing, schema validation), an LLM is overkill. Could the architecture bypass the model entirely for certain task types? I want to create an architecture with a cascade mode(and use LLMs for more complex models). Does it makes sense my hypothesis?
<br/> A:

- ❓ **Encoder-only(Bert) x Decoder-only(GPT)** For this situation maybe encoder can be better...?
<br/> A:

---

# Operational discussion

- ❓ **Presentation**: When do we schedule the day? Is it better remote?
<br/> A:


- ❓ **Final Document Submission**: Do you want(will have the availability) to read the document before submission?
<br/> A: 

- ❓ **Code submission**: Github links? .zip? Each method implementation is a different repository right now
<br/> A:

