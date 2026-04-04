"""Backend protocol for function-calling inference."""

from __future__ import annotations

from typing import Protocol

from .schema import FunctionCall, FunctionDef


class Backend(Protocol):
    """Minimal interface that both local and vLLM backends satisfy."""

    def process(self, prompt: str, functions: list[FunctionDef]) -> FunctionCall: ...
