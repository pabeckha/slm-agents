---
title: "ADR: Local LLM Runtime"
category: "architecture"
lastUpdated: "2026-03-07"
status: "active"
---

# ADR: Local LLM Runtime

## Status

**Accepted** — 2026-03-07

---

## Context

The local/self-hosted backend requires a runtime that can serve open-weight models via an API. The adapter must fit into the unified `LLMProvider` interface. Candidates evaluated:

| Runtime | API format | GPU support | CPU support | Model library | Ease of setup |
|---|---|---|---|---|---|
| **Ollama** | OpenAI-compatible | ✓ | ✓ | Large (Llama, Qwen, Phi, Gemma, Mistral…) | Very easy (1 command) |
| **llama.cpp** | Own HTTP server | ✓ | ✓ (optimized) | Any GGUF | Medium |
| **LM Studio** | OpenAI-compatible | ✓ | ✓ | Large | Easy (GUI) |
| **vLLM** | OpenAI-compatible | ✓ only | ✗ | HuggingFace | Complex |
| **TGI (HuggingFace)** | Own REST | ✓ only | ✗ | HuggingFace | Complex |

---

## Decision

**Ollama** as the primary local runtime.

The `LocalLLMAdapter` targets Ollama's OpenAI-compatible API endpoint (`/v1/chat/completions`). This means:

- `LocalLLMAdapter` is a thin extension of `OpenAIAdapter` — only the base URL and auth differ
- Any OpenAI-compatible runtime (LM Studio, llama.cpp server, vLLM) works as a drop-in replacement by changing `DG_LLM_BASE_URL`
- No new SDK required

**Recommended models via Ollama:**

| Use Case | Model | Min. VRAM |
|---|---|---|
| General tasks | `qwen2.5:72b-instruct-q4_K_M` | 48GB (2× RTX 4090) |
| Reasoning | `deepseek-r1:70b-q4_K_M` | 48GB (2× RTX 4090) |
| Coding | `qwen2.5-coder:32b-instruct-q4_K_M` | 24GB (1× RTX 4090) |
| Constrained / edge | `phi4:14b-q4_K_M` | 12GB (RTX 3060) |
| On-device | `phi4-mini:3.8b` | CPU / NPU |

---

## Consequences

**Positive:**
- `LocalLLMAdapter` reuses `OpenAIAdapter` — minimal new code
- Any OpenAI-compatible server works without adapter changes — just `DG_LLM_BASE_URL`
- Ollama is the de-facto standard for local LLM inference on developer machines
- Works on CPU (no GPU required for small models)

**Negative:**
- Ollama must be running locally before the local adapter is usable
- Quality and speed are hardware-dependent — no SLA
- Context window limited by available VRAM

---

## Alternatives Considered

| Runtime | Rejected because |
|---|---|
| llama.cpp | Lower-level; no out-of-the-box OpenAI-compatible server in all configs |
| vLLM | GPU-only; complex setup; overkill for local dev use |
| TGI | Non-standard API format; heavier infrastructure |
| LM Studio | GUI-only distribution; not scriptable in CI |

---

## Related Documents

- [PRD.md](../PRD.md) — § Local Backend
- [docs/research/llm-landscape.md](../research/llm-landscape.md) — SLM options
- [docs/architecture/cli-ui-llm-implementation-plan.md](cli-ui-llm-implementation-plan.md) — Phase 2, LocalLLMAdapter
- [issues/providers/provider-local-llm.md](../../issues/providers/provider-local-llm.md)
