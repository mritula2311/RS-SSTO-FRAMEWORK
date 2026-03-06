"""Math utility helpers for the RS-SSTO simulation."""

import numpy as np


def distance(a: np.ndarray, b: np.ndarray) -> float:
    """Euclidean distance between two 2-D points."""
    return float(np.linalg.norm(a - b))


def unit_vector(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Unit vector pointing from *a* toward *b*."""
    d = b - a
    n = np.linalg.norm(d)
    if n < 1e-8:
        return np.zeros(2)
    return d / n


def clamp_speed(vel: np.ndarray, max_speed: float) -> np.ndarray:
    """Clamp a velocity vector to *max_speed*."""
    s = np.linalg.norm(vel)
    if s > max_speed and s > 0:
        return vel * (max_speed / s)
    return vel
