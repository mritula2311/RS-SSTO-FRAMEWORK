"""
Artificial Potential Field (APF) Algorithm
==========================================
Three potential fields combine:
  1. **Attractive** — pulls agents toward the exit.
  2. **Repulsive (obstacles / hazard)** — pushes agents away from dangers.
  3. **Agent-agent repulsion** — prevents overcrowding.

    F_attract = k_att · (goal − x)
    F_repulse = k_rep · (1/d − 1/d0)² · (1/d²) · n̂     when d < d0
"""

from __future__ import annotations
import numpy as np
from config import APF_ATTRACT_GAIN, APF_REPULSE_GAIN, APF_REPULSE_RANGE
from utils.math_utils import unit_vector, distance, clamp_speed


def apf_step(agents: list, environment, dt: float = 1.0) -> None:
    """Advance every non-evacuated agent by one APF tick."""
    d0 = APF_REPULSE_RANGE

    for agent in agents:
        if agent.evacuated:
            continue

        force = np.zeros(2)

        # 1. Attractive force — toward exit
        diff_goal = agent.goal - agent.pos
        dist_goal = float(np.linalg.norm(diff_goal))
        if dist_goal > 1e-6:
            force += APF_ATTRACT_GAIN * (diff_goal / dist_goal)

        # 2. Repulsive — obstacles
        for obs in environment.obstacles:
            nearest = obs.nearest_point(agent.pos)
            diff = agent.pos - nearest
            d = float(np.linalg.norm(diff))
            if 0 < d < d0:
                n_hat = diff / d
                force += APF_REPULSE_GAIN * ((1.0 / d - 1.0 / d0) ** 2) * (1.0 / (d * d)) * n_hat * 0.2

        # 3. Repulsive — hazard zone
        hdiff = agent.pos - environment.hazard_pos
        hdist = float(np.linalg.norm(hdiff))
        if 0 < hdist < environment.hazard_radius * 2:
            h_hat = hdiff / hdist
            force += APF_REPULSE_GAIN * ((1.0 / hdist - 1.0 / (environment.hazard_radius * 2)) ** 2) * (1.0 / (hdist * hdist)) * h_hat * 0.15

        # 4. Agent-agent repulsion (light)
        for other in agents:
            if other is agent or other.evacuated:
                continue
            adiff = agent.pos - other.pos
            ad = float(np.linalg.norm(adiff))
            if 0 < ad < 25:
                force += (adiff / ad) * (25 - ad) * 0.05

        agent.apply_force(force, dt)
        # Keep APF in medium-speed regime and emphasize smooth field curvature.
        agent.vel = clamp_speed(agent.vel, agent.max_speed * 0.72)
        agent.update_position(dt)
