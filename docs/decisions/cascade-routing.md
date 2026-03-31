---
title: "Cascade Routing"
category: "architecture"
lastUpdated: "2026-03-07"
status: "active"
---

# Cascade Routing

## What It Is

Cascade routing means: **try the cheapest model first, only escalate to a more expensive one if the task requires it.**

A request flows down through tiers and stops at the first one capable of handling it — like a waterfall. The result is that the majority of queries are served by cheap or free models, and expensive frontier models are reserved for the minority of tasks that genuinely need them.

---

## Analogy

Think of it like a support centre:
- A **chatbot** handles 60% of tickets automatically
- A **junior agent** handles 30% of the remaining cases
- A **senior specialist** only sees the 10% that are genuinely complex

Same outcome. Dramatically lower cost.

---

## The DG Cascade

```
Incoming request
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Tier 0 — Self-hosted (Ollama)          ~$0 marginal    │
│  Qwen 3 72B · DeepSeek-R1-70B-Distill                   │
│                                                          │
│  Use when:                                               │
│  - Privacy-sensitive data (nothing leaves DG servers)   │
│  - High-volume / batch workloads (>50M tokens/month)    │
│  - Offline / no internet required                        │
└──────────────────── if not applicable ──────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Tier 1 — Budget cloud           $0.14–$0.20/M input    │
│  DeepSeek V3 · Grok 4.1 Fast                            │
│                                                          │
│  Use when:                                               │
│  - Routine queries, summarisation, classification        │
│  - High-volume tasks where quality threshold is met      │
│  - Simple Q&A against Granite docs                       │
└──────────────────── if task needs more ─────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Tier 2 — Quality cloud              $3.00/M input      │
│  Claude Sonnet 4.6                                       │
│                                                          │
│  Use when:                                               │
│  - Coding, refactoring, test generation                  │
│  - Agentic tool-use loops (read file, write, bash)       │
│  - Tasks requiring strict instruction following          │
│  - Long context up to 200K tokens                        │
└──────────────────── if task needs more ─────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Tier 3 — Reasoning              $0.55–$5.00/M input    │
│  DeepSeek R1 (cheap) · Claude Opus 4.6 (premium)        │
│                                                          │
│  Use when:                                               │
│  - Complex multi-step reasoning or planning              │
│  - Architecture decisions, trade-off analysis            │
│  - Math, theorem proving, deep debugging                 │
└──────────────────── if task needs more ─────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Tier 4 — Long context               $2.00/M input      │
│  Gemini 3.1 Pro (1M tokens)                              │
│                                                          │
│  Use when:                                               │
│  - Context window exceeds 150K tokens                    │
│  - Full repository scans                                 │
│  - Multimodal input (images, video, audio)               │
└─────────────────────────────────────────────────────────┘
```

---

## Self-Hosted Tier (Tier 0)

Tier 0 runs entirely on DG infrastructure using **Ollama** — no data leaves the building.

### Why self-host at all?

| Reason | Detail |
|---|---|
| **Privacy** | Client data never sent to third-party APIs. Critical for regulated industries (finance, legal, healthcare). |
| **Cost at scale** | Above ~50M tokens/month, hardware amortisation + electricity beats any cloud API on price. |
| **Offline** | Works without internet. Relevant for on-premises client deployments of unanswerable.ai. |
| **Latency** | Sub-100ms response times possible on local GPU — no network round-trip. |

### Recommended models (via Ollama)

| Use Case | Model | Min. Hardware | Est. tokens/sec |
|---|---|---|---|
| General tasks | `qwen2.5:72b-instruct-q4_K_M` | 2× RTX 4090 (48GB) | ~15 tok/s |
| Reasoning | `deepseek-r1:70b-q4_K_M` | 2× RTX 4090 (48GB) | ~12 tok/s |
| Coding | `qwen2.5-coder:32b-instruct-q4_K_M` | 1× RTX 4090 (24GB) | ~25 tok/s |
| Lightweight | `phi4-mini:3.8b` | CPU / 8GB RAM | ~40 tok/s |

### Hardware cost vs cloud

| Hardware | Upfront | Monthly (electricity) | Break-even vs Claude Sonnet |
|---|---|---|---|
| 1× RTX 4090 | ~$1,600 | ~$30–45 | ~50M tokens/month (~12–18 months) |
| 2× RTX 4090 | ~$3,200 | ~$60–90 | ~100M tokens/month (~12–18 months) |
| Cloud API only | $0 | pay-per-token | always cheaper below break-even |

**Rule of thumb:** invest in hardware when token volume is predictable and high. Use cloud cascade below the break-even.

---

## How Routing Decisions Are Made

Each provider adapter implements `getCapabilities()` which returns:

```ts
interface ProviderCapabilities {
  streaming: boolean
  maxContextTokens: number
  supportsFunctionCalling: boolean
  supportsVision: boolean
  supportsReasoning: boolean
  costPerInputToken: number   // USD per token
  costPerOutputToken: number  // USD per token
}
```

The router reads these capabilities + a `RoutingHint` on each request to select the tier:

```ts
interface RoutingHint {
  requiresFunctionCalling?: boolean
  requiresVision?: boolean
  requiresReasoning?: boolean
  estimatedInputTokens?: number
  privacySensitive?: boolean       // forces Tier 0 (self-hosted)
  maxCostPerInputToken?: number    // caller sets a budget ceiling
}
```

### Decision logic (simplified)

```ts
function selectProvider(hint: RoutingHint, providers: LLMProvider[]): LLMProvider {
  // Privacy override — must stay on-prem
  if (hint.privacySensitive) return selfHosted

  // Long context — only Gemini handles > 150K
  if (hint.estimatedInputTokens > 150_000) return gemini

  // Agentic / tool use — Claude is most reliable
  if (hint.requiresFunctionCalling) return claudeSonnet

  // Deep reasoning
  if (hint.requiresReasoning) return deepseekR1

  // Vision / multimodal
  if (hint.requiresVision) return gemini

  // Budget ceiling set by caller
  if (hint.maxCostPerInputToken) {
    return cheapestProviderBelow(hint.maxCostPerInputToken)
  }

  // Default: cheap budget tier
  return deepseekV3
}
```

---

## Cost Impact for DG

Using the estimates from `llm-pricing-analysis-dg.md`:

| Scenario | Claude only | Cascade (cloud) | Cascade + self-hosted |
|---|---|---|---|
| Internal team (5 devs) | $126/month | $53/month | ~$35/month |
| Small client (10 users) | $180/month | $35/month | ~$5/month (hardware amortised) |
| Medium client (50 users) | $1,200/month | $230/month | ~$50/month |
| 10 clients (mixed) | $14,300/month | $2,210/month | ~$800/month |
| **Annual (10 clients)** | **$171,600** | **$26,520** | **~$9,600** |

---

## Implementation Order

Cascade routing is built incrementally — each step is independently useful:

| Step | Deliverable | Cost impact |
|---|---|---|
| 1 | `StaticStrategy` (Claude default) | None — same as today, but through the abstraction |
| 2 | Add `DeepSeekAdapter` (extends OpenAIAdapter) | Immediate —60–80% of queries can shift to Tier 1 |
| 3 | `CascadeStrategy` (cheap → quality escalation) | Main cost saving unlocked |
| 4 | `LocalLLMAdapter` + Ollama setup | Tier 0 available for privacy + high-volume |
| 5 | `CapabilityStrategy` (routing by task type) | Fine-grained routing, avoids over-escalation |

Step 2 is the **highest-leverage single action** in the entire project — DeepSeek V3 extends `OpenAIAdapter` with just a base URL override, and shifts the majority of tokens to a provider that is ~20× cheaper on output.

---

## Related Documents

- [docs/architecture/adr-routing-strategy.md](adr-routing-strategy.md) — decision record
- [docs/architecture/cli-ui-llm-implementation-plan.md](cli-ui-llm-implementation-plan.md) — Phase 5 router implementation
- [docs/architecture/adr-local-runtime.md](adr-local-runtime.md) — Ollama decision
- [docs/research/llm-pricing-analysis-dg.md](../research/llm-pricing-analysis-dg.md) — full cost model
- [docs/research/llm-pricing.md](../research/llm-pricing.md) — raw pricing data
- [issues/architecture/model-routing-strategy.md](../../issues/architecture/model-routing-strategy.md)
