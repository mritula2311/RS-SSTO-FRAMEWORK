"""Surface tension inspired force to reduce excessive clustering."""

from __future__ import annotations

import numpy as np

from config import CONFIG
from utils.math_utils import normalize


def surface_tension_force(index: int, positions: np.ndarray) -> np.ndarray:
    """Repel close neighbors to maintain preferred spacing."""
    force = np.zeros(2, dtype=float)
    p_i = positions[index]
    for j, p_j in enumerate(positions):
        if j == index:
            continue
        delta = p_i - p_j
        dist = np.linalg.norm(delta)
        if dist < 1e-6:
            continue
        if dist < CONFIG.preferred_spacing:
            magnitude = CONFIG.rs_surface_gain * (CONFIG.preferred_spacing - dist)
            force += magnitude * normalize(delta) / CONFIG.preferred_spacing
    return force
