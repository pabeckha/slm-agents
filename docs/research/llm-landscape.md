---
title: "LLM Landscape"
category: "project"
lastUpdated: "2026-03-07"
status: "active"
---

# LLM Landscape

## Purpose

A research reference of all major Large Language Models and Small Language Models — their characteristics, capabilities, pricing, and relevance to the DG provider abstraction layer.

---

## 1. Proprietary Models

### OpenAI — GPT Series

| Model | Params | Context | Highlights |
|---|---|---|---|
| **GPT-4o** | Undisclosed | 128K | Multimodal (text, image, audio, video); real-time interaction; emotion reading |
| **GPT-4.5** | Undisclosed | 128K | MMLU: 85.1%; released Feb 2025 |
| **GPT-5** | Undisclosed | 128K | Dual-model (speed + reasoning); routes based on task complexity; released Aug 2025 |
| **GPT-5.2** | Undisclosed | 400K | AIME 2025: 100%; significant reasoning leap; most capable GPT as of early 2026 |
| **GPT-5.3 Codex** | Undisclosed | 400K | Specialized for code; Intelligence Index: 54 |
| **GPT-5.4** | Undisclosed | 400K | Latest flagship; Intelligence Index: 57 |

**Strengths:** Best all-purpose; top reasoning and coding benchmarks; widest ecosystem integration.
**Weaknesses:** Closed weights; cost; no self-hosting option.
**Pricing:** ~$2.50–$15/M tokens depending on model tier.

---

### Anthropic — Claude Series

| Model | Params | Context | Highlights |
|---|---|---|---|
| **Claude 3.7 Sonnet** | Undisclosed | 200K | Extended Thinking Mode; top-tier coding; released Feb 2025 |
| **Claude Haiku 4.5** | Undisclosed | 200K | Fast, cost-efficient; released Oct 2025 |
| **Claude Sonnet 4.5** | Undisclosed | 200K (1M beta) | SWE-bench: 77.2%; OSWorld: 61.4%; agentic computer use |
| **Claude Sonnet 4.6** | Undisclosed | 200K (1M beta) | Intelligence Index: 52; current production model |
| **Claude Opus 4.6** | Undisclosed | 200K (1M beta) | Intelligence Index: 53; top reasoning + agentic tasks |

**Strengths:** Best agentic/computer-use tasks; extended thinking; long context; safety-focused.
**Weaknesses:** Closed weights; no self-hosting; premium pricing.
**Pricing:** ~$0.25–$15/M tokens (Haiku → Opus).
**DG note:** Current primary backend. Must remain a supported provider.

---

### Google DeepMind — Gemini Series

| Model | Params | Context | Highlights |
|---|---|---|---|
| **Gemini Nano** | ~1–3B | 8K | On-device; runs on smartphones; no internet needed |
| **Gemini 2.0 Flash** | Undisclosed | 1M | Fast; low cost; long context; multimodal |
| **Gemini 2.5 Pro** | Undisclosed | 1M | #1 LMArena leaderboard (human feedback); GPQA top scores; HLE: 18.8%; released Mar 2025 |
| **Gemini 3 Deep Think** | Undisclosed | 1M | Tops reasoning and long-horizon tasks alongside GPT-5.2 |
| **Gemini 3.1 Pro Preview** | Undisclosed | 1M | Intelligence Index: 57 (tied #1 with GPT-5.4) |

**Strengths:** Best multimodal; longest context (1M); top math/science benchmarks; strong Google ecosystem integration.
**Weaknesses:** Closed weights; tied to Google infrastructure.
**Pricing:** ~$0.075–$7/M tokens.

---

### xAI — Grok Series

| Model | Params | Context | Highlights |
|---|---|---|---|
| **Grok 3** | Undisclosed | 128K | "Think" mode for step-by-step reasoning; "DeepSearch" for real-time research |
| **Grok 4** | Undisclosed | 128K | Strong reasoning; hallucination rate ~12% |
| **Grok 4.1** | Undisclosed | 128K | #1 LMArena Elo (1483); hallucination rate reduced to ~4%; released Nov 2025 |
| **Grok Code Fast 1** | Undisclosed | 128K | Specialized for agentic coding and automated dev workflows |

**Strengths:** Top Elo ranking; lowest hallucination rate among frontier models; real-time data access via X/Twitter.
**Weaknesses:** Closed weights; tied to xAI/X ecosystem.

---

### Cohere — Command Series

| Model | Params | Context | Highlights |
|---|---|---|---|
| **Command A** | Undisclosed | 256K | Enterprise-grade; on-premises deployable |
| **Command A Vision** | Undisclosed | 256K | Multimodal variant |
| **Command A Reasoning** | Undisclosed | 256K | Enhanced reasoning for complex enterprise tasks |
| **Command A Translate** | Undisclosed | 256K | Multilingual translation specialized |

**Strengths:** On-premises deployment; enterprise SLAs; custom fine-tuning; strong RAG + Embed ecosystem.
**Weaknesses:** Less performant than frontier models on general benchmarks; enterprise pricing.
**DG note:** Strong candidate if on-premises deployment becomes a requirement.

---

## 2. Open-Source / Open-Weight Models

### Meta — Llama Series

| Model | Params | Context | License | Highlights |
|---|---|---|---|---|
| **Llama 3.1 8B** | 8B | 128K | Llama 3 Community | Strong base for fine-tuning; runs on 1× 24GB GPU |
| **Llama 3.1 70B** | 70B | 128K | Llama 3 Community | Near-GPT-4 quality; 4-bit fits 48GB GPU |
| **Llama 3.1 405B** | 405B | 128K | Llama 3 Community | Largest open-weight model before Llama 4 |
| **Llama 4 Scout** | Undisclosed | 10M | Llama 4 Community | 10M context window — largest available; instruction-tuned |
| **Llama 4 Maverick** | Undisclosed | 128K | Llama 4 Community | High-performance instruction variant |

**Strengths:** Open weights; large fine-tuning ecosystem; self-hostable.
**Weaknesses:** Qwen overtook Llama in community downloads and derivative models in 2025.

---

### Alibaba — Qwen Series

| Model | Params | Context | License | Highlights |
|---|---|---|---|---|
| **Qwen 2.5 0.5B–72B** | 0.5B–72B | 128K | Apache 2.0 | Full size range; strong multilingual |
| **Qwen 2.5 72B** | 72B | 128K | Apache 2.0 | Top open-weight model of 2025; 4-bit fits 48GB GPU |
| **Qwen-2.5-VL** | 7B–72B | 128K | Apache 2.0 | Vision-language; strong image understanding |
| **Qwen-2.5-Omni** | 7B | 128K | Apache 2.0 | Multimodal: text, image, audio |
| **Qwen 3** | Up to 110B | 128K–2M | Apache 2.0 | Best-in-class multilingual RAG; long-context leader |

**Strengths:** #1 open-weight by community downloads in 2025; exceptional multilingual; Apache 2.0 license; strong RAG performance.
**Pricing (API):** ~$0.40/M input, $0.80–$1.20/M output.
**DG note:** Top candidate for open-weight backend, especially for multilingual and long-context use cases.

---

### DeepSeek

| Model | Total Params | Active Params | Context | License | Highlights |
|---|---|---|---|---|---|
| **DeepSeek-V2** | 236B | 21B | 128K | MIT | MoE; efficient inference |
| **DeepSeek-V3** | 685B | 37B | 128K | MIT | State-of-the-art open-source general model |
| **DeepSeek-V3-0324** | 685B | 37B | 128K | MIT | Latest V3 iteration; released Mar 2025 |
| **DeepSeek-R1-Zero** | 685B | 37B | 128K | MIT | Pure RL reasoning; no supervised fine-tuning |
| **DeepSeek-R1** | 685B | 37B | 128K | MIT | Advanced reasoning; math, finance, theorem proving |
| **DeepSeek-R1 Distill (Qwen 7B)** | 7B | 7B | 128K | MIT | Distilled reasoning model; runs locally |
| **DeepSeek-R1 Distill (Llama 70B)** | 70B | 70B | 128K | MIT | Distilled reasoning; near R1 quality at lower cost |

**Strengths:** MIT license (true open source); aggressive pricing ($0.07/M input with cache); MoE efficiency; best open reasoning.
**Pricing (API):** $0.07–$0.55/M tokens (with/without cache).
**DG note:** Most cost-competitive option; strong candidate for cost-sensitive routing tier.

---

### Mistral AI

| Model | Params | Context | License | Highlights |
|---|---|---|---|---|
| **Mistral 7B** | 7B | 32K | Apache 2.0 | Efficient; strong for size; grouped query attention |
| **Mixtral 8×7B** | 46.7B (12.9B active) | 32K | Apache 2.0 | MoE; 2 experts activated per token |
| **Mixtral 8×22B** | 141B (39B active) | 64K | Apache 2.0 | Larger MoE variant |
| **Mistral Small 3** | 24B | 128K | Apache 2.0 | Released early 2025; efficient mid-tier |
| **Mistral Large** | Undisclosed | 128K | Commercial | Frontier-class; function calling; multilingual |
| **Codestral** | Undisclosed | 32K | Commercial | Code-specialized |

**Strengths:** Pioneered open MoE at scale; efficient architecture; strong European model (GDPR-relevant).
**DG note:** Codestral relevant for code-generation routing.

---

### Google DeepMind — Gemma Series

| Model | Params | Context | License | Highlights |
|---|---|---|---|---|
| **Gemma 2 9B** | 9B | 8K | Gemma ToS | Strong for size; fits consumer GPU |
| **Gemma 2 27B** | 27B | 8K | Gemma ToS | Top open-weight quality at 27B |
| **Gemma 3** | 1B–27B | 128K | Gemma ToS | Updated series; improved reasoning |
| **Gemma 3n E2B** | ~2B effective | 32K | Gemma ToS | On-device; multimodal (text, image, audio, video) |

**Strengths:** Google-quality at open-weight; good distillation target; Gemma 3n designed for on-device.
**Weaknesses:** Gemma ToS (not fully Apache 2.0); short context on 2B/9B variants.

---

### Microsoft — Phi Series

| Model | Params | Context | License | Highlights |
|---|---|---|---|---|
| **Phi-3.5 Mini** | 3.8B | 128K | MIT | High reasoning-per-param; CPU/NPU capable |
| **Phi-4** | 14B | 16K | MIT | Rivals much larger models on math and coding |
| **Phi-4 Mini** | 3.8B | 128K | MIT | Edge-optimized; strongest SLM for reasoning |

**Strengths:** Best reasoning-per-parameter ratio in the SLM range; MIT license; runs on edge devices including NPUs.
**DG note:** Prime candidate for local SLM backend on constrained hardware.

---

### Technology Innovation Institute — Falcon Series

| Model | Params | Context | License | Highlights |
|---|---|---|---|---|
| **Falcon 7B** | 7B | 2K | Apache 2.0 | Original open-weight release |
| **Falcon 40B** | 40B | 2K | Apache 2.0 | Multilingual; strong general capability |
| **Falcon 180B** | 180B | 2K | Falcon License | Largest Falcon variant |
| **Falcon 2 11B** | 11B | 8K | Apache 2.0 | Multimodal capable |
| **Falcon 3 (1–10B)** | 1B–10B | 8K | Apache 2.0 | Efficient small series |

**Strengths:** Apache 2.0; multilingual (46+ languages); strong for Arabic/MENA languages.
**Weaknesses:** Short context window; newer models lag behind Qwen/Llama in benchmarks.

---

### BigScience — BLOOM

| Model | Params | Context | License | Highlights |
|---|---|---|---|---|
| **BLOOM** | 176B | 2K | BigScience Rail | 46 natural languages + 13 programming languages; fully open |

**Strengths:** Most multilingual open model; community-built.
**Weaknesses:** Outdated architecture; short context; outperformed by newer models.

---

### Moonshot AI — Kimi Series

| Model | Params | Context | License | Highlights |
|---|---|---|---|---|
| **Kimi K2** | ~1T (MoE) | 128K | Open-weight | 1T parameters; competitive performance; mid-2025 |
| **Kimi Linear** | Undisclosed | 1M+ | Open-weight | Linear attention; efficient long-context generation |

**Strengths:** Massive scale open-weight; efficient long-context via linear attention.

---

## 3. Small Language Models (SLMs)

Models under ~10B parameters designed for on-device, edge, or cost-constrained inference.

| Model | Params | Context | Runs On | Highlights |
|---|---|---|---|---|
| **Phi-4 Mini** | 3.8B | 128K | CPU, NPU, mobile | Best reasoning SLM; MIT license |
| **Phi-3.5 Mini** | 3.8B | 128K | CPU, NPU | Strong math/coding for size |
| **Gemma 3n E2B** | ~2B effective | 32K | Mobile, edge | Multimodal (text, image, audio, video); on-device |
| **Gemma 2 9B** | 9B | 8K | Consumer GPU | Google quality at 9B |
| **Gemini Nano** | ~1–3B | 8K | Smartphone | Built into Pixel; no internet needed |
| **Qwen 2.5 0.5B–3B** | 0.5B–3B | 32K | CPU, mobile | Strong multilingual at tiny size |
| **TinyLlama 1.1B** | 1.1B | 2K | CPU, Raspberry Pi | Ultra-low resource; real-time edge inference |
| **SmolLM3** | 3B | 64K (128K via YaRN) | CPU, edge | HuggingFace SLM; extended context via YaRN |
| **DeepSeek-R1 Distill 7B** | 7B | 128K | 1× 8GB GPU | Reasoning capability distilled from R1 |
| **Mistral 7B** | 7B | 32K | 1× 16GB GPU | Efficient; widely supported by runtimes |

**DG note:** SLMs are the primary target for `provider-local-llm.md`. Phi-4 Mini and Gemma 3n are the leading candidates for on-device deployment.

---

## 4. Benchmark Comparison (March 2026)

| Model | MMLU | HumanEval | MATH | GPQA | Context | Price/M input |
|---|---|---|---|---|---|---|
| GPT-5.4 | ~92% | ~95% | ~97% | ~75% | 400K | ~$15 |
| Gemini 3.1 Pro | ~91% | ~93% | ~96% | ~74% | 1M | ~$7 |
| Grok 4.1 | ~90% | ~92% | ~95% | ~73% | 128K | ~$10 |
| Claude Opus 4.6 | ~90% | ~92% | ~94% | ~72% | 200K | ~$15 |
| Claude Sonnet 4.6 | ~88% | ~89% | ~91% | ~68% | 200K | ~$3 |
| DeepSeek-V3 | ~87% | ~87% | ~90% | ~65% | 128K | $0.07 |
| Qwen 3 72B | ~85% | ~84% | ~88% | ~62% | 128K | $0.40 |
| Llama 4 Maverick | ~83% | ~82% | ~85% | ~58% | 128K | self-host |
| Mistral Large | ~81% | ~80% | ~82% | ~55% | 128K | ~$2 |
| Phi-4 14B | ~78% | ~79% | ~82% | ~50% | 16K | self-host |
| Gemma 2 27B | ~75% | ~74% | ~76% | ~45% | 8K | self-host |

*Scores are approximate composites from available public benchmarks.*

---

## 5. Capability Matrix

| Model | Reasoning | Coding | Multimodal | Long Context | Self-hostable | Cost |
|---|---|---|---|---|---|---|
| GPT-5.4 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★☆ | ✗ | $$$$ |
| Gemini 3.1 Pro | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★★★ | ✗ | $$$ |
| Grok 4.1 | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ✗ | $$$$ |
| Claude Opus 4.6 | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★☆ | ✗ | $$$$ |
| Claude Sonnet 4.6 | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★☆ | ✗ | $$$ |
| DeepSeek-V3 | ★★★★☆ | ★★★★☆ | ✗ | ★★★★☆ | ✓ | $ |
| DeepSeek-R1 | ★★★★★ | ★★★★☆ | ✗ | ★★★★☆ | ✓ | $ |
| Qwen 3 72B | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★★★ | ✓ | $ |
| Llama 4 Scout | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★★ | ✓ | free |
| Mistral Large | ★★★☆☆ | ★★★★☆ | ✗ | ★★★☆☆ | ✓* | $$ |
| Phi-4 Mini | ★★★★☆ | ★★★★☆ | ✗ | ★★☆☆☆ | ✓ | free |
| Gemma 3n E2B | ★★☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★☆☆ | ✓ | free |

*✓* = available via self-hosted API but also commercial tier*

---

## 6. DG Provider Selection Notes

| Use Case | Recommended Backend | Rationale |
|---|---|---|
| High-quality reasoning | Claude Opus 4.6 or GPT-5.4 | Best reasoning + safety |
| Agentic / computer use | Claude Sonnet 4.6 | OSWorld #1; computer use API |
| Coding | Claude Sonnet 4.6 or Grok Code Fast 1 | SWE-bench leaders |
| Multimodal | Gemini 3.1 Pro or GPT-5.4 | Best vision + audio |
| Cost-sensitive | DeepSeek-V3 ($0.07/M) | MIT license; near-frontier quality |
| Long context | Gemini 3.1 Pro (1M) or Llama 4 Scout (10M) | Largest available context |
| Offline / self-hosted | Qwen 3 72B or Phi-4 Mini | Best quality at respective sizes |
| Edge / mobile | Phi-4 Mini or Gemma 3n | Runs on CPU/NPU/mobile |

---

## Related Documents

- [PRD](../PRD.md) — Architecture goals
- [docs/research/llm-optimization-methods.md](llm-optimization-methods.md) — How to optimize these models
- [issues/architecture/model-routing-strategy.md](../../issues/architecture/model-routing-strategy.md) — Routing strategy decision
- [issues/providers/provider-local-llm.md](../../issues/providers/provider-local-llm.md) — Local LLM backend
- [memory/llm-papers.md](../../.deepgruble/memory/llm-papers.md) — Latest research

---

## Sources

- [Top 40 Large Language Models (LLMs) in 2026 — Bestarion](https://bestarion.com/top-large-language-models-llms/)
- [AI Leaderboards 2026: Compare All AI Models — llm-stats.com](https://llm-stats.com/)
- [Top 9 Large Language Models as of March 2026 — Shakudo](https://www.shakudo.io/blog/top-9-large-language-models)
- [AI Model Benchmarks Mar 2026 — LM Council](https://lmcouncil.ai/benchmarks)
- [LLM Leaderboard — Artificial Analysis](https://artificialanalysis.ai/leaderboards/models)
- [2025 LLM Review: GPT-5.2, Gemini 3, Claude 4.5, DeepSeek-V3.2, Qwen3 — atoms.dev](https://atoms.dev/blog/2025-llm-review-gpt-5-2-gemini-3-pro-claude-4-5)
- [The best large language models (LLMs) in 2026 — Zapier](https://zapier.com/blog/best-llm/)
- [10 Best Open-Source LLM Models (Llama 4, Qwen 3, DeepSeek R1) — HuggingFace](https://huggingface.co/blog/daya-shankar/open-source-llms)
- [Best Open-Source LLMs: Complete 2026 Guide — Contabo](https://contabo.com/blog/open-source-llms/)
- [Top 10 Open Source LLMs 2026: DeepSeek Revolution — o-mega.ai](https://o-mega.ai/articles/top-10-open-source-llms-the-deepseek-revolution-2026)
- [The Best Open-Source Small Language Models (SLMs) in 2026 — BentoML](https://www.bentoml.com/blog/the-best-open-source-small-language-models)
- [Top 15 Small Language Models for 2026 — DataCamp](https://www.datacamp.com/blog/top-small-language-models)
- [Small Language Models: Architecture, Evolution, and the Future — Preprints.org](https://www.preprints.org/manuscript/202601.0973)
- [The State of LLMs 2025 — Sebastian Raschka](https://magazine.sebastianraschka.com/p/state-of-llms-2025)
