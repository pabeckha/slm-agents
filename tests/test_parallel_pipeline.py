"""Regression tests for the parallel-category call pipeline.

These lock in the fix for the bug where every model scored exactly 0.0% on the
BFCL ``parallel`` category. The old two-step design selected a list of *distinct*
function names and extracted arguments once per name, so it could neither:
  - call the same function twice with different arguments, nor
  - emit more calls than there were distinct functions (``maxItems`` was capped
    at ``min(len(fn_names), 5)``, forcing a single call whenever one function
    was available -- which deterministically failed every parallel item).

The fix emits all calls in one guided generation as
``{"calls": [{"name", "arguments"}, ...]}`` with ``name`` allowed to repeat.

Run with:  uv run pytest tests/test_parallel_pipeline.py -v
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from src.bfcl_adapter import format_parallel_results
from src.schema import FunctionDef, FunctionParameter
from src.vllm_backend import VLLMBackend


def _spotify() -> FunctionDef:
    return FunctionDef(
        name="spotify.play",
        description="Play a song",
        parameters={
            "artist": FunctionParameter(type="string"),
            "duration": FunctionParameter(type="integer"),
        },
        returns=FunctionParameter(type="string"),
    )


def _backend_returning(text: str, guided: bool = True) -> VLLMBackend:
    """A VLLMBackend whose client returns a fixed completion text."""
    be = VLLMBackend.__new__(VLLMBackend)
    be._model = "test"
    be._guided = guided
    be._few_shot = False
    be._cot = False
    be._schema_rich = False

    class _Completions:
        def create(self, **_kw):
            return SimpleNamespace(choices=[SimpleNamespace(text=text)])

    be._client = SimpleNamespace(completions=_Completions())
    return be


def test_schema_not_capped_by_distinct_function_count():
    """maxItems must allow several calls even with a single available function."""
    be = _backend_returning("{}")
    schema = be._build_parallel_calls_schema([_spotify()])
    assert schema["properties"]["calls"]["maxItems"] >= 2


def test_same_function_emitted_twice_with_distinct_args():
    payload = {
        "calls": [
            {"name": "spotify.play", "arguments": {"artist": "Taylor Swift", "duration": 20}},
            {"name": "spotify.play", "arguments": {"artist": "Maroon 5", "duration": 15}},
        ]
    }
    be = _backend_returning(json.dumps(payload))
    fcs = be.process_parallel("play two songs", [_spotify()])
    assert len(fcs) == 2
    _, python_str = format_parallel_results(fcs)
    assert python_str.count("spotify.play") == 2
    assert "Taylor Swift" in python_str and "Maroon 5" in python_str


def test_no_guided_parses_calls_amid_extra_text():
    text = (
        'Sure, here are the calls:\n'
        '{"calls": [{"name": "spotify.play", "arguments": {"artist": "A", "duration": 5}}]}\n'
        'Hope that helps!'
    )
    be = _backend_returning(text, guided=False)
    fcs = be.process_parallel("play one song", [_spotify()])
    assert len(fcs) == 1
    assert fcs[0].fn_name == "spotify.play"


def test_empty_calls_falls_back_to_single_call():
    """A valid response with no calls still yields one attempted call."""
    be = _backend_returning("{}")
    # The parallel pass returns no calls, so process() runs as the fallback.
    # Give each downstream step a reply it can use via a prompt-aware client.
    def _create(**kw):
        prompt = kw["prompt"]
        if "Emit every function call" in prompt:   # parallel pass -> no calls
            text = '{"calls": []}'
        elif "Function name:" in prompt:           # _select_function fallback
            text = "spotify.play"
        else:                                      # _extract_args fallback
            text = '{"artist": "A", "duration": 5}'
        return SimpleNamespace(choices=[SimpleNamespace(text=text)])

    be._client = SimpleNamespace(completions=SimpleNamespace(create=_create))
    fcs = be.process_parallel("do something", [_spotify()])
    assert len(fcs) == 1
    assert fcs[0].fn_name == "spotify.play"
