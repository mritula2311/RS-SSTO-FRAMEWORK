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
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
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


def _draw_env(ax, env):
    """Draw environment elements: bounds, obstacles, hazard, exit."""
    ax.set_xlim(0, env.width)
    ax.set_ylim(0, env.height)
    ax.set_aspect("equal")
    ax.set_facecolor("#f6f6f6")
    for obs in env.obstacles:
        ax.add_patch(plt.Rectangle((obs.x, obs.y), obs.w, obs.h, color="black", zorder=2))
    ax.add_patch(plt.Circle(env.hazard_pos, env.hazard_radius, color="#ef4444", alpha=0.4, zorder=1))
    ax.add_patch(plt.Circle(env.exit.pos, env.exit.radius, color="#22c55e", alpha=0.6, zorder=1))
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_color("#777")
    ax.tick_params(axis="both", colors="#333", labelsize=8)


def _add_algorithm_annotations(ax, frames, algorithm_name, snapshot_idx, env):
    """
    Add visual annotations highlighting algorithm-specific behaviours.
    Makes scientific differences more visible.
    """
    if snapshot_idx >= len(frames):
        return
        
    positions = frames[snapshot_idx]
    active_pos = np.array([p for p in positions if np.linalg.norm(p) > 1.0])
    
    if len(active_pos) < 2:
        return
    
    # Algorithm-specific visual indicators
    if algorithm_name == "SFM":
        # Show crowd pressure zones (agents clustering together)
        for i, pos in enumerate(active_pos):
            nearby = sum(1 for other in active_pos 
                        if np.linalg.norm(pos - other) < 30.0) - 1
            if nearby >= 3:  # High-density cluster
                ax.add_patch(plt.Circle(pos, 20, color="#ff6b6b", 
                                       alpha=0.15, zorder=1, linewidth=0))
    
    elif algorithm_name == "ACO":
        # Show pheromone trail convergence (similar paths)
        # Draw guidance arrows showing trail direction toward exit
        exit_dir = env.exit.pos - active_pos.mean(axis=0)
        exit_dir = exit_dir / (np.linalg.norm(exit_dir) + 1e-6)
        center = active_pos.mean(axis=0)
        ax.arrow(center[0], center[1], exit_dir[0]*40, exit_dir[1]*40,
                head_width=15, head_length=12, fc="#f39c12", ec="#f39c12",
                alpha=0.3, zorder=2, linewidth=1.5)
    
    elif algorithm_name == "PSO":
        # Show swarm cohesion (agents moving together)
        centroid = active_pos.mean(axis=0)
        ax.add_patch(plt.Circle(centroid, 35, color="#3498db", 
                               fill=False, linewidth=2, linestyle="--",
                               alpha=0.4, zorder=2))
    
    elif algorithm_name == "APF":
        # Show potential field flow (smooth curves avoiding obstacles)
        # Draw field lines from agents toward exit
        for pos in active_pos[::3]:  # Sample every 3rd agent
            to_exit = env.exit.pos - pos
            dist = np.linalg.norm(to_exit)
            if dist > 10:
                direction = to_exit / dist
                ax.arrow(pos[0], pos[1], direction[0]*25, direction[1]*25,
                        head_width=8, head_length=6, fc="#f39c12", ec="#f39c12",
                        alpha=0.25, zorder=1, linewidth=1)
    
    elif algorithm_name == "RS-SSTO":
        # Show fluid flow distribution (spread out, avoiding congestion)
        # Highlight optimized spacing
        for i, pos in enumerate(active_pos[::4]):  # Sample every 4th
            ax.add_patch(plt.Circle(pos, 15, color="#9b59b6",
                                   fill=False, linewidth=1.5, alpha=0.3, zorder=2))


def _plot_sample_trajectories(ax, frames, count=30, algorithm_name=""):
    """
    Plot trajectories showing evacuation PROCESS matching reference image style.
    Shows agents at mid-evacuation with prominent curved trails.
    """
    if not frames or len(frames) < 3:
        return

    n_frames = len(frames)
    n_agents = frames[0].shape[0]

    # Use snapshot timing that shows clear evacuation process
    # Reference image shows agents well-distributed with visible trajectories
    if algorithm_name == "SFM" and n_frames > 200:
        snapshot_frame_idx = min(int(n_frames * 0.18), n_frames - 1)  # SFM: very early (18%) to show full approach trajectories
    elif algorithm_name == "ACO" and n_frames > 60:
        snapshot_frame_idx = min(40, n_frames - 1)  # ACO: early snapshot
    elif n_frames > 200:
        snapshot_frame_idx = min(int(n_frames * 0.6), n_frames - 1)  # 60% progress
    else:
        snapshot_frame_idx = min(int(n_frames * 0.7), n_frames - 1)  # 70% for shorter runs
    
    # Sample many agents to show clear movement patterns (like reference)
    idxs = np.linspace(0, max(0, n_agents - 1), min(count, n_agents), dtype=int)
    
    # blue → yellow → white gradient matching reference image style
    trail_cmap = LinearSegmentedColormap.from_list("trail", ["#2563eb", "#facc15", "#ffffff"])

    # Draw full trajectory paths (not just recent segments)
    for agent_idx in idxs:
        # Get complete path from start to snapshot frame
        path = np.array([f[agent_idx] for f in frames[:snapshot_frame_idx+1]], dtype=float)
        if len(path) < 3:
            continue
        
        # Use full path or last N frames (show complete movement patterns)
        # SFM gets longer trails to show full individual approach paths
        if algorithm_name == "SFM":
            keep = min(500, len(path))  # Extended trails for SFM
        else:
            keep = min(300, len(path))
        path = path[-keep:]
        
        if len(path) < 2:
            continue
            
        points = path.reshape(-1, 1, 2)
        segs = np.concatenate([points[:-1], points[1:]], axis=1)
        colours = np.linspace(0, 1, len(segs))
        lc = LineCollection(segs, cmap=trail_cmap, norm=plt.Normalize(0, 1))
        lc.set_array(colours)
        if algorithm_name == "PSO":
            lc.set_linewidth(1.5)
        elif algorithm_name == "RS-SSTO":
            lc.set_linewidth(2.5)
        else:
            lc.set_linewidth(2.5)
        lc.set_alpha(0.7)
        lc.set_zorder(3)
        ax.add_collection(lc)
    
    # Show ALL agent positions at the snapshot frame
    # Matches reference image style with clear blue dots
    snapshot_positions = frames[snapshot_frame_idx]
    
    # Filter to show only active agents (not already evacuated)
    active_positions = [pos for pos in snapshot_positions 
                       if not (np.linalg.norm(pos) < 1.0)]  # Exclude zero positions
    
    if len(active_positions) > 0:
        active_array = np.array(active_positions)
        # Blue dots matching reference image exactly
        ax.scatter(active_array[:, 0], active_array[:, 1], 
                  s=25, c="#1e40af", edgecolors="none", 
                  zorder=4, alpha=0.95)
    
    return snapshot_frame_idx


def generate_behavior_panel(traces: dict[str, list[np.ndarray]], env, output_dir: str = ".") -> None:
    """Create a 5-panel behaviour comparison with a common environment legend."""
    if not traces:
        return
    os.makedirs(output_dir, exist_ok=True)

    order = ["SFM", "ACO", "APF", "PSO", "RS-SSTO"]
    available = [name for name in order if name in traces and traces[name]]
    if not available:
        return

    fig = plt.figure(figsize=(14, 8.5))
    # 2x6 grid: top row has 3 equal panels, bottom row has 2 wide panels
    gs = fig.add_gridspec(2, 6, hspace=0.32, wspace=0.24)

    # custom placement so bottom row has two wide panels like reference style
    custom_axes = {
        "SFM": fig.add_subplot(gs[0, 0:2]),
        "ACO": fig.add_subplot(gs[0, 2:4]),
        "APF": fig.add_subplot(gs[0, 4:6]),
        "PSO": fig.add_subplot(gs[1, 0:3]),
        "RS-SSTO": fig.add_subplot(gs[1, 3:6]),
    }

    for name in order:
        if name not in custom_axes or name not in traces or not traces[name]:
            continue
        ax = custom_axes[name]
        frames = traces[name]
        _draw_env(ax, env)
        snapshot_idx = _plot_sample_trajectories(ax, frames, algorithm_name=name)
        # Clean title matching reference image style
        if snapshot_idx is not None:
            ax.set_title(f"{name} Evacuation", fontsize=14, fontweight="medium")
        else:
            ax.set_title(f"{name} Evacuation", fontsize=14, fontweight="medium")

    # Clean legend matching reference image style
    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#1d4ed8", 
                   markersize=8, label="Agents"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#22c55e", 
                   markersize=10, label="Exit"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#ef4444", 
                   markersize=10, label="Hazard"),
        plt.Rectangle((0, 0), 1, 1, color="black", label="Obstacles"),
        plt.Line2D([0], [0], color="#60a5fa", linewidth=2.5, 
                   label="Movement trajectories"),
    ]
    
    fig.legend(handles=legend_handles, loc="lower center", ncol=5, 
              frameon=False, fontsize=10)
    title = "Algorithm-wise Evacuation Behaviour Comparison"
    fig.suptitle(title, fontsize=16, fontweight="bold", y=0.98)
    fig.subplots_adjust(bottom=0.10)

    filename = "behaviour_comparison.png"
    out = os.path.join(output_dir, filename)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out}")
