"""
RS-SSTO Evacuation Simulation — Main Entry Point
=================================================
Usage:
    python main.py              # headless comparison (no pygame window)
    python main.py --visual     # real-time pygame visualisation
    python main.py --plots      # headless + save comparison plots
    python main.py --all        # visual + plots

Compares five algorithms:  SFM, PSO, ACO, APF, RS-SSTO
"""

from __future__ import annotations
import argparse
import sys
import os

# Ensure the project root is on sys.path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(
        description="RS-SSTO Evacuation Simulation Framework",
    )
    parser.add_argument("--visual", action="store_true",
                        help="Run with pygame visualisation")
    parser.add_argument("--visual-split", type=str, metavar="A,B",
                        help="Split-screen visualise two algorithms (comma-separated). Default when provided: PSO,RS-SSTO")
    parser.add_argument("--plots", action="store_true",
                        help="Generate matplotlib comparison plots")
    parser.add_argument("--all", action="store_true",
                        help="Visual + plots")
    parser.add_argument("--record-visual", action="store_true",
                        help="Record pygame visual runs to GIF/MP4")
    parser.add_argument("--record-format", default="mp4",
                        choices=["gif", "mp4", "both"],
                        help="Format for visual recordings (default mp4; both saves gif and mp4)")
    parser.add_argument("--record-dir", default=None,
                        help="Output directory for visual recordings (default: output/animations)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default 42)")
    args = parser.parse_args()

    if args.all:
        args.visual = True
        args.plots  = True

    # -- Run the simulation -----------------------------------------------
    anim_traces = None
    anim_env = None

    if args.visual_split:
        from visualization.simulator import run_visual_split
        pair = [s.strip() for s in args.visual_split.split(",") if s.strip()]
        if len(pair) != 2:
            print("[WARN] --visual-split expects two comma-separated names; using default PSO,RS-SSTO")
            pair = ["PSO", "RS-SSTO"]
        results = run_visual_split(
            pair,
            seed=args.seed,
            record=args.record_visual,
            record_format=args.record_format,
            record_dir=args.record_dir,
        )
    elif args.visual:
        from visualization.simulator import run_visual
        results = run_visual(
            seed=args.seed,
            record=args.record_visual,
            record_format=args.record_format,
            record_dir=args.record_dir,
        )
    else:
        from metrics.comparison import run_comparison
        results, anim_traces, anim_env = run_comparison(
            seed=args.seed, 
            record_positions=True
        )

    # -- Print comparison table -------------------------------------------
    if results:
        print()
        _print_table(results)

    # -- Generate plots ---------------------------------------------------
    if args.plots and results:
        from visualization.plots import generate_plots, generate_behavior_panel
        plot_dir = os.path.join(os.path.dirname(__file__), "output")
        print(f"\nGenerating plots → {plot_dir}")
        os.makedirs(plot_dir, exist_ok=True)
        generate_plots(results, output_dir=plot_dir)
        if anim_traces and anim_env is not None:
            generate_behavior_panel(anim_traces, anim_env, output_dir=plot_dir)

    print("\nDone.")


def _print_table(results: dict[str, dict]):
    """Pretty-print a comprehensive comparison table to stdout."""
    keys = ["Total Agents", "Evacuated", "Evac Time", "Avg Time", 
            "Throughput", "Congestion", "Efficiency"]
    header = f"{'Algorithm':>12s}"
    for k in keys:
        header += f"  {k:>12s}"
    print(header)
    print("-" * len(header))
    for name, m in results.items():
        row = f"{name:>12s}"
        for k in keys:
            val = m.get(k, "")
            row += f"  {str(val):>12s}"
        print(row)


if __name__ == "__main__":
    main()
