"""
Pygame Real-Time Simulator
===========================
Renders one algorithm at a time in a pygame window.
Agents are drawn as circles, exit as green, hazard as red, obstacles grey.
Press SPACE to pause/resume, ESC to skip current algorithm.
"""

from __future__ import annotations
import sys
import numpy as np

try:
    import pygame
except ImportError:
    pygame = None  # graceful fallback for headless runs

from config import (
    MAP_WIDTH, MAP_HEIGHT, FPS, NUM_AGENTS, MAX_FRAMES,
    COL_BG, COL_AGENT, COL_EXIT, COL_HAZARD, COL_OBS, COL_TEXT,
    EXIT_RADIUS, HAZARD_RADIUS,
)
from agents.agent import Agent
from radar.radar_input import generate_agent_positions
from environment.environment import Environment
from metrics.metrics import MetricsCollector

from algorithms.social_force import sfm_step
from algorithms.pso import pso_step
from algorithms.aco import aco_step, aco_init
from algorithms.apf import apf_step
from algorithms.rssto import rssto_step


ALGORITHMS = [
    ("SFM",     sfm_step),
    ("PSO",     pso_step),
    ("ACO",     aco_step),
    ("APF",     apf_step),
    ("RS-SSTO", rssto_step),
]


def _draw(screen, agents, env, algo_name, frame, font):
    """Draw one frame."""
    screen.fill(COL_BG)

    # Hazard zone
    pygame.draw.circle(
        screen, COL_HAZARD,
        (int(env.hazard_pos[0]), int(env.hazard_pos[1])),
        int(env.hazard_radius), 2,
    )

    # Obstacles
    for obs in env.obstacles:
        pygame.draw.rect(screen, COL_OBS, obs.rect)

    # Exit
    ex = env.exit
    pygame.draw.circle(
        screen, COL_EXIT,
        (int(ex.pos[0]), int(ex.pos[1])),
        int(ex.radius), 0,
    )

    # Agents
    for a in agents:
        if a.evacuated:
            continue
        colour = COL_AGENT
        # Tint red if panicking
        if hasattr(a, "panic") and a.panic > 0.5:
            colour = (255, int(200 * (1 - a.panic)), 0)
        pygame.draw.circle(
            screen, colour,
            (int(a.pos[0]), int(a.pos[1])),
            int(a.radius),
        )

    # HUD
    active = sum(1 for a in agents if not a.evacuated)
    evacuated = sum(1 for a in agents if a.evacuated)
    hud = font.render(
        f"{algo_name}  |  Frame {frame}  |  Active {active}  |  Evacuated {evacuated}/{NUM_AGENTS}",
        True, COL_TEXT,
    )
    screen.blit(hud, (10, 8))

    pygame.display.flip()


def run_visual(seed: int = 42) -> dict[str, dict]:
    """
    Run all algorithms sequentially with pygame visualisation.
    Returns comparison results dict.
    """
    if pygame is None:
        print("[WARN] pygame not installed — falling back to headless mode.")
        from metrics.comparison import run_comparison
        return run_comparison(seed=seed)

    pygame.init()
    screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT))
    pygame.display.set_caption("RS-SSTO Evacuation Simulation")
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("consolas", 16)

    positions = generate_agent_positions(NUM_AGENTS, seed=seed)
    env = Environment(seed=seed)
    all_results: dict[str, dict] = {}

    for algo_name, step_fn in ALGORITHMS:
        agents = [Agent(x, y) for x, y in positions]
        collector = MetricsCollector(len(agents))
        if algo_name == "ACO":
            aco_init()

        paused = False
        done   = False

        for frame in range(1, MAX_FRAMES + 1):
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    return all_results
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        done = True
                    if ev.key == pygame.K_SPACE:
                        paused = not paused

            if done:
                break

            if not paused:
                step_fn(agents, env)
                collector.record_frame(agents, frame)

            _draw(screen, agents, env, algo_name, frame, font)
            clock.tick(FPS)

            if all(a.evacuated for a in agents):
                # Pause briefly so user sees the final state
                pygame.time.wait(600)
                break

        result = collector.summary()
        all_results[algo_name] = result
        print(f"  {algo_name:>8s}  Evacuated {result['Evacuated']}/{NUM_AGENTS}"
              f"  Time {result['Evacuation Time']}"
              f"  Throughput {result['Throughput']:.4f}")

    pygame.quit()
    return all_results
