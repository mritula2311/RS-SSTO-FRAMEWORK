"""
Surface Tension Optimization Module
====================================
Treats agents as fluid particles.
If two agents are closer than the safe distance,
a repulsion (surface-tension) force pushes them apart:

    F = k · (x_i − x_j)    when  dist < safe_distance

This prevents congestion and stampede-like pileups.
"""

from __future__ import annotations
import numpy as np
from config import RSSTO_TENSION_K, RSSTO_SAFE_DIST


def compute_surface_tension_force(
    agent,
    agents: list,
    k: float = RSSTO_TENSION_K,
    safe_dist: float = RSSTO_SAFE_DIST,
) -> np.ndarray:
    """
    Compute the total surface-tension (separation) force on *agent*.

    For every neighbour within *safe_dist*:
        F += k · (agent.pos − other.pos) / dist

    Returns
    -------
    np.ndarray  (2,)  total repulsive force
    """
    force = np.zeros(2)
    for other in agents:
        if other is agent or other.evacuated:
            continue
        diff = agent.pos - other.pos
        dist = float(np.linalg.norm(diff))
        if 0 < dist < safe_dist:
            # Stronger push the closer they are
            strength = k * (safe_dist - dist) / dist
            force += strength * (diff / dist)
    return force
