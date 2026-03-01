"""
Obstacles Module
================
Generates and stores rectangular obstacles.
"""

from __future__ import annotations
import numpy as np
from config import (
    MAP_WIDTH, MAP_HEIGHT, NUM_OBSTACLES,
    OBS_MIN_SIZE, OBS_MAX_SIZE,
    EXIT_POS, HAZARD_POS, HAZARD_RADIUS,
)


class Obstacle:
    """Axis-aligned rectangular obstacle."""

    __slots__ = ("x", "y", "w", "h")

    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def rect(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.w, self.h)

    @property
    def centre(self) -> np.ndarray:
        return np.array([self.x + self.w / 2, self.y + self.h / 2])

    def contains(self, p: np.ndarray) -> bool:
        return self.x <= p[0] <= self.x + self.w and self.y <= p[1] <= self.y + self.h

    def nearest_point(self, p: np.ndarray) -> np.ndarray:
        """Closest point on the rectangle boundary to *p*."""
        cx = np.clip(p[0], self.x, self.x + self.w)
        cy = np.clip(p[1], self.y, self.y + self.h)
        return np.array([cx, cy])


def generate_obstacles(seed: int | None = None) -> list[Obstacle]:
    """Create random obstacles avoiding hazard and exit zones."""
    rng = np.random.default_rng(seed)
    obstacles: list[Obstacle] = []
    attempts = 0

    while len(obstacles) < NUM_OBSTACLES and attempts < 500:
        attempts += 1
        w = rng.uniform(OBS_MIN_SIZE, OBS_MAX_SIZE)
        h = rng.uniform(OBS_MIN_SIZE, OBS_MAX_SIZE)
        x = rng.uniform(50, MAP_WIDTH - w - 50)
        y = rng.uniform(50, MAP_HEIGHT - h - 50)

        centre = np.array([x + w / 2, y + h / 2])

        # Keep clear of exit
        if np.linalg.norm(centre - np.array(EXIT_POS)) < 100:
            continue
        # Keep clear of hazard
        if np.linalg.norm(centre - np.array(HAZARD_POS)) < HAZARD_RADIUS + 40:
            continue
        # No overlap with existing
        overlap = False
        for o in obstacles:
            if (x < o.x + o.w + 10 and x + w + 10 > o.x and
                    y < o.y + o.h + 10 and y + h + 10 > o.y):
                overlap = True
                break
        if overlap:
            continue

        obstacles.append(Obstacle(x, y, w, h))

    return obstacles
