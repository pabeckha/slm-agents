"""Prompt builders for function selection and argument extraction."""

from .schema import FunctionDef


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
