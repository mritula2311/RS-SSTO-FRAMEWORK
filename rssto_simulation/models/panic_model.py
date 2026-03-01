"""
Dynamic Panic Coefficient Model
================================
Pc = α · Density + β · HazardFactor

Panic influences agent speed and adds erratic perturbation.
"""

from __future__ import annotations
import numpy as np
from config import RSSTO_PANIC_ALPHA, RSSTO_PANIC_BETA, HAZARD_RADIUS


def compute_panic(agent, agents: list, hazard_pos: np.ndarray,
                  hazard_radius: float = HAZARD_RADIUS,
                  alpha: float = RSSTO_PANIC_ALPHA,
                  beta: float = RSSTO_PANIC_BETA) -> float:
    """
    Compute panic coefficient Pc ∈ [0, 1] for a single agent.

    Parameters
    ----------
    agent      : the agent whose panic we compute
    agents     : all active agents (for density)
    hazard_pos : centre of hazard zone
    hazard_radius : radius of hazard
    alpha, beta : weighting factors

    Returns
    -------
    Pc : float in [0, 1]
    """
    # ── density factor ──────────────────────────────────────────
    count = 0
    for other in agents:
        if other is agent or other.evacuated:
            continue
        if float(np.linalg.norm(agent.pos - other.pos)) < 30.0:
            count += 1
    # Normalise: 10+ neighbours → density 1.0
    density = min(count / 10.0, 1.0)

    # ── hazard proximity factor ─────────────────────────────────
    d_hazard = float(np.linalg.norm(agent.pos - hazard_pos))
    if d_hazard < hazard_radius:
        hazard_factor = 1.0
    elif d_hazard < hazard_radius * 3:
        hazard_factor = 1.0 - (d_hazard - hazard_radius) / (hazard_radius * 2)
    else:
        hazard_factor = 0.0
    hazard_factor = max(0.0, hazard_factor)

    # ── combine ─────────────────────────────────────────────────
    pc = alpha * density + beta * hazard_factor
    return float(np.clip(pc, 0.0, 1.0))


def panic_velocity_perturbation(panic: float, rng: np.random.Generator | None = None) -> np.ndarray:
    """
    Return a small random velocity perturbation scaled by panic.

    Higher panic → more erratic movement.
    """
    if rng is None:
        rng = np.random.default_rng()
    return rng.normal(0, 1, size=2) * panic * 0.6
