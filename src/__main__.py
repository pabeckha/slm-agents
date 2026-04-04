"""CLI entry point: uv run python -m src [--backend local|vllm] [--input <dir>] [--output <file>]."""

import argparse
import sys
from pathlib import Path

from .io import load_function_definitions, load_test_prompts, write_results
from .pipeline import run_pipeline

DEFAULT_INPUT_DIR = Path("data/input")
DEFAULT_OUTPUT_DIR = Path("data/output")


def main() -> None:
    """Parse arguments, build backend, and run the function-calling pipeline."""
    parser = argparse.ArgumentParser(
        description="Function calling via constrained decoding",
    )
    parser.add_argument(
        "--backend",
        choices=["local", "vllm"],
        default="local",
        help="Inference backend: 'local' for HuggingFace, 'vllm' for vLLM API",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name/path (default: Qwen/Qwen3-0.6B for local, Qwen/Qwen2.5-7B-Instruct for vllm)",
    )
    parser.add_argument(
        "--vllm-url",
        type=str,
        default="http://localhost:8000/v1",
        help="vLLM server base URL",
    )
    parser.add_argument(
        "--vllm-key",
        type=str,
        default="EMPTY",
        help="API key for vLLM server",
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

    # Build backend
    if args.backend == "local":
        from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
        from .local_backend import LocalBackend

        model_name = args.model or "Qwen/Qwen3-0.6B"
        print(f"Loading model {model_name}...")
        try:
            model = Small_LLM_Model(model_name)
        except Exception as exc:
            print(f"Error loading model: {exc}", file=sys.stderr)
            sys.exit(1)
        print("Model loaded.")
        backend = LocalBackend(model)

    elif args.backend == "vllm":
        from .vllm_backend import VLLMBackend

        model_name = args.model or "Qwen/Qwen2.5-7B-Instruct"
        print(f"Using vLLM backend at {args.vllm_url} with model {model_name}")
        backend = VLLMBackend(
            base_url=args.vllm_url,
            api_key=args.vllm_key,
            model_name=model_name,
        )

    # Run pipeline
    results = run_pipeline(prompts, functions, backend)

    # Write output
    write_results(output_path, results)
    print(f"Results written to {output_path}")


if __name__ == "__main__":
    main()
