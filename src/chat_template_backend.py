"""Chat-template baseline backend (Config B-template).

Prompts the model through its own tool-calling chat template instead of the
generic two-stage prompt, and parses the model's native ``<tool_call>``
output format. No guided decoding is applied.

This is the model-specific counterpart to Config B: it measures how much of
the Base configuration's failure rate is attributable to the generic
integration rather than to the model itself. Together with Config B and
Config CD it gives a three-point comparison under one harness:

    B           generic prompt, free generation        (model-agnostic floor)
    B-template  native template, free generation       (model-specific, no guarantee)
    CD          generic prompt, guided decoding         (model-agnostic, guaranteed format)

Scope: single-call categories only (one FunctionCall per test case). The
first ``<tool_call>`` block in the output is used.
"""

from __future__ import annotations

import json
import re

from openai import OpenAI

from .schema import FunctionCall, FunctionDef

_TOOL_CALL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)


def parse_tool_call(raw: str) -> tuple[str, dict]:
    """Parse the first tool call from a model completion.

    Accepts the native Qwen format::

        <tool_call>
        {"name": "fn", "arguments": {"a": 1}}
        </tool_call>

    Falls back to the first bare JSON object containing "name" and
    "arguments" keys. Raises ValueError if no tool call can be parsed;
    the adapter records such cases as failures, mirroring Config B.
    """
    match = _TOOL_CALL_RE.search(raw)
    candidates = [match.group(1)] if match else []

    if not candidates:
        # Fallback: scan for JSON objects with the expected keys.
        decoder = json.JSONDecoder()
        idx = 0
        while True:
            start = raw.find("{", idx)
            if start == -1:
                break
            try:
                obj, end = decoder.raw_decode(raw[start:])
            except json.JSONDecodeError:
                idx = start + 1
                continue
            if isinstance(obj, dict) and "name" in obj and "arguments" in obj:
                candidates.append(json.dumps(obj))
                break
            idx = start + end

    if not candidates:
        raise ValueError("no <tool_call> block or tool-call JSON found in output")

    obj = json.loads(candidates[0])
    name = obj["name"]
    args = obj["arguments"]
    if isinstance(args, str):
        args = json.loads(args)
    if not isinstance(args, dict):
        raise ValueError(f"tool-call arguments are not an object: {args!r}")
    return name, args


class ChatTemplateBackend:
    """Free generation through the model's native tool-calling template.

    The prompt is rendered client-side with the Hugging Face tokenizer's
    ``apply_chat_template(..., tools=...)`` and sent to the vLLM completions
    endpoint, so the same server job as Config B can be reused without
    extra server flags.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        api_key: str = "EMPTY",
        model_name: str = "Qwen/Qwen2.5-7B-Instruct",
    ) -> None:
        from transformers import AutoTokenizer

        self._client = OpenAI(base_url=base_url, api_key=api_key)
        self._model = model_name
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)

    def _build_prompt(self, prompt: str, raw_functions: list[dict]) -> str:
        tools = [{"type": "function", "function": fn} for fn in raw_functions]
        return self._tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tools=tools,
            add_generation_prompt=True,
            tokenize=False,
        )

    def process_raw(
        self,
        prompt: str,
        functions: list[FunctionDef],
        raw_functions: list[dict],
    ) -> FunctionCall:
        """Run one single-call test case through the native template."""
        templated = self._build_prompt(prompt, raw_functions)

        response = self._client.completions.create(
            model=self._model,
            prompt=templated,
            max_tokens=512,
            temperature=0,
            stop=["<|im_end|>"],
        )
        raw = response.choices[0].text

        name, args = parse_tool_call(raw)

        # Apply the same numeric type casting as the other backends so that
        # scoring differences reflect the prompting strategy, not harness
        # post-processing.
        func = next((f for f in functions if f.name == name), None)
        if func is not None:
            for pname, param in func.parameters.items():
                if pname not in args:
                    continue
                v = args[pname]
                if param.type == "number" and isinstance(v, float) and v == int(v):
                    args[pname] = int(v)
                elif param.type == "float" and isinstance(v, int):
                    args[pname] = float(v)

        return FunctionCall(prompt=prompt, fn_name=name, args=args)
