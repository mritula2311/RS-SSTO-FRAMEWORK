"""
Ant Colony Optimisation (ACO) Algorithm
========================================
Uses a pheromone grid overlaid on the map.

1. Each evacuated agent deposits pheromone along its recent trail.
2. Pheromone evaporates every tick by a factor ρ.
3. Active agents bias their movement toward cells with higher pheromone
   concentration (weighted by distance heuristic τ^α · η^β).

Grid resolution = ACO_GRID px per cell.
"""

from __future__ import annotations
import numpy as np
from config import (
    MAP_WIDTH, MAP_HEIGHT,
    ACO_EVAPORATION, ACO_DEPOSIT, ACO_GRID,
    ACO_ALPHA, ACO_BETA,
)
from utils.math_utils import unit_vector, distance, clamp_speed


class PheromoneGrid:
    """Pheromone map for ACO guidance."""

    def __init__(self):
        self.cell = ACO_GRID
        self.cols = MAP_WIDTH  // self.cell + 1
        self.rows = MAP_HEIGHT // self.cell + 1
        self.grid = np.zeros((self.rows, self.cols), dtype=float)

    def _idx(self, pos: np.ndarray) -> tuple[int, int]:
        c = int(np.clip(pos[0] // self.cell, 0, self.cols - 1))
        r = int(np.clip(pos[1] // self.cell, 0, self.rows - 1))
        return r, c

    def deposit(self, pos: np.ndarray, amount: float = ACO_DEPOSIT):
        r, c = self._idx(pos)
        self.grid[r, c] += amount

    def evaporate(self):
        self.grid *= (1.0 - ACO_EVAPORATION)

    def concentration(self, pos: np.ndarray) -> float:
        r, c = self._idx(pos)
        return float(self.grid[r, c])

    def best_neighbour_direction(self, pos: np.ndarray, goal: np.ndarray) -> np.ndarray:
        """Return a unit movement direction blending pheromone + heuristic."""
        r0, c0 = self._idx(pos)
        best_score = -1.0
        best_dir   = unit_vector(pos, goal)          # default: straight to goal

        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = r0 + dr, c0 + dc
                if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                    continue
                cell_centre = np.array([
                    (c + 0.5) * self.cell,
                    (r + 0.5) * self.cell,
                ], dtype=float)
                tau = max(self.grid[r, c], 1e-6)
                eta = 1.0 / max(distance(cell_centre, goal), 1.0)
                score = (tau ** ACO_ALPHA) * (eta ** ACO_BETA)
                if score > best_score:
                    best_score = score
                    best_dir   = unit_vector(pos, cell_centre)
        return best_dir


# Module-level pheromone grid (re-created each algorithm run via init)
_phero: PheromoneGrid | None = None


def aco_init():
    """Initialise / reset the pheromone grid."""
    global _phero
    _phero = PheromoneGrid()


def aco_step(agents: list, environment, dt: float = 1.0) -> None:
    """One ACO tick: move agents, deposit, evaporate."""
    global _phero
    if _phero is None:
        aco_init()

    # Evaporate once per tick
    _phero.evaporate()

    # Seed pheromone near exit so agents have something to follow
    from config import EXIT_POS
    exit_pos = np.array(EXIT_POS, dtype=float)
    _phero.deposit(exit_pos, ACO_DEPOSIT * 0.5)

    for agent in agents:
        if agent.evacuated:
            _phero.deposit(agent.pos, ACO_DEPOSIT * 2)
            continue

        # Pheromone concentration at current position determines blend
        local_phero = _phero.concentration(agent.pos)
        # As pheromone builds, trust it more; start with strong goal pull
        phero_weight = min(local_phero / 50.0, 0.6)
        goal_weight  = 1.0 - phero_weight

        # Direction from pheromone + heuristic
        phero_dir = _phero.best_neighbour_direction(agent.pos, agent.goal)

        # Direct goal pull (always present)
        goal_dir = unit_vector(agent.pos, agent.goal)

        direction = phero_weight * phero_dir + goal_weight * goal_dir
        norm = np.linalg.norm(direction)
        if norm > 1e-8:
            direction /= norm

        desired_vel = direction * agent.max_speed * 0.85

        # Simple obstacle / hazard avoidance
        for obs in environment.obstacles:
            nearest = obs.nearest_point(agent.pos)
            diff = agent.pos - nearest
            d = float(np.linalg.norm(diff))
            if 0 < d < 20:
                desired_vel += (diff / d) * 1.5

        hdiff = agent.pos - environment.hazard_pos
        hdist = float(np.linalg.norm(hdiff))
        if hdist < environment.hazard_radius * 1.5 and hdist > 1e-6:
            desired_vel += (hdiff / hdist) * 2.0

        agent.vel = clamp_speed(desired_vel, agent.max_speed)
        agent.update_position(dt)

        # Deposit pheromone at current cell
        _phero.deposit(agent.pos, ACO_DEPOSIT * 0.3)
