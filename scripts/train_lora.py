"""LoRA fine-tuning for function calling on Qwen2.5 models.

Uses TRL SFTTrainer + PEFT LoRA on the Salesforce/xlam-function-calling-60k
dataset, formatted as Qwen2.5 chat-template instruction-response pairs.

Usage (on HPC GPU node via train_lora.sh):
    uv run --group hpc python scripts/train_lora.py \
        --model Qwen/Qwen2.5-7B-Instruct \
        --output-dir models/lora/Qwen2.5-7B-FT \
        --dataset Salesforce/xlam-function-calling-60k \
        --epochs 2 --rank 16
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def format_xlam_example(row: dict, tokenizer) -> str:
    """Convert an xlam-function-calling-60k row to a chat-template string."""
    tools = json.loads(row["tools"]) if isinstance(row["tools"], str) else row["tools"]
    answers = json.loads(row["answers"]) if isinstance(row["answers"], str) else row["answers"]

    fn_lines = []
    for t in tools:
        params = t.get("parameters", {}).get("properties", {})
        param_str = ", ".join(
            f"{n}: {p.get('type', 'string')}" for n, p in params.items()
        )
        fn_lines.append(f"- {t['name']}({param_str}): {t.get('description', '')}")

    fn_block = "\n".join(fn_lines)
    user_msg = f"Available functions:\n{fn_block}\n\nUser request: {row['query']}"

    if isinstance(answers, list) and answers:
        call = answers[0]
        name = call.get("name", "")
        args = call.get("arguments", {})
        args_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
        assistant_msg = f"{name}({args_str})"
    else:
        assistant_msg = str(answers)

    messages = [
        {"role": "system", "content": "You are a helpful assistant that calls functions to answer user requests. Output only the function call, nothing else."},
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": assistant_msg},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="LoRA fine-tuning for function calling")
    parser.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--dataset", default="Salesforce/xlam-function-calling-60k")
    parser.add_argument("--data-path", type=str, default=None,
                        help="Local JSONL file from prepare_lora_data.py (skips HF download)")
    parser.add_argument("--output-dir", default="models/lora/Qwen2.5-7B-FT")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--rank", type=int, default=16, help="LoRA rank")
    parser.add_argument("--alpha", type=int, default=32, help="LoRA alpha")
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--max-length", type=int, default=2048)
    parser.add_argument("--max-samples", type=int, default=None, help="Limit training samples")
    parser.add_argument("--bf16", action="store_true", default=True)
    args = parser.parse_args()

    import torch
    from datasets import load_dataset
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
    from trl import SFTTrainer

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading tokenizer: {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading model: {args.model}")
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16 if args.bf16 else torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.rank,
        lora_alpha=args.alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    if args.data_path:
        print(f"Loading local dataset: {args.data_path}")
        ds = load_dataset("json", data_files=args.data_path, split="train")
    else:
        print(f"Loading dataset: {args.dataset}")
        ds = load_dataset(args.dataset, split="train")

    if args.max_samples:
        ds = ds.select(range(min(args.max_samples, len(ds))))
    print(f"Using {len(ds)} samples")

    print("Formatting dataset...")
    formatted = ds.map(
        lambda row: {"text": format_xlam_example(row, tokenizer)},
        remove_columns=ds.column_names,
        num_proc=4,
    )

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        bf16=args.bf16,
        fp16=not args.bf16,
        logging_steps=50,
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none",
        dataloader_num_workers=2,
        remove_unused_columns=False,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=formatted,
        dataset_text_field="text",
        max_seq_length=args.max_length,
        args=training_args,
    )

    print("Training...")
    trainer.train()

    print(f"Saving LoRA adapter to {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    # Save a metadata file for traceability.
    meta = {
        "base_model": args.model,
        "dataset": args.data_path if args.data_path else args.dataset,
        "epochs": args.epochs,
        "rank": args.rank,
        "alpha": args.alpha,
        "lr": args.lr,
        "max_samples": args.max_samples,
    }
    with open(output_dir / "train_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Done. Adapter saved to {output_dir}")
    print("Next step: merge adapter with scripts/merge_lora.py before serving via vLLM.")


if __name__ == "__main__":
    main()
