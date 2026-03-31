"""CLI entry point: uv run python -m src [--input <file>] [--output <file>]."""

import argparse
import sys
from pathlib import Path

from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]

from .io import load_function_definitions, load_test_prompts, write_results
from .pipeline import run_pipeline

DEFAULT_INPUT_DIR = Path("data/input")
DEFAULT_OUTPUT_DIR = Path("data/output")


def main() -> None:
    """Parse arguments, load model, and run the function-calling pipeline."""
    parser = argparse.ArgumentParser(
        description="Function calling via constrained decoding",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to input directory or specific test file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to output JSON file",
    )
    args = parser.parse_args()

    # Resolve input paths
    if args.input:
        input_path = Path(args.input)
        if input_path.is_dir():
            tests_path = input_path / "function_calling_tests.json"
            defs_path = input_path / "functions_definition.json"
        else:
            tests_path = input_path
            defs_path = input_path.parent / "functions_definition.json"
    else:
        tests_path = DEFAULT_INPUT_DIR / "function_calling_tests.json"
        defs_path = DEFAULT_INPUT_DIR / "functions_definition.json"

    # Resolve output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = DEFAULT_OUTPUT_DIR / "function_calling_results.json"

    # Load inputs
    functions = load_function_definitions(defs_path)
    prompts = load_test_prompts(tests_path)

    print(f"Loaded {len(functions)} functions, {len(prompts)} prompts")

    # Load model
    print("Loading model...")
    try:
        model = Small_LLM_Model()
    except Exception as exc:
        print(f"Error loading model: {exc}", file=sys.stderr)
        sys.exit(1)
    print("Model loaded.")

    # Run pipeline
    results = run_pipeline(prompts, functions, model)

    # Write output
    write_results(output_path, results)
    print(f"Results written to {output_path}")


if __name__ == "__main__":
    main()
