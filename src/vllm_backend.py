"""vLLM backend: OpenAI-compatible API with guided decoding."""

from __future__ import annotations

import json

from openai import OpenAI

from .prompt import build_function_selection_prompt, build_args_extraction_prompt
from .schema import FunctionCall, FunctionDef

# Map our simple type names to JSON Schema types.
_TYPE_MAP = {
    "number": "number",
    "string": "string",
    "boolean": "boolean",
    "integer": "integer",
}


def _build_args_json_schema(func: FunctionDef) -> dict:
    """Convert a FunctionDef's parameters to a JSON Schema object.

    Example output for fn_add_numbers(a: number, b: number)::

        {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"],
            "additionalProperties": false
        }
    """
    properties = {}
    for name, param in func.parameters.items():
        json_type = _TYPE_MAP.get(param.type, "string")
        properties[name] = {"type": json_type}

    return {
        "type": "object",
        "properties": properties,
        "required": list(func.parameters.keys()),
        "additionalProperties": False,
    }


class VLLMBackend:
    """Calls a vLLM server using guided_choice and guided_json."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        api_key: str = "EMPTY",
        model_name: str = "Qwen/Qwen2.5-7B-Instruct",
    ) -> None:
        self._client = OpenAI(base_url=base_url, api_key=api_key)
        self._model = model_name

    def process(self, prompt: str, functions: list[FunctionDef]) -> FunctionCall:
        fn_name = self._select_function(prompt, functions)
        func = next(f for f in functions if f.name == fn_name)
        args = self._extract_args(prompt, func)
        return FunctionCall(prompt=prompt, fn_name=fn_name, args=args)

    def _select_function(
        self, prompt: str, functions: list[FunctionDef],
    ) -> str:
        """Pick the function name using guided_choice."""
        fn_names = [f.name for f in functions]
        sel_prompt = build_function_selection_prompt(functions, prompt)

        response = self._client.completions.create(
            model=self._model,
            prompt=sel_prompt,
            max_tokens=50,
            temperature=0,
            extra_body={"guided_choice": fn_names},
        )
        return response.choices[0].text.strip()

    def _extract_args(
        self, prompt: str, func: FunctionDef,
    ) -> dict:
        """Extract all arguments at once using guided_json."""
        schema = _build_args_json_schema(func)
        ext_prompt = build_args_extraction_prompt(func, prompt)

        response = self._client.completions.create(
            model=self._model,
            prompt=ext_prompt,
            max_tokens=512,
            temperature=0,
            extra_body={"guided_json": json.dumps(schema)},
        )
        raw = response.choices[0].text.strip()
        args = json.loads(raw)

        # Cast number types: JSON parsing returns float, convert int-valued floats.
        for name, param in func.parameters.items():
            if param.type == "number" and name in args:
                v = args[name]
                if isinstance(v, float) and v == int(v):
                    args[name] = int(v)

        return args
