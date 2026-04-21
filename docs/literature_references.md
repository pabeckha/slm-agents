# Literature References

Key papers for the thesis, organized by topic area.

---

## 1. Constrained Decoding & Structured Output

- **Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning**
  Geng et al., 2023, 113 citations
  Foundational work showing GCD as a unified framework for structured tasks, outperforming fine-tuned models.
  https://consensus.app/papers/details/002a1b93a50052b2806289c475dd8c9e/

- **Automata-based constraints for language model decoding**
  Koo et al., 2024, 38 citations
  Derives efficient closed-form automata solution for regular languages (API calls, JSON, YAML). Compiles constraints ~7,000x faster than prior work, provably correct. Directly relevant to vLLM guided decoding implementation.
  https://consensus.app/papers/details/bfff47cf239d588fb27ce2c4af8d47a5/

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

- **A Unified Approach to Routing and Cascading for LLMs**
  Dekoninck et al., 2024, 14 citations
  Derives theoretically optimal cascade routing strategy, proves optimality conditions. Provides formal framework for the SLM+frontier cascade framing in the thesis.
  https://consensus.app/papers/details/a2db570f3cce5fedb139a619a780512a/

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
  Warns that smaller models suffer severe accuracy drops at 4-bit. AWQ tends to outperform GPTQ. At 7B scale, performance is stable — consistent with thesis CD+Q result (−0.5 pp).
  https://consensus.app/papers/details/bbe8413a9dea5b5b9f07ae12508715ab/

- **Quantization Meets Reasoning: Exploring LLM Low-Bit Quantization Degradation for Mathematical Reasoning**
  Li et al., 2025, 14 citations
  AWQ/GPTQ can cause up to 32.39% accuracy degradation (avg 11.31%) on reasoning tasks. Tool calling is simpler than math reasoning, explaining why thesis sees only −0.5 pp. Fine-tuning quantized models on 545 task-specific examples recovers performance.
  https://consensus.app/papers/details/d250021623115baca6578e8b43ada985/

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

- **Dynamic Tool Dependency Retrieval for Efficient Function Calling**
  Patel et al., 2025, 1 citation
  Finds static RAG retrieval fails to capture multi-step tool dependencies and misleads the agent. Explains thesis RAG negative result: BFCL provides all tools in context, so retrieval creates disambiguation noise rather than reducing it.
  https://consensus.app/papers/details/189e96a9643c54fb8c0cf86b61889179/

- **Graph RAG-Tool Fusion**
  Lumer et al., 2025, 6 citations
  Combines vector retrieval with graph traversal to capture tool dependencies. +71.7% over naïve RAG on ToolLinkOS. Suggests the RAG approach requires structural tool dependency modelling to work.
  https://consensus.app/papers/details/a00e682250415f8086e905d2035ddd4d/

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

---

## 10. Methods Considered but Out of Scope

- **Direct Preference Optimization (DPO)**
  Rafailov et al., 2023, 6,110 citations
  Natural upgrade over SFT LoRA: trains on preference pairs (correct vs. wrong call) rather than supervised targets. Typically outperforms SFT on instruction-following. Requires generating negative examples. Out of scope due to time constraints — cite as future work in Discussion.
  https://consensus.app/papers/details/1ee8db4229ee52ec8af09f4e12828ff2/

- **Speculative Decoding**
  Chen et al., 2023, 609 citations
  2–2.5x inference speedup via draft-then-verify with no accuracy change. Orthogonal to thesis RQs (accuracy-focused). Mention in Discussion as complementary deployment optimization.
  https://consensus.app/papers/details/98fc924b7305573faada2a6f2efbcc69/

- **Multi-LLM Agent Decomposition (Planner / Caller / Summarizer)**
  Shen et al., 2024, 84 citations
  Decomposes tool use into three specialized small models. Alternative architecture to the single-SLM + cascade design. Cite in Background as an alternative approach; not a missing experiment.
  https://consensus.app/papers/details/f83cb1d0436f5385a63003d4a32f2586/

---

## 11. Method Validation Notes (April 2026)

How the thesis results align with the literature, for use when writing the Discussion chapter.

### Constrained decoding (+71.25 pp over baseline)
The result is directly predicted. Geng et al. show GCD "substantially outperforms unconstrained LMs" on structured tasks. Koo et al. prove correctness and efficiency for exactly the API-call / JSON use case. The Sharma et al. 2025 survey names Qwen-2.5-7B and BFCL v3/v4 explicitly and states guided decoding "often lets SLMs match or surpass LLMs on tool use" — which is what the thesis observes (7B matching GPT-4.1 and Claude Sonnet on simple_python).

### AWQ quantization (−0.5 pp, −63.5% VRAM)
AWQ (Lin et al.) is the methodological standard. Lee et al. warn of severe drops at 4-bit for *smaller* models but note 7B-scale models maintain stable performance. Li et al. report up to 32.39% degradation on *mathematical reasoning* — tool calling is structurally simpler (schema-constrained generation vs. open-ended arithmetic), which explains why the thesis sees only −0.5 pp. The result is consistent with, and explained by, the literature.

### LoRA fine-tuning (results pending job 28248383)
Hu et al. is the foundation (14,222 citations). The Sharma et al. survey recommends LoRA/QLoRA as the standard lightweight adaptation method for SLM agent stacks. Li et al. show fine-tuning a quantized model on ~500 task-specific examples fully recovers quantization-induced accuracy loss — relevant if CD+Q+FT outperforms CD+Q by a significant margin.

### RAG negative result (−24.5 pp)
The negative result has a clean literature explanation: Patel et al. identify that static retrieval "fails to capture multi-step tool dependencies and misleads the agent." In BFCL simple_python, the model already receives all tools in context; retrieval replaces this full context with a subset, creating disambiguation noise instead of reducing it. Graph RAG-Tool Fusion (Lumer et al.) suggests that tool-dependency-aware retrieval would be needed to make RAG helpful here. Cite both papers when explaining the failure in the Discussion chapter.

### Cascade architecture framing
Three high-citation papers directly support the cascade framing: FrugalGPT (Chen et al., 353 citations) introduced LLM cascades; Hybrid LLM (Ding et al., 167 citations) showed 40% fewer frontier calls with no quality drop; Dekoninck et al. proved theoretical optimality of cascade routing. The thesis can position itself as providing empirical grounding for these frameworks in the tool-calling / agentic domain, where cascade design depends on knowing the SLM capability boundary — which is exactly what the ablation matrix establishes.

### CoT / ITC negative result (−7.25 pp)
Single-turn BFCL tasks require generating a precise function call, not reasoning steps. Chain-of-thought adds tokens that displace or corrupt the constrained JSON generation. The Wei et al. CoT paper (foundational, 13,442 citations) shows CoT helps complex multi-step reasoning — but function call generation is a retrieval/formatting task, not a reasoning task. ReAct (Yao et al.) is the appropriate CoT variant for multi-turn agentic tasks (τ-bench), not single-call BFCL. This distinction is worth a paragraph in the Discussion.
