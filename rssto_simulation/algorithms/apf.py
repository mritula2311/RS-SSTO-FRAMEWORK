"""Artificial Potential Field algorithm."""

from __future__ import annotations

import numpy as np

from config import CONFIG
from utils.math_utils import normalize


def compute_forces(agents, env, _state=None):
    forces = []
    for agent in agents:
        if agent.evacuated:
            forces.append(np.zeros(2))
            continue

        attr = CONFIG.apf_attr_gain * normalize(env.exit_center - agent.position) * 70.0
        rep = env.obstacle_repulsion(agent.position)

        for other in agents:
            if other is agent or other.evacuated:
                continue
            delta = agent.position - other.position
            dist = np.linalg.norm(delta)
            if 1e-6 < dist < 35:
                rep += CONFIG.apf_rep_gain * (1.0 / dist - 1.0 / 35.0) * normalize(delta)

        forces.append(attr + rep)
    return forces
