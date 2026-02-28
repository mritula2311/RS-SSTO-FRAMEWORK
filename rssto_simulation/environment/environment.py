"""Environment definition and collision / evacuation checks."""

from __future__ import annotations

import numpy as np

from config import CONFIG


class Environment:
    """2D evacuation scene with obstacles, hazard, and a single exit."""

    def __init__(self) -> None:
        self.width = CONFIG.width
        self.height = CONFIG.height
        self.exit_center = np.array(
            [CONFIG.exit_x, (CONFIG.exit_y_min + CONFIG.exit_y_max) / 2.0], dtype=float
        )

    def check_exit(self, position: np.ndarray) -> bool:
        x, y = position
        return x >= CONFIG.exit_x and CONFIG.exit_y_min <= y <= CONFIG.exit_y_max

    def enforce_bounds(self, position: np.ndarray, velocity: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Clip position to map and damp velocity upon wall contact."""
        x, y = position
        vx, vy = velocity

        if x < 0:
            x, vx = 0.0, -0.2 * vx
        elif x > self.width:
            x, vx = self.width, -0.2 * vx

        if y < 0:
            y, vy = 0.0, -0.2 * vy
        elif y > self.height:
            y, vy = self.height, -0.2 * vy

        return np.array([x, y], dtype=float), np.array([vx, vy], dtype=float)

    def obstacle_repulsion(self, position: np.ndarray) -> np.ndarray:
        """Repulsive force from rectangular obstacles."""
        total = np.zeros(2, dtype=float)
        for ox, oy, ow, oh in CONFIG.obstacles:
            nearest_x = np.clip(position[0], ox, ox + ow)
            nearest_y = np.clip(position[1], oy, oy + oh)
            delta = position - np.array([nearest_x, nearest_y], dtype=float)
            dist = np.linalg.norm(delta)
            if dist < 1e-6:
                delta = np.array([1.0, 0.0])
                dist = 1.0
            influence = max(0.0, 40.0 - dist)
            if influence > 0:
                total += (
                    CONFIG.obstacle_repulsion_gain
                    * influence
                    * delta
                    / (dist**3 + 1e-6)
                )
        return total

    def hazard_penalty_direction(self, position: np.ndarray) -> np.ndarray:
        """Direction pointing away from hazard center, weighted by proximity."""
        hazard = np.array(CONFIG.hazard_center, dtype=float)
        delta = position - hazard
        dist = np.linalg.norm(delta)
        if dist < 1e-6:
            delta = np.array([1.0, 0.0])
            dist = 1.0
        intensity = max(0.0, (CONFIG.hazard_radius * 2 - dist) / (CONFIG.hazard_radius * 2))
        return intensity * delta / dist
