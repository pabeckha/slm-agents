#!/usr/bin/env python3
"""
GitHub MCP real-world evaluation runner.

Feeds each of the 50 test cases (prompt + 21 GitHub tool schemas) to the
vLLM pipeline, evaluates predictions against ground truth, and executes
read-only calls via the GitHub REST API to measure execution success.

Read-only tools are executed live; write tools are scored on tool selection
and argument accuracy only (execution_success=null).

Outputs:
    data/output/github_mcp/{config}_{model_slug}/results.json

Usage (assumes vLLM server already running):
    uv run --group hpc python scripts/eval_github_mcp.py \\
        --config CD \\
        --model Qwen/Qwen2.5-7B-Instruct \\
        --vllm-url http://localhost:8000/v1
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.io import load_function_definitions  # noqa: E402
from src.vllm_backend import VLLMBackend  # noqa: E402

TOOLS_PATH = ROOT / "data/input/github_tools.json"
TESTS_PATH = ROOT / "data/input/github_mcp_tests.json"
OUTPUT_BASE = ROOT / "data/output/github_mcp"

# Tools safe to execute live during evaluation.
_READ_ONLY = {
    "get_issue", "list_issues", "search_issues",
    "get_pr", "list_prs", "list_pr_comments",
    "get_repo", "list_repos", "search_repos",
    "search_code", "search_users",
}


# ── argument comparison ──────────────────────────────────────────────────────

def _normalise(v: object) -> str:
    return str(v).strip().lower()


def _args_match(predicted: dict, ground_truth: dict) -> bool:
    """True iff every key in ground_truth is present and equal in predicted."""
    if not isinstance(predicted, dict):
        return False
    for key, expected in ground_truth.items():
        if key not in predicted:
            return False
        got = predicted[key]
        if isinstance(expected, bool):
            got_bool = str(got).lower() in ("true", "1", "yes")
            if got_bool != expected:
                return False
        elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
            if isinstance(got, bool):
                return False
            try:
                if float(got) != float(expected):
                    return False
            except (TypeError, ValueError):
                return False
        elif isinstance(expected, list):
            got_list = got if isinstance(got, list) else [got]
            if sorted(_normalise(x) for x in got_list) != sorted(_normalise(x) for x in expected):
                return False
        elif isinstance(expected, dict):
            if not isinstance(got, dict) or not _args_match(got, expected):
                return False
        else:
            if _normalise(got) != _normalise(expected):
                return False
    return True


# ── GitHub REST executor ─────────────────────────────────────────────────────

class GitHubExecutor:
    """Execute read-only tool predictions via GitHub REST API."""

    _BASE = "https://api.github.com"

    def __init__(self, token: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "slm-eval/1.0",
        }

    def execute(self, fn_name: str, args: dict) -> tuple[bool | None, str]:
        """Return (success, detail). success=None means write op skipped."""
        if fn_name not in _READ_ONLY:
            return None, "skipped_write"
        try:
            code = self._call(fn_name, args)
            return code < 400, f"http_{code}"
        except Exception as exc:
            return False, f"error: {exc}"

    def _get(self, path: str, params: dict | None = None) -> int:
        url = self._BASE + path
        if params:
            url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        req = urllib.request.Request(url, headers=self._headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status
        except urllib.error.HTTPError as exc:
            return exc.code

    def _call(self, fn_name: str, args: dict) -> int:
        owner = args.get("owner", "")
        repo = args.get("repo", "")
        extra = {k: v for k, v in args.items() if k not in ("owner", "repo")}

        match fn_name:
            case "get_issue":
                return self._get(f"/repos/{owner}/{repo}/issues/{args['issue_number']}")
            case "list_issues":
                return self._get(f"/repos/{owner}/{repo}/issues", extra)
            case "search_issues":
                return self._get("/search/issues", {"q": args["query"]})
            case "get_pr":
                return self._get(f"/repos/{owner}/{repo}/pulls/{args['pull_number']}")
            case "list_prs":
                return self._get(f"/repos/{owner}/{repo}/pulls", extra)
            case "list_pr_comments":
                return self._get(f"/repos/{owner}/{repo}/pulls/{args['pull_number']}/comments")
            case "get_repo":
                return self._get(f"/repos/{owner}/{repo}")
            case "list_repos":
                if owner:
                    return self._get(f"/users/{owner}/repos")
                return self._get("/user/repos")
            case "search_repos":
                return self._get("/search/repositories", {"q": args["query"]})
            case "search_code":
                return self._get("/search/code", {"q": args["query"]})
            case "search_users":
                return self._get("/search/users", {"q": args["query"]})
            case _:
                raise ValueError(f"Unmapped tool: {fn_name}")


# ── metrics ──────────────────────────────────────────────────────────────────

def _pct(n: int, total: int) -> float:
    return round(n / total, 4) if total else 0.0


def compute_metrics(results: list[dict]) -> dict:
    n = len(results)
    tool_ok = sum(1 for r in results if r["tool_correct"])
    args_ok = sum(1 for r in results if r["args_correct"])
    executed = [r for r in results if r["execution_success"] is not None]
    exec_ok = sum(1 for r in executed if r["execution_success"])

    by_cluster: dict = {}
    for c in sorted({r["cluster"] for r in results}):
        sub = [r for r in results if r["cluster"] == c]
        by_cluster[c] = {
            "n": len(sub),
            "tool_accuracy": _pct(sum(1 for r in sub if r["tool_correct"]), len(sub)),
            "arg_accuracy": _pct(sum(1 for r in sub if r["args_correct"]), len(sub)),
        }

    by_difficulty: dict = {}
    for d in ("easy", "medium", "hard"):
        sub = [r for r in results if r["difficulty"] == d]
        if sub:
            by_difficulty[d] = {
                "n": len(sub),
                "tool_accuracy": _pct(sum(1 for r in sub if r["tool_correct"]), len(sub)),
                "arg_accuracy": _pct(sum(1 for r in sub if r["args_correct"]), len(sub)),
            }

    return {
        "n_total": n,
        "tool_selection_accuracy": _pct(tool_ok, n),
        "arg_accuracy": _pct(args_ok, n),
        "n_executed": len(executed),
        "execution_success_rate": _pct(exec_ok, len(executed)) if executed else None,
        "by_cluster": by_cluster,
        "by_difficulty": by_difficulty,
    }


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    import os

    parser = argparse.ArgumentParser(description="GitHub MCP real-world evaluation")
    parser.add_argument(
        "--config", choices=["B", "CD", "CDQ"], required=True,
        help="B=baseline (no guided), CD=constrained decoding, CDQ=CD+quantized",
    )
    parser.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--vllm-url", default="http://localhost:8000/v1")
    parser.add_argument("--vllm-key", default="EMPTY")
    parser.add_argument(
        "--no-execute", action="store_true",
        help="Skip GitHub API calls; score tool selection and arg accuracy only",
    )
    cli = parser.parse_args()

    guided = cli.config in ("CD", "CDQ")

    functions = load_function_definitions(TOOLS_PATH)
    tests = json.loads(TESTS_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(functions)} tools, {len(tests)} test cases")
    print(f"Config: {cli.config} | guided={guided} | model={cli.model}")

    backend = VLLMBackend(
        base_url=cli.vllm_url,
        api_key=cli.vllm_key,
        model_name=cli.model,
        guided=guided,
    )

    executor: GitHubExecutor | None = None
    if not cli.no_execute:
        token = os.environ.get("GITHUB_TOKEN", "")
        if token:
            executor = GitHubExecutor(token)
            print(f"GitHub execution: enabled ({len([t for t in tests if t['ground_truth']['fn_name'] in _READ_ONLY])} read-only cases)")
        else:
            print("Warning: GITHUB_TOKEN not set — execution skipped (pass --no-execute to suppress this)")

    results = []
    for i, case in enumerate(tests):
        prompt = case["prompt"]
        gt = case["ground_truth"]

        t0 = time.perf_counter()
        try:
            fc = backend.process(prompt, functions)
            pred_fn, pred_args = fc.fn_name, fc.args
        except Exception as exc:
            pred_fn, pred_args = "error", {"error": str(exc)}
        latency = round(time.perf_counter() - t0, 3)

        tool_correct = pred_fn == gt["fn_name"]
        args_correct = tool_correct and _args_match(pred_args, gt["args"])

        exec_success, exec_detail = None, "not_attempted"
        if executor is not None:
            exec_success, exec_detail = executor.execute(pred_fn, pred_args)

        mark = "✓" if tool_correct else "✗"
        print(
            f"[{i+1:02d}/{len(tests)}] {mark} "
            f"pred={pred_fn!r} gt={gt['fn_name']!r} "
            f"args={'ok' if args_correct else 'WRONG'} "
            f"exec={exec_detail} ({latency}s)"
        )

        results.append({
            "id": case["id"],
            "cluster": case["cluster"],
            "difficulty": case["difficulty"],
            "prompt": prompt,
            "predicted": {"fn_name": pred_fn, "args": pred_args},
            "ground_truth": gt,
            "tool_correct": tool_correct,
            "args_correct": args_correct,
            "execution_success": exec_success,
            "execution_detail": exec_detail,
            "latency_s": latency,
        })

    metrics = compute_metrics(results)
    n = metrics["n_total"]
    tool_n = int(metrics["tool_selection_accuracy"] * n)
    args_n = int(metrics["arg_accuracy"] * n)
    print(f"\n=== {cli.config} results ===")
    print(f"  Tool selection:   {metrics['tool_selection_accuracy']:.1%}  ({tool_n}/{n})")
    print(f"  Arg accuracy:     {metrics['arg_accuracy']:.1%}  ({args_n}/{n})")
    if metrics["execution_success_rate"] is not None:
        exec_n = int(metrics["execution_success_rate"] * metrics["n_executed"])
        print(f"  Execution:        {metrics['execution_success_rate']:.1%}  ({exec_n}/{metrics['n_executed']} read-only calls)")
    print("  By cluster:")
    for c, v in metrics["by_cluster"].items():
        print(f"    {c:<20} tool={v['tool_accuracy']:.0%}  args={v['arg_accuracy']:.0%}  (n={v['n']})")

    model_slug = cli.model.replace("/", "_").replace(".", "-")
    out_dir = OUTPUT_BASE / f"{cli.config}_{model_slug}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "results.json"
    out_path.write_text(json.dumps({
        "config": cli.config,
        "model": cli.model,
        "guided": guided,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "metrics": metrics,
    }, indent=2), encoding="utf-8")
    print(f"\nResults → {out_path}")


if __name__ == "__main__":
    main()
