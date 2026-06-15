"""vLLM backend: OpenAI-compatible API with guided decoding."""

from __future__ import annotations

import json

from openai import OpenAI

from .prompt import build_function_selection_prompt, build_args_extraction_prompt, build_parallel_selection_prompt, build_reasoning_prompt
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
        cot: bool = False,
        schema_rich: bool = False,
    ) -> None:
        self._client = OpenAI(base_url=base_url, api_key=api_key)
        self._model = model_name
        self._guided = guided
        self._few_shot = few_shot
        self._cot = cot
        self._schema_rich = schema_rich

    def process(self, prompt: str, functions: list[FunctionDef]) -> FunctionCall:
        fn_name = self._select_function(prompt, functions)
        func = next(f for f in functions if f.name == fn_name)
        args = self._extract_args(prompt, func)
        return FunctionCall(prompt=prompt, fn_name=fn_name, args=args)

    # BFCL parallel queries need up to 8 calls (ground-truth distribution tops
    # out at 8); cap the generated list there so the grammar stays bounded.
    _MAX_PARALLEL_CALLS = 8

    def _build_parallel_calls_schema(self, functions: list[FunctionDef]) -> dict:
        """Schema for a list of calls, each pinned to one function's args.

        Each array element is one of the per-function call objects
        (``name`` fixed with ``const`` + that function's argument schema), so
        the same function may appear multiple times with *different* arguments
        -- the case the previous "select distinct names, extract once" design
        could not express. ``maxItems`` is bounded by the available functions
        only when fewer than the global cap, never by the count of *distinct*
        functions (the old ``min(len(fn_names), 5)`` cap forced a single call
        whenever just one function was available, which deterministically
        failed every parallel item).
        """
        variants = []
        for func in functions:
            variants.append(
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": func.name},
                        "arguments": _build_args_json_schema(func),
                    },
                    "required": ["name", "arguments"],
                    "additionalProperties": False,
                }
            )
        item_schema = variants[0] if len(variants) == 1 else {"oneOf": variants}

        return {
            "type": "object",
            "properties": {
                "calls": {
                    "type": "array",
                    "items": item_schema,
                    "minItems": 1,
                    "maxItems": self._MAX_PARALLEL_CALLS,
                }
            },
            "required": ["calls"],
            "additionalProperties": False,
        }

    def process_parallel(
        self, prompt: str, functions: list[FunctionDef]
    ) -> list[FunctionCall]:
        """Emit all calls for a parallel-category query in one guided pass.

        A single guided_json generation produces
        ``{"calls": [{"name", "arguments"}, ...]}``, where ``name`` may repeat
        and each element carries its own arguments. This replaces the previous
        two-step "select distinct names, then extract args once per name"
        pipeline, which could neither call the same function twice with
        different arguments nor emit more calls than there were distinct
        functions.
        """
        by_name = {f.name: f for f in functions}
        sel_prompt = build_parallel_selection_prompt(functions, prompt)

        kwargs: dict = {}
        if self._guided:
            schema = self._build_parallel_calls_schema(functions)
            kwargs["extra_body"] = {"guided_json": json.dumps(schema)}

        response = self._client.completions.create(
            model=self._model,
            prompt=sel_prompt,
            max_tokens=1024,
            temperature=0,
            **kwargs,
        )
        raw = response.choices[0].text.strip()

        calls = self._parse_parallel_calls(raw)

        results: list[FunctionCall] = []
        for call in calls:
            func = by_name.get(call.get("name"))
            if func is None:
                continue
            args = self._coerce_args(func, dict(call.get("arguments") or {}))
            results.append(FunctionCall(prompt=prompt, fn_name=func.name, args=args))

        # Never return empty: fall back to a single best-effort call so the
        # item is scored against a real attempt rather than a parse error.
        return results or [self.process(prompt, functions)]

    @staticmethod
    def _parse_parallel_calls(raw: str) -> list[dict]:
        """Parse the calls list, tolerating extra text in the no-guided path."""
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            if start == -1:
                return []
            try:
                obj = json.JSONDecoder().raw_decode(raw, start)[0]
            except json.JSONDecodeError:
                return []
        calls = obj.get("calls") if isinstance(obj, dict) else None
        return [c for c in calls if isinstance(c, dict)] if isinstance(calls, list) else []

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

    def _reason_about_args(self, prompt: str, func: FunctionDef) -> str:
        """Free-generation CoT step. Returns reasoning text (capped at 256 tokens)."""
        reasoning_prompt = build_reasoning_prompt(func, prompt)
        response = self._client.completions.create(
            model=self._model,
            prompt=reasoning_prompt,
            max_tokens=256,
            temperature=0,
            stop=["\nJSON:", "\nFunction:"],
        )
        return response.choices[0].text

    def _extract_args(
        self, prompt: str, func: FunctionDef,
    ) -> dict:
        """Extract arguments, optionally using guided_json."""
        schema = _build_args_json_schema(func)
        reasoning = self._reason_about_args(prompt, func) if self._cot else None
        ext_prompt = build_args_extraction_prompt(
            func,
            prompt,
            few_shot=self._few_shot,
            reasoning=reasoning,
            schema_rich=self._schema_rich,
        )

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

        # Without guided decoding the model may emit extra text around JSON,
        # including further few-shot-style examples after the answer. Decode
        # the first complete JSON object rather than slicing to the last brace.
        if not self._guided:
            start = raw.find("{")
            if start == -1:
                raise ValueError(f"no JSON object in completion: {raw!r}")
            args = json.JSONDecoder().raw_decode(raw, start)[0]
        else:
            args = json.loads(raw)

        return self._coerce_args(func, args)

    @staticmethod
    def _coerce_args(func: FunctionDef, args: dict) -> dict:
        """Cast numeric values to match each parameter's declared type."""
        for name, param in func.parameters.items():
            if name not in args:
                continue
            v = args[name]
            if param.type == "number" and isinstance(v, float) and v == int(v):
                args[name] = int(v)
            elif param.type == "float" and isinstance(v, int):
                args[name] = float(v)
        return args
