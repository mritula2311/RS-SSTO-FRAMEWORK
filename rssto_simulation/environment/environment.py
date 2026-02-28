"""
Environment Module
==================
Aggregates the map, exit, hazard zone, and obstacles.
"""

from __future__ import annotations
import numpy as np
from config import MAP_WIDTH, MAP_HEIGHT, HAZARD_POS, HAZARD_RADIUS
from environment.exit import Exit
from environment.obstacles import Obstacle, generate_obstacles


class Environment:
    """Complete simulation environment."""

    def __init__(self, seed: int | None = None):
        self.width: int             = MAP_WIDTH
        self.height: int            = MAP_HEIGHT
        self.exit: Exit             = Exit()
        self.hazard_pos: np.ndarray = np.array(HAZARD_POS, dtype=float)
        self.hazard_radius: float   = HAZARD_RADIUS
        self.obstacles: list[Obstacle] = generate_obstacles(seed)

    def is_inside_hazard(self, pos: np.ndarray) -> bool:
        return float(np.linalg.norm(pos - self.hazard_pos)) < self.hazard_radius

    def is_inside_obstacle(self, pos: np.ndarray) -> bool:
        return any(o.contains(pos) for o in self.obstacles)

    def nearest_obstacle_point(self, pos: np.ndarray) -> tuple[np.ndarray, float]:
        """Return (nearest_point, distance) to the closest obstacle edge."""
        best_p   = pos.copy()
        best_d   = float("inf")
        for o in self.obstacles:
            p = o.nearest_point(pos)
            d = float(np.linalg.norm(pos - p))
            if d < best_d:
                best_d = d
                best_p = p
        return best_p, best_d
