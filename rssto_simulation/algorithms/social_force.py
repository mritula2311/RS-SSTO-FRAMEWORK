"""Social Force Model (Helbing-inspired) implementation."""

from __future__ import annotations

import numpy as np

from config import CONFIG
from utils.math_utils import normalize


def compute_forces(agents, env, _state=None):
    positions = np.array([a.position for a in agents])
    forces = []
    for i, agent in enumerate(agents):
        if agent.evacuated:
            forces.append(np.zeros(2))
            continue

        to_goal = env.exit_center - agent.position
        goal_force = CONFIG.goal_force_gain * normalize(to_goal)

        repulsion = np.zeros(2, dtype=float)
        for j, other in enumerate(agents):
            if i == j or other.evacuated:
                continue
            delta = agent.position - other.position
            dist = np.linalg.norm(delta)
            if dist < 1e-6:
                continue
            repulsion += CONFIG.repulsion_gain * np.exp(-dist / 18.0) * normalize(delta)

        obstacle_force = env.obstacle_repulsion(agent.position)
        total = goal_force + repulsion + obstacle_force
        forces.append(total)
    return forces
