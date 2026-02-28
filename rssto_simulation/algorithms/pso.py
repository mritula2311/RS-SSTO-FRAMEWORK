"""
Particle Swarm Optimisation (PSO) Algorithm
============================================
Velocity update:
    v = w·v + c1·r1·(pbest − x) + c2·r2·(gbest − x)

Where:
  - pbest  = personal best position (closest to exit so far)
  - gbest  = global best position (agent currently closest to exit)
  - w      = inertia weight
  - c1, c2 = cognitive / social coefficients
"""

from __future__ import annotations
import numpy as np
from config import PSO_W, PSO_C1, PSO_C2
from utils.math_utils import distance, clamp_speed


def _find_gbest(agents: list) -> np.ndarray:
    """Return the position of the agent with the smallest pbest_dist."""
    best_agent = min(
        (a for a in agents if not a.evacuated),
        key=lambda a: a.pbest_dist,
        default=None,
    )
    if best_agent is None:
        return np.array([780, 300], dtype=float)   # fallback to exit
    return best_agent.pbest_pos.copy()


def pso_step(agents: list, environment, dt: float = 1.0) -> None:
    """Advance every non-evacuated agent by one PSO tick."""
    gbest = _find_gbest(agents)
    rng = np.random.default_rng()

    for agent in agents:
        if agent.evacuated:
            continue

        r1 = rng.random(2)
        r2 = rng.random(2)

        # PSO velocity update
        new_vel = (
            PSO_W  * agent.vel
            + PSO_C1 * r1 * (agent.pbest_pos - agent.pos)
            + PSO_C2 * r2 * (gbest           - agent.pos)
        )
        agent.vel = clamp_speed(new_vel, agent.max_speed)

        # Simple obstacle avoidance nudge
        for obs in environment.obstacles:
            nearest = obs.nearest_point(agent.pos)
            diff = agent.pos - nearest
            d = float(np.linalg.norm(diff))
            if 0 < d < 20:
                agent.vel += (diff / d) * 1.5

        # Hazard avoidance
        hdiff = agent.pos - environment.hazard_pos
        hdist = float(np.linalg.norm(hdiff))
        if hdist < environment.hazard_radius * 1.5 and hdist > 1e-6:
            agent.vel += (hdiff / hdist) * 2.0

        agent.vel = clamp_speed(agent.vel, agent.max_speed)
        agent.update_position(dt)
