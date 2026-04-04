# Literature References

Key papers for the thesis, organized by topic area.

---

## 1. Constrained Decoding & Structured Output

- **Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning**
  Geng et al., 2023, 113 citations
  Foundational work showing GCD as a unified framework for structured tasks, outperforming fine-tuned models.
  https://consensus.app/papers/details/002a1b93a50052b2806289c475dd8c9e/

- **SLOT: Structuring the Output of Large Language Models**
  Wang et al., 2025, 6 citations
  Shows even Llama-3.2-1B can match proprietary models with constrained decoding. Directly relevant to SLM thesis.
  https://consensus.app/papers/details/a8afb9b17086546995025c4951adf6d4/

- **Type-Constrained Code Generation with Language Models**
  Mündler et al., 2025, 17 citations
  Leverages type systems to guide code generation via constrained decoding, reducing compilation errors by >50%.
  https://consensus.app/papers/details/8079b82de15d5280a3ad19c8d3a19e65/

## 2. SLMs for Tool Calling (Core Topic)

- **Small Language Models for Agentic Systems: A Survey** ⭐ MUST-READ
  Sharma et al., 2025, 0 citations
  Comprehensive survey covering SLMs + guided decoding + BFCL + LoRA + cascade routing. Covers nearly entire thesis scope.
  https://consensus.app/papers/details/e2b6a6f169825d17a89b8658099dd356/

- **Optimizing Small Language Models for In-Vehicle Function-Calling**
  Khiabani et al., 2025, 3 citations
  Pruning + quantization + fine-tuning for SLM function calling on edge devices (Phi-3 mini).
  https://consensus.app/papers/details/a4e4759e72ad5b078e3f25d07b11d360/

- **Improving Small-Scale LLMs Function Calling for Reasoning Tasks**
  Manduzio et al., 2024, 6 citations
  Trains smaller models via DPO on reasoning chains from larger models. Framework with step-by-step function calling.
  https://consensus.app/papers/details/529ec91c9cdb59d186035600d54ed04d/

## 3. Cascade / Routing Architectures

- **FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance**
  Chen et al., 2023, 353 citations
  Seminal paper on LLM cascades — 98% cost reduction matching GPT-4 performance.
  https://consensus.app/papers/details/724bf395d6a95d449b6ac241f2a115d4/

- **Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing**
  Ding et al., 2024, 167 citations
  Router-based small/large model switching, 40% fewer calls to large model with no quality drop.
  https://consensus.app/papers/details/9123c513bf805feda0288b7d0170a592/

- **Large Language Model Cascades with Mixture of Thoughts Representations for Cost-efficient Reasoning**
  Yue et al., 2023, 108 citations
  Answer consistency as difficulty signal for cascading. CoT + PoT mixture.
  https://consensus.app/papers/details/8c3c6384ae0f5b76ae62b62820e26738/

## 4. LoRA / Fine-Tuning

- **LoRA: Low-Rank Adaptation of Large Language Models**
  Hu et al., 2021, 14,222 citations
  Foundational paper. 10,000x fewer trainable parameters, no additional inference latency.
  https://consensus.app/papers/details/1431353d4e615dc1bad45d8db1506cea/

- **Chain of LoRA: Efficient Fine-tuning of Language Models via Residual Learning**
  Xia et al., 2024, 81 citations
  Iterative LoRA optimization to bridge gap with full fine-tuning, no additional cost.
  https://consensus.app/papers/details/9c5d4e99bef25f99b8e3fa5e92500b52/

- **LongLoRA: Efficient Fine-tuning of Long-Context Large Language Models**
  Chen et al., 2023, 208 citations
  Extends context with sparse local attention + improved LoRA. Relevant for long tool schema contexts.
  https://consensus.app/papers/details/4cee274080f252b8bfe64049eb2e489b/

## 5. Quantization

- **AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration**
  Lin et al., 2023, 550 citations
  Primary quantization method. 1.45x speedup over GPTQ, hardware-friendly, preserves generalization.
  https://consensus.app/papers/details/d6c61576c34d5d5aa3d4760a16aa3585/

- **GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers**
  Frantar et al., 2022, 1,375 citations
  One-shot weight quantization via approximate second-order info. Key baseline to compare against AWQ.
  https://consensus.app/papers/details/27999f5e6a3d5d5d956fc30be1f3e6f2/

- **Exploring the Trade-Offs: Quantization Methods, Task Difficulty, and Model Size**
  Lee et al., 2024, 3 citations
  Warns that smaller models suffer severe accuracy drops at 4-bit. AWQ tends to outperform GPTQ.
  https://consensus.app/papers/details/bbe8413a9dea5b5b9f07ae12508715ab/

## 6. Knowledge Distillation

- **Teaching Small Language Models to Reason**
  Magister et al., 2022, 304 citations
  CoT distillation from PaLM 540B/GPT-3 175B to smaller models. T5 XXL accuracy 8% → 22% on GSM8K.
  https://consensus.app/papers/details/95dc59aca07751638e93e2596619ce3b/

- **Symbolic Chain-of-Thought Distillation: Small Models Can Also "Think" Step-by-Step**
  Li et al., 2023, 182 citations
  Shows 125M–1.3B models benefit from teacher CoT. Sampling many chains per instance is key.
  https://consensus.app/papers/details/1007f72a9a4b5716b2c030a674b75e11/

- **SCOTT: Self-Consistent Chain-of-Thought Distillation**
  Wang et al., 2023, 114 citations
  Faithful distillation via contrastive decoding + counterfactual reasoning objective.
  https://consensus.app/papers/details/dce0436ea76552bc88c4e50afcdf419f/

## 7. RAG for Tool Selection

- **RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via Retrieval-Augmented Generation**
  Gan et al., 2025, 8 citations
  Semantic retrieval to select relevant tools. Cuts prompt tokens by 50%, triples tool selection accuracy.
  https://consensus.app/papers/details/4b802b3e07195fddbea8438a18d45a47/

- **ToolGen: Unified Tool Retrieval and Calling via Generation**
  Wang et al., 2024, 26 citations
  Alternative approach: embeds tools as tokens for generative retrieval. 47,000+ tools.
  https://consensus.app/papers/details/fedacdb03b665b9ab865dc74616e88ac/

- **A study on classification based concurrent API calls and optimal model combination for tool augmented LLMs**
  Go et al., 2025, 0 citations
  Multi-step reasoning with optimal model combinations per stage. 4.4-9.3% accuracy improvement.
  https://consensus.app/papers/details/5e65f2caa0f052179fc7deb8adfabb5c/

## 8. Reasoning & Prompting

- **Chain of Thought Prompting Elicits Reasoning in Large Language Models**
  Wei et al., 2022, 13,442 citations
  Foundational CoT paper. Few-shot CoT achieves SOTA on math reasoning.
  https://consensus.app/papers/details/5537f874605a58abbbe3a1019b3d9f90/

- **ReAct: Synergizing Reasoning and Acting in Language Models**
  Yao et al., 2022, 4,591 citations
  Interleaved reasoning + actions. Used for multi-turn evaluation (tau-bench).
  https://consensus.app/papers/details/925849938da857b9a1538f2a0a5f652f/

- **Iteratively Prompt Pre-trained Language Models for Chain of Thought**
  Wang et al., 2022, 113 citations
  Context-aware iterative prompting for multi-step reasoning.
  https://consensus.app/papers/details/8cba7426efab58ada77be3ad9008b1a8/

## 9. Benchmarks & Evaluation

- **ToolACE: Winning the Points of LLM Function Calling**
  Liu et al., 2024, 91 citations
  8B model achieving SOTA on BFCL via synthetic training data pipeline.
  https://consensus.app/papers/details/ed221278fc2c588db7bbe04f8b212243/

- **On the Robustness of Agentic Function Calling**
  Rabinovich et al., 2025, 4 citations
  Identifies robustness weaknesses in BFCL evaluation methodology.
  https://consensus.app/papers/details/a2c78c4bb56e5ab39a92960d7455e778/

- **Granite-Function Calling Model: Introducing Function Calling Abilities via Multi-task Learning**
  Abdelaziz et al., 2024, 39 citations
  Multi-task training for function calling. Top results on BFCL among open models.
  https://consensus.app/papers/details/f79187a146c45668aab8f705af2c9769/
