---
title: "LLM Optimization Methods"
category: "project"
lastUpdated: "2026-03-07"
status: "active"
---

# LLM Optimization Methods

## Purpose

A reference of all known methods to optimize a Large Language Model — covering inference speed, memory footprint, training efficiency, output quality, and deployment cost. Each method notes its trade-offs and relevance to the DG LLM architecture.

---

## 1. Quantization

Reduces the numerical precision of model weights and/or activations to lower memory usage and increase inference speed.

| Method | Precision | Notes |
|---|---|---|
| **FP16 / BF16** | 16-bit float | Near-lossless; standard baseline for GPU inference |
| **INT8** | 8-bit integer | ~2x memory reduction; minimal quality loss with calibration |
| **INT4 / GPTQ** | 4-bit integer | ~4x reduction; small perplexity increase; widely used for local LLMs |
| **AWQ** | 4-bit integer | Activation-aware Weight Quantization; better quality than GPTQ at same bit-width |
| **BitNet / 1.58-bit** | ~1.58-bit ternary | Extreme compression; designed for models trained from scratch in low-bit regime |
| **GGUF (llama.cpp)** | Mixed (2–8 bit) | File format for CPU/GPU inference; flexible per-layer quantization |

**Trade-offs:** Lower bit-width → less VRAM → faster inference, but potential accuracy degradation. Best combined with calibration datasets.

**DG relevance:** Critical for `provider-local-llm.md` — enables running SLMs on commodity hardware.

---

## 2. Pruning

Removes redundant weights or structures from the model to reduce size and compute.

| Method | Type | Notes |
|---|---|---|
| **Unstructured pruning** | Weight-level | Sets individual weights to zero; requires sparse hardware support to realize speedups |
| **Structured pruning** | Layer/head/neuron-level | Removes entire attention heads or MLP neurons; hardware-friendly |
| **N:M sparsity** | Semi-structured | N zeros out of every M weights (e.g., 2:4); supported natively by NVIDIA Ampere+ GPUs |
| **Magnitude pruning** | Unstructured | Removes lowest-magnitude weights; simple but less accurate than gradient-based methods |
| **Movement pruning** | Unstructured | Prunes based on weight importance during fine-tuning; better for task-specific models |

**Trade-offs:** Reduces model size and FLOPs, but can degrade quality if applied aggressively without fine-tuning recovery.

---

## 3. Knowledge Distillation

Trains a smaller "student" model to mimic the outputs of a larger "teacher" model.

| Method | Notes |
|---|---|
| **Output distillation** | Student learns to match teacher's softmax probability distribution |
| **Feature distillation** | Student matches intermediate activations of the teacher |
| **Task-specific distillation** | Teacher fine-tuned on a task; student distilled on same task (e.g., DistilBERT, TinyLLM) |
| **Speculative distillation** | Small draft model trained to approximate a large target model for speculative decoding |

**Trade-offs:** Produces smaller, faster models but requires access to the teacher model and additional training compute.

**DG relevance:** Useful for producing lightweight local backends that approximate Claude/Gemini quality.

---

## 4. Efficient Fine-Tuning (PEFT)

Parameter-Efficient Fine-Tuning methods adapt a pre-trained model to a task by training only a small subset of parameters.

| Method | Description |
|---|---|
| **LoRA** | Injects low-rank matrices into attention layers; trains only these adapters (~0.1–1% of params) |
| **QLoRA** | LoRA applied to a quantized (4-bit) base model; enables fine-tuning large models on consumer GPUs |
| **AdaLoRA** | Adaptive LoRA; dynamically allocates rank budget across layers based on importance |
| **Prefix Tuning** | Prepends trainable virtual tokens to the input; freezes the base model entirely |
| **Prompt Tuning** | Learns soft prompt embeddings; the lightest PEFT method |
| **IA³** | Scales activations with learned vectors; extremely few parameters |

**Trade-offs:** Much cheaper than full fine-tuning; quality slightly below full fine-tuning for large distribution shifts.

---

## 5. Alignment & Preference Optimization

Methods to align model outputs with human intent, safety, and preferences.

| Method | Description |
|---|---|
| **RLHF** | Reinforcement Learning from Human Feedback; trains a reward model then optimizes policy via PPO |
| **DPO** | Direct Preference Optimization; eliminates reward model; optimizes directly from preference pairs |
| **RLAIF** | Replaces human feedback with AI-generated feedback (e.g., Constitutional AI) |
| **KTO** | Kahneman-Tversky Optimization; uses binary signals (good/bad) instead of pairwise preferences |
| **IPO** | Identity Preference Optimization; improves DPO stability |
| **Instruction Tuning** | Supervised fine-tuning on (instruction, response) pairs; foundational step before RLHF |

**DG relevance:** Relevant when evaluating which provider offers the best-aligned model for DG's use cases.

---

## 6. Architecture-Level Optimizations

Design choices that improve efficiency at the model architecture level.

| Method | Description |
|---|---|
| **Multi-Query Attention (MQA)** | All attention heads share a single key/value head; reduces KV cache size significantly |
| **Grouped Query Attention (GQA)** | Groups of heads share key/value heads; balance between MQA and standard MHA (used in Llama 3) |
| **Sliding Window Attention** | Each token attends only to a fixed local window; enables long contexts with linear complexity |
| **Flash Attention** | IO-aware exact attention algorithm; same output as standard attention but much faster on GPU |
| **Flash Attention 2 / 3** | Improved parallelism and arithmetic throughput over FA1 |
| **Mixture of Experts (MoE)** | Activates only a subset of "expert" FFN layers per token; scales params without scaling compute |
| **Sparse MoE** | MoE with top-K routing (e.g., Mixtral, DeepSeek-MoE); widely adopted at scale |
| **Linear Attention** | Replaces softmax attention with linear approximations; O(n) complexity vs O(n²) |
| **State Space Models (SSM)** | Mamba, S4 — recurrent-style models with linear inference complexity; alternative to transformers |

---

## 7. Inference-Time Optimizations

Techniques applied at runtime to accelerate generation without changing the model.

| Method | Description |
|---|---|
| **KV Cache** | Caches key/value tensors from prior tokens to avoid recomputation during autoregressive generation |
| **PagedAttention** | Manages KV cache with virtual memory paging (used in vLLM); enables high-throughput batching |
| **Continuous Batching** | Processes requests at the token level, not request level; dramatically improves GPU utilization |
| **Speculative Decoding** | Small draft model generates candidates; large model verifies in parallel; same output, faster |
| **Assisted Generation** | HuggingFace variant of speculative decoding |
| **Early Exit** | Exits computation at an intermediate layer when confidence is high; adaptive compute per token |
| **Token Streaming** | Returns tokens as they are generated; reduces perceived latency |
| **Prompt Caching** | Caches KV state of a shared system prompt prefix across requests (supported by Claude, Gemini) |

**DG relevance:** Prompt caching and continuous batching directly affect cost and latency in the routing layer (`model-routing-strategy.md`).

---

## 8. Retrieval-Augmented Generation (RAG)

Augments the model's context with retrieved external knowledge instead of baking knowledge into weights.

| Method | Description |
|---|---|
| **Naive RAG** | Retrieve top-K documents by vector similarity; prepend to prompt |
| **HyDE** | Hypothetical Document Embeddings; generates a fake answer first, then retrieves using it |
| **Re-ranking** | Two-stage retrieval: broad recall → cross-encoder re-ranker for precision |
| **GraphRAG** | Organizes documents as a knowledge graph; uses community summaries for global reasoning |
| **Agentic RAG** | LLM decides when and what to retrieve; multi-step retrieval loops |

**Trade-offs:** Reduces hallucination and keeps knowledge fresh without retraining; adds latency and retrieval infrastructure.

---

## 9. Prompt Optimization

Improves output quality or reduces token usage through better prompting strategies.

| Method | Description |
|---|---|
| **Chain-of-Thought (CoT)** | Asks the model to reason step-by-step before answering; improves multi-step reasoning |
| **Few-Shot Prompting** | Provides examples in the prompt; improves task adherence without fine-tuning |
| **Self-Consistency** | Samples multiple CoT paths; majority votes on final answer |
| **Tree of Thoughts (ToT)** | Explores multiple reasoning branches simultaneously |
| **Prompt Compression** | Compresses long contexts using a smaller model (e.g., LLMLingua); reduces token cost |
| **System Prompt Engineering** | Carefully designed system prompts that constrain behavior and improve reliability |

---

## 10. Hardware & Deployment Optimizations

| Method | Description |
|---|---|
| **Tensor Parallelism** | Splits individual layers across GPUs; used for models too large for one device |
| **Pipeline Parallelism** | Splits layers into stages across GPUs; each GPU handles a different set of layers |
| **Operator Fusion** | Merges multiple GPU kernels into one; reduces kernel launch overhead (e.g., in TensorRT) |
| **CUDA Graphs** | Captures the computation graph and replays it; reduces CPU-GPU sync overhead |
| **Model Compilation** | `torch.compile`, TensorRT, or ONNX export; optimizes the execution graph at compile time |
| **Offloading** | Offloads inactive layers to CPU RAM or NVMe during inference; enables larger-than-VRAM models |

---

## 11. Routing & Cost Optimization

Reduces cost and latency at the system level by intelligently directing requests.

| Method | Description |
|---|---|
| **Capability-based routing** | Routes to the cheapest model that can handle the task (e.g., simple queries → small model) |
| **Cost-based routing** | Routes based on token price per provider |
| **Latency-based routing** | Routes to the fastest available provider for real-time use cases |
| **Semantic caching** | Caches LLM responses for semantically similar queries; skips inference entirely on cache hit |
| **Cascading** | Tries a small model first; escalates to a large model only if confidence is low |

**DG relevance:** Directly implements the goals of `model-routing-strategy.md`.

---

## Related Documents

- [PRD](../PRD.md) — Project goals and open questions
- [issues/architecture/model-routing-strategy.md](../../issues/architecture/model-routing-strategy.md) — Routing strategy decision
- [issues/providers/provider-local-llm.md](../../issues/providers/provider-local-llm.md) — Local LLM backend
- [memory/llm-papers.md](../../.deepgruble/memory/llm-papers.md) — Latest research

---

## Sources

**Quantization**
- [GPTQ: Accurate Post-Training Quantization — Frantar et al., 2022](https://arxiv.org/abs/2210.17323)
- [AWQ: Activation-aware Weight Quantization — Lin et al., 2023](https://arxiv.org/abs/2306.00978)
- [BitNet: Scaling 1-bit Transformers — Ma et al., 2024](https://arxiv.org/abs/2402.17764)
- [GGUF format — llama.cpp documentation](https://github.com/ggerganov/llama.cpp)

**Pruning**
- [SparseGPT: Massive Language Models Can Be Accurately Pruned in One Shot — Frantar & Alistarh, 2023](https://arxiv.org/abs/2301.00774)
- [2:4 Structured Sparsity — NVIDIA Ampere Architecture](https://developer.nvidia.com/blog/accelerating-inference-with-sparsity-using-ampere-and-tensorrt/)

**Knowledge Distillation**
- [Distilling the Knowledge in a Neural Network — Hinton et al., 2015](https://arxiv.org/abs/1503.02531)
- [DistilBERT — Sanh et al., 2019](https://arxiv.org/abs/1910.01108)

**Efficient Fine-Tuning (PEFT)**
- [LoRA: Low-Rank Adaptation of Large Language Models — Hu et al., 2021](https://arxiv.org/abs/2106.09685)
- [QLoRA: Efficient Finetuning of Quantized LLMs — Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
- [The Power of Scale for Parameter-Efficient Prompt Tuning — Lester et al., 2021](https://arxiv.org/abs/2104.08691)

**Alignment**
- [Training Language Models to Follow Instructions with Human Feedback (InstructGPT / RLHF) — Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Direct Preference Optimization — Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Constitutional AI — Bai et al., 2022](https://arxiv.org/abs/2212.08073)

**Architecture Optimizations**
- [Flash Attention — Dao et al., 2022](https://arxiv.org/abs/2205.14135)
- [Flash Attention 2 — Dao, 2023](https://arxiv.org/abs/2307.08691)
- [GQA: Training Generalized Multi-Query Transformer Models — Ainslie et al., 2023](https://arxiv.org/abs/2305.13245)
- [Mixtral of Experts — Jiang et al., 2024](https://arxiv.org/abs/2401.04088)
- [Mamba: Linear-Time Sequence Modeling — Gu & Dao, 2023](https://arxiv.org/abs/2312.00752)

**Inference-Time Optimizations**
- [Efficient Memory Management for Large Language Model Serving (PagedAttention / vLLM) — Kwon et al., 2023](https://arxiv.org/abs/2309.06180)
- [Fast Inference from Transformers via Speculative Decoding — Leviathan et al., 2022](https://arxiv.org/abs/2211.17192)

**RAG**
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks — Lewis et al., 2020](https://arxiv.org/abs/2005.11401)
- [From Local to Global: A Graph RAG Approach — Edge et al., 2024](https://arxiv.org/abs/2404.16130)

**Prompt Optimization**
- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models — Wei et al., 2022](https://arxiv.org/abs/2201.11903)
- [Tree of Thoughts — Yao et al., 2023](https://arxiv.org/abs/2305.10601)
- [LLMLingua: Compressing Prompts for Accelerated Inference — Jiang et al., 2023](https://arxiv.org/abs/2310.05736)
