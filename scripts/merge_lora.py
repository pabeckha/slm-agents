"""Merge a LoRA adapter into its base model for vLLM serving.

vLLM serves full models, not adapters. This script merges the adapter weights
into the base model and saves the result to a local path that vLLM can load.

Usage:
    uv run --group hpc python scripts/merge_lora.py \
        --adapter models/lora/Qwen2.5-7B-FT \
        --output  models/merged/Qwen2.5-7B-FT-merged
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge LoRA adapter into base model")
    parser.add_argument("--adapter", required=True, help="Path to LoRA adapter directory")
    parser.add_argument("--output", required=True, help="Output path for merged model")
    parser.add_argument(
        "--base-model", default=None,
        help="Base model ID or path (default: read from adapter_config.json)",
    )
    args = parser.parse_args()

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    adapter_dir = Path(args.adapter)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve base model.
    base_model = args.base_model
    if base_model is None:
        cfg_path = adapter_dir / "adapter_config.json"
        if cfg_path.exists():
            with open(cfg_path) as f:
                cfg = json.load(f)
            base_model = cfg.get("base_model_name_or_path")
    if base_model is None:
        raise ValueError("Could not determine base model. Pass --base-model explicitly.")

    print(f"Base model: {base_model}")
    print(f"Adapter:    {adapter_dir}")
    print(f"Output:     {output_dir}")

    print("Loading base model...")
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16,
        device_map="cpu",
        trust_remote_code=True,
    )

    print("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(model, str(adapter_dir))

    print("Merging and unloading...")
    model = model.merge_and_unload()

    print(f"Saving merged model to {output_dir} ...")
    model.save_pretrained(output_dir, safe_serialization=True)
    tokenizer.save_pretrained(output_dir)

    # Propagate training metadata.
    meta_src = adapter_dir / "train_metadata.json"
    if meta_src.exists():
        import shutil
        shutil.copy(meta_src, output_dir / "train_metadata.json")

    print(f"Done. Serve with: vllm serve {output_dir}")


if __name__ == "__main__":
    main()
