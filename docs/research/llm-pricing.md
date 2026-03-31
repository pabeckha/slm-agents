---
title: "LLM Pricing Research"
category: "project"
lastUpdated: "2026-03-07"
status: "active"
---

# LLM Pricing Research

## Purpose

A reference of current LLM pricing — per-token API costs, third-party hosting, and self-hosted infrastructure — to support trade-off decisions on the routing strategy and provider selection.

---

## 1. Proprietary API Pricing

All prices are per 1 million tokens (input / output).

### Frontier Models

| Model | Input | Output | Context | Notes |
|---|---|---|---|---|
| **GPT-5.2 Pro** | $21.00 | $168.00 | 400K | Highest quality; very expensive at scale |
| **GPT-5** | $1.25 | $10.00 | 128K | Good quality/cost balance |
| **GPT-4.1** | $2.00 | $8.00 | 128K | Solid mid-tier |
| **Claude Opus 4.6** | $5.00 | $25.00 | 200K | Best agentic tasks; 1M ctx in beta |
| **Claude Sonnet 4.6** | $3.00 | $15.00 | 200K | Best coding; production workhorse |
| **Claude Haiku 4.5** | $0.25 | $1.25 | 200K | Fast, cheap; good for simple tasks |
| **Gemini 3.1 Pro** | $2.00 | $12.00 | 1M | Doubles to $4/$18 beyond 200K ctx |
| **Gemini 2.5 Pro** | $1.25 | $10.00 | 1M | Doubles to $2.50/... beyond 200K ctx |
| **Gemini 2.0 Flash** | $0.075 | $0.30 | 1M | Cheapest capable multimodal |
| **Grok 4** | $3.00 | $15.00 | 2M | Largest context of any frontier model |
| **Grok 4.1 Fast** | $0.20 | $0.50 | 2M | Best value frontier + 2M context |

### Budget / High-Efficiency

| Model | Input | Output | Context | Notes |
|---|---|---|---|---|
| **DeepSeek V3** | $0.14 | $0.28 | 128K | MIT license; ~100× cheaper than GPT-5.2 Pro output |
| **DeepSeek R1** | $0.55 | $2.19 | 128K | Reasoning model; 100× cheaper than Claude Opus |
| **Grok 4.1 Fast** | $0.20 | $0.50 | 2M | Budget frontier with massive context |
| **Gemini 2.0 Flash** | $0.075 | $0.30 | 1M | Cheapest multimodal |
| **Claude Haiku 4.5** | $0.25 | $1.25 | 200K | Cheapest Anthropic model |

---

## 2. Open-Source Models via Third-Party Hosts

Third-party inference platforms (Together.ai, Fireworks, Groq) host open-weight models via API — no infrastructure needed.

| Model | Host | Input | Output | Context | Notes |
|---|---|---|---|---|---|
| **Llama 4 Maverick** | Together.ai | $0.27 | $0.85 | 1M | Meta's flagship open-weight |
| **Llama 3.1 70B** | Together.ai | $0.54 | $0.54 | 128K | Reliable workhorse |
| **Qwen 3 72B** | Together.ai | $0.40 | $1.20 | 128K | Best multilingual open model |
| **DeepSeek R1 Distill 70B** | Together.ai | $0.54 | $0.54 | 128K | Distilled reasoning at open-weight prices |
| **Mistral 7B** | Fireworks | $0.25 | $0.25 | 32K | Ultra-efficient small model |
| **Mistral Nemo** | Mistral API | $0.02 | $0.02 | 128K | Cheapest capable model available |
| **Mixtral 8×22B** | Fireworks | $0.65 | $0.65 | 64K | MoE; strong general capability |
| **Cohere Command R** | Cohere API | $0.15 | $0.60 | 128K | Enterprise; strong RAG |
| **Cohere Command R7B** | Cohere API | $0.0375 | $0.15 | 128K | Edge-deployable |
| **Gemma 3 27B** | Fireworks | ~$0.20 | ~$0.20 | 128K | Google quality; open weights |

**Key platforms:**
- **Together.ai** — 200+ models, single API, serverless
- **Fireworks** — fast inference, $0.10–$3.00/M depending on model size
- **Groq** — hardware-accelerated; very low latency; generous free tier (1K req/day, 6K TPM)

---

## 3. Self-Hosted Infrastructure

Running models locally with Ollama, llama.cpp, or LM Studio.

### Hardware Costs

| GPU | VRAM | Purchase Price | What It Runs |
|---|---|---|---|
| RTX 3060 | 12GB | ~$300 | 7B–13B models (INT4) |
| RTX 4070 | 12GB | ~$550 | 7B–13B models; fast inference |
| RTX 4090 | 24GB | ~$1,600 | Up to 70B (INT4); 34B comfortably |
| 2× RTX 4090 | 48GB | ~$3,200 | 70B full precision; 140B INT4 |
| NVIDIA A100 (cloud) | 80GB | ~$2/hr (cloud) | 70B–180B models full precision |

### Operational Costs

| Scenario | Power Draw | Monthly Cost (est.) |
|---|---|---|
| RTX 4090 at 50% utilization | ~225W | $15–$30 |
| RTX 4090 at 100% utilization | ~450W | $30–$60 |
| 2× RTX 4090 at 50% utilization | ~450W | $30–$60 |

*Assumes $0.15/kWh average electricity rate.*

### Break-Even vs Cloud APIs

| Scenario | Break-Even Point |
|---|---|
| RTX 4090 vs Claude Sonnet 4.6 ($3/M input) | ~50M tokens/month → 12–18 months |
| RTX 4090 vs DeepSeek V3 ($0.14/M input) | ~500M tokens/month → may never break even purely on cost |
| Blackwell GPU (H100/B200) at 30M tokens/day | 1–4 months |

**Self-hosting is economically justified when:**
- Token volume exceeds **50M/month**
- Data residency / privacy requirements exist (no data leaves your infrastructure)
- Sub-100ms latency is required
- You can commit **0.5–1.0 FTE** to operations

**Cloud API is better when:**
- Volume stays under 50M tokens/month
- You need formal SLAs for customer-facing workloads
- You cannot staff infrastructure operations

---

## 4. Pricing Trends

- LLM API prices dropped **~80% from 2025 to 2026** across all providers
- Output tokens cost **3–10× more** than input tokens — the biggest hidden cost
- DeepSeek V3.2 output ($0.28/M) vs GPT-5.2 Pro output ($168/M) = **600× price gap**
- Self-hosting is increasingly driven by **privacy and liability**, not pure cost

---

## 5. Trade-Off Matrix

A structured comparison for DG's routing decision.

| Dimension | Claude Sonnet 4.6 | GPT-4.1 | Gemini 3.1 Pro | Grok 4.1 Fast | DeepSeek V3 | Self-hosted (Qwen 72B) |
|---|---|---|---|---|---|---|
| **Input cost** | $3.00/M | $2.00/M | $2.00/M | $0.20/M | $0.14/M | ~$0 (hardware amortized) |
| **Output cost** | $15.00/M | $8.00/M | $12.00/M | $0.50/M | $0.28/M | ~$0 |
| **Context** | 200K | 128K | 1M | 2M | 128K | 128K |
| **Quality (reasoning)** | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| **Quality (coding)** | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| **Multimodal** | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ | ✗ | ✗ |
| **Data privacy** | ✗ cloud | ✗ cloud | ✗ cloud | ✗ cloud | ✗ cloud | ✓ on-prem |
| **Latency** | Medium | Medium | Medium | Fast | Medium | Depends on HW |
| **Ops overhead** | None | None | None | None | None | High |
| **License** | Commercial | Commercial | Commercial | Commercial | MIT | Apache 2.0 |

---

## 6. Routing Cost Scenarios

Estimated monthly API cost for a workload of **10M input + 2M output tokens/month**:

| Provider | Input cost | Output cost | **Total/month** |
|---|---|---|---|
| GPT-5.2 Pro | $210.00 | $336.00 | **$546.00** |
| Claude Opus 4.6 | $50.00 | $50.00 | **$100.00** |
| Claude Sonnet 4.6 | $30.00 | $30.00 | **$60.00** |
| Gemini 3.1 Pro | $20.00 | $24.00 | **$44.00** |
| GPT-4.1 | $20.00 | $16.00 | **$36.00** |
| Grok 4 | $30.00 | $30.00 | **$60.00** |
| Grok 4.1 Fast | $2.00 | $1.00 | **$3.00** |
| DeepSeek V3 | $1.40 | $0.56 | **$1.96** |
| Mistral Nemo | $0.20 | $0.04 | **$0.24** |
| Self-hosted | $0 | $0 | **~$45 (electricity)** |

*At this scale, a **cascade strategy** (route simple tasks to DeepSeek/Grok Fast, escalate complex tasks to Claude/Gemini) could cut costs by 70–90% with minimal quality loss.*

---

## 7. Recommendation for DG Routing Strategy

Given DG's use cases (agentic tasks, coding, research):

1. **Default tier** — DeepSeek V3 or Grok 4.1 Fast for routine tasks ($0.14–$0.20/M input)
2. **Quality tier** — Claude Sonnet 4.6 for coding and agentic tasks ($3/M input)
3. **Reasoning tier** — Claude Opus 4.6 or DeepSeek R1 for complex reasoning ($5/M vs $0.55/M)
4. **Local fallback** — Qwen 3 72B or Phi-4 Mini for offline/privacy-sensitive tasks ($0 marginal)

This maps directly to a **cascade / capability-based routing strategy** as defined in `issues/architecture/model-routing-strategy.md`.

---

## Related Documents

- [docs/research/llm-landscape.md](llm-landscape.md) — Model capabilities and characteristics
- [issues/architecture/model-routing-strategy.md](../../issues/architecture/model-routing-strategy.md) — Routing strategy decision
- [issues/providers/provider-local-llm.md](../../issues/providers/provider-local-llm.md) — Local LLM backend
- [docs/architecture/cli-ui-llm-implementation-plan.md](../architecture/cli-ui-llm-implementation-plan.md) — Implementation plan

---

## Sources

- [LLM API Pricing 2026: Compare 300+ Models — pricepertoken.com](https://pricepertoken.com/)
- [LLM API Pricing Compared Feb 2026 — TLDL](https://www.tldl.io/resources/llm-api-pricing-2026)
- [Complete LLM Pricing Comparison 2026: 60+ Models — CloudIDR](https://www.cloudidr.com/blog/llm-pricing-comparison-2026)
- [AI API Pricing Comparison 2026: Grok vs Gemini vs GPT vs Claude — IntuitionLabs](https://intuitionlabs.ai/articles/ai-api-pricing-comparison-grok-gemini-openai-claude)
- [LLM API Pricing Comparison & Cost Guide Mar 2026 — CostGoat](https://costgoat.com/compare/llm-api)
- [Grok API Pricing 2026 — aifreeapi.com](https://www.aifreeapi.com/en/posts/xai-grok-api-pricing)
- [Gemini API Pricing March 2026 — TLDL](https://www.tldl.io/resources/google-gemini-api-pricing)
- [Gemini API Pricing 2026 — aifreeapi.com](https://www.aifreeapi.com/en/posts/gemini-api-pricing-2026)
- [Self-Hosted LLM Guide: Setup, Tools & Cost Comparison 2026 — Prem AI](https://blog.premai.io/self-hosted-llm-guide-setup-tools-cost-comparison-2026/)
- [Cost Comparison: Ollama Self-hosting vs Cloud APIs — Ventus Servers](https://ventusserver.com/self-hosting-vs-cloud-apis/)
- [Top 11 LLM API Providers in 2026 — Future AGI](https://futureagi.substack.com/p/top-11-llm-api-providers-in-2026)
- [Mistral AI API Pricing 2026 — pricepertoken.com](https://pricepertoken.com/pricing-page/provider/mistral-ai)
