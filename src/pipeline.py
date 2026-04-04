"""Orchestrates function calling: select function, extract args."""

from __future__ import annotations

from .backend import Backend
from .schema import FunctionCall, FunctionDef
from .decoder import ConstrainedDecoder, encode_prompt
from .prompt import (
    build_function_selection_prompt,
    build_argument_extraction_prompt,
)


def _cast_arg(value: str, arg_type: str) -> object:
    """Cast a raw string value to the declared argument type.

    Args:
        value: The string produced by the decoder.
        arg_type: One of ``"number"``, ``"string"``, ``"boolean"``.

    Returns:
        The value cast to the appropriate Python type.
    """
    if arg_type == "number":
        try:
            f = float(value)
            return int(f) if f == int(f) else f
        except (ValueError, OverflowError):
            return 0.0
    if arg_type == "boolean":
        return value.strip().lower() == "true"
    return value


def process_prompt(
    prompt: str,
    functions: list[FunctionDef],
    decoder: ConstrainedDecoder,
    model: object,
) -> FunctionCall:
    """Process a single natural-language prompt into a function call.

    Args:
        prompt: The user's natural-language request.
        functions: All available function definitions.
        decoder: The constrained decoder instance.
        model: The LLM model (used for tokenisation).

    Returns:
        A :class:`FunctionCall` with the selected function and extracted args.
    """
    # Step 1: select function name
    fn_names = [f.name for f in functions]
    sel_prompt = build_function_selection_prompt(functions, prompt)
    sel_ids = encode_prompt(model, sel_prompt)
    fn_name = decoder.generate_from_choices(sel_ids, fn_names)

    # Step 2: look up function definition
    func = next(f for f in functions if f.name == fn_name)

    # Step 3: extract each argument
    args: dict[str, object] = {}
    for arg_name, param in func.parameters.items():
        arg_type = param.type
        ext_prompt = build_argument_extraction_prompt(
            func, arg_name, arg_type, prompt,
        )
        ext_ids = encode_prompt(model, ext_prompt)

        if arg_type == "number":
            raw = decoder.generate_number(ext_ids)
        elif arg_type == "boolean":
            raw = decoder.generate_bool(ext_ids)
        elif arg_type == "string":
            raw = decoder.generate_string(ext_ids)
        else:
            raw = decoder.generate_string(ext_ids)

        args[arg_name] = _cast_arg(raw, arg_type)

    return FunctionCall(prompt=prompt, fn_name=fn_name, args=args)


def run_pipeline(
    prompts: list[str],
    functions: list[FunctionDef],
    backend: Backend,
) -> list[FunctionCall]:
    """Run the full pipeline over all prompts.

    Args:
        prompts: List of natural-language requests.
        functions: Available function definitions.
        backend: A backend satisfying the :class:`~src.backend.Backend` protocol.

    Returns:
        A list of :class:`FunctionCall` results, one per prompt.
    """
    results: list[FunctionCall] = []

    for i, prompt in enumerate(prompts):
        print(f"[{i + 1}/{len(prompts)}] Processing: {prompt}")
        try:
            result = backend.process(prompt, functions)
            print(f"  -> {result.fn_name}({result.args})")
            results.append(result)
        except Exception as exc:
            print(f"  Error: {exc}")
            results.append(FunctionCall(
                prompt=prompt,
                fn_name="error",
                args={"error": str(exc)},
            ))

    return results
