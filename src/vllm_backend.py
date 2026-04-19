"""vLLM backend: OpenAI-compatible API with guided decoding."""

from __future__ import annotations

import json

from openai import OpenAI

from .prompt import build_function_selection_prompt, build_args_extraction_prompt, build_parallel_selection_prompt
from .schema import FunctionCall, FunctionDef

# Map our simple type names to JSON Schema types.
_TYPE_MAP = {
    "number": "number",
    "string": "string",
    "boolean": "boolean",
    "integer": "integer",
    "float": "number",
    "array": "array",
    "dict": "object",
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

    required = func.required if func.required is not None else list(func.parameters.keys())

    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


class VLLMBackend:
    """Calls a vLLM server using guided_choice and guided_json."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        api_key: str = "EMPTY",
        model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        guided: bool = True,
        few_shot: bool = False,
    ) -> None:
        self._client = OpenAI(base_url=base_url, api_key=api_key)
        self._model = model_name
        self._guided = guided
        self._few_shot = few_shot

    def process(self, prompt: str, functions: list[FunctionDef]) -> FunctionCall:
        fn_name = self._select_function(prompt, functions)
        func = next(f for f in functions if f.name == fn_name)
        args = self._extract_args(prompt, func)
        return FunctionCall(prompt=prompt, fn_name=fn_name, args=args)

    def process_parallel(
        self, prompt: str, functions: list[FunctionDef]
    ) -> list[FunctionCall]:
        """Select and call multiple functions for parallel-category queries.

        Step 1: guided_json to get list of function names to call.
        Step 2: extract args for each selected function (same as single-call path).
        """
        fn_names = [f.name for f in functions]

        calls_schema = {
            "type": "object",
            "properties": {
                "calls": {
                    "type": "array",
                    "items": {"type": "string", "enum": fn_names},
                    "minItems": 1,
                    "maxItems": min(len(fn_names), 5),
                }
            },
            "required": ["calls"],
            "additionalProperties": False,
        }

        sel_prompt = build_parallel_selection_prompt(functions, prompt)
        kwargs: dict = {}
        if self._guided:
            kwargs["extra_body"] = {"guided_json": json.dumps(calls_schema)}

        response = self._client.completions.create(
            model=self._model,
            prompt=sel_prompt,
            max_tokens=200,
            temperature=0,
            **kwargs,
        )
        raw = response.choices[0].text.strip()

        try:
            selected_names = json.loads(raw)["calls"]
        except (json.JSONDecodeError, KeyError, TypeError):
            # Fallback: try to pick names mentioned in the raw output.
            selected_names = [n for n in fn_names if n in raw] or fn_names[:1]

        results: list[FunctionCall] = []
        for name in selected_names:
            func = next((f for f in functions if f.name == name), None)
            if func is None:
                continue
            args = self._extract_args(prompt, func)
            results.append(FunctionCall(prompt=prompt, fn_name=name, args=args))

        return results or [self.process(prompt, functions)]

    def _select_function(
        self, prompt: str, functions: list[FunctionDef],
    ) -> str:
        """Pick the function name, optionally using guided_choice."""
        fn_names = [f.name for f in functions]
        sel_prompt = build_function_selection_prompt(functions, prompt)

        kwargs: dict = {}
        if self._guided:
            kwargs["extra_body"] = {"guided_choice": fn_names}

        response = self._client.completions.create(
            model=self._model,
            prompt=sel_prompt,
            max_tokens=50,
            temperature=0,
            **kwargs,
        )
        raw = response.choices[0].text.strip()

        # Without guided decoding the model may wrap the name in quotes or
        # extra text.  Try to match against valid function names.
        if raw in fn_names:
            return raw
        for name in fn_names:
            if name in raw:
                return name
        return raw

    def _extract_args(
        self, prompt: str, func: FunctionDef,
    ) -> dict:
        """Extract arguments, optionally using guided_json."""
        schema = _build_args_json_schema(func)
        ext_prompt = build_args_extraction_prompt(func, prompt, few_shot=self._few_shot)

        kwargs: dict = {}
        if self._guided:
            kwargs["extra_body"] = {"guided_json": json.dumps(schema)}

        response = self._client.completions.create(
            model=self._model,
            prompt=ext_prompt,
            max_tokens=512,
            temperature=0,
            **kwargs,
        )
        raw = response.choices[0].text.strip()

        # Without guided decoding the model may emit extra text around JSON.
        if not self._guided:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                raw = raw[start:end]

        args = json.loads(raw)

        # Cast numeric types to match the declared parameter type.
        for name, param in func.parameters.items():
            if name not in args:
                continue
            v = args[name]
            if param.type == "number" and isinstance(v, float) and v == int(v):
                args[name] = int(v)
            elif param.type == "float" and isinstance(v, int):
                args[name] = float(v)

        return args
