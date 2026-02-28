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
    parser.add_argument("--plots", action="store_true",
                        help="Generate matplotlib comparison plots")
    parser.add_argument("--all", action="store_true",
                        help="Visual + plots")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default 42)")
    args = parser.parse_args()

    if args.all:
        args.visual = True
        args.plots  = True

    # -- Run the simulation ------------------------------------------------
    if args.visual:
        from visualization.simulator import run_visual
        results = run_visual(seed=args.seed)
    else:
        from metrics.comparison import run_comparison
        results = run_comparison(seed=args.seed)

    # -- Print comparison table -------------------------------------------
    if results:
        print()
        _print_table(results)

    # -- Generate plots ---------------------------------------------------
    if args.plots and results:
        from visualization.plots import generate_plots
        plot_dir = os.path.join(os.path.dirname(__file__), "output")
        print(f"\nGenerating comparison plots → {plot_dir}")
        generate_plots(results, output_dir=plot_dir)

    print("\nDone.")


def _print_table(results: dict[str, dict]):
    """Pretty-print a comparison table to stdout."""
    keys = ["Evacuated", "Evacuation Time", "Avg Speed",
            "Congestion", "Throughput", "Efficiency %"]
    header = f"{'Algorithm':>10s}"
    for k in keys:
        header += f"  {k:>16s}"
    print(header)
    print("-" * len(header))
    for name, m in results.items():
        row = f"{name:>10s}"
        for k in keys:
            val = m.get(k, "")
            row += f"  {str(val):>16s}"
        print(row)


if __name__ == "__main__":
    main()
