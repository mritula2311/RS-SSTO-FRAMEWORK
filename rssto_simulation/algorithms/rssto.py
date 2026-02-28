"""Proposed RS-SSTO algorithm combining swarm, surface tension, and panic."""

from __future__ import annotations

import numpy as np

from config import CONFIG
from models.panic_model import compute_dynamic_panic
from models.surface_tension import surface_tension_force
from utils.math_utils import normalize, pairwise_neighbors


def compute_forces(agents, env, _state=None):
    positions = np.array([a.position for a in agents])
    panic_vals = compute_dynamic_panic(positions)
    neighbors = pairwise_neighbors(positions, CONFIG.sensor_radius)

    forces = []
    for i, agent in enumerate(agents):
        if agent.evacuated:
            forces.append(np.zeros(2))
            continue

        # Swarm intelligence: align with local crowd heading + attraction to exit.
        local_alignment = np.zeros(2, dtype=float)
        if neighbors[i]:
            mean_vel = np.mean([agents[j].velocity for j in neighbors[i]], axis=0)
            local_alignment = normalize(mean_vel)

        to_exit = normalize(env.exit_center - agent.position)
        swarm_force = CONFIG.rs_swarm_gain * (0.6 * to_exit + 0.4 * local_alignment) * 90.0

        # Surface tension force: anti-clustering if agents are too close.
        tension = surface_tension_force(i, positions)

        # Panic force: dynamic coefficient amplifies urgency and hazard avoidance.
        panic_coeff = panic_vals[i]
        hazard_away = env.hazard_penalty_direction(agent.position)
        panic_force = CONFIG.rs_panic_gain * panic_coeff * (0.7 * to_exit + 0.3 * hazard_away)

        obstacle_force = env.obstacle_repulsion(agent.position)

        # Final force composition.
        total_force = swarm_force + tension + panic_force + obstacle_force
        forces.append(total_force)
        agent.panic_coeff = float(panic_coeff)

    return forces
