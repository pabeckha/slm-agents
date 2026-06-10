"""Prompt builders for function selection and argument extraction."""

from __future__ import annotations

import json

from .schema import FunctionDef


# ── Few-shot examples for argument extraction ──────────────────────────
# Each example targets a known failure mode from Config CD evaluation:
# - Numeric precision: use exact values from the query, don't round
# - String format: preserve the user's phrasing (abbreviations, qualifiers)
# - Optional parameters: use sensible defaults when user doesn't specify

_FEW_SHOT_EXAMPLES = [
    {
        "function": "calculate_force(mass: number, acceleration: number, unit: string) -> number",
        "description": "Calculate force using mass and acceleration",
        "query": "What force is needed to accelerate a 9.81 kg object at 3.2 m/s²?",
        "arg_desc": "mass (number), acceleration (number), unit (string)",
        "json": '{"mass": 9.81, "acceleration": 3.2, "unit": "m/s²"}',
    },
    {
        "function": "find_restaurant(location: string, cuisine: string, max_distance: number) -> string",
        "description": "Find restaurants near a location",
        "query": "Find me a Thai restaurant near San Francisco, CA",
        "arg_desc": "location (string), cuisine (string), max_distance (number)",
        "json": '{"location": "San Francisco, CA", "cuisine": "Thai", "max_distance": 0}',
    },
    {
        "function": "solve_equation(expression: string, variable: string) -> number",
        "description": "Solve a mathematical equation",
        "query": "Solve the equation 3*x**2 + 2*x - 5 = 0 for x",
        "arg_desc": 'expression (string), variable (string)',
        "json": '{"expression": "3*x**2 + 2*x - 5", "variable": "x"}',
    },
]


def _format_few_shot_block() -> str:
    """Format few-shot examples as a prompt block."""
    parts = []
    for ex in _FEW_SHOT_EXAMPLES:
        parts.append(
            f"Function: {ex['function']}\n"
            f"Description: {ex['description']}\n"
            f"User request: {ex['query']}\n"
            f"Extract the argument values as a JSON object with keys: {ex['arg_desc']}.\n"
            f"JSON: {ex['json']}"
        )
    return "\n\n".join(parts)


def _signature(func: FunctionDef) -> str:
    """Return a compact one-line signature for a function.

    Args:
        func: The function definition to format.

    Returns:
        A string like ``fn_add_numbers(a: number, b: number) -> number``.
    """
    params = ", ".join(
        f"{name}: {ptype}"
        for name, ptype in zip(func.arg_names, func.arg_types)
    )
    return f"{func.name}({params}) -> {func.returns.type}"


def build_parallel_selection_prompt(
    functions: list[FunctionDef], query: str
) -> str:
    """Build a prompt asking which functions to call in parallel.

    The model should output JSON: {"calls": ["fn1", "fn2", ...]}
    """
    lines = ["Available functions:"]
    for func in functions:
        lines.append(f"- {_signature(func)}: {func.description}")

    lines.append(f"\nUser request: {query}")
    lines.append(
        "List ALL function names that must be called to fulfil this request."
        " Output a JSON object with a 'calls' key containing the list."
    )
    lines.append("JSON: ")
    return "\n".join(lines)


def build_function_selection_prompt(
    functions: list[FunctionDef], query: str
) -> str:
    """Build a prompt that asks the model to pick the right function name.

    The prompt ends with ``Function name: `` so the model completes it with
    the function identifier. The constrained decoder then restricts output
    to one of the valid function names.

    Args:
        functions: All available function definitions.
        query: The natural-language user request.

    Returns:
        A formatted prompt string.
    """
    lines = ["Available functions:"]
    for func in functions:
        lines.append(f"- {_signature(func)}: {func.description}")

    lines.append(f'\nUser request: {query}')
    lines.append("Function name: ")
    return "\n".join(lines)


def build_argument_extraction_prompt(
    func: FunctionDef,
    arg_name: str,
    arg_type: str,
    query: str,
) -> str:
    """Build a prompt that asks the model to extract one argument value.

    The prompt ending depends on ``arg_type``:
    - ``"string"``: ends with ``Value: "`` so :func:`generate_string` can
      stop at the closing quote.
    - All other types: ends with ``Value: `` for numeric/boolean generation.

    Args:
        func: The function being called.
        arg_name: The argument name to extract.
        arg_type: The declared type (``"number"``, ``"string"``, etc.).
        query: The natural-language user request.

    Returns:
        A formatted prompt string.
    """
    lines = [
        f"Function: {_signature(func)}",
        f"Description: {func.description}",
        f"User request: {query}",
        f"Extract the value for argument '{arg_name}' (type: {arg_type}).",
    ]

    if arg_type == "string":
        lines.append('Value: "')
    else:
        lines.append("Value: ")

    return "\n".join(lines)


def _format_parameter_lines(func: FunctionDef) -> str:
    """Render one line per parameter with full schema detail.

    Used by the schema-rich argument extraction prompt (Config CD+schema) to
    carry the parameter descriptions, allowed values, and defaults that the
    compact ``name (type)`` listing omits. Values are JSON-encoded so string
    defaults keep their quoting (e.g. ``"all"`` rather than ``all``).
    """
    required = set(func.required) if func.required is not None else set(func.parameters)
    lines = ["Parameters:"]
    for name, param in func.parameters.items():
        requirement = "required" if name in required else "optional"
        line = f"- {name} ({param.type}, {requirement})"
        details = []
        if param.description:
            details.append(param.description.strip().rstrip("."))
        if param.enum:
            details.append(
                "Allowed values: " + ", ".join(json.dumps(v) for v in param.enum)
            )
        if param.has_default:
            details.append("Default: " + json.dumps(param.default))
        if details:
            line += ": " + ". ".join(details) + "."
        lines.append(line)
    return "\n".join(lines)


def build_reasoning_prompt(func: FunctionDef, query: str) -> str:
    """Build a chain-of-thought prompt for the ITC reasoning step.

    The model completes the ``Reasoning:`` block in free mode (no guided
    decoding). The resulting text is then injected into the args extraction
    prompt before the ``JSON: `` anchor.
    """
    return (
        f"Function: {_signature(func)}\n"
        f"Description: {func.description}\n"
        f"User request: {query}\n"
        "\n"
        "Before extracting the arguments, think step by step about:\n"
        "- Which exact values from the user's request should go into each argument?\n"
        "- Are there any numeric precisions, units, or string formats that must be preserved exactly as stated?\n"
        "- What are reasonable defaults for any optional arguments not mentioned?\n"
        "\n"
        "Reasoning:"
    )


def build_args_extraction_prompt(
    func: FunctionDef,
    query: str,
    *,
    few_shot: bool = False,
    reasoning: str | None = None,
    schema_rich: bool = False,
) -> str:
    """Build a prompt for extracting all arguments as a single JSON object.

    Used by the vLLM backend with ``guided_json`` to extract every argument
    in one API call.

    Args:
        func: The function being called.
        query: The natural-language user request.
        few_shot: If True, prepend few-shot examples to the prompt. The
            examples use the compact parameter format, so this option must
            not be combined with ``schema_rich``.
        reasoning: Optional CoT reasoning text to inject before the JSON anchor.
        schema_rich: If True, insert a per-parameter block carrying the
            descriptions, allowed values, and defaults from the source schema
            (Config CD+schema). The structural constraint is unchanged; only
            the prompt gains information.

    Returns:
        A formatted prompt string ending with ``JSON: ``.
    """
    if few_shot and schema_rich:
        raise ValueError(
            "few_shot and schema_rich are mutually exclusive: the few-shot "
            "examples use the compact parameter format"
        )

    arg_desc = ", ".join(
        f"{name} ({param.type})" for name, param in func.parameters.items()
    )

    parts: list[str] = []
    if few_shot:
        parts.append(_format_few_shot_block())
        parts.append("")  # blank line separator

    body = (
        f"Function: {_signature(func)}\n"
        f"Description: {func.description}\n"
    )
    if schema_rich:
        body += f"{_format_parameter_lines(func)}\n"
    body += f"User request: {query}\n"
    if reasoning:
        body += f"Reasoning: {reasoning.strip()}\n"
    body += (
        f"Extract the argument values as a JSON object with keys: {arg_desc}.\n"
        f"JSON: "
    )
    parts.append(body)
    return "\n".join(parts)
