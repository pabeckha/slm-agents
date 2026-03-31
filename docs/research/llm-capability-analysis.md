---
title: "LLM Capability Analysis for CLI/UI Assistants"
category: "architecture"
lastUpdated: "2026-03-07"
status: "active"
---

# LLM Capability Analysis for CLI/UI Assistants

## Purpose

Map the capabilities required by a coding CLI/UI assistant to what each provider and model family actually delivers. This analysis drives routing decisions: which model to use for which task type.

---

## Part 1: Required Capabilities

For a CLI/UI assistant to understand a message and guide the user correctly (coding, planning, explanation, etc.), it needs all of the following:

### 1.1 Core Language Capabilities

| Capability | What It Means | Why It Matters |
|---|---|---|
| **Instruction following** | Does exactly what was asked — no more, no less | Prevents unwanted refactors, extra features, or scope creep |
| **Ambiguity resolution** | Asks for clarification when intent is unclear | Avoids acting on wrong assumptions in complex tasks |
| **Output formatting** | Produces correct markdown, code blocks, diffs, lists | CLI rendering depends on well-structured output |
| **Conciseness** | Answers directly without excessive preamble | Interactive CLI needs low noise-to-signal ratio |
| **Multilingual understanding** | Handles non-English input gracefully | Teams with mixed language use |

### 1.2 Reasoning Capabilities

| Capability | What It Means | Why It Matters |
|---|---|---|
| **Multi-step reasoning** | Breaks a complex problem into sequential logical steps | Required for architecture decisions, debugging chains, refactors |
| **Planning** | Produces an actionable sequence before executing | Prevents mid-task course corrections |
| **Self-correction** | Identifies and fixes its own mistakes | Reduces hallucinated code that compiles but is wrong |
| **Causal reasoning** | Understands cause-and-effect in systems | Debugging, tracing errors to root causes |
| **Counterfactual reasoning** | Evaluates "what if" scenarios | Architecture trade-off analysis |

### 1.3 Code-Specific Capabilities

| Capability | What It Means | Why It Matters |
|---|---|---|
| **Code generation** | Writes correct, idiomatic code in any language | Core use case |
| **Code understanding** | Reads and explains existing code accurately | Required before any modification task |
| **Debugging** | Diagnoses bugs from error messages, stack traces, logs | Daily CLI use case |
| **Refactoring** | Improves structure without breaking behavior | Long-term codebase health |
| **Test generation** | Writes useful, non-trivial tests | Reduces manual test writing |
| **Type awareness** | Understands type systems (TypeScript, Rust, Python typing) | Prevents type-incorrect suggestions |
| **Framework knowledge** | Knows idioms for major frameworks (React, Next.js, etc.) | Domain-specific correctness |
| **Diff/patch output** | Produces minimal, targeted changes | Prevents whole-file rewrites for small fixes |

### 1.4 Context & Memory Capabilities

| Capability | What It Means | Why It Matters |
|---|---|---|
| **Long context retention** | Keeps track of information across a large window | Reading a full codebase in one pass |
| **Context coherence** | References prior turns accurately | Multi-turn sessions degrade without this |
| **Cross-file reasoning** | Understands relationships between multiple files | Required for refactors that span modules |
| **Session memory** | Tracks what was already done in the current session | Avoids repeating or contradicting earlier actions |

### 1.5 Tool Use & Agentic Capabilities

| Capability | What It Means | Why It Matters |
|---|---|---|
| **Function/tool calling** | Reliably invokes tools (read file, write file, bash) | Agentic CLI loop depends on this |
| **Tool result interpretation** | Correctly reads tool output and continues | Errors propagate if tool results are misread |
| **Loop termination** | Knows when a task is complete | Prevents infinite agentic loops |
| **Parallel tool use** | Issues multiple tool calls in one turn | Speeds up multi-file reads and searches |
| **Error recovery** | Adapts plan when a tool call fails | Robustness in real codebases |

### 1.6 Safety & Reliability Capabilities

| Capability | What It Means | Why It Matters |
|---|---|---|
| **Hallucination resistance** | Avoids inventing APIs, file paths, or behaviors | Silent errors are worse than visible ones |
| **Scope discipline** | Does not modify things outside the stated scope | Prevents unintended side effects |
| **Confirmation before destructive actions** | Asks before deleting, overwriting, force-pushing | Safety in agentic contexts |
| **Consistency** | Same input produces reliable output across runs | Predictable behavior in CI/automation |

---

## Part 2: Provider Capability Matrix

Rating scale: ★★★★★ excellent · ★★★★ good · ★★★ adequate · ★★ weak · ★ poor

### 2.1 Claude (Anthropic) — claude-sonnet-4-6 / claude-opus-4-6

| Capability | Sonnet 4.6 | Opus 4.6 | Notes |
|---|---|---|---|
| Instruction following | ★★★★★ | ★★★★★ | Best in class; very literal and disciplined |
| Multi-step reasoning | ★★★★ | ★★★★★ | Opus leads on complex chains |
| Code generation | ★★★★★ | ★★★★★ | Idiomatic, clean, minimal |
| Code understanding | ★★★★★ | ★★★★★ | Reads context deeply before acting |
| Debugging | ★★★★★ | ★★★★★ | Strong causal reasoning |
| Tool/function calling | ★★★★★ | ★★★★★ | Native, highly reliable, parallel support |
| Long context (200K) | ★★★★★ | ★★★★★ | Full fidelity across large files |
| Hallucination resistance | ★★★★★ | ★★★★★ | Rarely invents APIs or paths |
| Scope discipline | ★★★★★ | ★★★★★ | Strong; does not over-modify |
| Conciseness | ★★★★★ | ★★★★ | Opus can over-explain on complex tasks |
| Speed | ★★★★ | ★★★ | Sonnet is fast; Opus slower |
| Cost | ★★★ | ★★ | Mid-to-high per token |
| Vision/multimodal | ★★★★★ | ★★★★★ | Screenshots, diagrams |

**Best for:** Instruction-sensitive tasks, agentic loops, long-context codebase work, anything requiring discipline and precision.

---

### 2.2 GPT-4o / o3 (OpenAI)

| Capability | GPT-4o | o3 | Notes |
|---|---|---|---|
| Instruction following | ★★★★ | ★★★★ | Good, but occasionally adds unrequested content |
| Multi-step reasoning | ★★★★ | ★★★★★ | o3 is a dedicated reasoning model |
| Code generation | ★★★★★ | ★★★★★ | Broad language coverage, mature |
| Code understanding | ★★★★ | ★★★★★ | o3 excels at deep analysis |
| Debugging | ★★★★ | ★★★★★ | o3 traces root causes methodically |
| Tool/function calling | ★★★★★ | ★★★★ | Mature API, very reliable in 4o |
| Long context (128K) | ★★★★ | ★★★★ | Shorter than Claude/Gemini |
| Hallucination resistance | ★★★★ | ★★★★★ | o3 is more reliable than 4o |
| Scope discipline | ★★★★ | ★★★★ | Occasionally verbose |
| Conciseness | ★★★★ | ★★★ | o3 shows its reasoning chain |
| Speed | ★★★★★ | ★★★ | 4o is very fast; o3 is slow (reasoning) |
| Cost | ★★★ | ★★ | o3 is expensive per token |
| Vision/multimodal | ★★★★★ | ★★★★ | 4o is best-in-class for vision |

**Best for:** Speed-sensitive tasks (4o), deep reasoning/math problems (o3), broad framework knowledge, vision tasks.

---

### 2.3 Gemini 2.0 Flash / 2.5 Pro (Google)

| Capability | Gemini 2.0 Flash | Gemini 2.5 Pro | Notes |
|---|---|---|---|
| Instruction following | ★★★★ | ★★★★★ | 2.5 Pro improved significantly |
| Multi-step reasoning | ★★★★ | ★★★★★ | 2.5 Pro is a reasoning model |
| Code generation | ★★★★ | ★★★★★ | Strong, especially with Google stack |
| Code understanding | ★★★★ | ★★★★★ | — |
| Debugging | ★★★★ | ★★★★★ | — |
| Tool/function calling | ★★★★ | ★★★★★ | Improving rapidly |
| Long context (1M tokens) | ★★★★★ | ★★★★★ | Best context window available |
| Hallucination resistance | ★★★★ | ★★★★ | Grounding helps; still improving |
| Scope discipline | ★★★ | ★★★★ | Flash can be verbose |
| Conciseness | ★★★★ | ★★★ | 2.5 Pro shows reasoning steps |
| Speed | ★★★★★ | ★★★ | Flash is the fastest major model |
| Cost | ★★★★★ | ★★★ | Flash is extremely cheap |
| Vision/multimodal | ★★★★★ | ★★★★★ | Best-in-class; native multimodal |

**Best for:** Very long context (entire repos), cost-sensitive high-volume tasks (Flash), speed-sensitive real-time interactions (Flash), multimodal input.

---

### 2.4 Local Models (Ollama / llama.cpp)

Representative models: **Qwen2.5-Coder-32B**, **Llama 3.3-70B**, **DeepSeek-R1**, **Phi-4**, **Mistral-Small-3.1**

| Capability | Qwen2.5-Coder | Llama 3.3 70B | DeepSeek-R1 | Phi-4 (14B) |
|---|---|---|---|---|
| Instruction following | ★★★★ | ★★★★ | ★★★★ | ★★★★ |
| Multi-step reasoning | ★★★ | ★★★★ | ★★★★★ | ★★★ |
| Code generation | ★★★★★ | ★★★★ | ★★★★ | ★★★★ |
| Code understanding | ★★★★★ | ★★★★ | ★★★★ | ★★★ |
| Debugging | ★★★★ | ★★★ | ★★★★★ | ★★★ |
| Tool/function calling | ★★★ | ★★★★ | ★★★ | ★★★ |
| Long context | ★★★ | ★★★ | ★★★ | ★★★ |
| Hallucination resistance | ★★★ | ★★★ | ★★★★ | ★★★ |
| Privacy | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ |
| Speed (hardware-dependent) | ★★★ | ★★ | ★★ | ★★★★ |
| Cost (after hardware) | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ |

**Best for:** Offline use, privacy-sensitive codebases, cost reduction on simple tasks, high-volume batch jobs where API costs are prohibitive.

**Limitations:** Context window constrained by VRAM, tool calling less reliable than cloud providers, quality degrades on complex multi-file reasoning without sufficient hardware.

---

## Part 3: Capability-to-Provider Routing Guide

This maps specific CLI/UI task types to the recommended provider:

| Task | Best Provider | Fallback | Avoid |
|---|---|---|---|
| Agentic loop (tool-heavy) | Claude Sonnet | GPT-4o | Local (unreliable tool calling) |
| Complex multi-step reasoning | Claude Opus / o3 | Gemini 2.5 Pro | Local (< 70B) |
| Fast interactive response | Gemini Flash / GPT-4o | Claude Sonnet | Opus, o3 (slow) |
| Code generation (any language) | Claude Sonnet / Qwen2.5-Coder | GPT-4o | — |
| Deep debugging / root cause | Claude Opus / DeepSeek-R1 | o3 | Flash models |
| Long context (full repo scan) | Gemini 2.5 Pro (1M ctx) | Claude (200K) | GPT-4o (128K) |
| Instruction-sensitive task | Claude (any) | GPT-4o | Gemini Flash |
| Vision / screenshot input | Gemini / GPT-4o | Claude | Local (no vision) |
| Cost-sensitive high volume | Gemini Flash | Local | Opus, o3 |
| Privacy-sensitive codebase | Local (Qwen2.5-Coder) | — | Any cloud |
| Refactoring (scope discipline) | Claude Sonnet | GPT-4o | — |
| Architecture planning | Claude Opus | Gemini 2.5 Pro | Small local models |
| Test generation | Claude Sonnet / Qwen2.5-Coder | GPT-4o | — |

---

## Part 4: Minimum Viable Capability Set

For a provider to be usable as the primary CLI/UI backend, it must satisfy all of the following:

| Requirement | Minimum Bar |
|---|---|
| Context window | ≥ 32K tokens |
| Tool/function calling | Supported and reliable |
| Streaming | Supported (token-by-token) |
| Instruction following | Does not add unrequested code or features |
| Code generation | Passes basic language-specific benchmarks (HumanEval, MBPP) |
| Hallucination resistance | Does not invent file paths or API signatures under normal conditions |

Providers that do not meet all six are demoted to **specialist use only** (e.g. routing only specific task types to them).

---

## Part 5: Routing Strategy Recommendation

Given the analysis, the recommended routing approach for the DeepGruble CLI/UI:

```
Default provider: Claude Sonnet
├── Long context (> 150K tokens)     → Gemini 2.5 Pro
├── Pure reasoning / math            → Claude Opus or o3
├── Speed-sensitive (< 1s response)  → Gemini Flash
├── Cost reduction (simple queries)  → Gemini Flash or local
└── Privacy-sensitive                → Local (Qwen2.5-Coder)
```

This maps directly to the `CascadeStrategy` and `CapabilityStrategy` defined in `phase-5-router.md`.

---

## Related Documents

- [PRD.md](../PRD.md) — project goals
- [docs/architecture/cli-ui-llm-implementation-plan.md](../architecture/cli-ui-llm-implementation-plan.md) — implementation plan
- [docs/research/llm-optimization-methods.md](llm-optimization-methods.md) — optimization techniques per provider
- [issues/architecture/model-routing-strategy.md](../../issues/architecture/model-routing-strategy.md) — routing strategy decision
- [issues/architecture/phase-5-router.md](../../issues/architecture/phase-5-router.md) — router implementation
