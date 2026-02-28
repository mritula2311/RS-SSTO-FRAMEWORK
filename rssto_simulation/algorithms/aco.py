"""Ant Colony Optimization inspired flow with pheromone field."""

from __future__ import annotations

import numpy as np

from config import CONFIG
from utils.math_utils import normalize


def init_state(_agents, _env):
    grid_h, grid_w = 60, 80
    pheromone = np.ones((grid_h, grid_w), dtype=float) * 0.1
    return {"pheromone": pheromone, "grid_w": grid_w, "grid_h": grid_h}


def _cell_index(position: np.ndarray, state: dict) -> tuple[int, int]:
    gx = int(np.clip(position[0] / CONFIG.width * state["grid_w"], 0, state["grid_w"] - 1))
    gy = int(np.clip(position[1] / CONFIG.height * state["grid_h"], 0, state["grid_h"] - 1))
    return gy, gx


def compute_forces(agents, env, state):
    pheromone = state["pheromone"]
    pheromone *= (1.0 - CONFIG.pheromone_evaporation)

    exit_cell = _cell_index(env.exit_center, state)
    pheromone[exit_cell] += CONFIG.pheromone_deposit * 0.2

    forces = []
    for agent in agents:
        if agent.evacuated:
            forces.append(np.zeros(2))
            continue

        gy, gx = _cell_index(agent.position, state)
        local_best = (gy, gx)
        best_ph = -1.0
        for ny in range(max(0, gy - 1), min(state["grid_h"], gy + 2)):
            for nx in range(max(0, gx - 1), min(state["grid_w"], gx + 2)):
                if pheromone[ny, nx] > best_ph:
                    best_ph = pheromone[ny, nx]
                    local_best = (ny, nx)

        target = np.array(
            [
                (local_best[1] + 0.5) / state["grid_w"] * CONFIG.width,
                (local_best[0] + 0.5) / state["grid_h"] * CONFIG.height,
            ],
            dtype=float,
        )
        to_exit = normalize(env.exit_center - agent.position)
        to_pheromone = normalize(target - agent.position)
        obstacle = env.obstacle_repulsion(agent.position)
        force = 50.0 * to_exit + 20.0 * to_pheromone + obstacle
        forces.append(force)

        pheromone[gy, gx] += CONFIG.pheromone_deposit

    return forces
