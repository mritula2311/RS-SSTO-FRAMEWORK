"""
Exit Module
===========
Represents the evacuation exit point.
"""

import numpy as np
from config import EXIT_POS, EXIT_RADIUS


class Exit:
    """Single exit point on the map."""

    def __init__(self):
        self.pos    = np.array(EXIT_POS, dtype=float)
        self.radius = EXIT_RADIUS

    def contains(self, point: np.ndarray) -> bool:
        return float(np.linalg.norm(point - self.pos)) < self.radius
