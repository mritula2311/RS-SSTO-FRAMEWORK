"""
Agent Module
============
Represents a single evacuating person in the simulation.
"""

from __future__ import annotations
import numpy as np
from utils.math_utils import distance, clamp_speed
from config import AGENT_MAX_SPEED, EXIT_POS, EXIT_RADIUS


class Agent:
    """A single evacuee / victim."""

    __slots__ = (
        "pos", "vel", "panic", "goal", "evacuated",
        "mass", "max_speed", "radius",
        # PSO memory
        "pbest_pos", "pbest_dist",
    )

    def __init__(self, x: float, y: float):
        self.pos: np.ndarray      = np.array([x, y], dtype=float)
        self.vel: np.ndarray      = np.zeros(2, dtype=float)
        self.panic: float         = 0.0
        self.goal: np.ndarray     = np.array(EXIT_POS, dtype=float)
        self.evacuated: bool      = False
        self.mass: float          = 1.0
        self.max_speed: float     = AGENT_MAX_SPEED
        self.radius: float        = 4.0

        # PSO personal best
        self.pbest_pos: np.ndarray  = self.pos.copy()
        self.pbest_dist: float      = distance(self.pos, self.goal)

    # ── core interface ────────────────────────────────────────────────────
    def apply_force(self, force: np.ndarray, dt: float = 1.0) -> None:
        """Apply a force vector and update velocity (F = ma, a = F/m)."""
        acc = force / self.mass
        self.vel = self.vel + acc * dt
        self.vel = clamp_speed(self.vel, self.max_speed)

    def update_position(self, dt: float = 1.0) -> None:
        """Advance position by velocity × dt and check exit."""
        self.pos = self.pos + self.vel * dt

        # Boundary clamping
        self.pos[0] = np.clip(self.pos[0], 0, 800)
        self.pos[1] = np.clip(self.pos[1], 0, 600)

        if self.calculate_distance(self.goal) < EXIT_RADIUS:
            self.evacuated = True

        # Update PSO personal best
        d = self.calculate_distance(self.goal)
        if d < self.pbest_dist:
            self.pbest_pos  = self.pos.copy()
            self.pbest_dist = d

    def calculate_distance(self, target: np.ndarray) -> float:
        """Euclidean distance to *target*."""
        return distance(self.pos, target)

    def reset(self, x: float, y: float) -> None:
        """Reset agent to a fresh starting state at (x, y)."""
        self.pos          = np.array([x, y], dtype=float)
        self.vel          = np.zeros(2, dtype=float)
        self.panic        = 0.0
        self.goal         = np.array(EXIT_POS, dtype=float)
        self.evacuated    = False
        self.pbest_pos    = self.pos.copy()
        self.pbest_dist   = distance(self.pos, self.goal)
