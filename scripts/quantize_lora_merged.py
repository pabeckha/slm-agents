"""Quantize a merged LoRA model to AWQ INT4 for use with vLLM."""
import argparse

from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to merged model directory")
    parser.add_argument("--output", required=True, help="Output path for quantized model")
    parser.add_argument("--bits", type=int, default=4)
    parser.add_argument("--group-size", type=int, default=128)
    args = parser.parse_args()

    print(f"Loading model from {args.model}")
    model = AutoAWQForCausalLM.from_pretrained(
        args.model, low_cpu_mem_usage=True, use_cache=False
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)

    quant_config = {
        "zero_point": True,
        "q_group_size": args.group_size,
        "w_bit": args.bits,
        "version": "GEMM",
    }
    print(f"Quantizing: bits={args.bits}, group_size={args.group_size}")
    model.quantize(tokenizer, quant_config=quant_config)

    print(f"Saving to {args.output}")
    model.save_quantized(args.output)
    tokenizer.save_pretrained(args.output)
    print("Done.")


if __name__ == "__main__":
    main()
