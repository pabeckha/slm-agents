# LoRA Training Data

## Dataset

**Source:** Salesforce/xlam-function-calling-60k (gated, HuggingFace)  
**Split:** 90/10 train/val, random shuffle with seed=42  
**Script:** `scripts/prepare_lora_data.py`  
**Files:** `data/input/lora_train.jsonl` (77.6 MB), `data/input/lora_val.jsonl` (8.6 MB)

## Statistics

|                     | Train     | Val      |
|---------------------|-----------|----------|
| Examples            | 54,000    | 6,000    |
| Tools per example   | avg 2.8 (min 1, max 8) | avg 2.8 (min 1, max 8) |
| Calls per example   | avg 1.7 (min 1, max 52) | avg 1.7 (min 1, max 12) |
| Multi-call examples | 28,393 (52.6%) | 3,146 (52.4%) |
| Unique functions    | 3,166     | 2,266    |
| Avg query length    | 112 chars | 112 chars |

Top-5 functions (train): `search` (1321), `loginuser` (415), `calculate_standard_deviation` (361), `calculate_investment_return` (350), `is_sum_of_cubes` (342)

## Format

Each row is formatted as a Qwen2.5 chat-template string via `format_xlam_example()` in `scripts/train_lora.py`:

- **System:** "You are a helpful assistant that calls functions..."
- **User:** available function signatures + user query
- **Assistant:** `function_name(arg=value, ...)`

## Training vs. Evaluation Distribution Mismatch

Over half the training examples (52.6%) contain multiple function calls, but the BFCL `simple_python` evaluation category is single-call only. This means the model is trained on a broader distribution than it is tested on.

**Implication for thesis:** This is a mild train/eval mismatch. It is unlikely to hurt — the model sees single-call examples too — but any accuracy gain from fine-tuning cannot be fully attributed to single-call specialisation. If results are weaker than expected, filtering xlam to single-call examples only (`len(answers) == 1`, ~47% of the dataset, ~28k examples) is a straightforward ablation.

## BFCL Test Set

**Source:** `vendor/gorilla/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v4_simple_python.json`  
**Size:** 400 entries, 1 function per entry, single-call answers  
**Format:** JSONL with `id`, `question`, `function` keys
