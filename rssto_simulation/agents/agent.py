"""Agent data structure and kinematics helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from config import CONFIG


@dataclass
class Agent:
    """Single evacuee with state used by all navigation algorithms."""

    position: np.ndarray
    velocity: np.ndarray
    acceleration: np.ndarray
    panic_coeff: float
    goal: np.ndarray
    evacuated: bool = False
    personal_best: np.ndarray = field(default_factory=lambda: np.zeros(2))

    def __post_init__(self) -> None:
        self.personal_best = self.position.copy()

    def apply_force(self, force: np.ndarray) -> None:
        """Apply resultant force as acceleration (unit mass assumption)."""
        self.acceleration = force

    def update(self, dt: float) -> None:
        """Integrate acceleration and velocity with speed clamping."""
        if self.evacuated:
            return
        self.velocity = self.velocity + self.acceleration * dt
        speed = np.linalg.norm(self.velocity)
        if speed > CONFIG.max_speed:
            self.velocity = self.velocity / (speed + 1e-8) * CONFIG.max_speed
        self.position = self.position + self.velocity * dt

    def distance(self, point: np.ndarray) -> float:
        """Euclidean distance to a point."""
        return float(np.linalg.norm(self.position - point))
