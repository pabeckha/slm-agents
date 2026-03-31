---
title: "ADR: Model Routing Strategy"
category: "architecture"
lastUpdated: "2026-03-07"
status: "active"
---

# ADR: Model Routing Strategy

## Status

**Accepted** — 2026-03-07

---

## Context

The unified LLM interface supports multiple backends. Requests must be routed to the right backend based on task type, cost, and latency requirements. Four strategies were evaluated:

- **Static** — always use one configured provider
- **Rule-based** — explicit task-type → provider mapping
- **Cost-based** — always route to the cheapest capable provider
- **Capability-based** — route by what the task requires (vision, reasoning, long context)
- **Cascade** — try a cheaper provider first, escalate to a more capable one if needed

Pricing research showed a 600× price gap between cheapest and most expensive providers at equivalent quality for many tasks. Capability analysis showed that no single provider is best across all task types.

---

## Decision

**Cascade + capability-based routing**, implemented in priority order:

```
Default:   Claude Sonnet 4.6         ($3.00/M input)
├── Long context > 150K tokens    → Gemini 3.1 Pro   ($2.00/M, 1M ctx)
├── Pure reasoning / math         → DeepSeek R1      ($0.55/M)
├── Speed-sensitive < 1s          → Gemini Flash     ($0.075/M)
├── Cost reduction / simple tasks → DeepSeek V3      ($0.14/M)
└── Privacy-sensitive / offline   → Local Ollama     (~$0 marginal)
```

Implementation starts with `StaticStrategy` (Claude default — same behavior as today), then adds `CascadeStrategy` and `CapabilityStrategy` incrementally.

---

## Consequences

**Positive:**
- Expected 70–90% cost reduction vs using Claude Sonnet exclusively
- No single provider is a hard dependency — swapping is config-only
- `ProviderCapabilities` interface exposes `costPerInputToken`, `costPerOutputToken`, `supportsReasoning` to enable automated routing decisions

**Negative:**
- More complexity than a static strategy — requires testing each routing path
- Requires `ProviderCapabilities` to be accurate and kept up to date per model
- Cascade adds latency if the first provider fails (fallback round-trip)

---

## Alternatives Considered

| Strategy | Rejected because |
|---|---|
| Static only | No cost reduction; single point of failure |
| Pure cost-based | Ignores capability requirements; low-quality output on complex tasks |
| Rule-based only | Brittle; requires manual updates as providers evolve |

---

## Related Documents

- [PRD.md](../PRD.md) — § Routing Strategy
- [docs/research/llm-pricing.md](../research/llm-pricing.md) — pricing trade-off matrix
- [docs/research/llm-capability-analysis.md](../research/llm-capability-analysis.md) — capability matrix
- [docs/architecture/cli-ui-llm-implementation-plan.md](cli-ui-llm-implementation-plan.md) — Phase 5 router
- [issues/architecture/model-routing-strategy.md](../../issues/architecture/model-routing-strategy.md)
