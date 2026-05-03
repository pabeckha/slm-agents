"""
Generate thesis figures for BFCL v4 simple_python results.
Outputs PDF files to thesis/pictures/figures/.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent.parent / "thesis" / "pictures" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Shared style -----------------------------------------------------------

BODY_FONTSIZE = 10
LABEL_FONTSIZE = 9
TICK_FONTSIZE = 9

plt.rcParams.update({
    "font.family": "serif",
    "font.size": BODY_FONTSIZE,
    "axes.titlesize": BODY_FONTSIZE,
    "axes.labelsize": BODY_FONTSIZE,
    "xtick.labelsize": TICK_FONTSIZE,
    "ytick.labelsize": TICK_FONTSIZE,
    "legend.fontsize": LABEL_FONTSIZE,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
})

# DTU-friendly colour palette (distinguishable in greyscale)
C_BLUE   = "#1f77b4"
C_ORANGE = "#ff7f0e"
C_GREEN  = "#2ca02c"
C_RED    = "#d62728"
C_GREY   = "#7f7f7f"
C_LIGHT  = "#aec7e8"
C_PURPLE = "#9467bd"

# ---------------------------------------------------------------------------
# Figure 1 — BFCL ablation bar chart (all 10 configurations)
# ---------------------------------------------------------------------------

CONFIGS = [
    ("B",             "B\n(raw)",              1.50,  C_RED),
    ("FT-aligned-ng", "FT-aligned\n(no CD)",  13.25, C_ORANGE),
    ("FT-only",       "FT-only\n(no CD)",     13.75, C_ORANGE),
    ("CD+Q+RAG",      "CD+Q\n+RAG",           47.75, C_GREY),
    ("CD+Q+ITC",      "CD+Q\n+CoT",           65.50, C_GREY),
    ("CD+FT",         "CD+FT\n(misaligned)",  69.75, C_BLUE),
    ("PE",            "PE\n(few-shot)",        70.25, C_BLUE),
    ("CD+Q",          "CD+Q\n(INT4)",         72.25, C_GREEN),
    ("CD",            "CD",                   72.75, C_GREEN),
    ("CD+FT-aligned", "CD+FT\n(aligned)",     76.75, C_PURPLE),
]

labels   = [c[1] for c in CONFIGS]
accs     = [c[2] for c in CONFIGS]
colours  = [c[3] for c in CONFIGS]

fig, ax = plt.subplots(figsize=(8.5, 3.6))

bars = ax.bar(range(len(CONFIGS)), accs, color=colours, width=0.65, zorder=3)

# Frontier reference lines
FRONTIERS = [
    ("Gemini 3 Pro",    79.58, "--", C_RED),
    ("Claude Opus 4.5", 76.83, "-.", C_ORANGE),
    ("GPT-4.1",         72.67, ":",  C_GREY),
]
for name, val, ls, col in FRONTIERS:
    ax.axhline(val, linestyle=ls, color=col, linewidth=1.2, zorder=2, label=name)

# Value labels above bars
for i, (bar, val) in enumerate(zip(bars, accs)):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        val + 1.5,
        f"{val:.1f}%",
        ha="center", va="bottom",
        fontsize=7.5, color="black",
    )

ax.set_xticks(range(len(CONFIGS)))
ax.set_xticklabels(labels, fontsize=TICK_FONTSIZE)
ax.set_ylabel("AST Accuracy (↑) [%]")
ax.set_ylim(0, 95)
ax.yaxis.grid(True, linestyle="--", linewidth=0.5, alpha=0.7, zorder=0)
ax.set_axisbelow(True)
ax.legend(loc="upper left", framealpha=0.9, fontsize=LABEL_FONTSIZE)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
out = OUT_DIR / "fig_bfcl_ablation.pdf"
fig.savefig(out)
plt.close(fig)
print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Figure 2 — Frontier comparison (SLM configs vs frontier models)
# ---------------------------------------------------------------------------

SLM_NAMES  = ["CD\n(Qwen 7B)", "CD+Q\n(Qwen 7B)", "CD+FT-aligned\n(Qwen 7B)"]
SLM_ACCS   = [72.75, 72.25, 76.75]
SLM_COLS   = [C_GREEN, C_GREEN, C_PURPLE]

FRONTIER_NAMES = [
    "GPT-5-mini", "Claude\nHaiku 4.5", "Claude\nSonnet 4.5",
    "GPT-4.1", "GPT-4.1\nmini", "Claude\nOpus 4.5", "Gemini\n3 Pro",
]
FRONTIER_ACCS = [59.92, 71.00, 72.58, 72.67, 73.33, 76.83, 79.58]

all_names = SLM_NAMES + FRONTIER_NAMES
all_accs  = SLM_ACCS  + FRONTIER_ACCS
all_cols  = SLM_COLS + [C_GREY] * len(FRONTIER_NAMES)

fig, ax = plt.subplots(figsize=(7.0, 3.6))

bars = ax.bar(range(len(all_names)), all_accs, color=all_cols, width=0.65, zorder=3)

for bar, val in zip(bars, all_accs):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        val + 0.8,
        f"{val:.1f}%",
        ha="center", va="bottom",
        fontsize=7.5,
    )

ax.set_xticks(range(len(all_names)))
ax.set_xticklabels(all_names, fontsize=TICK_FONTSIZE)
ax.set_ylabel("AST Accuracy (↑) [%]")
ax.set_ylim(50, 88)

slm_patch      = mpatches.Patch(color=C_GREEN,  label="Qwen 2.5 7B + CD (this work)")
slm_ft_patch   = mpatches.Patch(color=C_PURPLE, label="Qwen 2.5 7B + CD+FT-aligned (this work)")
frontier_patch = mpatches.Patch(color=C_GREY,   label="Frontier models (leaderboard)")
ax.legend(handles=[slm_patch, slm_ft_patch, frontier_patch], loc="lower right",
          framealpha=0.9, fontsize=LABEL_FONTSIZE)

ax.yaxis.grid(True, linestyle="--", linewidth=0.5, alpha=0.7, zorder=0)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Divider between SLM and frontier groups
ax.axvline(2.5, color="black", linewidth=0.8, linestyle=":", alpha=0.5)

fig.tight_layout()
out = OUT_DIR / "fig_frontier_comparison.pdf"
fig.savefig(out)
plt.close(fig)
print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Figure 3 — CoT flip analysis (gains vs losses per question type)
# ---------------------------------------------------------------------------
# 400 test cases: CoT active on CD+Q+ITC (65.5%) vs CD+Q (72.25%)
# Net: 262 correct (ITC) vs 289 correct (CD+Q) => net -27 correct
# Flip details: 24 gains (wrong->right), 51 losses (right->wrong)
# Remaining: 238 stable-correct, 87 stable-wrong

FLIP_LABELS = ["Stable\ncorrect\n(238)", "CoT gain\n(24)", "CoT loss\n(51)", "Stable\nwrong\n(87)"]
FLIP_COUNTS = [238, 24, 51, 87]
FLIP_COLS   = [C_GREEN, C_BLUE, C_RED, C_GREY]

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

ax.set_ylabel("Number of test cases")
ax.set_ylim(0, 280)
ax.yaxis.grid(True, linestyle="--", linewidth=0.5, alpha=0.7, zorder=0)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
out = OUT_DIR / "fig_cot_flip.pdf"
fig.savefig(out)
plt.close(fig)
print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Figure 4 — RAG failure breakdown (pie chart)
# ---------------------------------------------------------------------------

RAG_LABELS = [
    "Correct answer\nidentical to non-RAG",
    "Wrong function\nselected",
    "Wrong parameter\nvalues",
]
RAG_SIZES  = [66, 32, 2]
RAG_COLS   = [C_GREEN, C_RED, C_ORANGE]
RAG_EXPLODE = (0.03, 0.03, 0.06)

fig, ax = plt.subplots(figsize=(4.5, 3.2))

wedges, texts, autotexts = ax.pie(
    RAG_SIZES,
    labels=RAG_LABELS,
    colors=RAG_COLS,
    explode=RAG_EXPLODE,
    autopct="%1.0f%%",
    startangle=140,
    textprops={"fontsize": LABEL_FONTSIZE},
    pctdistance=0.75,
)
for at in autotexts:
    at.set_fontsize(LABEL_FONTSIZE)
    at.set_color("white")

ax.set_title("RAG failure breakdown\n(209 incorrect answers, CD+Q+RAG)", fontsize=BODY_FONTSIZE)

fig.tight_layout()
out = OUT_DIR / "fig_rag_breakdown.pdf"
fig.savefig(out)
plt.close(fig)
print(f"Saved {out}")


# ---------------------------------------------------------------------------
# Figure 5 — Memory vs accuracy scatter
# ---------------------------------------------------------------------------

MEM_POINTS = [
    ("B",             14.25,  1.50,  C_RED,    "o"),
    ("FT-only",       14.25, 13.75,  C_ORANGE, "D"),
    ("CD+FT",         14.25, 69.75,  C_BLUE,   "s"),
    ("CD",            14.25, 72.75,  C_GREEN,  "o"),
    ("CD+FT-aligned", 14.25, 76.75,  C_PURPLE, "*"),
    ("CD+Q",           5.20, 72.25,  C_GREEN,  "^"),
]

fig, ax = plt.subplots(figsize=(5.0, 3.4))

for name, mem, acc, col, marker in MEM_POINTS:
    ax.scatter(mem, acc, color=col, marker=marker, s=80, zorder=5)
    offset_x = 0.3 if name != "B" else 0.3
    offset_y = 1.5 if name not in ("CD", "CD+FT") else -3.5
    if name == "CD+FT":
        offset_x = 0.3
    ax.annotate(
        name,
        (mem, acc),
        xytext=(mem + offset_x, acc + offset_y),
        fontsize=LABEL_FONTSIZE,
        arrowprops=dict(arrowstyle="-", color="grey", lw=0.6),
        va="center",
    )

ax.set_xlabel("GPU Memory (↓) [GiB]")
ax.set_ylabel("AST Accuracy (↑) [%]")
ax.set_xlim(3, 17)
ax.set_ylim(-5, 85)

ax.axhline(72.67, linestyle=":", color=C_GREY, linewidth=1.0, label="GPT-4.1 (72.67%)")
ax.legend(fontsize=LABEL_FONTSIZE, loc="lower right")

ax.yaxis.grid(True, linestyle="--", linewidth=0.5, alpha=0.7, zorder=0)
ax.xaxis.grid(True, linestyle="--", linewidth=0.5, alpha=0.7, zorder=0)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
out = OUT_DIR / "fig_memory_vs_accuracy.pdf"
fig.savefig(out)
plt.close(fig)
print(f"Saved {out}")

print("\nAll figures saved to", OUT_DIR)
