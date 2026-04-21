"""Quick smoke test for format_xlam_example — no GPU or model required.

Loads the local training JSONL and runs the formatter over every row using a
mock tokenizer. Any data-format bugs will surface here before wasting HPC time.

Usage:
    python scripts/test_lora_format.py
    python scripts/test_lora_format.py --data-path data/input/lora_val.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.train_lora import format_xlam_example


class MockTokenizer:
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        return json.dumps(messages)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", default="data/input/lora_train.jsonl")
    args = parser.parse_args()

    path = Path(args.data_path)
    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(1)

    tokenizer = MockTokenizer()
    errors = []
    rows = path.read_text().strip().splitlines()

    print(f"Checking {len(rows)} rows in {path}...")

    for i, line in enumerate(rows):
        try:
            row = json.loads(line)
            result = format_xlam_example(row, tokenizer)
            if not result:
                errors.append((i, "empty output", row))
        except Exception as e:
            errors.append((i, str(e), line[:200]))

        if len(errors) >= 10:
            print(f"  Stopping early after 10 errors (row {i})")
            break

    if errors:
        print(f"\nFAIL — {len(errors)} error(s):")
        for idx, msg, ctx in errors:
            print(f"  Row {idx}: {msg}")
            print(f"    Context: {ctx}")
        sys.exit(1)
    else:
        print(f"OK — all {len(rows)} rows formatted without error")


if __name__ == "__main__":
    main()
