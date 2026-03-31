"""I/O helpers for loading input files and writing results."""

import json
from pathlib import Path

from pydantic import ValidationError

from .schema import FunctionCall, FunctionDef


def load_function_definitions(path: str | Path) -> list[FunctionDef]:
    """Load and validate function definitions from a JSON file.

    Args:
        path: Path to the ``functions_definition.json`` file.

    Returns:
        A list of validated :class:`FunctionDef` instances.

    Raises:
        SystemExit: On missing file, invalid JSON, or schema mismatch.
    """
    file = Path(path)
    try:
        raw = file.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"Error: function definitions file not found: {file}")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error: invalid JSON in {file}: {exc}")

    if not isinstance(data, list):
        raise SystemExit(f"Error: expected a JSON array in {file}")

    functions: list[FunctionDef] = []
    for i, entry in enumerate(data):
        try:
            functions.append(FunctionDef(**entry))
        except (ValidationError, TypeError) as exc:
            raise SystemExit(
                f"Error: invalid function definition "
                f"at index {i}: {exc}"
            )

    return functions


def load_test_prompts(path: str | Path) -> list[str]:
    """Load test prompts from a JSON file.

    Each entry must be an object with a ``"prompt"`` key.

    Args:
        path: Path to the ``function_calling_tests.json`` file.

    Returns:
        A list of prompt strings.

    Raises:
        SystemExit: On missing file, invalid JSON, or missing ``"prompt"`` key.
    """
    file = Path(path)
    try:
        raw = file.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"Error: test prompts file not found: {file}")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error: invalid JSON in {file}: {exc}")

    if not isinstance(data, list):
        raise SystemExit(f"Error: expected a JSON array in {file}")

    prompts: list[str] = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict) or "prompt" not in entry:
            raise SystemExit(
                f"Error: entry at index {i} is missing the 'prompt' key"
            )
        prompts.append(str(entry["prompt"]))

    return prompts


def write_results(path: str | Path, results: list[FunctionCall]) -> None:
    """Serialize function call results to a JSON file.

    Args:
        path: Destination file path (parent directories are created if needed).
        results: List of :class:`FunctionCall` instances to serialize.
    """
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)

    data = [r.model_dump() for r in results]
    file.write_text(json.dumps(data, indent=2), encoding="utf-8")
