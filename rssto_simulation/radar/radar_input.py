"""Radar input module that initializes agent detections in the scene."""

from __future__ import annotations

import numpy as np

from config import CONFIG


def generate_radar_detections(seed: int | None = 42) -> list[tuple[float, float]]:
    """Generate initial agent coordinates as if detected by radar sensing.

    Positions are sampled away from obstacles, hazard center, and map boundaries.
    """

    rng = np.random.default_rng(seed)
    positions: list[tuple[float, float]] = []

    def in_obstacle(x: float, y: float) -> bool:
        for ox, oy, ow, oh in CONFIG.obstacles:
            if ox <= x <= ox + ow and oy <= y <= oy + oh:
                return True
        return False

    while len(positions) < CONFIG.n_agents:
        x = rng.uniform(40.0, 240.0)
        y = rng.uniform(40.0, CONFIG.height - 40.0)
        hx, hy = CONFIG.hazard_center
        if np.hypot(x - hx, y - hy) < CONFIG.hazard_radius * 0.5:
            continue
        if in_obstacle(x, y):
            continue
        positions.append((x, y))

    return positions
