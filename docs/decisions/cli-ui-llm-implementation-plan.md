---
title: "CLI/UI Flexible LLM Implementation Plan"
category: "architecture"
lastUpdated: "2026-03-07"
status: "active"
---

# CLI/UI Flexible LLM Implementation Plan

## Goal

Enable the DeepGruble CLI/UI to use any LLM backend — Claude, Gemini, OpenAI, or a local model — by selecting it via config, environment variable, or CLI flag, with zero code changes required per provider.

---

## Phase 1: Define the Unified LLM Interface

**What:** A single abstract interface that every provider adapter must implement. All core framework logic calls this interface only — never a provider SDK directly.

**Interface shape (TypeScript):**

```ts
interface LLMProvider {
  complete(messages: Message[], options?: CompletionOptions): Promise<CompletionResult>
  stream(messages: Message[], options?: CompletionOptions): AsyncIterable<string>
  getCapabilities(): ProviderCapabilities
}

interface ProviderCapabilities {
  streaming: boolean
  maxContextTokens: number
  supportsFunctionCalling: boolean
  supportsVision: boolean
  supportsReasoning: boolean       // dedicated reasoning mode (e.g. Claude extended thinking, o3, DeepSeek R1)
  costPerInputToken: number        // USD per token — used by CostStrategy and CascadeStrategy
  costPerOutputToken: number       // USD per token
}

interface CompletionOptions {
  model?: string          // override the default model for this provider
  maxTokens?: number
  temperature?: number
  systemPrompt?: string
}
```

**Deliverable:** `src/llm/interface.ts` — the interface + shared types.

---

## Phase 2: Implement Provider Adapters

One adapter per provider. Each adapter wraps the provider's SDK and translates it into the unified interface.

| Adapter | SDK | Notes |
|---|---|---|
| `ClaudeAdapter` | `@anthropic-ai/sdk` | Current default; maintain full feature parity |
| `GeminiAdapter` | `@google/generative-ai` | Map Gemini's `generateContent` to `complete` |
| `OpenAIAdapter` | `openai` | Covers OpenAI and any OpenAI-compatible endpoint |
| `DeepSeekAdapter` | extends `OpenAIAdapter` | OpenAI-compatible API — minimal override, just base URL + auth |
| `GrokAdapter` | extends `OpenAIAdapter` | OpenAI-compatible API — minimal override, just base URL + auth |
| `LocalLLMAdapter` | HTTP (OpenAI-compatible API) | Targets Ollama, llama.cpp, LM Studio |

**Deliverables:**
- `src/llm/adapters/claude.ts`
- `src/llm/adapters/gemini.ts`
- `src/llm/adapters/openai.ts`
- `src/llm/adapters/deepseek.ts`  ← extends OpenAIAdapter
- `src/llm/adapters/grok.ts`      ← extends OpenAIAdapter
- `src/llm/adapters/local.ts`

Each adapter handles auth, error mapping, and token streaming internally. The rest of the codebase never imports a provider SDK directly.

> **Note:** DeepSeek, Grok, and Local all use the OpenAI-compatible API format. Their adapters extend `OpenAIAdapter` with only a base URL and API key override — no new SDK required.

---

## Phase 3: Provider Registry and Factory

A registry maps provider names to adapter constructors. A factory instantiates the right adapter from config/flags.

```ts
// src/llm/registry.ts
const PROVIDERS = {
  claude:  ClaudeAdapter,
  gemini:  GeminiAdapter,
  openai:  OpenAIAdapter,
  local:   LocalLLMAdapter,
}

function createProvider(config: LLMConfig): LLMProvider {
  const Adapter = PROVIDERS[config.provider]
  if (!Adapter) throw new Error(`Unknown provider: ${config.provider}`)
  return new Adapter(config)
}
```

Adding a new provider = add one entry to `PROVIDERS` + implement the adapter. Nothing else changes.

---

## Phase 4: Configuration Layer

Provider selection is resolved in priority order:

```
CLI flag  >  environment variable  >  config file  >  default (claude)
```

### CLI flag
```bash
dg --llm claude:claude-sonnet-4-6
dg --llm gemini:gemini-2.0-flash
dg --llm openai:gpt-4o
dg --llm local:llama3.2          # Ollama model name
```

Format: `provider:model` — model is optional (falls back to provider's default).

### Environment variable
```bash
DG_LLM_PROVIDER=gemini
DG_LLM_MODEL=gemini-2.0-flash
DG_LLM_BASE_URL=http://localhost:11434   # for local
```

### Config file (`~/.deepgruble/config.json`)
```json
{
  "llm": {
    "provider": "claude",
    "model": "claude-sonnet-4-6"
  }
}
```

**Deliverable:** `src/llm/config.ts` — resolves and validates `LLMConfig` from all three sources.

---

## Phase 5: Router (Optional, Phase 2+)

A router sits on top of the interface and dispatches calls to the right provider based on strategy. Useful once multiple providers are stable.

```ts
interface RoutingStrategy {
  selectProvider(request: CompletionRequest, providers: LLMProvider[]): LLMProvider
}
```

Strategies to implement (per `model-routing-strategy.md`):

| Strategy | Trigger |
|---|---|
| `StaticStrategy` | Always use configured provider (Phase 1 default) |
| `CapabilityStrategy` | Route by required capability (vision, function calling) |
| `CostStrategy` | Route to cheapest provider for estimated token count |
| `CascadeStrategy` | Try small model first, escalate on low confidence |

**Deliverable:** `src/llm/router.ts` — starts as `StaticStrategy`, strategies added incrementally.

---

## Phase 6: CLI/UI Integration

1. **Startup:** CLI resolves `LLMConfig` via Phase 4, creates an `LLMProvider` via the factory, injects it into the app context.
2. **All agent/completion calls** use the injected provider — no direct SDK imports outside `src/llm/adapters/`.
3. **Mid-session switching (optional):** A `/provider` command lets the user swap providers without restarting.

```
> /provider gemini:gemini-2.0-flash
Switched to gemini (gemini-2.0-flash)
```

---

## Phase 7: Testing

| Layer | Approach |
|---|---|
| Adapters | Unit test each adapter against a mock HTTP server / SDK mock |
| Factory | Unit test that correct adapter is instantiated per config |
| Config resolver | Unit test priority order (flag > env > file > default) |
| Integration | One integration test per adapter that calls the real API (opt-in, requires keys) |

A `MockProvider` implementing `LLMProvider` is available for all upstream tests that need an LLM but don't care which one.

---

## Implementation Order

```
1. src/llm/interface.ts            ← foundation, unblocks everything
2. src/llm/adapters/claude.ts      ← migrate existing Claude usage here
3. src/llm/config.ts               ← flag + env + file resolution
4. src/llm/registry.ts             ← factory
5. CLI integration                 ← inject provider at startup
6. src/llm/adapters/openai.ts      ← also covers local (OpenAI-compatible)
7. src/llm/adapters/local.ts       ← Ollama / llama.cpp
8. src/llm/adapters/gemini.ts
9. src/llm/router.ts               ← static strategy first
10. Advanced routing strategies    ← capability, cost, cascade
```

Steps 1–5 deliver a working system where Claude still runs as before, but through the abstraction. Every step after that adds a new provider without touching core logic.

---

## Related Documents

- [PRD.md](../PRD.md) — project goals and non-goals
- [issues/architecture/unified-llm-interface.md](../../issues/architecture/unified-llm-interface.md)
- [issues/architecture/model-routing-strategy.md](../../issues/architecture/model-routing-strategy.md)
- [docs/research/llm-optimization-methods.md](../research/llm-optimization-methods.md) — optimization methods per provider type
