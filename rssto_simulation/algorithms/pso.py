"""Particle Swarm Optimization based evacuation steering."""

from __future__ import annotations

import numpy as np

from config import CONFIG
from utils.math_utils import normalize


def init_state(agents, env):
    gbest = min(agents, key=lambda a: a.distance(env.exit_center)).position.copy()
    return {"gbest": gbest}


def compute_forces(agents, env, state):
    active = [a for a in agents if not a.evacuated]
    if active:
        state["gbest"] = min(active, key=lambda a: a.distance(env.exit_center)).position.copy()
    gbest = state["gbest"]

    forces = []
    for agent in agents:
        if agent.evacuated:
            forces.append(np.zeros(2))
            continue

        if agent.distance(env.exit_center) < np.linalg.norm(agent.personal_best - env.exit_center):
            agent.personal_best = agent.position.copy()

        r1 = np.random.rand(2)
        r2 = np.random.rand(2)
        v_new = (
            CONFIG.pso_w * agent.velocity
            + CONFIG.pso_c1 * r1 * (agent.personal_best - agent.position)
            + CONFIG.pso_c2 * r2 * (gbest - agent.position)
        )

        desired = normalize(env.exit_center - agent.position)
        obstacle = env.obstacle_repulsion(agent.position)
        forces.append(v_new + 35.0 * desired + obstacle)
    return forces
