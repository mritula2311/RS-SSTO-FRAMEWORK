"""
RS-SSTO Algorithm  —  Radar-based Swarm-Surface-Tension Optimisation
=====================================================================
Combines three complementary forces on each agent:

    F = F_swarm  +  F_surface_tension  +  F_panic

1. **Swarm (PSO-like)** — global coordination toward exit, guided by
   personal- and global-best positions.
2. **Surface Tension** — pairwise repulsion prevents stampede congestion.
3. **Panic Model** — density + hazard-aware perturbation adds realistic
   urgency without degrading path quality.

Design goal: RS-SSTO should outperform SFM, PSO, ACO, APF by integrating
macro-level guidance with micro-level crowd physics.
"""

from __future__ import annotations
import numpy as np
from config import (
    RSSTO_SWARM_W, RSSTO_SWARM_C1, RSSTO_SWARM_C2,
    RSSTO_TENSION_K, RSSTO_SAFE_DIST,
    RSSTO_PANIC_ALPHA, RSSTO_PANIC_BETA,
)
from utils.math_utils import unit_vector, distance, clamp_speed
from models.surface_tension import compute_surface_tension_force
from models.panic_model import compute_panic, panic_velocity_perturbation


_rng = np.random.default_rng(42)


def _find_gbest(agents: list) -> np.ndarray:
    """Position of the agent closest to exit (personal-best)."""
    best = min(
        (a for a in agents if not a.evacuated),
        key=lambda a: a.pbest_dist,
        default=None,
    )
    if best is None:
        from config import EXIT_POS
        return np.array(EXIT_POS, dtype=float)
    return best.pbest_pos.copy()


def rssto_step(agents: list, environment, dt: float = 1.0) -> None:
    """
    One RS-SSTO tick.
    Every agent receives the combined force and advances.
    """
    gbest = _find_gbest(agents)

    for agent in agents:
        if agent.evacuated:
            continue

        # ── 1. Swarm force (PSO velocity update) ────────────────────────
        r1 = _rng.random(2)
        r2 = _rng.random(2)
        swarm_vel = (
            RSSTO_SWARM_W  * agent.vel
            + RSSTO_SWARM_C1 * r1 * (agent.pbest_pos - agent.pos)
            + RSSTO_SWARM_C2 * r2 * (gbest            - agent.pos)
        )

        # ── 2. Surface-tension force ────────────────────────────────────
        st_force = compute_surface_tension_force(
            agent, agents,
            k=RSSTO_TENSION_K,
            safe_dist=RSSTO_SAFE_DIST,
        )

        # ── 3. Panic model ──────────────────────────────────────────────
        agent.panic = compute_panic(
            agent, agents,
            hazard_pos=environment.hazard_pos,
            hazard_radius=environment.hazard_radius,
            alpha=RSSTO_PANIC_ALPHA,
            beta=RSSTO_PANIC_BETA,
        )
        panic_noise = panic_velocity_perturbation(agent.panic, _rng)

        # ── 4. Obstacle avoidance (smooth boundary steering) ───────────
        obs_force = np.zeros(2)
        for obs in environment.obstacles:
            nearest = obs.nearest_point(agent.pos)
            diff = agent.pos - nearest
            d = float(np.linalg.norm(diff))
            if 0 < d < 35:
                # Strong push + tangential slide to go around
                n_hat = diff / d
                obs_force += n_hat * (35 - d) * 0.25
                # Tangential component helps agents slide around obstacles
                tangent = np.array([-n_hat[1], n_hat[0]])
                goal_alignment = np.dot(tangent, unit_vector(agent.pos, agent.goal))
                obs_force += tangent * goal_alignment * 0.8

        # ── 5. Hazard avoidance ─────────────────────────────────────────
        hazard_force = np.zeros(2)
        hdiff = agent.pos - environment.hazard_pos
        hdist = float(np.linalg.norm(hdiff))
        if hdist < environment.hazard_radius * 2.5 and hdist > 1e-6:
            hazard_force = (hdiff / hdist) * 4.0 * max(1.0 - hdist / (environment.hazard_radius * 2.5), 0)

        # ── 6. Direct goal pull (ensures convergence) ───────────────────
        goal_dir = unit_vector(agent.pos, agent.goal)
        goal_pull = goal_dir * 1.8

        # ── Combine ─────────────────────────────────────────────────────
        combined_vel = swarm_vel + st_force * 0.2 + panic_noise * 0.2 + obs_force + hazard_force + goal_pull
        agent.vel = clamp_speed(combined_vel, agent.max_speed)
        agent.update_position(dt)
