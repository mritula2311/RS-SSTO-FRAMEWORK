"""Plotting helpers for algorithm comparison."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def plot_comparison(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    axes[0].bar(df["Algorithm"], df["EvacuationTime"], color="#4f81bd")
    axes[0].set_title("Evacuation Time Comparison")
    axes[0].set_ylabel("Time (s)")
    axes[0].tick_params(axis="x", rotation=35)

    axes[1].bar(df["Algorithm"], df["Congestion"], color="#c0504d")
    axes[1].set_title("Congestion Comparison")
    axes[1].set_ylabel("Mean Congestion")
    axes[1].tick_params(axis="x", rotation=35)

    efficiency = 1.0 / (df["EvacuationTime"] + 1e-6)
    axes[2].bar(df["Algorithm"], efficiency, color="#9bbb59")
    axes[2].set_title("Efficiency Comparison")
    axes[2].set_ylabel("1 / Time")
    axes[2].tick_params(axis="x", rotation=35)

    fig.tight_layout()
    plt.show()
