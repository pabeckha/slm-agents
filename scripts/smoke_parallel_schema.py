"""Local smoke test: can the guided backend compile the proposed parallel schema?

The redesigned parallel pipeline emits a single guided JSON object::

    {"calls": [{"name": <fnX>, "arguments": {<fnX's args>}}, ...]}

where ``name`` may repeat and each element carries its own arguments. The array
items are a ``oneOf`` over per-function call objects (``name`` pinned with
``const`` + that function's argument schema). The only open risk is whether
vLLM's guided backend (xgrammar by default, outlines as fallback) can express
this ``oneOf`` + ``const`` discriminator. This script compiles the grammar
structurally -- no GPU or running server required -- so we de-risk before any
HPC grid re-run.

Run::

    uv run --group hpc python scripts/smoke_parallel_schema.py
"""

from __future__ import annotations

import json
import sys


def build_parallel_calls_schema(funcs: list[dict], max_calls: int = 8) -> dict:
    """Build the {"calls": [oneOf per-function call objects]} schema.

    ``funcs`` is a list of {"name": str, "arg_schema": <json-schema object>}.
    """
    call_variants = []
    for f in funcs:
        call_variants.append(
            {
                "type": "object",
                "properties": {
                    "name": {"const": f["name"]},
                    "arguments": f["arg_schema"],
                },
                "required": ["name", "arguments"],
                "additionalProperties": False,
            }
        )

    item_schema = call_variants[0] if len(call_variants) == 1 else {"oneOf": call_variants}

    return {
        "type": "object",
        "properties": {
            "calls": {
                "type": "array",
                "items": item_schema,
                "minItems": 1,
                "maxItems": max_calls,
            }
        },
        "required": ["calls"],
        "additionalProperties": False,
    }


# Two representative cases that the live grid actually hits:
#   single-function-repeated (the deterministic 0% case: parallel_0)
#   multiple distinct functions
SPOTIFY_ARGS = {
    "type": "object",
    "properties": {"artist": {"type": "string"}, "duration": {"type": "integer"}},
    "required": ["artist", "duration"],
    "additionalProperties": False,
}
WEATHER_ARGS = {
    "type": "object",
    "properties": {"city": {"type": "string"}, "unit": {"type": "string"}},
    "required": ["city"],
    "additionalProperties": False,
}

CASES = {
    "single_fn_repeated": [{"name": "spotify.play", "arg_schema": SPOTIFY_ARGS}],
    "multi_fn": [
        {"name": "spotify.play", "arg_schema": SPOTIFY_ARGS},
        {"name": "weather.get", "arg_schema": WEATHER_ARGS},
    ],
}


def try_xgrammar(schema: dict) -> tuple[bool, str]:
    try:
        import xgrammar as xgr
    except Exception as e:  # noqa: BLE001
        return False, f"import failed: {e}"
    try:
        # Structural compile, no tokenizer needed.
        xgr.Grammar.from_json_schema(json.dumps(schema))
        return True, "compiled"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def try_outlines(schema: dict) -> tuple[bool, str]:
    try:
        from outlines.fsm.json_schema import build_regex_from_schema
    except Exception:  # noqa: BLE001
        try:
            from outlines_core.fsm.json_schema import build_regex_from_schema  # type: ignore
        except Exception as e:  # noqa: BLE001
            return False, f"import failed: {e}"
    try:
        rx = build_regex_from_schema(json.dumps(schema))
        return True, f"regex built (len={len(rx)})"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def main() -> int:
    ok = True
    for case_name, funcs in CASES.items():
        schema = build_parallel_calls_schema(funcs)
        xg_ok, xg_msg = try_xgrammar(schema)
        ol_ok, ol_msg = try_outlines(schema)
        print(f"[{case_name}]")
        print(f"  xgrammar: {'OK ' if xg_ok else 'FAIL'} - {xg_msg}")
        print(f"  outlines: {'OK ' if ol_ok else 'FAIL'} - {ol_msg}")
        # Need at least one backend to support it.
        if not (xg_ok or ol_ok):
            ok = False
    print()
    print("RESULT:", "oneOf schema is supported by at least one backend"
          if ok else "NEITHER backend compiled the schema -- use flat fallback")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
