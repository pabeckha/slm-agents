#!/bin/bash
# Submit a matrix of BFCL evaluation jobs across models, categories, and configs.
#
# Usage:
#   bash scripts/hpc/run_bfcl_sweep.sh [OPTIONS]
#
# Options:
#   --models   "m1 m2 ..."    Space-separated model IDs (default: all Qwen AWQ sizes)
#   --cats     "c1 c2 ..."    BFCL categories (default: simple_python multiple parallel)
#   --configs  "B CDQ CDQRAG" Configs to run (default: CDQ)
#   --dry-run                 Print bsub commands without submitting
#
# Example — run CDQ config on all models for simple_python only:
#   bash scripts/hpc/run_bfcl_sweep.sh --cats "simple_python" --configs "CDQ"
#
# Example — full matrix:
#   bash scripts/hpc/run_bfcl_sweep.sh --configs "B CDQ CDQRAG"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Defaults ──────────────────────────────────────────────────────────────
MODELS="${MODELS:-Qwen/Qwen2.5-0.5B-Instruct Qwen/Qwen2.5-1.5B-Instruct Qwen/Qwen2.5-3B-Instruct Qwen/Qwen2.5-7B-Instruct-AWQ}"
CATEGORIES="${CATEGORIES:-simple_python multiple parallel}"
CONFIGS="${CONFIGS:-CDQ}"
DRY_RUN=0

# ── Argument parsing ──────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --models)  MODELS="$2";     shift 2 ;;
        --cats)    CATEGORIES="$2"; shift 2 ;;
        --configs) CONFIGS="$2";    shift 2 ;;
        --dry-run) DRY_RUN=1;       shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ── Config → script mapping ───────────────────────────────────────────────
config_to_script() {
    case "$1" in
        B)      echo "${SCRIPT_DIR}/run_bfcl_no_guided.sh" ;;
        CD)     echo "${SCRIPT_DIR}/run_bfcl_eval.sh" ;;
        CDQ)    echo "${SCRIPT_DIR}/run_bfcl_quant.sh" ;;
        CDQRAG) echo "${SCRIPT_DIR}/run_bfcl_rag.sh" ;;
        CDQITC) echo "${SCRIPT_DIR}/run_bfcl_itc.sh" ;;
        CDQFT)  echo "${SCRIPT_DIR}/run_bfcl_ft.sh" ;;
        CDQFTA) echo "${SCRIPT_DIR}/run_bfcl_cdqft_aligned.sh" ;;
        FT)     echo "${SCRIPT_DIR}/run_bfcl_ft_no_guided.sh" ;;
        PE)     echo "${SCRIPT_DIR}/run_bfcl_few_shot.sh" ;;
        *)      echo "Unknown config: $1" >&2; exit 1 ;;
    esac
}

# ── Submit jobs ───────────────────────────────────────────────────────────
submitted=0
skipped=0

for model in $MODELS; do
    for category in $CATEGORIES; do
        for config in $CONFIGS; do
            script=$(config_to_script "$config")

            safe_model=$(echo "$model" | tr '/' '_' | tr '.' '-')
            job_name="bfcl_${config}_${safe_model}_${category}"

            if [[ $DRY_RUN -eq 1 ]]; then
                echo "DRY RUN: MODEL=$model CATEGORY=$category bsub -J $job_name < $script"
            else
                echo "Submitting: MODEL=$model CATEGORY=$category config=$config"
                bsub -J "$job_name" -env "all,MODEL=$model,CATEGORY=$category" < "$script"
                submitted=$((submitted + 1))
                sleep 0.5  # avoid flooding LSF
            fi
        done
    done
done

if [[ $DRY_RUN -eq 1 ]]; then
    echo ""
    echo "Dry run complete. Pass no --dry-run to submit."
else
    echo ""
    echo "Submitted $submitted jobs."
    echo "Monitor with: bjobs | grep bfcl"
fi
