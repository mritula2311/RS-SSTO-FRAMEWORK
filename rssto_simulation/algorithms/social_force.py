"""
Social Force Model (SFM) — Helbing & Molnár 1995
=================================================
Each agent feels:
  1. **Goal force** — accelerating toward the exit at desired speed.
  2. **Agent-agent repulsion** — exponential decay: A·exp(−d/B)·n̂
  3. **Obstacle repulsion** — same exponential form from nearest obstacle edge.
"""

from __future__ import annotations
import numpy as np
from config import (
    SFM_DESIRED_SPEED, SFM_RELAX_TIME,
    SFM_REPULSION_A, SFM_REPULSION_B,
)
from utils.math_utils import unit_vector, distance


def sfm_step(agents: list, environment, dt: float = 1.0) -> None:
    """Advance every non-evacuated agent by one SFM tick."""
    for agent in agents:
        if agent.evacuated:
            continue

        force = np.zeros(2)

        # 1. Goal (driving) force
        direction = unit_vector(agent.pos, agent.goal)
        desired_vel = SFM_DESIRED_SPEED * direction
        force += (desired_vel - agent.vel) / SFM_RELAX_TIME

        # 2. Agent-agent social repulsion (bounded)
        for other in agents:
            if other is agent or other.evacuated:
                continue
            diff = agent.pos - other.pos
            d = float(np.linalg.norm(diff))
            if d < 1e-6 or d > 40:
                continue
            n_hat = diff / d
            # Helbing-style but capped to avoid blow-up
            rep_mag = min(SFM_REPULSION_A * np.exp(-d / (SFM_REPULSION_B * 100)), 8.0)
            force += rep_mag * n_hat

        # 3. Obstacle repulsion
        for obs in environment.obstacles:
            nearest = obs.nearest_point(agent.pos)
            diff = agent.pos - nearest
            d = float(np.linalg.norm(diff))
            if d < 1e-6 or d > 60:
                continue
            n_hat = diff / d
            force += min(SFM_REPULSION_A * np.exp(-d / (SFM_REPULSION_B * 300)), 5.0) * n_hat

        # 4. Hazard avoidance — push away from hazard centre
        hdiff = agent.pos - environment.hazard_pos
        hdist = float(np.linalg.norm(hdiff))
        if hdist < environment.hazard_radius * 2.5 and hdist > 1e-6:
            h_hat = hdiff / hdist
            strength = 4.0 * max(1.0 - hdist / (environment.hazard_radius * 2.5), 0)
            force += strength * h_hat

        agent.apply_force(force, dt)
        agent.update_position(dt)
