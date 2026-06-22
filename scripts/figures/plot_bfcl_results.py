"""
Generate thesis figures for BFCL v4 simple_python results.
Outputs PDF files to thesis/pictures/figures/.

Design principles applied (Knaflic, Storytelling with Data, 2015):
- Single highlight colour (C_HIGHLIGHT) for the primary finding (CD+schema);
  all other SLM configurations recede to muted grey.
- Direct annotations on reference lines instead of a separate legend.
- Reduced gridline opacity (alpha=0.25) so data stands out.
- Semantic colours for gain/loss charts (red = negative, blue = positive).
- Single marker shape in scatter plots (redundant shape encoding removed).
"""

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent.parent / "thesis" / "pictures" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Shared style
# ---------------------------------------------------------------------------

BODY_FONTSIZE  = 10
LABEL_FONTSIZE = 9
TICK_FONTSIZE  = 9

plt.rcParams.update({
    "font.family":        "serif",
    "font.size":          BODY_FONTSIZE,
    "axes.titlesize":     BODY_FONTSIZE,
    "axes.labelsize":     BODY_FONTSIZE,
    "xtick.labelsize":    TICK_FONTSIZE,
    "ytick.labelsize":    TICK_FONTSIZE,
    "legend.fontsize":    LABEL_FONTSIZE,
    "figure.dpi":         150,
    "savefig.bbox":       "tight",
    "savefig.pad_inches": 0.05,
})

# Primary palette
C_HIGHLIGHT      = "#1a6faf"   # Strong blue  — CD+schema (the key result)
C_SECONDARY      = "#5b9bd5"   # Medium blue  — B-template control
C_MUTED          = "#cccccc"   # Light grey   — other SLM configurations
C_FRONTIER       = "#999999"   # Medium grey  — frontier model bars
C_REF_LINE       = "#666666"   # Dark grey    — reference/annotation lines

# Semantic colours for gain / loss charts
C_LOSS           = "#d62728"   # Red   — negative result
C_GAIN           = "#1f77b4"   # Blue  — positive result
C_NEUTRAL_DARK   = "#aaaaaa"   # Medium grey — supporting / neutral
C_NEUTRAL_LIGHT  = "#dddddd"   # Light grey  — background / stable


def _add_value_labels(ax, bars, values, highlight_key=None, fmt=".2f"):
    """Add value labels above each bar; bold the highlighted bar."""
    for bar, val in zip(bars, values):
        is_hl = (highlight_key is not None) and (val == highlight_key)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 1.2,
            f"{val:{fmt}}%",
            ha="center", va="bottom",
            fontsize=7.5,
            fontweight="bold" if is_hl else "normal",
            color=C_HIGHLIGHT if is_hl else "#333333",
        )


def _clean_axes(ax):
    """Remove top/right spines, reduce gridline noise."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", linewidth=0.4, alpha=0.25, zorder=0)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------
# Figure 1 — Frontier comparison (SLM configs vs frontier models)
# ---------------------------------------------------------------------------
# Story: CD+schema (highlighted) crosses into the frontier band; other SLM
# configs are shown for context in muted grey.

SLM_CONFIGS = [
    ("CD+Q",          72.25, C_MUTED),
    ("CD",            72.75, C_MUTED),
    ("CD+FT-aligned", 76.75, C_MUTED),
    ("CD+schema",     89.00, C_HIGHLIGHT),
    ("B-template",    96.00, C_SECONDARY),
]

FRONTIER_CONFIGS = [
    ("GPT-5-mini",        78.75),
    ("GPT-4.1 mini",      91.00),
    ("GPT-4.1",           91.00),
    ("Gemini 3 Pro",      94.75),
    ("Claude Haiku 4.5",  95.00),
    ("Claude Opus 4.5",   96.50),
    ("Claude Sonnet 4.5", 97.75),
]

all_names = [c[0] for c in SLM_CONFIGS] + [c[0] for c in FRONTIER_CONFIGS]
all_accs  = [c[1] for c in SLM_CONFIGS] + [c[1] for c in FRONTIER_CONFIGS]
all_cols  = [c[2] for c in SLM_CONFIGS] + [C_FRONTIER] * len(FRONTIER_CONFIGS)

fig, ax = plt.subplots(figsize=(8.5, 3.6))

bars = ax.bar(range(len(all_names)), all_accs, color=all_cols, width=0.65, zorder=3)

# Label only the CD+schema bar and the frontier endpoints to reduce clutter
LABEL_THESE = {"CD+schema", "GPT-5-mini", "Claude Sonnet 4.5"}
for bar, name, val in zip(bars, all_names, all_accs):
    if name in LABEL_THESE:
        is_hl = (name == "CD+schema")
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.8,
            f"{val:.2f}%",
            ha="center", va="bottom",
            fontsize=7.5,
            fontweight="bold" if is_hl else "normal",
            color=C_HIGHLIGHT if is_hl else "#333333",
        )

ax.set_xticks(range(len(all_names)))
ax.set_xticklabels(all_names, fontsize=TICK_FONTSIZE, rotation=35, ha="right")
ax.set_ylabel("AST Accuracy (↑) [%]")
ax.set_ylim(0, 107)

# Compact 4-item legend (colour groups only)
legend_handles = [
    mpatches.Patch(color=C_HIGHLIGHT, label="CD+schema — Qwen 2.5 7B (this work)"),
    mpatches.Patch(color=C_MUTED,     label="Other constrained configs — Qwen 2.5 7B (this work)"),
    mpatches.Patch(color=C_SECONDARY, label="B-template control — Qwen 2.5 7B (this work)"),
    mpatches.Patch(color=C_FRONTIER,  label="Frontier models (BFCL leaderboard, Python Simple AST)"),
]
ax.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, 1.01),
          ncol=2, framealpha=0.9, fontsize=LABEL_FONTSIZE, borderaxespad=0.0)

# Divider between SLM and frontier groups (Gestalt enclosure)
ax.axvline(4.5, color=C_REF_LINE, linewidth=0.8, linestyle=":", alpha=0.6)

_clean_axes(ax)
fig.tight_layout()
out = OUT_DIR / "fig_frontier_comparison.pdf"
fig.savefig(out)
plt.close(fig)
print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Figure 2 — CoT flip analysis
# ---------------------------------------------------------------------------
# Story: CoT causes more losses (51) than gains (24); net −27 at 7B.
# Stable counts recede to grey; the loss bar is the visual anchor.

FLIP_LABELS = ["Stable\ncorrect", "CoT\ngain", "CoT\nloss", "Stable\nwrong"]
FLIP_COUNTS = [238, 24, 51, 87]
FLIP_COLS   = [C_NEUTRAL_LIGHT, C_GAIN, C_LOSS, C_NEUTRAL_DARK]

fig, ax = plt.subplots(figsize=(4.5, 3.2))

bars = ax.bar(FLIP_LABELS, FLIP_COUNTS, color=FLIP_COLS, width=0.6, zorder=3)

for bar, val in zip(bars, FLIP_COUNTS):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        val + 3,
        str(val),
        ha="center", va="bottom",
        fontsize=BODY_FONTSIZE,
    )

# Annotation stating the net result
ax.text(
    0.97, 0.95,
    "Net: −27 correct\n(CoT hurts at 7B)",
    transform=ax.transAxes,
    ha="right", va="top",
    fontsize=LABEL_FONTSIZE,
    color=C_LOSS,
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
              edgecolor=C_LOSS, linewidth=0.8),
)

ax.set_ylabel("Number of test cases")
ax.set_ylim(0, 280)
_clean_axes(ax)

fig.tight_layout()
out = OUT_DIR / "fig_cot_flip.pdf"
fig.savefig(out)
plt.close(fig)
print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Figure 3 — RAG outcome breakdown (horizontal bars)
# ---------------------------------------------------------------------------
# Story: wrong function selection (32 %) is the dominant failure mode.

RAG_LABELS = [
    "Correct function,\nwrong arguments (8/400)",
    "Wrong function selected (128/400)",
    "Output identical to CD+Q (264/400)",
]
RAG_SIZES = [2, 32, 66]
RAG_COLS  = [C_NEUTRAL_DARK, C_LOSS, C_NEUTRAL_LIGHT]

fig, ax = plt.subplots(figsize=(4.8, 2.4))

bars = ax.barh(RAG_LABELS, RAG_SIZES, color=RAG_COLS, height=0.5)

for bar, val in zip(bars, RAG_SIZES):
    ax.text(
        bar.get_width() + 1.0,
        bar.get_y() + bar.get_height() / 2,
        f"{val}%",
        va="center",
        fontsize=LABEL_FONTSIZE,
    )

ax.set_xlim(0, 80)
ax.set_xlabel("Share of all 400 test cases (%)", fontsize=LABEL_FONTSIZE)
# Title states the finding, not just a description of the data
ax.set_title("Wrong function selection causes most RAG failures",
             fontsize=BODY_FONTSIZE)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="y", labelsize=LABEL_FONTSIZE)

fig.tight_layout()
out = OUT_DIR / "fig_rag_breakdown.pdf"
fig.savefig(out)
plt.close(fig)
print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Figure 4 — Memory vs accuracy scatter
# ---------------------------------------------------------------------------
# Story: CD+schema achieves 89 % above the GPT-5-mini line at the same
# 14.25 GiB footprint as CD.
# Design: single marker shape (o) — shape encoding removed; colour +
# direct labels carry all differentiation. Labels at x=14.25 are staggered
# left/right so leader lines never cross. Error bars are 95 % binomial
# (Wilson) confidence intervals over the 400 BFCL test cases.

N_BFCL = 400  # test cases per configuration


def _wilson_ci_errors(acc_pct, n=N_BFCL, z=1.96):
    """Asymmetric 95 % Wilson score interval errors, in percentage points."""
    p = acc_pct / 100.0
    denom  = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half   = (z / denom) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lo, hi = centre - half, centre + half
    # Asymmetric errors as [[lower_error], [upper_error]] for matplotlib
    return [[(p - lo) * 100.0], [(hi - p) * 100.0]]


MEM_POINTS = [
    # (label, mem_gib, acc, text_x_offset, text_y_offset, ha)
    ("B",              14.25,  1.50,  0.4,   0.0, "left"),
    ("FT-only",        14.25, 53.00,  0.4,   0.0, "left"),
    ("CD+FT",          14.25, 69.75, -0.5,  -4.0, "right"),  # below-left
    ("CD",             14.25, 72.75, -0.6,   0.0, "right"),  # left
    ("CD+FT-aligned",  14.25, 76.75,  0.4,  -1.5, "left"),   # below ref line
    ("CD+Q (INT4)",     5.20, 72.25,  0.4,   0.0, "left"),
    ("CD+schema",      14.25, 89.00,  0.4,   0.0, "left"),
]

fig, ax = plt.subplots(figsize=(5.0, 3.6))

# Region above the GPT-5-mini reference: frontier-level accuracy
ax.axhspan(78.75, 97, facecolor=C_HIGHLIGHT, alpha=0.05, zorder=0)
ax.text(3.3, 95.5, "above GPT-5-mini",
        ha="left", va="top",
        fontsize=7.5, color=C_REF_LINE, style="italic")

for name, mem, acc, dx, dy, ha in MEM_POINTS:
    is_hl = name.startswith("CD+schema")
    col = C_HIGHLIGHT if is_hl else C_NEUTRAL_DARK
    ax.errorbar(mem, acc, yerr=_wilson_ci_errors(acc),
                fmt="none", ecolor=col, elinewidth=0.8, capsize=2, zorder=4)
    ax.scatter(mem, acc, color=col, marker="o", s=80 if is_hl else 60, zorder=5)
    ax.annotate(
        name,
        xy=(mem, acc),
        xytext=(mem + dx, acc + dy),
        fontsize=LABEL_FONTSIZE,
        fontweight="bold" if is_hl else "normal",
        color=C_HIGHLIGHT if is_hl else "black",
        arrowprops=dict(arrowstyle="-", color=C_NEUTRAL_DARK, lw=0.6)
        if abs(dy) > 2 else None,
        ha=ha, va="center",
    )

ax.set_xlabel("GPU Memory (↓) [GiB]")
ax.set_ylabel("AST Accuracy (↑) [%]")
ax.set_xlim(3, 18)
ax.set_ylim(-5, 97)

# Direction cue: ideal configurations sit towards the top-left
ax.annotate("better",
            xy=(0.07, 0.52), xytext=(0.23, 0.36),
            xycoords="axes fraction", textcoords="axes fraction",
            fontsize=LABEL_FONTSIZE, color=C_REF_LINE, style="italic",
            ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=C_REF_LINE, lw=0.9))

# GPT-5-mini reference line — direct label on the left, clear of the
# point cluster at x = 14.25
ax.axhline(78.75, linestyle=":", color=C_REF_LINE, linewidth=1.0, zorder=2)
ax.text(3.3, 79.7, "GPT-5-mini (78.75%)",
        ha="left", va="bottom",
        fontsize=7.5, color=C_REF_LINE, style="italic")

_clean_axes(ax)
ax.xaxis.grid(True, linestyle="--", linewidth=0.4, alpha=0.25, zorder=0)

fig.tight_layout()
out = OUT_DIR / "fig_memory_vs_accuracy.pdf"
fig.savefig(out)
plt.close(fig)
print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Figure 5 — LoRA training loss curves (v1 misaligned vs v2 aligned)
# ---------------------------------------------------------------------------
# Story: aligned-format training (C_HIGHLIGHT) converges to a lower loss
# and produces the better evaluation result.

LORA_ROOT = Path(__file__).parent.parent.parent / "models" / "lora"

_v1_path = LORA_ROOT / "Qwen_Qwen2.5-7B-Instruct"         / "checkpoint-6750" / "trainer_state.json"
_v2_path = LORA_ROOT / "Qwen_Qwen2.5-7B-Instruct-aligned" / "checkpoint-6750" / "trainer_state.json"

if _v1_path.exists() and _v2_path.exists():
    def _load_loss(path):
        logs    = json.loads(path.read_text())["log_history"]
        entries = [l for l in logs if "loss" in l and "eval_loss" not in l]
        return [l["step"] for l in entries], [l["loss"] for l in entries]

    v1_steps, v1_loss = _load_loss(_v1_path)
    v2_steps, v2_loss = _load_loss(_v2_path)

    EPOCH_BOUNDARY = 3375  # step at end of epoch 1

    fig, ax = plt.subplots(figsize=(5.5, 3.4))

    ax.plot(v1_steps, v1_loss, color=C_NEUTRAL_DARK, linewidth=1.5,
            label="v1 — misaligned format (CD+FT: 69.75%)")
    ax.plot(v2_steps, v2_loss, color=C_HIGHLIGHT, linewidth=1.5,
            label="v2 — aligned format (CD+FT-aligned: 76.75%)")

    ax.axvline(EPOCH_BOUNDARY, color=C_NEUTRAL_DARK, linestyle="--",
               linewidth=0.9, alpha=0.7)
    ax.text(EPOCH_BOUNDARY + 80, max(v1_loss[0], v2_loss[0]) * 0.72,
            "epoch 2", fontsize=LABEL_FONTSIZE, color=C_NEUTRAL_DARK, va="top")

    ax.set_xlabel("Training step")
    ax.set_ylabel("Training loss")
    ax.set_xlim(0, 6750)
    ax.set_ylim(0, max(v1_loss[0], v2_loss[0]) * 1.05)
    ax.legend(fontsize=LABEL_FONTSIZE, loc="upper right", framealpha=0.9)
    _clean_axes(ax)

    fig.tight_layout()
    out = OUT_DIR / "fig_lora_training_loss.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")
else:
    print("Skipping fig_lora_training_loss: trainer_state.json not found (models/ lives on HPC)")


# ---------------------------------------------------------------------------
# Figure 6 — Model-size scaling (Qwen 2.5) with cross-family CD overlay
# ---------------------------------------------------------------------------
# Story: every technique improves with scale, but the constraint mechanism (CD,
# CD+schema) carries the accuracy at every size while the raw base (B) stays on
# the floor. Cross-family CD points (other labs) track the Qwen CD line by
# capacity, not by lineage. Data: Table size-sweep-full + Table cross-family-cd.

SIZES = [0.5, 1.5, 3.0, 7.0]

# (label, accuracies over SIZES, colour, linestyle, marker, linewidth)
SIZE_LINES = [
    ("B-template", [78.00, 84.75, 95.00, 96.00], C_FRONTIER,  "--", "s", 1.3),
    ("CD+schema",  [74.25, 84.00, 88.00, 89.00], C_HIGHLIGHT, "-",  "D", 2.2),
    ("CD",         [51.50, 62.25, 64.75, 72.75], C_REF_LINE,  "-",  "o", 1.6),
    ("CD+Q",       [47.75, 60.50, 64.50, 72.25], C_REF_LINE,  ":",  "x", 1.3),
    ("PE",         [53.50, 64.75, 67.00, 70.25], C_SECONDARY, "-",  "^", 1.6),
    ("B (raw)",    [ 3.50,  4.75,  2.75,  1.50], C_NEUTRAL_DARK, "-", ".", 1.2),
]

# Cross-family CD points: (label, approx_size_B, accuracy)
CROSS_FAMILY = [
    ("Gemma 3 1B",  1.0, 55.50),
    ("Llama 3.2 1B", 1.2, 60.50),
    ("Llama 3.2 3B", 3.2, 62.50),
    ("Phi-4-mini",   3.8, 68.25),
]

fig, ax = plt.subplots(figsize=(6.2, 4.0))

for label, accs, col, ls, mk, lw in SIZE_LINES:
    is_hl = (label == "CD+schema")
    ax.plot(SIZES, accs, color=col, linestyle=ls, marker=mk,
            markersize=5 if not is_hl else 6, linewidth=lw,
            zorder=5 if is_hl else 3, label=label,
            markerfacecolor=col if mk != "x" else "none")

# Cross-family CD points (other labs) — single marker style, distinct hue so
# they read apart from the Qwen lines.
C_CROSS = "#e0892b"  # muted orange — cross-family CD points
cf_x = [c[1] for c in CROSS_FAMILY]
cf_y = [c[2] for c in CROSS_FAMILY]
ax.scatter(cf_x, cf_y, marker="*", s=130, color=C_CROSS,
           edgecolor="white", linewidth=0.5, zorder=6,
           label="Other families (CD)")
for name, x, y in CROSS_FAMILY:
    ax.annotate(name, xy=(x, y), xytext=(0, -11),
                textcoords="offset points", ha="center", va="top",
                fontsize=6.8, color=C_CROSS)

ax.set_xscale("log")
ax.set_xticks(SIZES)
ax.set_xticklabels([f"{s:g}B" for s in SIZES])
ax.minorticks_off()
ax.set_xlim(0.42, 8.2)
ax.set_ylim(0, 100)
ax.set_xlabel("Model size (parameters, log scale)")
ax.set_ylabel("AST Accuracy (↑) [%]")
ax.legend(loc="lower right", framealpha=0.9, fontsize=LABEL_FONTSIZE, ncol=2)
_clean_axes(ax)

fig.tight_layout()
out = OUT_DIR / "fig_size_scaling.pdf"
fig.savefig(out)
plt.close(fig)
print(f"Saved {out}")


print("\nAll figures saved to", OUT_DIR)
