"""Dynamic panic model driven by local density and hazard proximity."""

from __future__ import annotations

import numpy as np

from config import CONFIG
from utils.math_utils import pairwise_neighbors


def compute_dynamic_panic(positions: np.ndarray) -> np.ndarray:
    """panic = density_factor + hazard_proximity_factor for each agent."""
    neighbors = pairwise_neighbors(positions, CONFIG.sensor_radius)
    hazard = np.array(CONFIG.hazard_center, dtype=float)

    panic = np.zeros(len(positions), dtype=float)
    for i, pos in enumerate(positions):
        density_factor = min(1.0, len(neighbors[i]) / 10.0)
        hazard_dist = np.linalg.norm(pos - hazard)
        hazard_proximity = max(0.0, 1.0 - hazard_dist / (CONFIG.hazard_radius * 2.5))
        panic[i] = density_factor + hazard_proximity
    return panic
