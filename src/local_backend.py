"""Local backend: HuggingFace model with token-level constrained decoding."""

from __future__ import annotations

from .decoder import ConstrainedDecoder
from .pipeline import process_prompt
from .schema import FunctionCall, FunctionDef


class LocalBackend:
    """Wraps Small_LLM_Model + ConstrainedDecoder into the Backend protocol."""

    def __init__(self, model: object) -> None:
        self._model = model
        self._decoder = ConstrainedDecoder(model)

    def process(self, prompt: str, functions: list[FunctionDef]) -> FunctionCall:
        return process_prompt(prompt, functions, self._decoder, self._model)
