"""
Radar Input Module
==================
Simulates radar-based victim detection.
Returns a list of (x, y) positions for detected agents.
"""

from __future__ import annotations
import numpy as np
from config import MAP_WIDTH, MAP_HEIGHT, EXIT_POS, HAZARD_POS, HAZARD_RADIUS


def generate_agent_positions(n: int, seed: int | None = None) -> list[tuple[float, float]]:
    """
    Generate *n* random victim positions detected by radar.

    Positions are placed inside the map, outside the hazard zone,
    and away from the exit so agents must actually evacuate.

    Returns
    -------
    list of (x, y) tuples
    """
    rng = np.random.default_rng(seed)
    positions: list[tuple[float, float]] = []
    margin = 40  # keep away from edges

    while len(positions) < n:
        x = rng.uniform(margin, MAP_WIDTH - margin)
        y = rng.uniform(margin, MAP_HEIGHT - margin)

        # Must not be inside hazard
        dx = x - HAZARD_POS[0]
        dy = y - HAZARD_POS[1]
        if np.sqrt(dx * dx + dy * dy) < HAZARD_RADIUS + 20:
            continue

        # Must not be already at exit
        dx = x - EXIT_POS[0]
        dy = y - EXIT_POS[1]
        if np.sqrt(dx * dx + dy * dy) < 60:
            continue

        positions.append((x, y))

    return positions
