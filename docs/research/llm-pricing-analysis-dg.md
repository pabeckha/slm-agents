---
title: "LLM Pricing Analysis — DeepGruble"
category: "project"
lastUpdated: "2026-03-07"
status: "active"
---

# LLM Pricing Analysis — DeepGruble

## Purpose

Estimate DeepGruble's actual LLM costs across two usage contexts — **internal team tooling** and **unanswerable.ai product delivery** — and model the cost impact of implementing the cascade routing strategy.

---

## Assumptions

| Variable | Value | Basis |
|---|---|---|
| Team size | 5 people (3 active developers + PM + CEO) | `team.md` |
| Active developer-days/month | 3 devs × 20 days = **60 dev-days** | Standard working month |
| Tokens per developer per day (input) | ~300K | Heavy Claude Code sessions: 4–6 sessions × ~50–70K tokens context |
| Tokens per developer per day (output) | ~80K | Responses, code generation, edits |
| PR reviews via Gemini Code Assist | ~50 PRs/month × 8K tokens | Gemini handles this; billed via GCP quota |
| Unanswerable.ai agentic query (input) | ~10K tokens | System prompt + Granite docs + user message |
| Unanswerable.ai agentic query (output) | ~2K tokens | Agent response |
| Janitor pipeline (LLM analysis pass) | ~500K tokens/month | If LLM summarizes results, otherwise ~$0 |

---

## Part 1: Internal Team Usage

### 1.1 Current State — Claude Only

All developer LLM usage routes through Claude Sonnet 4.6 today.

| Metric | Value |
|---|---|
| Monthly input tokens | 60 dev-days × 300K = **18M tokens** |
| Monthly output tokens | 60 dev-days × 80K = **4.8M tokens** |
| Claude Sonnet 4.6 input cost | 18M × $3.00/M = **$54.00** |
| Claude Sonnet 4.6 output cost | 4.8M × $15.00/M = **$72.00** |
| **Total/month (current)** | | **$126/month** |

> Note: Gemini CLI is on a GCP quota plan — ~free for the team's usage volume, not modelled here.

### 1.2 Post-Implementation — Cascade Routing

After implementing the routing strategy, tasks are distributed across providers:

| Tier | % of queries | Provider | Input | Output | Monthly cost |
|---|---|---|---|---|---|
| Simple / routine | 50% | DeepSeek V3 | 9M × $0.14 = $1.26 | 2.4M × $0.28 = $0.67 | **$1.93** |
| Coding / agentic | 35% | Claude Sonnet 4.6 | 6.3M × $3.00 = $18.90 | 1.68M × $15.00 = $25.20 | **$44.10** |
| Complex reasoning | 10% | DeepSeek R1 | 1.8M × $0.55 = $0.99 | 0.48M × $2.19 = $1.05 | **$2.04** |
| Long context (>150K) | 5% | Gemini 3.1 Pro | 0.9M × $2.00 = $1.80 | 0.24M × $12.00 = $2.88 | **$4.68** |
| **Total/month** | | | | | **$52.75** |

### 1.3 Internal Savings Summary

| Scenario | Monthly cost | vs. current |
|---|---|---|
| Current (Claude only) | $126 | baseline |
| Post-implementation (cascade) | ~$53 | **−58%** |
| Aggressive (DeepSeek V3 for 80%) | ~$20 | **−84%** |

**Estimated annual saving from cascade routing on internal usage: ~$880/year**

---

## Part 2: unanswerable.ai Product Usage

This is the more significant cost driver as DG scales to multiple clients.

### 2.1 Per-Client Monthly Token Estimates

| Client Size | Users | Queries/user/day | Working days | Total queries/month | Input tokens/month | Output tokens/month |
|---|---|---|---|---|---|---|
| **Small** | 10 | 15 | 20 | 3,000 | 30M | 6M |
| **Medium** | 50 | 20 | 20 | 20,000 | 200M | 40M |
| **Large** | 200 | 25 | 20 | 100,000 | 1,000M | 200M |

### 2.2 Per-Client Monthly Cost — Provider Comparison

#### Small Client (10 users)

| Provider | Input | Output | **Total/month** |
|---|---|---|---|
| Claude Sonnet 4.6 only | 30M × $3.00 = $90 | 6M × $15.00 = $90 | **$180** |
| Gemini 3.1 Pro only | 30M × $2.00 = $60 | 6M × $12.00 = $72 | **$132** |
| DeepSeek V3 only | 30M × $0.14 = $4.20 | 6M × $0.28 = $1.68 | **$5.88** |
| **Cascade (recommended)** | mixed | mixed | **~$35** |

#### Medium Client (50 users)

| Provider | Input | Output | **Total/month** |
|---|---|---|---|
| Claude Sonnet 4.6 only | 200M × $3.00 = $600 | 40M × $15.00 = $600 | **$1,200** |
| Gemini 3.1 Pro only | 200M × $2.00 = $400 | 40M × $12.00 = $480 | **$880** |
| DeepSeek V3 only | 200M × $0.14 = $28 | 40M × $0.28 = $11.20 | **$39.20** |
| **Cascade (recommended)** | mixed | mixed | **~$230** |

#### Large Client (200 users)

| Provider | Input | Output | **Total/month** |
|---|---|---|---|
| Claude Sonnet 4.6 only | 1,000M × $3.00 = $3,000 | 200M × $15.00 = $3,000 | **$6,000** |
| Gemini 3.1 Pro only | 1,000M × $2.00 = $2,000 | 200M × $12.00 = $2,400 | **$4,400** |
| DeepSeek V3 only | 1,000M × $0.14 = $140 | 200M × $0.28 = $56 | **$196** |
| **Cascade (recommended)** | mixed | mixed | **~$1,100** |

### 2.3 Cascade Breakdown (per client)

The cascade model routes ~60% of queries to cheap providers, 30% to Claude, 10% to reasoning:

| Tier | % | Provider | Small client | Medium client | Large client |
|---|---|---|---|---|---|
| Routine agent queries | 60% | DeepSeek V3 | $3.53 | $23.50 | $118 |
| Coding / complex agentic | 30% | Claude Sonnet | $16.20 | $108 | $540 |
| Deep reasoning | 10% | DeepSeek R1 | $1.70 | $11.50 | $57 |
| Long context queries | per need | Gemini 3.1 Pro | ~$13 | ~$87 | ~$435 |
| **Total/month** | | | **~$35** | **~$230** | **~$1,150** |

---

## Part 3: DG Business Model Impact

The routing strategy determines whether unanswerable.ai can be priced profitably.

### 3.1 Margin Analysis per Client Tier

Assuming DG charges a platform fee per client (hypothetical pricing):

| Client size | LLM cost (Claude only) | LLM cost (cascade) | Platform fee (est.) | Margin (cascade) |
|---|---|---|---|---|
| Small (10 users) | $180/mo | $35/mo | $300/mo | **$265/mo (88%)** |
| Medium (50 users) | $1,200/mo | $230/mo | $800/mo | **$570/mo (71%)** |
| Large (200 users) | $6,000/mo | $1,150/mo | $2,500/mo | **$1,350/mo (54%)** |

**Without cascade routing, a medium client at $800/month platform fee would lose $400/month on LLM costs alone.**

### 3.2 DG at Scale — 10 Clients

Assuming a mix of 5 small + 3 medium + 2 large clients:

| Scenario | Total LLM cost/month | Total LLM cost/year |
|---|---|---|
| Claude only (current approach) | $14,300 | **$171,600** |
| Cascade routing | $2,210 | **$26,520** |
| **Annual saving** | | **$145,000** |

---

## Part 4: Self-Hosted Threshold

At what client scale does self-hosting become worth it?

| Scale | Monthly API cost (cascade) | Hardware cost (amortized) | Electricity | Self-host total | Break-even |
|---|---|---|---|---|---|
| 5 clients (mixed) | ~$1,100 | $267 (2× RTX 4090 over 12 mo) | $45 | **$312** | **Yes — API is 3.5× more expensive** |
| 3 clients | ~$660 | $267 | $45 | **$312** | Borderline |
| 1 client | ~$230 | $267 | $45 | **$312** | No — cloud API cheaper |

**Self-hosting is justified at ~4+ clients.** Below that, cloud cascade routing is cheaper and simpler.

---

## Part 5: Recommendations

### Short term (0–5 clients)
- Use **cascade routing** via cloud APIs
- Default: DeepSeek V3 for routine, Claude Sonnet for agentic/coding
- Estimated blended rate: **~$0.75/M tokens effective** vs $9/M (Claude only)

### Medium term (5–15 clients)
- Introduce **self-hosted Qwen 3 72B or DeepSeek-V3 distill** via Ollama for routine queries
- Keep Claude for agentic tasks where reliability is critical
- Hybrid model: local for volume, cloud for quality tier

### Long term (15+ clients)
- Full self-hosted cluster for base tier
- Cloud APIs reserved for frontier tasks (Claude, Gemini)
- Target: **>80% of tokens served locally**

### Immediate action
- Implement cascade routing **before** first paying client — the margin impact is too large to delay
- DeepSeek V3 adapter is lowest effort (extends OpenAIAdapter, just base URL)

---

## Related Documents

- [docs/research/llm-pricing.md](llm-pricing.md) — raw pricing data and trade-off matrix
- [docs/architecture/adr-routing-strategy.md](../architecture/adr-routing-strategy.md) — routing strategy decision
- [docs/architecture/cli-ui-llm-implementation-plan.md](../architecture/cli-ui-llm-implementation-plan.md) — implementation plan
- [docs/PRD.md](../PRD.md) — project goals

---

## Sources

- [LLM API Pricing 2026 — pricepertoken.com](https://pricepertoken.com/)
- [LLM API Pricing Compared Feb 2026 — TLDL](https://www.tldl.io/resources/llm-api-pricing-2026)
- [Self-Hosted LLM Cost Comparison 2026 — Prem AI](https://blog.premai.io/self-hosted-llm-guide-setup-tools-cost-comparison-2026/)
- [Cost Comparison: Ollama Self-hosting vs Cloud APIs — Ventus Servers](https://ventusserver.com/self-hosting-vs-cloud-apis/)
- [Top 11 LLM API Providers in 2026 — Future AGI](https://futureagi.substack.com/p/top-11-llm-api-providers-in-2026)
