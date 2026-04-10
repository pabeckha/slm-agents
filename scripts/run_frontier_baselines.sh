#!/bin/sh
# Run frontier model baselines on BFCL simple_python.
# This runs LOCALLY (no GPU needed) — just API calls.
# Requires: OPENAI_API_KEY and ANTHROPIC_API_KEY environment variables.

set -e

PROJECT_DIR="$HOME/Documents/slm-agents"
cd "$PROJECT_DIR"

CATEGORY="simple_python"

echo "=== Frontier Baselines on BFCL $CATEGORY ==="
echo "Date: $(date)"

# ── GPT-4.1 ──────────────────────────────────────────────────────────
if [ -n "$OPENAI_API_KEY" ]; then
    echo ""
    echo "=== Running GPT-4.1 ==="
    uv run python -m src.bfcl_adapter \
        --backend gpt \
        --model gpt-4.1 \
        --category "$CATEGORY" \
        --output-dir "data/output/bfcl_frontier"
else
    echo "OPENAI_API_KEY not set, skipping GPT-4.1"
fi

# ── Claude Sonnet 4.6 ────────────────────────────────────────────────
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "=== Running Claude Sonnet 4.6 ==="
    uv run python -m src.bfcl_adapter \
        --backend claude \
        --model claude-sonnet-4-20250514 \
        --category "$CATEGORY" \
        --output-dir "data/output/bfcl_frontier"
else
    echo "ANTHROPIC_API_KEY not set, skipping Claude Sonnet 4.6"
fi

echo ""
echo "=== Done ==="
echo "Results in data/output/bfcl_frontier/"
