"""BFCL evaluation adapter.

Reads BFCL test data, runs it through our pipeline, and scores results
using BFCL's ast_checker directly.

Usage:
    uv run --group hpc python -m src.bfcl_adapter \
        --backend vllm --model Qwen/Qwen2.5-7B-Instruct \
        --category simple_python
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .schema import FunctionCall, FunctionDef, FunctionParameter

BFCL_DATA_DIR = Path(
    "vendor/gorilla/berkeley-function-call-leaderboard/bfcl_eval/data"
)


# ── BFCL data loading ───────────────────────────────────────────────────


def bfcl_function_to_function_def(bfcl_func: dict) -> FunctionDef:
    """Convert a BFCL function schema to our FunctionDef."""
    params: dict[str, FunctionParameter] = {}
    bfcl_params = bfcl_func.get("parameters", {})
    properties = bfcl_params.get("properties", {})

    for name, spec in properties.items():
        params[name] = FunctionParameter(type=spec.get("type", "string"))

    required = bfcl_params.get("required", list(params.keys()))

    return FunctionDef(
        name=bfcl_func["name"],
        description=bfcl_func.get("description", ""),
        parameters=params,
        returns=FunctionParameter(type="string"),
        required=required,
    )


def load_bfcl_test_data(category: str, data_dir: Path) -> list[dict]:
    """Load BFCL test entries from JSONL file.

    Returns list of dicts with keys: id, prompt, functions, raw_functions.
    """
    path = data_dir / f"BFCL_v4_{category}.json"
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            prompt = raw["question"][0][0]["content"]
            functions = [bfcl_function_to_function_def(fn) for fn in raw["function"]]
            entries.append({
                "id": raw["id"],
                "prompt": prompt,
                "functions": functions,
                "raw_functions": raw["function"],
            })
    return entries


def load_bfcl_answers(category: str, data_dir: Path) -> dict[str, list]:
    """Load BFCL ground truth answers, keyed by id."""
    path = data_dir / "possible_answer" / f"BFCL_v4_{category}.json"
    answers = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            answers[raw["id"]] = raw["ground_truth"]
    return answers


# ── Result formatting ────────────────────────────────────────────────────


def format_result_dict(fc: FunctionCall) -> list[dict]:
    """Convert FunctionCall to BFCL's expected decoded format.

    Returns: [{"function_name": {"param": value, ...}}]
    """
    return [{fc.fn_name: dict(fc.args)}]


def format_result_python(fc: FunctionCall) -> str:
    """Convert FunctionCall to Python call string for BFCL result files.

    Returns: '[function_name(param1=value1, param2=value2)]'
    """
    args_str = ", ".join(f"{k}={repr(v)}" for k, v in fc.args.items())
    return f"[{fc.fn_name}({args_str})]"


# ── Evaluation ───────────────────────────────────────────────────────────


def _resolve_checker_model_name(model_name: str) -> str:
    """Return a model name recognised by BFCL's ast_checker.

    The checker looks up *model_name* in ``MODEL_CONFIG_MAPPING`` to decide
    whether to convert dots in function names to underscores.  Models not in
    that mapping (e.g. Qwen2.5-7B-Instruct) cause a ``KeyError``.

    We fall back to a known registered Qwen entry with the same
    ``underscore_to_dot=False`` behaviour so the checker runs without
    modification.  If no compatible registered model is available, raise
    ``KeyError`` instead of returning an unregistered model name.
    """
    from bfcl_eval.constants.model_config import MODEL_CONFIG_MAPPING

    escaped = model_name.replace("_", "/")
    if escaped in MODEL_CONFIG_MAPPING:
        return escaped

    # Prefer deterministic known-safe Qwen fallbacks if BFCL has them.
    for key in (
        "Qwen/Qwen2.5-7B-Instruct",
        "Qwen/Qwen2-7B-Instruct",
        "Qwen/Qwen1.5-7B-Chat",
    ):
        if key in MODEL_CONFIG_MAPPING:
            return key

    # Otherwise, deterministically choose a registered Qwen model.
    qwen_keys = sorted(key for key in MODEL_CONFIG_MAPPING if "Qwen" in key)
    if qwen_keys:
        return qwen_keys[0]

    raise KeyError(
        f"Model {model_name!r} is not registered in BFCL MODEL_CONFIG_MAPPING "
        "and no safe Qwen fallback is available."
    )


def evaluate(
    results: list[dict],
    answers: dict[str, list],
    test_data: list[dict],
    category: str,
    model_name: str,
) -> dict:
    """Score results using BFCL's ast_checker.

    Returns dict with accuracy, correct_count, total_count, and failures.
    """
    from bfcl_eval.eval_checker.ast_eval.ast_checker import ast_checker
    from bfcl_eval.constants.enums import Language

    checker_model = _resolve_checker_model_name(model_name)

    correct = 0
    total = len(results)
    failures = []

    for result, entry in zip(results, test_data):
        entry_id = entry["id"]
        ground_truth = answers.get(entry_id, [])

        checker_result = ast_checker(
            func_description=entry["raw_functions"],
            model_output=result["decoded"],
            possible_answer=ground_truth,
            language=Language.PYTHON,
            test_category=category,
            model_name=checker_model,
        )

        if checker_result["valid"]:
            correct += 1
        else:
            checker_result["id"] = entry_id
            failures.append(checker_result)

    accuracy = correct / total if total > 0 else 0.0
    return {
        "accuracy": accuracy,
        "correct_count": correct,
        "total_count": total,
        "failures": failures,
    }


def write_results_jsonl(
    results: list[dict],
    model_name: str,
    category: str,
    output_dir: Path,
) -> Path:
    """Write BFCL-format result JSONL file."""
    safe_name = model_name.replace("/", "_")
    result_dir = output_dir / safe_name / "non_live"
    result_dir.mkdir(parents=True, exist_ok=True)
    path = result_dir / f"BFCL_v4_{category}_result.json"

    with open(path, "w") as f:
        for r in results:
            f.write(json.dumps({"id": r["id"], "result": r["python_str"]}) + "\n")

    return path


def write_run_manifest(
    *,
    model_name: str,
    category: str,
    backend: str,
    guided: bool,
    few_shot: bool = False,
    rag: bool = False,
    rag_top_k: int | None = None,
    rag_recall: float | None = None,
    scores: dict | None,
    output_dir: Path,
) -> Path:
    """Write a structured run manifest for experiment tracking."""
    ts = datetime.now(timezone.utc)
    safe_model = model_name.replace("/", "_")
    config_tag = "guided" if guided else "no_guided"
    if few_shot:
        config_tag += "_few_shot"
    if rag:
        config_tag += f"_rag_top{rag_top_k}"
    run_id = f"{ts:%Y-%m-%dT%H-%M-%S}_{safe_model}_{category}_{config_tag}"

    manifest = {
        "run_id": run_id,
        "timestamp": ts.isoformat(),
        "model": model_name,
        "category": category,
        "backend": backend,
        "guided": guided,
        "few_shot": few_shot,
        "rag": rag,
    }
    if rag:
        manifest["rag_top_k"] = rag_top_k
        if rag_recall is not None:
            manifest["rag_recall"] = rag_recall
    if scores is not None:
        manifest["accuracy"] = scores["accuracy"]
        manifest["correct_count"] = scores["correct_count"]
        manifest["total_count"] = scores["total_count"]
        manifest["failure_count"] = len(scores.get("failures", []))

    manifest_dir = output_dir / "runs"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = manifest_dir / f"{run_id}.json"
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)

    return path


# ── Main ─────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BFCL evaluation")
    parser.add_argument(
        "--backend", choices=["local", "vllm", "gpt", "claude"], default="vllm",
    )
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--category", type=str, default="simple_python")
    parser.add_argument("--bfcl-dir", type=str, default=str(BFCL_DATA_DIR))
    parser.add_argument("--vllm-url", type=str, default="http://localhost:8000/v1")
    parser.add_argument("--vllm-key", type=str, default="EMPTY")
    parser.add_argument("--output-dir", type=str, default="data/output/bfcl")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Load data and print stats without running inference",
    )
    parser.add_argument(
        "--no-guided", action="store_true",
        help="Disable guided decoding (free generation baseline)",
    )
    parser.add_argument(
        "--few-shot", action="store_true",
        help="Add few-shot examples to argument extraction prompts (Config PE)",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Only process first N test cases",
    )
    parser.add_argument(
        "--rag", action="store_true",
        help="Enable RAG: retrieve top-k functions from a pooled corpus instead of using ground-truth functions",
    )
    parser.add_argument(
        "--rag-top-k", type=int, default=5,
        help="Number of functions to retrieve per query (default: 5)",
    )
    parser.add_argument(
        "--rag-index-dir", type=str, default=None,
        help="Directory to save/load the FAISS index (default: <output-dir>/rag_index)",
    )
    args = parser.parse_args()

    data_dir = Path(args.bfcl_dir)
    output_dir = Path(args.output_dir)

    # Load test data and answers
    print(f"Loading BFCL {args.category} test data...")
    test_data = load_bfcl_test_data(args.category, data_dir)
    answers = load_bfcl_answers(args.category, data_dir)
    print(f"Loaded {len(test_data)} test cases, {len(answers)} ground truth entries")

    if args.limit:
        test_data = test_data[: args.limit]
        print(f"Limited to first {args.limit} test cases")

    # ── RAG index ──────────────────────────────────────────────────────
    rag_index = None
    rag_corpus = None
    if args.rag:
        from .rag import FunctionIndex, build_corpus, recall_at_k, retrieve_functions

        # Build corpus from ALL test data (before limiting), so the pool
        # contains the full set of functions as distractors.
        all_test_data = load_bfcl_test_data(args.category, data_dir)
        rag_corpus = build_corpus(all_test_data)
        print(f"RAG corpus: {len(rag_corpus)} unique functions")

        index_dir = Path(args.rag_index_dir) if args.rag_index_dir else output_dir / "rag_index"
        index_faiss = index_dir / "index.faiss"

        if index_faiss.exists():
            print(f"Loading existing FAISS index from {index_dir}")
            rag_index = FunctionIndex.load(index_dir, rag_corpus)
        else:
            print("Building FAISS index (this may take a moment)...")
            rag_index = FunctionIndex(rag_corpus)
            rag_index.build()
            rag_index.save(index_dir)
            print(f"Index saved to {index_dir}")

    if args.dry_run:
        print("\n=== Dry run: sample entries ===")
        for entry in test_data[:3]:
            print(f"\nID: {entry['id']}")
            print(f"Prompt: {entry['prompt'][:100]}...")
            print(f"Functions: {[f.name for f in entry['functions']]}")
            gt = answers.get(entry["id"], [])
            print(f"Ground truth: {gt}")
            if rag_index is not None:
                retrieved = retrieve_functions(rag_index, entry["prompt"], top_k=args.rag_top_k)
                hit = recall_at_k(retrieved, entry["functions"])
                print(f"RAG top-{args.rag_top_k}: {[f.name for f in retrieved]}  (recall: {'HIT' if hit else 'MISS'})")

        if rag_index is not None:
            # Compute recall over the current test set (possibly limited by --limit)
            hits = 0
            for entry in test_data:
                retrieved = retrieve_functions(rag_index, entry["prompt"], top_k=args.rag_top_k)
                if recall_at_k(retrieved, entry["functions"]):
                    hits += 1
            print(f"\nRAG recall@{args.rag_top_k}: {hits}/{len(test_data)} ({hits/len(test_data):.1%})")
        return

    # Build backend
    if args.backend == "vllm":
        from .vllm_backend import VLLMBackend

        backend = VLLMBackend(
            base_url=args.vllm_url,
            api_key=args.vllm_key,
            model_name=args.model,
            guided=not args.no_guided,
            few_shot=args.few_shot,
        )
    elif args.backend == "gpt":
        from .frontier_backend import GPTBackend

        backend = GPTBackend(model_name=args.model)
    elif args.backend == "claude":
        from .frontier_backend import ClaudeBackend

        backend = ClaudeBackend(model_name=args.model)
    elif args.backend == "local":
        from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
        from .local_backend import LocalBackend

        print(
            "WARNING: --backend local only supports number/boolean/string "
            "types. BFCL entries with float/array/dict parameters will fall "
            "back to string decoding, which may produce misleading scores.",
            file=sys.stderr,
        )
        backend = LocalBackend(Small_LLM_Model(args.model))

    # Run pipeline and collect results
    print(f"\n=== Running {len(test_data)} test cases ===")
    results = []
    rag_hits = 0
    for i, entry in enumerate(test_data):
        print(f"[{i + 1}/{len(test_data)}] {entry['id']}: {entry['prompt'][:60]}...")

        # Replace functions with RAG-retrieved candidates when enabled.
        functions = entry["functions"]
        if rag_index is not None:
            functions = retrieve_functions(rag_index, entry["prompt"], top_k=args.rag_top_k)
            hit = recall_at_k(functions, entry["functions"])
            if hit:
                rag_hits += 1
            else:
                print(f"  RAG MISS: correct={[f.name for f in entry['functions']]}")

        try:
            fc = backend.process(entry["prompt"], functions)
            decoded = format_result_dict(fc)
            python_str = format_result_python(fc)
            print(f"  -> {fc.fn_name}({fc.args})")
            results.append({
                "id": entry["id"],
                "decoded": decoded,
                "python_str": python_str,
            })
        except Exception as exc:
            print(f"  ERROR: {exc}")
            results.append({
                "id": entry["id"],
                "decoded": [{}],
                "python_str": "[]",
            })

    if rag_index is not None:
        print(f"\nRAG recall@{args.rag_top_k}: {rag_hits}/{len(test_data)} ({rag_hits/len(test_data):.1%})")

    # Write result files
    result_path = write_results_jsonl(results, args.model, args.category, output_dir)
    print(f"\nResults written to {result_path}")

    # Evaluate
    print("\n=== Evaluating ===")
    scores = None
    guided = not args.no_guided
    try:
        scores = evaluate(results, answers, test_data, args.category, args.model)
        print(f"Accuracy: {scores['accuracy']:.1%} ({scores['correct_count']}/{scores['total_count']})")

        if scores["failures"]:
            print(f"\nFirst 5 failures:")
            for f in scores["failures"][:5]:
                print(f"  {f.get('id', '?')}: {f.get('error', ['?'])}")

        # Write scores
        scores_path = output_dir / "scores" / f"{args.category}_scores.json"
        scores_path.parent.mkdir(parents=True, exist_ok=True)
        with open(scores_path, "w") as fh:
            serializable = {k: v for k, v in scores.items() if k != "failures"}
            serializable["failure_count"] = len(scores["failures"])
            json.dump(serializable, fh, indent=2)
        print(f"Scores written to {scores_path}")
    except ImportError as exc:
        print(f"Could not import ast_checker ({exc}), skipping inline evaluation.")
        print(f"Run manually: bfcl evaluate --model {args.model} --test-category {args.category} --partial-eval")

    # Write run manifest
    manifest_path = write_run_manifest(
        model_name=args.model,
        category=args.category,
        backend=args.backend,
        guided=guided,
        few_shot=args.few_shot,
        rag=args.rag,
        rag_top_k=args.rag_top_k if args.rag else None,
        rag_recall=rag_hits / len(test_data) if rag_index is not None else None,
        scores=scores,
        output_dir=output_dir,
    )
    print(f"Run manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
