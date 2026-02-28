"""Central configuration for the RS-SSTO evacuation simulation."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration values shared across environment, agents, and algorithms."""

    width: int = 800
    height: int = 600
    n_agents: int = 50
    dt: float = 0.1
    max_steps: int = 1800
    max_speed: float = 80.0
    agent_radius: float = 6.0
    sensor_radius: float = 80.0

    # Exit represented by a line segment on the right wall.
    exit_x: float = 785.0
    exit_y_min: float = 260.0
    exit_y_max: float = 340.0

    # Hazard zone (circle)
    hazard_center: tuple[float, float] = (450.0, 300.0)
    hazard_radius: float = 80.0

    # Obstacles (rectangles): (x, y, width, height)
    obstacles: tuple[tuple[float, float, float, float], ...] = (
        (200.0, 150.0, 70.0, 280.0),
        (520.0, 80.0, 60.0, 200.0),
        (530.0, 350.0, 70.0, 180.0),
    )

    # General force scales
    goal_force_gain: float = 1.2
    repulsion_gain: float = 900.0
    obstacle_repulsion_gain: float = 1200.0

    # PSO
    pso_w: float = 0.55
    pso_c1: float = 1.6
    pso_c2: float = 1.8

    # ACO
    pheromone_evaporation: float = 0.02
    pheromone_deposit: float = 2.0

    # APF
    apf_attr_gain: float = 1.0
    apf_rep_gain: float = 1700.0

    # RS-SSTO
    rs_swarm_gain: float = 1.4
    rs_surface_gain: float = 1500.0
    rs_panic_gain: float = 180.0
    preferred_spacing: float = 14.0

    # Visualization
    fps: int = 60
    visualize: bool = os.getenv("RSSTO_VISUALIZE", "0") == "1"


CONFIG = SimulationConfig()
