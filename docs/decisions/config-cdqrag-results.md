# Config CD+Q+RAG Results — RAG Top-5 Retrieval + AWQ INT4 + Guided Decoding

**Date**: 2026-04-13
**Jobs**: 28193415 (crashed — SentenceTransformer OOM on GPU), 28194208 (completed)
**Model**: Qwen/Qwen2.5-7B-Instruct-AWQ via vLLM 0.8.5
**Backend**: `src/vllm_backend.py` (guided_choice + guided_json, quantization=awq_marlin, enforce-eager)
**Benchmark**: BFCL v4 simple_python (400 test cases)
**Configuration**: Config CD+Q+RAG — AWQ INT4 quantization with constrained decoding + RAG top-5 retrieval

## Setup

Instead of providing each test case with its ground-truth function definition (as in all prior configs), RAG pools all 370 unique functions from simple_python into a FAISS index using `sentence-transformers/all-MiniLM-L6-v2` embeddings. At inference time, the query is embedded and the top-5 most similar functions are retrieved as candidates. The model must select and call the correct function from these 5 candidates.

This simulates a realistic tool-calling scenario where the agent faces a catalog of tools rather than being given the exact function.

## Results

**AST accuracy: 47.8% (191/400)**
**RAG recall@5: 97.2% (389/400)**

### Comparison across configs

| Config | Accuracy | Correct | Candidates | Delta vs CD+Q |
|--------|----------|---------|------------|---------------|
| B (no guided) | 1.5% | 6/400 | 1 (oracle) | -70.5 pp |
| PE (few-shot + guided) | 70.25% | 281/400 | 1 (oracle) | -1.75 pp |
| CD (guided, full precision) | 72.75% | 291/400 | 1 (oracle) | +0.75 pp |
| CD+Q (guided, AWQ INT4) | 72.0% | 288/400 | 1 (oracle) | baseline |
| **CD+Q+RAG (guided, AWQ INT4, top-5)** | **47.8%** | **191/400** | **5 (retrieved)** | **-24.2 pp** |

### Failure breakdown

Of 400 test cases:
- **264** (66.0%) — identical output to CD+Q baseline (model unaffected by extra candidates)
- **128** (32.0%) — model selected a **wrong function** from the retrieved candidates
- **8** (2.0%) — model selected the correct function but with different (wrong) parameters

Of the 128 wrong-function cases, the model consistently picks a semantically similar but incorrect function. Examples:
- `calculate_triangle_area` → `calculate_area` (more generic variant)
- `algebra.quadratic_roots` → `solve_quadratic_equation` (synonym)
- `geometry.circumference` → `calculate_circumference` (different namespace)
- `calculus.derivative` → `calculate_derivative` (flattened name)

### RAG retrieval quality

Recall@5 is 97.2% — the retriever fails to include the correct function for only 11 cases:
`calculate_density`, `calculate_probability`, `probabilities.calculate_single`, `probability_of_event`, `event_finder.find_upcoming`, `sentiment_analysis`, `get_event_date`, `board_game_info`, `recipe_search`, `cooking_conversion.convert`, `find_recipe`.

These are mostly domain-ambiguous functions where the query doesn't provide enough lexical overlap with the function signature.

## Analysis

The accuracy drop from 72.0% to 47.8% is almost entirely caused by **function disambiguation failure**, not retrieval failure. RAG recall@5 at 97.2% means the pipeline surfaces the correct tool nearly every time — but the model picks a wrong sibling function 32% of the time when presented with multiple similar options.

This reveals a fundamental SLM limitation: when multiple functions share semantic similarity (e.g., `calculate_area` vs `calculate_triangle_area` vs `calc_area_triangle`), the 7B model cannot reliably distinguish which one matches the user's intent. With oracle selection (1 candidate), this problem doesn't exist.

The 8 cases where the model selected the correct function but produced wrong parameters suggest that expanding the candidate set also introduces minor distraction effects on parameter generation, though this is a small fraction.

### Infrastructure note

The first run (job 28193415) crashed because `SentenceTransformer` defaulted to GPU, but vLLM held the device in exclusive mode. Fixed by forcing `device="cpu"` in `src/rag.py` — the MiniLM-L6-v2 embedder is only 80MB and processes 370 short strings, so CPU is adequate.

## Implications for Thesis

### RQ (RAG as tool selection mechanism)

RAG retrieval works well (97.2% recall@5) but the SLM cannot disambiguate among retrieved candidates. This means RAG alone is insufficient for realistic tool selection with SLMs — the model needs either:
1. Better function discrimination (via fine-tuning, i.e., LoRA on tool-selection data)
2. Fewer candidates (top-1 or top-2 instead of top-5)
3. Stronger prompting to help the model distinguish between similar functions

### Cascade architecture

This result strengthens the cascade argument. In a cascade, the SLM handles cases where tool selection is unambiguous (the 66% that matched baseline), while ambiguous cases (the 32% with similar candidate functions) get escalated to a frontier model that can better discriminate between semantically similar tools.

The 97.2% recall@5 means the retrieval stage is not the bottleneck — the cascade's routing decision should be based on candidate similarity (high similarity among retrieved functions → escalate).

## Result Files

- Results: `data/output/bfcl_rag/Qwen_Qwen2.5-7B-Instruct-AWQ/non_live/BFCL_v4_simple_python_result.json`
- Scores: `data/output/bfcl_rag/scores/simple_python_scores.json`
- Run manifest: `data/output/bfcl_rag/runs/2026-04-13T07-08-50_Qwen_Qwen2.5-7B-Instruct-AWQ_simple_python_guided_rag_top5.json`
- FAISS index: `data/output/bfcl_rag/rag_index/`
- Logs: `logs/bfcl_rag_28193415.out` (crashed), `logs/bfcl_rag_28194208.out` (completed)
