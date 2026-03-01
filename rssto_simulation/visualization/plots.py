"""
Matplotlib Comparison Plots
============================
Generates publication-quality bar charts comparing all algorithms on:
  - Evacuated (agents out of 50)
  - Evacuation Time (frames)
  - Throughput (agents / frame)
  - Efficiency (%)
"""

from __future__ import annotations
import matplotlib
matplotlib.use("Agg")          # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

# ── Colour palette per algorithm ────────────────────────────────────────────
ALGO_COLOURS = {
    "SFM":     "#e74c3c",
    "PSO":     "#3498db",
    "ACO":     "#2ecc71",
    "APF":     "#f39c12",
    "RS-SSTO": "#9b59b6",
}

WINNER_EDGE = "#FFD700"   # gold border for the best bar


def _bar_chart(
    ax, names, values, ylabel, title,
    higher_is_better: bool = True,
    fmt: str = "auto",
    total_agents: int = 50,
    show_fraction: bool = False,
):
    """Draw a single styled bar chart on *ax*."""
    colours = [ALGO_COLOURS.get(n, "#888") for n in names]
    bars = ax.bar(names, values, color=colours, edgecolor="white",
                  linewidth=0.8, width=0.55, zorder=3)

    # Value labels on top of each bar
    y_max = max(values) if max(values) > 0 else 1
    for bar, val, name in zip(bars, values, names):
        if show_fraction:
            label = f"{int(val)}/{total_agents}"
        elif fmt == "pct":
            label = f"{val:.0f}%"
        elif fmt == "f4":
            label = f"{val:.4f}"
        elif isinstance(val, float) and val < 1:
            label = f"{val:.4f}"
        else:
            label = f"{int(val)}" if val == int(val) else f"{val}"

        weight = "semibold"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + y_max * 0.025,
            label, ha="center", va="bottom",
            fontsize=11, fontweight=weight, color="#222",
        )

    ax.set_ylabel(ylabel, fontsize=11, fontweight="medium")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#bbb")
    ax.spines["bottom"].set_color("#bbb")
    ax.tick_params(axis="x", labelsize=11, length=0)
    ax.tick_params(axis="y", labelsize=9, colors="#555")
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.3)
    ax.set_ylim(0, y_max * 1.18)


def generate_plots(results: dict[str, dict], output_dir: str = ".") -> None:
    """
    Create four individual bar charts + one 2×2 overview, all saved as PNG.
    """
    os.makedirs(output_dir, exist_ok=True)
    names = list(results.keys())
    total_agents = 50

    # ── Metrics definitions ─────────────────────────────────────────────
    #  ( result-key,       y-label,                  title,                        file,                higher_better, fmt,    fraction )
    specs = [
        ("Evacuated",      "Agents Evacuated",       "Evacuated Agents (out of 50)", "evacuated.png",     True,  "auto", True),
        ("Evacuation Time","Time (frames)",           "Evacuation Time",              "evacuation_time.png", False, "auto", False),
        ("Throughput",     "Throughput (agents/frame)","Throughput",                  "throughput.png",    True,  "f4",   False),
        ("Efficiency %",   "Efficiency (%)",          "Evacuation Efficiency",        "efficiency.png",    True,  "pct",  False),
    ]

    # ── Individual charts ───────────────────────────────────────────────
    for key, ylabel, title, fname, higher, fmt, frac in specs:
        values = [results[n].get(key, 0) for n in names]
        fig, ax = plt.subplots(figsize=(8, 4.5))
        _bar_chart(ax, names, values, ylabel,
                   f"Algorithm Comparison — {title}",
                   higher_is_better=higher, fmt=fmt,
                   total_agents=total_agents, show_fraction=frac)
        fig.tight_layout()
        path = os.path.join(output_dir, fname)
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {path}")

    # ── Combined 2×2 overview ──────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    for idx, (key, ylabel, title, _, higher, fmt, frac) in enumerate(specs):
        ax = axes[idx // 2][idx % 2]
        values = [results[n].get(key, 0) for n in names]
        _bar_chart(ax, names, values, ylabel, title,
                   higher_is_better=higher, fmt=fmt,
                   total_agents=total_agents, show_fraction=frac)

    fig.suptitle("RS-SSTO Framework — Algorithm Comparison",
                 fontsize=16, fontweight="bold", y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    overview = os.path.join(output_dir, "comparison_overview.png")
    fig.savefig(overview, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {overview}")
