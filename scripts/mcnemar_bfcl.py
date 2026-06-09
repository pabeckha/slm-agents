"""McNemar's exact test for paired BFCL configuration comparisons.

Re-scores two stored result files (written by src.bfcl_adapter) on the same
BFCL category and reports the discordant-pair counts and the exact two-sided
p-value. Use this to attach a significance level to paired deltas such as
CD vs CD+FT-aligned (thesis Section 4.4.1), which a single-proportion
confidence interval cannot settle.

Run on the HPC checkout, where the BFCL vendor data and bfcl_eval package
are available:

    uv run --group hpc python scripts/mcnemar_bfcl.py \
        data/output/bfcl/Qwen_Qwen2.5-7B-Instruct/non_live/BFCL_v4_simple_python_result.json \
        data/output/bfcl_ft_aligned/<model>/non_live/BFCL_v4_simple_python_result.json \
        --category simple_python

The result files contain one {"id", "result"} line per test case, where
"result" is a Python call string like "[fn(a=1, b='x')]". Correctness is
recomputed with the same ast_checker used for the thesis scores.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.bfcl_adapter import (  # noqa: E402
    BFCL_DATA_DIR,
    evaluate,
    load_bfcl_answers,
    load_bfcl_test_data,
)


def _safe_eval(n: ast.AST) -> object:
    """Recursively evaluate the AST nodes repr() can produce, and nothing else."""
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.Name):
        if n.id == "nan":
            return float("nan")
        if n.id == "inf":
            return float("inf")
        raise ValueError(f"unsupported name: {n.id}")
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
        return -_safe_eval(n.operand)
    if isinstance(n, ast.List):
        return [_safe_eval(elt) for elt in n.elts]
    if isinstance(n, ast.Tuple):
        return tuple(_safe_eval(elt) for elt in n.elts)
    if isinstance(n, ast.Set):
        return {_safe_eval(elt) for elt in n.elts}
    if isinstance(n, ast.Dict):
        return {_safe_eval(k): _safe_eval(v) for k, v in zip(n.keys, n.values)}
    raise ValueError(f"unsupported AST node: {type(n).__name__}")


def _eval_value(node: ast.expr):
    """Evaluate one keyword value from a stored repr().

    ast.literal_eval covers every repr() of the basic types except float
    nan/inf, which repr() writes as bare names that literal_eval rejects.
    Fall back to a restricted recursive AST evaluation so that nan, inf,
    -inf, and containers holding them round-trip correctly, without
    eval() on model-derived text.
    """
    try:
        return ast.literal_eval(node)
    except ValueError:
        return _safe_eval(node)


def decode_python_str(python_str: str) -> list[dict]:
    """Decode "[fn(a=1), g.h(b='x')]" into [{"fn": {"a": 1}}, ...].

    Mirrors the inverse of format_result_python/format_parallel_results in
    src.bfcl_adapter. Returns [{}] when the string cannot be decoded, which
    the checker scores as incorrect (same treatment as pipeline errors).
    """
    try:
        tree = ast.parse(python_str.strip(), mode="eval")
        calls = tree.body
        if not isinstance(calls, ast.List):
            return [{}]
        decoded = []
        for call in calls.elts:
            if not isinstance(call, ast.Call):
                return [{}]
            func = call.func
            parts = []
            while isinstance(func, ast.Attribute):
                parts.append(func.attr)
                func = func.value
            if isinstance(func, ast.Name):
                parts.append(func.id)
            else:
                return [{}]
            name = ".".join(reversed(parts))
            args = {
                kw.arg: _eval_value(kw.value)
                for kw in call.keywords
                if kw.arg is not None
            }
            decoded.append({name: args})
        return decoded or [{}]
    except (SyntaxError, ValueError, NameError):
        return [{}]


def load_results(path: Path, test_data: list[dict]) -> list[dict]:
    """Load a result JSONL file and align it with test_data order."""
    by_id = {}
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            by_id[obj["id"]] = obj["result"]

    missing = [e["id"] for e in test_data if e["id"] not in by_id]
    if missing:
        raise SystemExit(
            f"{path}: missing {len(missing)} test ids (first: {missing[:3]}); "
            "both runs must cover the same test cases"
        )

    results = [
        {
            "id": e["id"],
            "decoded": decode_python_str(by_id[e["id"]]),
            "python_str": by_id[e["id"]],
        }
        for e in test_data
    ]

    # Surface decode failures: stored strings that did not round-trip.
    # A nonempty list here means the re-scored accuracy is NOT comparable
    # to the original run and the discordant counts cannot be trusted.
    bad = [r["id"] for r in results
           if r["decoded"] == [{}] and r["python_str"].strip() not in ("[]", "")]
    if bad:
        print(f"WARNING {path}: {len(bad)} stored results failed to decode "
              f"and will score as wrong: {bad[:10]}")
        print("  Inspect these lines in the result file before using the "
              "p-value; the paired counts are unreliable until this is 0.")

    return results


def mcnemar_exact(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value from discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / 2**n
    return min(1.0, 2 * tail)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_a", type=Path, help="result JSONL, configuration A")
    parser.add_argument("result_b", type=Path, help="result JSONL, configuration B")
    parser.add_argument("--category", default="simple_python")
    parser.add_argument("--bfcl-dir", type=Path, default=BFCL_DATA_DIR)
    parser.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct",
                        help="model name for the ast_checker lookup")
    args = parser.parse_args()

    test_data = load_bfcl_test_data(args.category, args.bfcl_dir)
    answers = load_bfcl_answers(args.category, args.bfcl_dir)

    fail_sets = []
    for path in (args.result_a, args.result_b):
        results = load_results(path, test_data)
        scores = evaluate(results, answers, test_data, args.category, args.model)
        fails = {f["id"] for f in scores["failures"]}
        fail_sets.append(fails)
        print(f"{path}: {scores['correct_count']}/{scores['total_count']} "
              f"({scores['accuracy']:.2%}), {len(fails)} failures")

    fail_a, fail_b = fail_sets
    total = len(test_data)
    b = len(fail_a - fail_b)  # A wrong, B correct
    c = len(fail_b - fail_a)  # B wrong, A correct
    both_wrong = len(fail_a & fail_b)
    both_right = total - b - c - both_wrong
    p = mcnemar_exact(b, c)

    print(f"\nboth correct: {both_right}")
    print(f"both wrong:   {both_wrong}")
    print(f"A wrong, B correct (b): {b}")
    print(f"B wrong, A correct (c): {c}")
    print(f"net difference (b - c): {b - c}")
    print(f"McNemar exact two-sided p-value: {p:.5f}")


if __name__ == "__main__":
    main()
