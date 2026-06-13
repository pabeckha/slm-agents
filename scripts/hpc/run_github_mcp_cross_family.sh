#!/bin/sh
# Cross-family GitHub MCP real-world evaluation (extends issue #36 beyond Qwen2.5).
#
# Runs scripts/hpc/run_github_mcp_eval.sh (21 GitHub MCP tools, 50 NL prompts,
# live read-only API execution) across the contrast model families, so the
# strongest RQ3 / real-world result is no longer Qwen-only.
#
# Per model: configs B + CD (default mode of run_github_mcp_eval.sh).
#   - CD+Q is excluded: AWQ INT4 variants per family are not sourced yet.
#   - Qwen-7B reruns B only (CONFIG=B): its CD/CDQ numbers are already valid;
#     only the B baseline predates the no-guided parser fix (PR #163) and the
#     port-collision fix (PR #167), so it is the one number worth recomputing.
#
# Serialization (avoids the shared-NFS .venv `uv sync` race — see memory
# project_uv_sync_venv_race): the jobs are submitted as a single LSF dependency
# CHAIN (each `ended()` the previous), and the chain HEAD waits on every job
# that is already active at submit time. No two `uv sync` runs ever overlap.
#
# Usage:
#   bash scripts/hpc/run_github_mcp_cross_family.sh            # submit the chain
#   DRY_RUN=1 bash scripts/hpc/run_github_mcp_cross_family.sh  # print only
#   ANCHOR="" bash scripts/hpc/run_github_mcp_cross_family.sh  # don't wait on in-flight jobs
#   MODELS="meta-llama/Llama-3.2-3B-Instruct:" ...             # override the model:config list

set -e

HPC_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="run_github_mcp_eval.sh"

# "model:config" pairs; empty config => B+CD (script default).
MODELS="${MODELS:-\
Qwen/Qwen2.5-7B-Instruct:B \
meta-llama/Llama-3.2-3B-Instruct: \
meta-llama/Llama-3.2-1B-Instruct: \
google/gemma-3-4b-it: \
google/gemma-3-1b-it: \
microsoft/Phi-4-mini-instruct:}"

# Anchor: depend on every currently-active job so our uv sync never overlaps
# with the in-flight batch. Override with ANCHOR="" to disable, or a custom list.
if [ -z "${ANCHOR+set}" ]; then
    ANCHOR=$(bjobs -o "jobid stat" -noheader 2>/dev/null \
        | awk '$2!="DONE" && $2!="EXIT"{print $1}' | tr '\n' ' ')
fi

build_dep() {  # echoes an LSF -w expression from a space-separated id list, or nothing
    expr=""
    for id in $1; do
        [ -z "$id" ] && continue
        if [ -z "$expr" ]; then expr="ended($id)"; else expr="$expr && ended($id)"; fi
    done
    [ -n "$expr" ] && printf '%s' "$expr"
}

echo "=== Cross-family GitHub MCP eval chain ==="
[ -n "$ANCHOR" ] && echo "Anchoring head on active jobs: $ANCHOR"

PREV=""
for pair in $MODELS; do
    MODEL="${pair%:*}"
    CONFIG="${pair##*:}"
    LABEL="$(printf '%s' "$MODEL" | sed 's#.*/##')${CONFIG:+ ($CONFIG)}"

    # Dependency: previous chain job if any, else the anchor set.
    if [ -n "$PREV" ]; then
        DEP=$(build_dep "$PREV")
    else
        DEP=$(build_dep "$ANCHOR")
    fi

    vars="MODEL=$MODEL"
    [ -n "$CONFIG" ] && vars="$vars,CONFIG=$CONFIG"

    cmd="bsub"
    [ -n "$DEP" ] && cmd="$cmd -w \"$DEP\""
    cmd="$cmd -env \"all,$vars\" < $HPC_DIR/$SCRIPT"

    echo "  [$LABEL] $cmd"
    if [ -n "$DRY_RUN" ]; then
        PREV="DRY$(printf '%s' "$MODEL$CONFIG" | tr -cd '0-9')"
        continue
    fi
    out=$(eval "$cmd")
    echo "    $out"
    PREV=$(echo "$out" | sed -n 's/^Job <\([0-9]*\)>.*/\1/p')
    [ -z "$PREV" ] && { echo "ERROR: could not parse job id for $LABEL"; exit 1; }
done

echo
echo "Chain submitted. Track with: bjobs -w"
echo "Results land in: data/output/github_mcp/{B,CD}_<model_slug>/results.json"
