"""Metric helpers for evacuation performance evaluation."""

from __future__ import annotations

import numpy as np


def compute_average_speed(speed_history: list[float]) -> float:
    return float(np.mean(speed_history)) if speed_history else 0.0


def compute_congestion(neighbor_counts: list[float]) -> float:
    """Mean local occupancy proxy (higher implies more congestion)."""
    return float(np.mean(neighbor_counts)) if neighbor_counts else 0.0


def compute_throughput(evacuated_counts: list[int], dt: float) -> float:
    if len(evacuated_counts) < 2:
        return 0.0
    total_time = len(evacuated_counts) * dt
    return float(evacuated_counts[-1] / max(total_time, 1e-6))
