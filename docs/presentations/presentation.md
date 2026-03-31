---
title: "Flexible LLM Architecture — Strategic Recommendation"
category: "project"
lastUpdated: "2026-03-07"
status: "active"
---

# Flexible LLM Architecture
## Strategic Recommendation for DeepGruble

**Prepared by:** LLM Architecture Initiative
**Date:** March 2026
**Confidential — Internal Use Only**

---

# Executive Summary

> **DeepGruble is currently paying 20× more than necessary for LLM infrastructure, and a single vendor dependency threatens the viability of unanswerable.ai as a scalable product. Implementing a provider-agnostic architecture with cascade routing will reduce LLM costs by up to 94%, eliminate vendor lock-in, and increase gross margin per client from negative to 54–88%.**

## The Three Findings

| # | Finding | Implication |
|---|---|---|
| 1 | **Single-vendor dependency creates existential product risk** | Claude price change or outage directly disrupts unanswerable.ai |
| 2 | **Current cost structure makes the product unprofitable at scale** | A 50-user client costs $1,200/month in LLM fees — more than a viable platform fee |
| 3 | **A 7-phase technical solution exists and is ready to build** | Phase 1 is unblocked today; the highest-leverage step (DeepSeek adapter) is ~10 lines of code |

## The Recommendation

Implement a **3-tier cascade routing architecture** (self-hosted → budget cloud → quality cloud) that:
- Routes 60% of queries to models costing $0.14/M tokens
- Reserves Claude for the 30% of tasks where it is genuinely best-in-class
- Self-hosts the remainder for privacy-sensitive or high-volume workloads

**Expected outcome at 10 clients:** Annual LLM cost drops from **$171,600 → $9,600** (-94%).

---

# 1. The Situation — Where DeepGruble Stands Today

## 1.1 What DeepGruble Has Built

DeepGruble has developed **unanswerable.ai** — an Autonomous Intelligence Platform that gives any organisation its own AI nervous system:

- **Granite** — structured company knowledge accessible to any LLM
- **MCP layer** — standardised protocol connecting LLMs to internal tools and data
- **Governance** — behavioural rules enforced across all AI interactions
- **Janitors** — automated agents that keep knowledge fresh and relevant

The product is designed to be **LLM-agnostic by philosophy** — the whole value proposition is that organisations can move between providers without losing their nervous system.

## 1.2 The Contradiction

**The product promises LLM independence. The infrastructure delivers LLM dependency.**

| Dimension | Current state | Target state |
|---|---|---|
| Provider | Claude only | Claude + Gemini + OpenAI + DeepSeek + Self-hosted |
| Switching | Requires code changes | Config flag only |
| Cost per M output tokens | $15.00 (Claude Sonnet) | $0.28 (DeepSeek V3) — 54× cheaper |
| Data residency | Cloud only | On-premises option available |
| Resilience | Single point of failure | Provider failover built-in |

---

# 2. The Problem — Three Distinct Risks

> *The current architecture creates three independent risks, each sufficient on its own to justify immediate action.*

## 2.1 Commercial Risk — Unprofitable Unit Economics

At current LLM costs, unanswerable.ai **cannot be priced profitably** for medium and large clients:

| Client size | LLM cost/month (Claude only) | Viable platform fee | P&L |
|---|---|---|---|
| Small (10 users) | $180 | $300 | +$120 ✓ |
| Medium (50 users) | **$1,200** | $800 | **−$400 ✗** |
| Large (200 users) | **$6,000** | $2,500 | **−$3,500 ✗** |

**Any client above ~25 users destroys margin under the current setup.**

## 2.2 Strategic Risk — Vendor Lock-in

Anthropic controls DeepGruble's cost structure, product availability, and competitive positioning:

- A **10% Claude price increase** passes directly to DG margins — no buffer
- A **Claude API outage** takes down unanswerable.ai entirely
- Anthropic can **change terms** (rate limits, acceptable use, data handling) with 30 days' notice
- Competing frameworks that offer multi-provider support gain a **structural sales advantage**

## 2.3 Capability Risk — Leaving Performance on the Table

No single provider is best for all task types. Routing everything through Claude means:

| Task type | Best provider | Currently used | Quality gap |
|---|---|---|---|
| Long context (>150K tokens) | Gemini 3.1 Pro (1M ctx) | Claude (200K max) | Context truncated |
| Reasoning / math | DeepSeek R1 | Claude Opus ($5/M) | 9× overpaying |
| Speed-sensitive (<1s) | Gemini Flash ($0.075/M) | Claude Sonnet ($3/M) | 40× overpaying |
| Privacy-sensitive | Self-hosted (free) | Cloud API | Data sovereignty risk |

---

# 3. The Opportunity — What Becomes Possible

## 3.1 Cost Opportunity

The LLM market has undergone a structural shift. Frontier-quality models are now available at 1–2% of the cost of Claude Sonnet:

| Provider | Output cost/M | vs Claude Sonnet | Quality tier |
|---|---|---|---|
| Claude Sonnet 4.6 | $15.00 | baseline | ★★★★★ |
| Gemini 3.1 Pro | $12.00 | −20% | ★★★★★ |
| DeepSeek V3 | $0.28 | **−98%** | ★★★★☆ |
| Grok 4.1 Fast | $0.50 | **−97%** | ★★★★☆ |
| Self-hosted Qwen 72B | ~$0 | **−100%** | ★★★★☆ |

> **The key insight: output tokens cost 3–10× more than input tokens, and that is where 70%+ of DG's spend sits.**

## 3.2 Product Opportunity

A provider-agnostic architecture is itself a **product differentiator**:

- Clients with **data residency requirements** (finance, healthcare, legal) can use self-hosted tier — currently impossible
- Clients in **Google ecosystems** can use Gemini natively — better integration, lower cost
- DG can offer **SLA-backed failover** — if Claude is down, route to Gemini automatically
- The architecture makes unanswerable.ai **future-proof** — new providers plug in without rebuilding

## 3.3 Competitive Opportunity

The LLM infrastructure market is moving fast. Organisations that build provider abstraction now will not need to rebuild when:
- A new open-source model outperforms Claude (already happening with DeepSeek R1 on reasoning)
- Anthropic raises prices or tightens terms
- A client specifically requires a non-Claude provider

---

# 4. The Solution — A 3-Tier Architecture

## 4.1 Architecture Overview

The solution has **three components** that work together:

```
┌─────────────────────────────────────────────────────┐
│                   unanswerable.ai                   │
│              (Balthazar / CLI / Agents)              │
└──────────────────────┬──────────────────────────────┘
                       │ calls
                       ▼
┌─────────────────────────────────────────────────────┐
│              Unified LLM Interface                   │  ← Component 1
│     complete() · stream() · getCapabilities()        │
└──────────────────────┬──────────────────────────────┘
                       │ routes via
                       ▼
┌─────────────────────────────────────────────────────┐
│                 Cascade Router                       │  ← Component 2
│   privacy? → self-hosted                            │
│   agentic?  → Claude                               │
│   reasoning? → DeepSeek R1                         │
│   default   → DeepSeek V3                          │
└──────────────────────┬──────────────────────────────┘
                       │ dispatches to
                       ▼
┌───────────┬───────────┬───────────┬─────────────────┐
│  Tier 0   │  Tier 1   │  Tier 2   │    Tier 3–4     │  ← Component 3
│Self-hosted│  Budget   │  Quality  │  Specialised    │
│  Ollama   │ DeepSeek  │  Claude   │Gemini/Opus/R1   │
│   ~$0     │ $0.14/M   │  $3.00/M  │ $0.55–$5.00/M   │
└───────────┴───────────┴───────────┴─────────────────┘
```

## 4.2 Component 1 — Unified LLM Interface

A single TypeScript interface that **all providers implement**. The rest of the codebase never imports a provider SDK directly.

```ts
interface LLMProvider {
  complete(messages: Message[], options?: CompletionOptions): Promise<CompletionResult>
  stream(messages: Message[], options?: CompletionOptions): AsyncIterable<string>
  getCapabilities(): ProviderCapabilities  // cost, context, features
}
```

**Impact:** Adding a new provider = implement one interface. No changes to Balthazar, the CLI, or any agent logic.

## 4.3 Component 2 — Cascade Router

Routes each request to the optimal provider based on task requirements and cost constraints:

| Routing signal | Provider selected | Rationale |
|---|---|---|
| `privacySensitive: true` | Self-hosted (Ollama) | Data never leaves DG infrastructure |
| Context > 150K tokens | Gemini 3.1 Pro | Only provider with 1M token window |
| `requiresFunctionCalling: true` | Claude Sonnet 4.6 | Most reliable tool-use in production |
| `requiresReasoning: true` | DeepSeek R1 | Frontier reasoning at $0.55/M vs $5.00/M |
| Vision / multimodal input | Gemini 3.1 Pro | Best-in-class multimodal |
| Everything else | DeepSeek V3 | Near-frontier quality at $0.14/M input |

## 4.4 Component 3 — Provider Adapters

Six adapters, three are near-zero effort:

| Adapter | Effort | Notes |
|---|---|---|
| `ClaudeAdapter` | Medium | Wrap existing Claude usage in the interface |
| `GeminiAdapter` | Medium | Map `generateContent` to `complete()` |
| `OpenAIAdapter` | Medium | Covers OpenAI natively |
| `DeepSeekAdapter` | **Minimal** | Extends OpenAIAdapter — just base URL + key |
| `GrokAdapter` | **Minimal** | Extends OpenAIAdapter — just base URL + key |
| `LocalLLMAdapter` | **Minimal** | Ollama is OpenAI-compatible — same as above |

> **DeepSeek, Grok, and Ollama all speak the OpenAI API format.** Three of the six adapters are ~10 lines each.

---

# 5. The Business Case

## 5.1 Cost Model — Internal Team

**Team:** 5 people, 3 active developers, ~18M input + 4.8M output tokens/month

| Scenario | Monthly cost | Annual cost | vs. today |
|---|---|---|---|
| Today — Claude only | $126 | $1,512 | baseline |
| Cascade (cloud only) | $53 | $636 | **−58%** |
| Cascade + self-hosted | $35 | $420 | **−72%** |

## 5.2 Cost Model — unanswerable.ai Product

**Per client, per month:**

| Client size | Claude only | Cascade (cloud) | Cascade + self-hosted |
|---|---|---|---|
| Small — 10 users | $180 | $35 | ~$5 |
| Medium — 50 users | $1,200 | $230 | ~$50 |
| Large — 200 users | $6,000 | $1,150 | ~$250 |

## 5.3 Gross Margin Impact

With cascade routing, unanswerable.ai becomes **profitable across all client sizes**:

| Client size | Platform fee | LLM cost (cascade) | Gross margin |
|---|---|---|---|
| Small (10 users) | $300/mo | $35/mo | **$265/mo (88%)** |
| Medium (50 users) | $800/mo | $230/mo | **$570/mo (71%)** |
| Large (200 users) | $2,500/mo | $1,150/mo | **$1,350/mo (54%)** |

## 5.4 At Scale — 10 Clients

| Scenario | Annual LLM cost | Annual saving vs. today |
|---|---|---|
| Claude only | $171,600 | — |
| Cascade (cloud) | $26,520 | **$145,080** |
| Cascade + self-hosted | ~$9,600 | **$162,000** |

## 5.5 Self-Hosted Break-Even

| Hardware investment | Monthly overhead | Break-even volume | Break-even timeline |
|---|---|---|---|
| 2× RTX 4090 ($3,200) | ~$75/mo electricity | ~100M tokens/month | ~4 clients, ~12–18 months |

**Self-hosting is the right choice from ~4 clients onward.** Below that, cloud cascade is simpler and still 82% cheaper than Claude-only.

---

# 6. The Roadmap — 7 Phases, Fully Defined

> *The implementation is phased so each step delivers independent value. The system works end-to-end after Phase 4.*

## 6.1 Phase Overview

| Phase | Deliverable | Value unlocked | Dependency |
|---|---|---|---|
| **1** | `src/llm/interface.ts` | Foundation — unblocks all other phases | None |
| **2** | Provider adapters (6×) | All providers available | Phase 1 |
| **3** | Registry + factory | Single entry point for provider creation | Phase 2 |
| **4** | Config layer | Provider selectable via flag / env / file | Phase 3 |
| **5** | Router (cascade) | Cost savings activated | Phase 4 |
| **6** | CLI integration | End-to-end working system | Phase 4 |
| **7** | Tests | Production-grade reliability | Phases 2–5 |

## 6.2 Implementation Sequence

```
Week 1
  └─ Phase 1: interface.ts + shared types
  └─ Phase 2a: ClaudeAdapter (migrate existing usage)

Week 2
  └─ Phase 2b: DeepSeekAdapter + GrokAdapter (trivial — OpenAI-compatible)
  └─ Phase 3: Registry + factory
  └─ Phase 4: Config layer (flag > env > file > default)

Week 3
  └─ Phase 5: StaticStrategy (Claude default, end-to-end working)
  └─ Phase 6: CLI integration

Week 4
  └─ Phase 2c: GeminiAdapter + LocalLLMAdapter (Ollama)
  └─ Phase 5b: CascadeStrategy (cost savings fully active)
  └─ Phase 7: Tests

Week 5+
  └─ Phase 5c: CapabilityStrategy (fine-grained routing)
  └─ Local infrastructure setup (Ollama + first model)
```

## 6.3 Critical Path

The single critical path item is **Phase 1 → Phase 2a → Phase 4 → Phase 6** (interface → Claude adapter → config → CLI). This can be done in one week and delivers a working system that is behaviourally identical to today but built on the abstraction — every subsequent phase adds capability without risk.

---

# 7. Risks and Mitigations

> *Three categories of risk, all manageable.*

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | **Quality degradation** — DeepSeek V3 underperforms on a task class previously handled by Claude | Medium | Medium | Routing hints let callers opt out of budget tier per request; rollback is one config change |
| 2 | **Self-hosted ops burden** — Ollama/GPU management requires ongoing maintenance | Medium | Low | Start with cloud cascade only; add self-hosted when volume justifies it |
| 3 | **DeepSeek data privacy** — Chinese-operated API may raise concerns for some clients | Low–Medium | High for regulated clients | Solved by self-hosted tier — privacy-sensitive traffic never reaches DeepSeek |
| 4 | **Adapter maintenance** — Provider APIs change | Low | Low | Each adapter is isolated; a change to the Gemini SDK touches only `gemini.ts` |
| 5 | **Target codebase integration** — unknown until a specific DG repo is identified | High | Medium | Phase 6 is deliberately last; Phases 1–5 are codebase-agnostic |

---

# 8. Recommendation and Next Steps

## 8.1 The Recommendation

**Proceed immediately with the 7-phase implementation.**

The business case is unambiguous:
- The architecture makes unanswerable.ai **viable as a commercial product**
- The highest-leverage steps have **near-zero implementation risk**
- Delay has a direct cost — every month at Claude-only pricing at 10 clients = **$14,300 in avoidable spend**

## 8.2 Immediate Next Steps (This Week)

| Action | Owner | Why now |
|---|---|---|
| **Create GitHub repo** | Engineering | Unblocks all code work |
| **Identify target codebase** | Engineering / CEO | Required for Phase 6 CLI integration |
| **Start Phase 1** (`interface.ts`) | Engineering | Fully unblocked; unblocks everything else |
| **Decide janitor cadence** | Team | Last open architecture question |

## 8.3 One-Month Target

By end of April 2026, the system should:
- Route all internal DG traffic through the abstraction (Claude still default — zero behaviour change)
- Have DeepSeek V3 and Grok 4.1 Fast adapters live and tested
- Have cascade routing active for internal usage — capturing the **58% cost reduction**

## 8.4 Three-Month Target

By end of May 2026, the system should:
- Have all 6 adapters implemented and tested
- Have Ollama running on DG infrastructure with Qwen 72B
- Be ready to serve the first unanswerable.ai client through the multi-provider stack

---

# Appendix

## A. Document Map

| Document | Purpose |
|---|---|
| [`docs/PRD.md`](PRD.md) | Goals, decisions, open questions |
| [`docs/architecture/cli-ui-llm-implementation-plan.md`](architecture/cli-ui-llm-implementation-plan.md) | Full 7-phase plan with code shapes |
| [`docs/architecture/cascade-routing.md`](architecture/cascade-routing.md) | Cascade routing explained with decision logic |
| [`docs/architecture/adr-routing-strategy.md`](architecture/adr-routing-strategy.md) | Decision record: why cascade was chosen |
| [`docs/architecture/adr-local-runtime.md`](architecture/adr-local-runtime.md) | Decision record: why Ollama was chosen |
| [`docs/research/llm-landscape.md`](research/llm-landscape.md) | All major models, capabilities, benchmarks |
| [`docs/research/llm-pricing.md`](research/llm-pricing.md) | Raw pricing data across 30+ models |
| [`docs/research/llm-pricing-analysis-dg.md`](research/llm-pricing-analysis-dg.md) | DG-specific cost model and margin analysis |
| [`docs/research/llm-optimization-methods.md`](research/llm-optimization-methods.md) | Technical optimisation reference |
| [`docs/research/llm-capability-analysis.md`](research/llm-capability-analysis.md) | Per-provider capability matrix |
| [`docs/master-plan.md`](master-plan.md) | Project state: done, missing, implementation order |

## B. Key Numbers at a Glance

| Metric | Value |
|---|---|
| Current LLM cost (Claude only, 10 clients/yr) | $171,600 |
| Projected cost (cascade + self-hosted, 10 clients/yr) | $9,600 |
| **Total annual saving** | **$162,000 (−94%)** |
| Medium client margin (Claude only) | **−50%** |
| Medium client margin (cascade) | **+71%** |
| Phase 1 effort | ~1 day |
| DeepSeek adapter effort | ~2 hours |
| Break-even for self-hosting | ~4 clients |
| Months to full implementation | ~2 months |

## C. Glossary

| Term | Definition |
|---|---|
| **Cascade routing** | Route requests through tiers cheapest-first, escalate only when needed |
| **Provider adapter** | A class that wraps one LLM provider's SDK and exposes the unified interface |
| **Unified LLM interface** | The single TypeScript interface all adapters implement |
| **Tier 0** | Self-hosted models via Ollama — no cloud, no token cost |
| **Tier 1** | Budget cloud providers (DeepSeek V3, Grok 4.1 Fast) |
| **Tier 2** | Quality cloud (Claude Sonnet 4.6) |
| **Tier 3–4** | Specialised: reasoning (DeepSeek R1), long context (Gemini), premium (Claude Opus) |
| **Granite** | DeepGruble's standard for structured, AI-readable company documentation |
| **MCP** | Model Context Protocol — connects LLMs to external tools and data |
| **unanswerable.ai** | DeepGruble's Autonomous Intelligence Platform product |
| **Balthazar** | Internal codename for the unanswerable.ai engine |
