"""Frontier model backends using native tool-calling APIs.

Provides Claude and GPT backends for establishing frontier baselines
on BFCL evaluation.  Uses each model's native tool-calling mechanism
for fair comparison against constrained-decoded SLMs.
"""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from .schema import FunctionCall, FunctionDef, FunctionParameter


def _function_def_to_openai_tool(func: FunctionDef) -> dict:
    """Convert a FunctionDef to OpenAI tool format."""
    properties: dict[str, dict[str, str]] = {}
    for name, param in func.parameters.items():
        json_type = {
            "number": "number",
            "string": "string",
            "boolean": "boolean",
            "integer": "integer",
            "float": "number",
            "array": "array",
            "dict": "object",
        }.get(param.type, "string")
        properties[name] = {"type": json_type}

    required = func.required if func.required is not None else list(func.parameters.keys())

    return {
        "type": "function",
        "function": {
            "name": func.name,
            "description": func.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def _function_def_to_anthropic_tool(func: FunctionDef) -> dict:
    """Convert a FunctionDef to Anthropic tool format."""
    properties: dict[str, dict[str, str]] = {}
    for name, param in func.parameters.items():
        json_type = {
            "number": "number",
            "string": "string",
            "boolean": "boolean",
            "integer": "integer",
            "float": "number",
            "array": "array",
            "dict": "object",
        }.get(param.type, "string")
        properties[name] = {"type": json_type}

    required = func.required if func.required is not None else list(func.parameters.keys())

    return {
        "name": func.name,
        "description": func.description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


class GPTBackend:
    """Calls OpenAI GPT models using native tool calling."""

    def __init__(
        self,
        model_name: str = "gpt-4.1",
        api_key: str | None = None,
    ) -> None:
        self._client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self._model = model_name

    def process(self, prompt: str, functions: list[FunctionDef]) -> FunctionCall:
        tools = [_function_def_to_openai_tool(f) for f in functions]

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
            tool_choice="required",
            temperature=0,
        )

        tool_call = response.choices[0].message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        return FunctionCall(
            prompt=prompt,
            fn_name=tool_call.function.name,
            args=args,
        )


class ClaudeBackend:
    """Calls Anthropic Claude models using native tool use."""

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-20250514",
        api_key: str | None = None,
    ) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ImportError(
                "Install anthropic SDK: uv add anthropic"
            ) from exc

        self._client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self._model = model_name

    def process(self, prompt: str, functions: list[FunctionDef]) -> FunctionCall:
        tools = [_function_def_to_anthropic_tool(f) for f in functions]

        response = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            tools=tools,
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": prompt}],
        )

        # Find the tool_use block in the response
        for block in response.content:
            if block.type == "tool_use":
                return FunctionCall(
                    prompt=prompt,
                    fn_name=block.name,
                    args=block.input,
                )

        raise ValueError(f"No tool_use block in Claude response: {response.content}")
