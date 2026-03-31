---
title: "Local LLM Deployment Options"
category: "architecture"
lastUpdated: "2026-03-07"
status: "active"
---

# Local LLM Deployment Options

## Purpose

Analyze all realistic options for running a self-hosted LLM for DeepGruble — covering on-premise hardware, cloud GPU rentals, and managed inference platforms. Each option is evaluated on cost, latency, privacy, maintenance burden, and suitability for different model sizes.

> **Note:** All prices are as of mid-2025 (knowledge cutoff). Hardware prices and cloud rates change frequently — verify before purchasing.

---

## Part 1: Hardware Requirements by Model Size

| Model Size | Example Models | Min VRAM (INT4) | Min VRAM (FP16) | Recommended Setup |
|---|---|---|---|---|
| 3–4B | Phi-4, Llama 3.2 3B | 3 GB | 8 GB | Single consumer GPU |
| 7–8B | Llama 3.1 8B, Mistral 7B | 6 GB | 16 GB | Single consumer GPU |
| 14B | Qwen2.5-Coder 14B, Phi-4 | 10 GB | 28 GB | Single RTX 3090/4090 |
| 32B | Qwen2.5-Coder 32B, Mistral Small | 20 GB | 64 GB | Single RTX 4090 or A6000 48GB |
| 70B | Llama 3.3 70B, DeepSeek-R1 | 40 GB | 140 GB | 2× A100 80GB or 4× RTX 4090 |
| 235B | DeepSeek-R1, Llama 3.1 405B | 128 GB | 470 GB | 4–8× H100 80GB |

> For code-focused local use, **Qwen2.5-Coder 32B at INT4 on a single RTX 4090** is the best quality-per-hardware ratio.

---

## Part 2: On-Premise Hardware

You own and operate the hardware. Full control, maximum privacy, no recurring compute cost.

### 2.1 Consumer / Prosumer GPU Workstation

**Target:** Single developer machine or small team workstation.

| Component | Option A — Budget | Option B — Recommended | Option C — High-end |
|---|---|---|---|
| GPU | 1× RTX 3090 24GB | 1× RTX 4090 24GB | 2× RTX 4090 24GB |
| GPU price | ~$750 (used) | ~$1,800 (new) | ~$3,600 (2× new) |
| CPU | Ryzen 7 7700X (~$280) | Ryzen 9 7950X (~$550) | Threadripper Pro (~$1,400) |
| RAM | 64 GB DDR5 (~$120) | 128 GB DDR5 (~$220) | 256 GB DDR5 (~$440) |
| Motherboard | ~$200 | ~$350 | ~$600 |
| PSU + case + storage | ~$450 | ~$580 | ~$960 |
| **Total hardware** | **~$1,800** | **~$3,500** | **~$7,000** |
| Max model size (INT4) | 14B | 32B | 65B |
| Approx tokens/sec (32B INT4) | n/a | ~20–30 tok/s | ~40–55 tok/s |
| Power draw (under load) | ~350W | ~450W | ~900W |
| **Monthly power cost** (~$0.12/kWh, 8hr/day use) | **~$10** | **~$13** | **~$26** |
| **Hardware amortized (3 yr) + power** | **~$60/mo** | **~$110/mo** | **~$220/mo** |

---

### 2.2 Professional GPU Server

**Target:** Team or production workload requiring larger models or multi-user concurrency.

| Config | GPU | VRAM | GPU Price | Full Server Est. | Max Model | Monthly (amortized 3yr + power) |
|---|---|---|---|---|---|---|
| Entry Pro | 1× RTX 6000 Ada | 48 GB | ~$4,800 | ~$8,000 | 32B FP16 / 65B INT4 | ~$240/mo |
| Mid Pro | 2× A6000 Ada 48GB | 96 GB | ~$9,600 | ~$15,000 | 70B FP16 | ~$450/mo |
| High-end | 2× A100 80GB SXM4 | 160 GB | ~$28,000 | ~$36,000 | 70B FP16 comfortably | ~$1,050/mo |
| Large scale | 4× H100 80GB SXM5 | 320 GB | ~$100,000+ | ~$140,000+ | 235B INT4 | ~$3,950/mo |

> Power for server configs adds ~$50–$250/mo depending on GPU count and hours/day.

**Apple Silicon alternative:**

| Model | Unified Memory | Price | Max LLM | Approx tok/s (70B FP16) | Monthly (amortized 3yr) |
|---|---|---|---|---|---|
| Mac Studio M4 Ultra | 192 GB | $9,999 | 70B FP16 | ~15–20 tok/s | ~$285/mo |
| Mac Pro M4 Ultra | 192 GB | $7,999 (base config) | 70B FP16 | ~15–20 tok/s | ~$230/mo |

Apple Silicon is uniquely good value for 70B FP16 because unified memory eliminates VRAM constraints, but CUDA-only tools (vLLM, GPTQ) do not run on it. Use llama.cpp or Ollama.

**Pros of on-premise:**
- Zero ongoing compute cost
- Full data privacy — no traffic leaves the building
- No network latency (local Unix socket or localhost)
- Full control: model weights, inference config, updates

**Cons:**
- High upfront CAPEX
- No redundancy — hardware failure = downtime
- Power, cooling, and physical space requirements
- Maintenance burden

---

## Part 3: Cloud GPU Rentals

No upfront cost — pay per hour of GPU time.

### 3.1 Hyperscale Cloud (AWS / GCP / Azure)

| Provider | Instance | GPU | VRAM | On-demand Price | Monthly (24/7) |
|---|---|---|---|---|---|
| AWS | g5.xlarge | 1× A10G 24GB | 24 GB | $1.01/hr | ~$727/mo |
| AWS | g5.12xlarge | 4× A10G 24GB | 96 GB | $5.67/hr | ~$4,082/mo |
| AWS | p4d.24xlarge | 8× A100 40GB | 320 GB | $32.77/hr | ~$23,594/mo |
| AWS | p5.48xlarge | 8× H100 80GB | 640 GB | $98.32/hr | ~$70,790/mo |
| GCP | a2-highgpu-1g | 1× A100 40GB | 40 GB | $3.67/hr | ~$2,642/mo |
| GCP | a2-highgpu-2g | 2× A100 40GB | 80 GB | $7.35/hr | ~$5,292/mo |
| GCP | a3-highgpu-8g | 8× H100 80GB | 640 GB | ~$60/hr | ~$43,200/mo |
| Azure | NC24ads A100 v4 | 1× A100 80GB | 80 GB | $3.67/hr | ~$2,642/mo |
| Azure | ND96asr A100 v4 | 8× A100 80GB | 640 GB | $27.20/hr | ~$19,584/mo |

> Spot / preemptible instances reduce cost by 60–90% but can be interrupted at any time. Suitable for batch jobs, not interactive CLI.

**Verdict:** Only justifiable if you are already deeply invested in AWS/GCP/Azure infrastructure. Otherwise far too expensive for LLM inference compared to alternatives below.

---

### 3.2 GPU-Specialized Cloud

These providers are GPU-only and 3–10× cheaper than hyperscalers.

#### Lambda Labs

| GPU | VRAM | On-demand Price | Monthly (24/7) | Good For |
|---|---|---|---|---|
| RTX 4090 | 24 GB | $0.50/hr | $360/mo | 32B INT4 dev use |
| A100 40GB PCIe | 40 GB | $1.10/hr | $792/mo | 32B FP16 |
| A100 80GB SXM4 | 80 GB | $1.99/hr | $1,433/mo | 70B INT4 |
| H100 80GB PCIe | 80 GB | $1.99/hr | $1,433/mo | 70B FP16 |
| H100 80GB SXM5 | 80 GB | $2.49/hr | $1,793/mo | 70B FP16 fast |
| 8× H100 80GB (cluster) | 640 GB | $19.92/hr | $14,342/mo | 235B models |

#### CoreWeave

| GPU | VRAM | Price | Monthly (24/7) |
|---|---|---|---|
| RTX 4090 | 24 GB | $0.76/hr | $547/mo |
| A100 40GB | 40 GB | $2.06/hr | $1,483/mo |
| A100 80GB | 80 GB | $2.21/hr | $1,591/mo |
| H100 80GB PCIe | 80 GB | $3.85/hr | $2,772/mo |
| H100 80GB SXM5 | 80 GB | $4.25/hr | $3,060/mo |

> CoreWeave offers reserved pricing (1–3 year) that reduces rates by ~30–40%.

#### RunPod

| GPU | VRAM | On-demand | Monthly (24/7) | Spot | Monthly (spot) |
|---|---|---|---|---|---|
| RTX 3090 | 24 GB | $0.44/hr | $317/mo | $0.20/hr | $144/mo |
| RTX 4090 | 24 GB | $0.74/hr | $533/mo | $0.34/hr | $245/mo |
| A100 40GB | 40 GB | $1.19/hr | $857/mo | $0.89/hr | $641/mo |
| A100 80GB | 80 GB | $1.99/hr | $1,433/mo | $1.49/hr | $1,073/mo |
| H100 80GB PCIe | 80 GB | $2.39/hr | $1,721/mo | $1.89/hr | $1,361/mo |
| H100 80GB SXM5 | 80 GB | $3.49/hr | $2,513/mo | $2.49/hr | $1,793/mo |

#### Vast.ai (marketplace, price range)

| GPU | VRAM | Price Range/hr | Monthly Range |
|---|---|---|---|
| RTX 3090 | 24 GB | $0.10–$0.35/hr | $72–$252/mo |
| RTX 4090 | 24 GB | $0.28–$0.55/hr | $202–$396/mo |
| A100 40GB | 40 GB | $0.65–$1.20/hr | $468–$864/mo |
| A100 80GB | 80 GB | $0.90–$1.80/hr | $648–$1,296/mo |
| H100 80GB | 80 GB | $1.50–$2.80/hr | $1,080–$2,016/mo |

> Vast.ai is peer-to-peer — no SLA, variable availability, but cheapest rates available for burst or dev workloads.

#### Hetzner (EU, GDPR-friendly)

| Instance | GPU | VRAM | Price | Monthly (24/7) |
|---|---|---|---|---|
| GX2 (cloud) | 2× RTX 4000 Ada | 2× 20 GB | €2.49/hr | ~€1,793/mo (~$1,970/mo) |
| Dedicated GPU server | 1× RTX 3090 | 24 GB | ~€3.00/mo (bare metal, limited stock) | ~€3.00/mo |

> Hetzner's GPU options are limited and underpowered for 32B+ models. Best if EU data residency is a hard requirement and small models suffice.

#### OVHcloud (EU)

| Instance | GPU | VRAM | Price | Monthly (24/7) |
|---|---|---|---|---|
| T4-35 | 1× Tesla T4 | 16 GB | €0.56/hr | ~€403/mo |
| A100-40 | 1× A100 40GB | 40 GB | €2.60/hr | ~€1,872/mo |
| A100-80 | 1× A100 80GB | 80 GB | €3.49/hr | ~€2,513/mo |

> OVH is solid for EU compliance; pricing is slightly higher than Lambda Labs but with French/Canadian data centers.

---

### 3.3 Managed LLM Inference APIs

No infrastructure to manage — call an API. All use OpenAI-compatible endpoints.

#### Per-Token Pricing

| Provider | Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|---|
| **Groq** | Llama 3.1 8B | $0.05 | $0.08 |
| **Groq** | Llama 3.3 70B | $0.59 | $0.79 |
| **Groq** | DeepSeek-R1 (70B distill) | $0.75 | $0.99 |
| **Together.ai** | Llama 3.1 8B | $0.18 | $0.18 |
| **Together.ai** | Llama 3.1 70B | $0.88 | $0.88 |
| **Together.ai** | Qwen2.5-Coder 32B | $0.80 | $0.80 |
| **Together.ai** | Llama 3.1 405B | $3.50 | $3.50 |
| **Together.ai** | DeepSeek-R1 | $1.20 | $1.20 |
| **Fireworks.ai** | Llama 3.1 8B | $0.20 | $0.20 |
| **Fireworks.ai** | Llama 3.1 70B | $0.90 | $0.90 |
| **Fireworks.ai** | Qwen2.5-Coder 32B | $0.90 | $0.90 |
| **Fireworks.ai** | DeepSeek-R1 (fast) | $3.00 | $3.00 |
| **Replicate** | Any custom model | $0.001/sec GPU time | — |
| **Anyscale** | Llama 3.1 70B | $0.50 | $0.50 |

#### Estimated Monthly Cost by Usage Level

Assumptions: avg request = 2,000 tokens (input + output combined), split 50/50.

| Usage Level | Requests/day | Tokens/month | Groq 70B | Together 70B | Fireworks 70B |
|---|---|---|---|---|---|
| Light (dev/test) | 20 | 1.2M | ~$0.83 | ~$1.06 | ~$1.08 |
| Medium (team daily use) | 100 | 6M | ~$4.14 | ~$5.28 | ~$5.40 |
| Heavy (production) | 500 | 30M | ~$20.70 | ~$26.40 | ~$27.00 |
| Very heavy | 2,000 | 120M | ~$82.80 | ~$105.60 | ~$108.00 |

> **Groq** is the clear winner for interactive CLI use: fastest throughput (~500 tok/s), cheapest per token, OpenAI-compatible API. The only constraint is limited model selection and no custom model upload.

---

## Part 4: Hybrid Architecture

Layer deployment options by request type:

```
Request type              → Deployment tier          → Cost profile
──────────────────────────────────────────────────────────────────
Privacy-sensitive code    → On-prem RTX 4090          → ~$110/mo fixed
Fast interactive CLI      → Groq (Llama 3.3 70B)      → ~$0.69/1M tokens
High-volume batch tasks   → Together.ai (Llama 3.1 70B) → ~$0.88/1M tokens
Large context (>150K tok) → Cloud A100 (Lambda Labs)   → $1.99/hr on-demand
Dev/test experiments      → RunPod spot (RTX 4090)     → $0.34/hr
EU compliance required    → OVHcloud A100              → €3.49/hr
```

---

## Part 5: Full Cost Comparison

Scenario: running a 70B model, 8 hours/day, 5 days/week (business hours only).
Monthly GPU hours: 8 × 5 × 4.33 = ~173 hr/month.

| Option | Setup | GPU | Monthly Compute | Monthly Total | Privacy |
|---|---|---|---|---|---|
| On-prem 2× RTX 4090 | $7,000 one-time | Own | ~$0 (power: ~$26) | **~$220** (amortized) | ★★★★★ |
| On-prem 2× A100 80GB | $36,000 one-time | Own | ~$0 (power: ~$52) | **~$1,052** (amortized) | ★★★★★ |
| Mac Studio M4 Ultra | $9,999 one-time | Own | ~$0 (power: ~$5) | **~$283** (amortized) | ★★★★★ |
| Lambda Labs A100 80GB | None | Rented | $1.99 × 173 = **$344** | $344 | ★★★★ |
| RunPod A100 80GB (spot) | None | Rented | $1.49 × 173 = **$258** | $258 | ★★★★ |
| Vast.ai A100 80GB | None | Rented | ~$1.20 × 173 = **$208** | $208 | ★★★ |
| AWS p4d.24xlarge | None | Rented | $32.77 × 173 = **$5,669** | $5,669 | ★★★ |
| Together.ai Llama 3.1 70B | None | API | usage-based ~**$5–$106/mo** | $5–$106 | ★★★ |
| Groq Llama 3.3 70B | None | API | usage-based ~**$4–$83/mo** | $4–$83 | ★★★ |

> Break-even point for on-prem RTX 4090 vs Lambda Labs A100: ~10 months of continuous use. After that, on-prem is cheaper every month.

---

## Part 6: Recommendation by Stage

| Stage | Recommended Option | Monthly Cost | Rationale |
|---|---|---|---|
| **Dev / exploration** | Groq (Llama 3.3 70B) | $1–$20 | Zero setup, fastest responses, cheapest |
| **Early production** | Together.ai or Fireworks.ai | $5–$100 | Reliable, managed, more model choice than Groq |
| **Growing team usage** | Lambda Labs A100 80GB | ~$344/mo (173hr) | Better $/token than APIs at medium scale |
| **Privacy-sensitive** | On-prem RTX 4090 (Qwen2.5-Coder 32B) | ~$110/mo amortized | Zero data egress |
| **EU compliance** | OVHcloud A100 80GB | ~€605/mo (173hr) | EU data residency, GDPR |
| **High-scale production** | CoreWeave H100 cluster (reserved) | ~$2,200/mo (reserved) | Best perf/cost at high volume |
| **Largest models (70B+)** | On-prem 2× A100 or Mac Studio M4 Ultra | ~$283–$1,052/mo | Best cost after 10 months |

---

## Part 7: Inference Server Software

| Software | Best Deployment | License | Notes |
|---|---|---|---|
| **Ollama** | Developer workstations | MIT | Dead-simple, OpenAI-compatible, GGUF + safetensors |
| **vLLM** | Cloud / production servers | Apache 2 | PagedAttention, continuous batching, highest throughput |
| **llama.cpp** | CPU / low VRAM | MIT | Runs on anything, GGUF format, good for small models |
| **TGI (HuggingFace)** | Kubernetes / Docker | Apache 2 | HF model hub integration, easy container deploy |
| **LM Studio** | Local desktop | Proprietary (free) | GUI, non-technical users |

For production servers: **vLLM**. For local developer use: **Ollama** (already OpenAI-compatible — plugs directly into `LocalLLMAdapter` from Phase 2 with no changes).

---

## Related Documents

- [docs/llm-capability-analysis.md](./llm-capability-analysis.md) — capability per provider
- [docs/llm-optimization-methods.md](./llm-optimization-methods.md) — quantization methods relevant to local inference
- [issues/provider-local-llm.md](../issues/provider-local-llm.md) — local provider implementation
- [issues/phase-5-router.md](../issues/phase-5-router.md) — routing strategy that ties deployment tiers together
