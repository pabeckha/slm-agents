"""Capture raw Config-B generations for the introduction's failure-mode example.

The thesis Config B (the 1.5%/6-of-400 baseline documented in
``docs/decisions/config-b-no-guided-baseline.md``) is the generic, model-agnostic
two-stage pipeline run with ``--no-guided``: the model first completes a function
*selection* prompt, then completes an argument *extraction* prompt whose answer is
parsed directly as JSON. With no constrained decoding the dominant failure is
format non-compliance — the model emits the answer object and then keeps going
(further JSON objects, few-shot-style continuations, or conversational prose), so
the completion as a whole no longer parses as a single JSON object ("Extra data"),
or it produces no JSON at all.

This script reproduces that *exact* path against a running vLLM server by reusing
the real pipeline's prompt builders (:func:`build_function_selection_prompt` and
:func:`build_args_extraction_prompt`) and the real BFCL loader, then records the
*raw* model text — which the BFCL result files do not retain (they store only the
post-processed function call, with parse failures collapsed to ``[]``).

An earlier version of this script invented its own single-shot
``{"name", "arguments"}`` prompt with an explicit "respond with JSON" instruction.
That prompt is much easier than the real extraction prompt and a strong model
(Qwen 2.5 7B) satisfies it every time, so it captured zero failures and did not
reproduce the 1.5% baseline. This version sends the same prompts the baseline run
sent.

Two prompt sources are captured:
  1. The constructed ``add`` example used in the introduction, so a genuine
     transcript can replace the illustrative one.
  2. A sample of real BFCL v4 simple_python cases, so an authentic failure with
     a real query is also available.

Outputs are written to data/output/base_failure_capture/:
  - captures.json : structured records (id, query, stage prompts, raw outputs,
                    selected function, parses_as_json, parse_error)
  - captures.txt  : human-readable transcript, FAILS-PARSE cases listed first

Usage (on HPC, with a vLLM server already serving the model):
  python -m scripts.capture_base_failure \
      --model Qwen/Qwen2.5-7B-Instruct \
      --vllm-url http://localhost:8000/v1 \
      --num-bfcl 20
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from openai import OpenAI

from src.bfcl_adapter import bfcl_function_to_function_def, load_bfcl_test_data, BFCL_DATA_DIR
from src.prompt import build_args_extraction_prompt, build_function_selection_prompt
from src.schema import FunctionDef, FunctionParameter

OUTPUT_DIR = Path("data/output/base_failure_capture")


def select_function(client: OpenAI, model: str, query: str,
                    functions: list[FunctionDef]) -> tuple[str, str]:
    """Reproduce the no-guided selection step from src/vllm_backend.py.

    Free generation completes the ``Function name: `` anchor; the name is matched
    leniently against the valid names (exact, then substring), exactly as the
    pipeline does without ``guided_choice``. Returns the resolved name and the
    raw selection completion.
    """
    fn_names = [f.name for f in functions]
    sel_prompt = build_function_selection_prompt(functions, query)
    raw = client.completions.create(
        model=model, prompt=sel_prompt, max_tokens=50, temperature=0.0,
    ).choices[0].text.strip()

    if raw in fn_names:
        return raw, raw
    for name in fn_names:
        if name in raw:
            return name, raw
    return raw, raw


def parses_as_json_object(text: str) -> tuple[bool, str]:
    """Return (parses, error) for the lenient success criterion of Config B.

    The extraction step asks for the argument values as a single JSON object, so
    a success is the whole stripped completion loading as a JSON object. Trailing
    text or extra objects raise ``Extra data``; pure prose raises a decode error.
    The error string is captured verbatim so the introduction can quote it.
    """
    try:
        obj = json.loads(text.strip())
    except (json.JSONDecodeError, ValueError) as exc:
        return False, str(exc)
    if not isinstance(obj, dict):
        return False, f"top-level JSON is {type(obj).__name__}, not an object"
    return True, ""


def capture(client: OpenAI, model: str, query: str, functions: list[FunctionDef],
            case_id: str, max_tokens: int, temperature: float) -> dict:
    """Run one case through the no-guided two-stage path and record raw text."""
    fn_name, sel_raw = select_function(client, model, query, functions)
    func = next((f for f in functions if f.name == fn_name), functions[0])

    ext_prompt = build_args_extraction_prompt(func, query)
    ext_raw = client.completions.create(
        model=model, prompt=ext_prompt, max_tokens=max_tokens, temperature=temperature,
    ).choices[0].text

    parses, parse_error = parses_as_json_object(ext_raw)
    return {
        "id": case_id,
        "query": query,
        "selected_function": fn_name,
        "selection_raw": sel_raw,
        "extraction_prompt": ext_prompt,
        "raw_output": ext_raw,
        "temperature": temperature,
        "parses_as_json": parses,
        "parse_error": parse_error,
    }


def capture_case(client: OpenAI, model: str, query: str, functions: list[FunctionDef],
                 case_id: str, args: argparse.Namespace) -> list[dict]:
    """Capture one case: one deterministic run plus optional sampled repeats.

    The first run is deterministic (temperature 0) and is the one to quote. When
    ``--repeat`` exceeds one, the remaining runs sample at ``--repeat-temp`` to
    show the failure is not an artefact of a single decode path. Repeats are
    tagged ``<id>#k`` so they stay distinguishable in the output.
    """
    records = [capture(client, model, query, functions, case_id, args.max_tokens, 0.0)]
    for k in range(1, args.repeat):
        records.append(capture(
            client, model, query, functions,
            f"{case_id}#{k}", args.max_tokens, args.repeat_temp,
        ))
    return records


def load_bfcl_cases(n: int) -> list[dict]:
    """Load the first ``n`` real BFCL v4 simple_python cases via the adapter loader.

    Reusing :func:`load_bfcl_test_data` guarantees the FunctionDef conversion and
    query extraction match the evaluation pipeline exactly.
    """
    entries = load_bfcl_test_data("simple_python", BFCL_DATA_DIR)
    return [
        {"id": e["id"], "query": e["prompt"], "functions": e["functions"]}
        for e in entries[:n]
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--vllm-url", default="http://localhost:8000/v1")
    parser.add_argument("--vllm-key", default="EMPTY")
    parser.add_argument("--num-bfcl", type=int, default=20,
                        help="Number of real BFCL simple_python cases to capture.")
    parser.add_argument("--max-tokens", type=int, default=512,
                        help="Generation cap for the extraction step. Matches the "
                             "no-guided pipeline (512); a high cap lets the model "
                             "ramble past the first object, which is the failure.")
    parser.add_argument("--repeat", type=int, default=1,
                        help="Total runs per prompt: 1 deterministic plus "
                             "(repeat-1) sampled runs to show non-determinism.")
    parser.add_argument("--repeat-temp", type=float, default=0.7,
                        help="Sampling temperature for the repeated runs.")
    args = parser.parse_args()

    client = OpenAI(base_url=args.vllm_url, api_key=args.vllm_key)

    # The constructed add example from the introduction, as a FunctionDef so it
    # runs through the same two-stage path as the real cases.
    add_function = [bfcl_function_to_function_def({
        "name": "add",
        "description": "Add two numbers and return their sum.",
        "parameters": {
            "type": "dict",
            "properties": {
                "a": {"type": "number", "description": "The first addend."},
                "b": {"type": "number", "description": "The second addend."},
            },
            "required": ["a", "b"],
        },
    })]

    records: list[dict] = []
    print("=== Capturing constructed add example ===")
    records.extend(capture_case(
        client, args.model,
        "What is the sum of 265 and 345?",
        add_function, "intro_add_example", args,
    ))

    print(f"=== Capturing {args.num_bfcl} real BFCL simple_python cases ===")
    for case in load_bfcl_cases(args.num_bfcl):
        records.extend(capture_case(
            client, args.model, case["query"], case["functions"],
            case["id"], args,
        ))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "captures.json").write_text(json.dumps(records, indent=2))

    # Sort so FAILS-PARSE cases are listed first — they are the ones to quote.
    failures = sum(1 for r in records if not r["parses_as_json"])
    ordered = sorted(records, key=lambda r: r["parses_as_json"])
    lines = []
    for rec in ordered:
        status = "PARSES" if rec["parses_as_json"] else "FAILS-PARSE"
        lines.append(f"[{rec['id']}] ({status}, temp={rec['temperature']})")
        lines.append(f"  query    : {rec['query']}")
        lines.append(f"  selected : {rec['selected_function']}")
        if not rec["parses_as_json"]:
            lines.append(f"  error    : {rec['parse_error']}")
        lines.append(f"  output   : {rec['raw_output'].strip()}")
        lines.append("")
    (OUTPUT_DIR / "captures.txt").write_text("\n".join(lines))

    total = len(records)
    print(f"\n=== Done: {failures}/{total} outputs fail to parse as JSON ===")
    print(f"Wrote {OUTPUT_DIR}/captures.json and captures.txt")
    if failures:
        print("captures.txt lists FAILS-PARSE cases first — pick one to quote.")
    else:
        print("No parse failures captured. Try a weaker model, --num-bfcl with "
              "harder (multi-arg) cases, or --repeat to sample non-deterministically.")


if __name__ == "__main__":
    main()
