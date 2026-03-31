---
title: "Master Plan: LLM Architecture"
category: "project"
lastUpdated: "2026-03-07"
status: "active"
---

# Master Plan: LLM Architecture

## Purpose

A consolidated view of what is done, what is ready to build, what is still missing, and what the implementation order is. Single source of truth for project state.

---

## Current State

### Research Phase — COMPLETE

| Document | Status |
|---|---|
| `docs/PRD.md` | Done — routing strategy + hardware resolved |
| `docs/research/llm-landscape.md` | Done — all major models documented |
| `docs/research/llm-pricing.md` | Done — trade-off matrix + routing cost scenarios |
| `docs/research/llm-optimization-methods.md` | Done — 11 categories with sources |
| `docs/llm-capability-analysis.md` | Done — capability matrix per provider + routing guide |
| `docs/architecture/cli-ui-llm-implementation-plan.md` | Done — Phases 1–7 with code shapes and deliverables |
| `.deepgruble/janitors/llm-papers.ts` | Done — running, fetches top 20 LLM papers from arXiv |

### Open Decisions — 1 remaining

| Decision | Status | Location |
|---|---|---|
| Routing strategy | **Resolved** — cascade + capability-based | PRD § Routing Strategy |
| Local runtime | **Resolved** — Ollama (OpenAI-compatible API) | PRD § Local Backend |
| Local SLM hardware minimum | **Resolved** — RTX 4090 for 70B; RTX 3060 for 7B | PRD § Local Backend |
| Janitor pipeline cadence + delivery | **Open** | `issues/janitors/janitor-pipeline-cadence.md` |

### Code — NOT STARTED

Zero code exists. `src/` does not exist yet.

---

## What Is Missing

### 1. Docs — Gaps

| Gap | Impact | Status |
|---|---|---|
| `llm-capability-analysis.md` is at `docs/` root instead of `docs/research/` | Inconsistent structure | **Fixed** — moved to `docs/research/` |
| `llm-capability-analysis.md` has broken links (old issue paths before restructure) | Broken references | **Fixed** — all links updated |
| No ADR for routing strategy | Decision not formally recorded | **Fixed** — `docs/architecture/adr-routing-strategy.md` |
| No ADR for local runtime choice (Ollama) | Decision not formally recorded | **Fixed** — `docs/architecture/adr-local-runtime.md` |
| Implementation plan missing DeepSeek and Grok adapters | Plan only covered Claude, Gemini, OpenAI, Local | **Fixed** — added to Phase 2 |
| `ProviderCapabilities` missing `costPerInputToken`, `costPerOutputToken`, `supportsReasoning` | Cascade router needs these fields | **Fixed** — updated in implementation plan |

### 2. Infrastructure — Not Done

| Item | Needed For | Status |
|---|---|---|
| GitHub repo created | Everything | Not created |
| Target codebase identified | Phase 6 (CLI integration) | Unknown — which DG codebase does `src/llm/` plug into? |
| Janitor cadence decided | News + Paper janitors | Open |

### 3. Code — Everything

| Phase | Deliverable | Blocked by |
|---|---|---|
| **Phase 1** | `src/llm/interface.ts` | Nothing — start here |
| **Phase 2** | `src/llm/adapters/claude.ts` | Phase 1 |
| **Phase 2** | `src/llm/adapters/gemini.ts` | Phase 1 |
| **Phase 2** | `src/llm/adapters/openai.ts` | Phase 1 |
| **Phase 2** | `src/llm/adapters/local.ts` | Phase 1 + Ollama running |
| **Phase 2** | `src/llm/adapters/deepseek.ts` | Phase 1 (OpenAI-compatible — reuse OpenAI adapter) |
| **Phase 3** | `src/llm/registry.ts` | Phase 2 |
| **Phase 4** | `src/llm/config.ts` | Phase 3 |
| **Phase 5** | `src/llm/router.ts` (StaticStrategy first) | Phase 4 |
| **Phase 5** | `src/llm/router.ts` (CascadeStrategy) | Phase 5 StaticStrategy |
| **Phase 5** | `src/llm/router.ts` (CapabilityStrategy) | Phase 5 StaticStrategy |
| **Phase 6** | CLI integration | Phase 4 + target codebase identified |
| **Phase 7** | Tests (unit + integration) | Phase 2–4 |

---

## Implementation Order

```
Now
 │
 ├─ [TODAY] Fix docs/llm-capability-analysis.md links + move to docs/research/
 ├─ [TODAY] Create GitHub repo
 ├─ [TODAY] Identify target codebase for Phase 6
 ├─ [TODAY] Decide janitor cadence (last open question)
 │
 ├─ [Phase 1] src/llm/interface.ts ← UNBLOCKED, start here
 │           Add: costPerInputToken, costPerOutputToken, supportsReasoning to ProviderCapabilities
 │
 ├─ [Phase 2] src/llm/adapters/claude.ts   ← migrates existing Claude usage
 │            src/llm/adapters/openai.ts   ← also covers DeepSeek (OpenAI-compatible)
 │            src/llm/adapters/local.ts    ← Ollama via OpenAI-compatible API
 │            src/llm/adapters/gemini.ts
 │
 ├─ [Phase 3] src/llm/registry.ts
 ├─ [Phase 4] src/llm/config.ts (flag > env > file > default)
 │
 ├─ [Phase 5] src/llm/router.ts
 │            StaticStrategy first (Claude default, same behavior as today)
 │            CascadeStrategy (cheap → expensive escalation)
 │            CapabilityStrategy (route by task type using ProviderCapabilities)
 │
 ├─ [Phase 6] CLI integration (inject provider at startup)
 └─ [Phase 7] Tests
```

---

## Routing Strategy Summary (Decided)

```
Default:   Claude Sonnet 4.6         ($3.00/M input)
├── Long context > 150K tokens    → Gemini 3.1 Pro   ($2.00/M, 1M ctx)
├── Pure reasoning / math         → DeepSeek R1      ($0.55/M) or Claude Opus ($5/M)
├── Speed-sensitive < 1s          → Gemini Flash     ($0.075/M)
├── Cost reduction / simple tasks → DeepSeek V3      ($0.14/M) or Grok 4.1 Fast ($0.20/M)
└── Privacy-sensitive / offline   → Local Ollama     (~$0 marginal)
```

Expected cost reduction vs Claude Sonnet exclusively: **70–90%**

---

## Related Documents

- [`docs/PRD.md`](PRD.md) — goals, resolved decisions, open questions
- [`docs/architecture/cli-ui-llm-implementation-plan.md`](architecture/cli-ui-llm-implementation-plan.md) — full phase plan
- [`docs/research/llm-capability-analysis.md`](research/llm-capability-analysis.md) — capability matrix per provider
- [`docs/research/llm-landscape.md`](research/llm-landscape.md) — all models and characteristics
- [`docs/research/llm-pricing.md`](research/llm-pricing.md) — pricing trade-off matrix
- [`docs/research/llm-optimization-methods.md`](research/llm-optimization-methods.md) — optimization reference
