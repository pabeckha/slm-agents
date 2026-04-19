"""Prepare LoRA training data from Salesforce/xlam-function-calling-60k.

Downloads the dataset, creates train/val splits, saves JSONL files to
data/input/, and prints statistics. Runs on the login node (CPU only).

Requires HF_TOKEN in environment (dataset is gated on HuggingFace).

Usage:
    uv run --group hpc python scripts/prepare_lora_data.py
    uv run --group hpc python scripts/prepare_lora_data.py \
        --val-ratio 0.05 --max-samples 20000 --seed 42
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path


def load_row(row: dict) -> dict:
    tools = json.loads(row["tools"]) if isinstance(row["tools"], str) else row["tools"]
    answers = json.loads(row["answers"]) if isinstance(row["answers"], str) else row["answers"]
    return {"tools": tools, "query": row["query"], "answers": answers}


def stats_block(rows: list[dict], label: str) -> str:
    n_tools = [len(r["tools"]) for r in rows]
    n_calls = [len(r["answers"]) if isinstance(r["answers"], list) else 1 for r in rows]
    fn_counts: Counter = Counter()
    for r in rows:
        if isinstance(r["answers"], list):
            for a in r["answers"]:
                fn_counts[a.get("name", "?")] += 1

    lines = [
        f"\n{label} ({len(rows):,} examples)",
        f"  Tools per example  : min={min(n_tools)} max={max(n_tools)} avg={sum(n_tools)/len(n_tools):.1f}",
        f"  Calls per example  : min={min(n_calls)} max={max(n_calls)} avg={sum(n_calls)/len(n_calls):.1f}",
        f"  Multi-call examples: {sum(1 for c in n_calls if c > 1):,} ({sum(1 for c in n_calls if c > 1)/len(rows):.1%})",
        f"  Unique functions   : {len(fn_counts):,}",
        f"  Top-5 functions    : {', '.join(f'{fn}({c})' for fn, c in fn_counts.most_common(5))}",
        f"  Avg query length   : {sum(len(r['query']) for r in rows)/len(rows):.0f} chars",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare LoRA training splits")
    parser.add_argument("--dataset", default="Salesforce/xlam-function-calling-60k")
    parser.add_argument("--output-dir", default="data/input")
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--max-samples", type=int, default=None,
                        help="Cap total samples before splitting (for quick tests)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    import os
    from datasets import load_dataset

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN not set. The xlam dataset is gated — export HF_TOKEN=<your_token> and retry.")
        raise SystemExit(1)
    from huggingface_hub import login
    login(token=hf_token, add_to_git_credential=False)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading {args.dataset} ...")
    ds = load_dataset(args.dataset, split="train")
    print(f"Raw dataset size: {len(ds):,} rows")

    rows = [load_row(ds[i]) for i in range(len(ds))]

    if args.max_samples and args.max_samples < len(rows):
        rng = random.Random(args.seed)
        rows = rng.sample(rows, args.max_samples)
        print(f"Capped to {len(rows):,} samples (--max-samples)")

    rng = random.Random(args.seed)
    rng.shuffle(rows)
    split = int(len(rows) * (1 - args.val_ratio))
    train_rows, val_rows = rows[:split], rows[split:]

    train_path = output_dir / "lora_train.jsonl"
    val_path = output_dir / "lora_val.jsonl"

    with open(train_path, "w") as f:
        for r in train_rows:
            f.write(json.dumps(r) + "\n")

    with open(val_path, "w") as f:
        for r in val_rows:
            f.write(json.dumps(r) + "\n")

    print(stats_block(train_rows, "Train split"))
    print(stats_block(val_rows, "Val split"))
    print(f"\nFiles written:")
    print(f"  {train_path}  ({train_path.stat().st_size / 1e6:.1f} MB)")
    print(f"  {val_path}  ({val_path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
