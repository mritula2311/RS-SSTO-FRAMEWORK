"""Entry point for running algorithm comparisons in RS-SSTO project."""

from __future__ import annotations

import argparse
import pandas as pd

from config import CONFIG
from metrics.comparison import build_comparison_table
from visualization.simulator import Simulator
from visualization.plots import plot_comparison


def run_all_algorithms(visualize: bool = False) -> pd.DataFrame:
    algorithm_order = ["social_force", "pso", "aco", "apf", "rssto"]
    results = []

    for idx, algo in enumerate(algorithm_order):
        sim = Simulator(algorithm_module=algo, visualize=visualize, seed=42 + idx)
        results.append(sim.run())

    return build_comparison_table(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="RS-SSTO Evacuation Algorithm Comparison")
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Enable real-time pygame visualization for each algorithm run.",
    )
    args = parser.parse_args()

    visualize = args.visualize or CONFIG.visualize
    df = run_all_algorithms(visualize=visualize)

    # Output table requested in the specification.
    print("\nAlgorithm | Time | Congestion | Throughput")
    for _, row in df.iterrows():
        print(
            f"{row['Algorithm']:>10s} | {row['EvacuationTime']:>6.2f} | "
            f"{row['Congestion']:>10.3f} | {row['Throughput']:>10.3f}"
        )

    print("\nFull comparison DataFrame:\n")
    print(df.to_string(index=False))

    plot_comparison(df)


if __name__ == "__main__":
    main()
