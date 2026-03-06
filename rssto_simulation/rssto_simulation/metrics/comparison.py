"""
Comparison Runner
=================
Runs all five algorithms with identical starting conditions,
collects metrics, and produces a comparison table.
"""

from __future__ import annotations
import copy, time
import numpy as np
from config import NUM_AGENTS, MAX_FRAMES
from agents.agent import Agent
from radar.radar_input import generate_agent_positions
from environment.environment import Environment
from metrics.metrics import MetricsCollector

# Algorithm step functions
from algorithms.social_force import sfm_step
from algorithms.pso import pso_step
from algorithms.aco import aco_step, aco_init
from algorithms.apf import apf_step
from algorithms.rssto import rssto_step


ALGORITHMS = {
    "SFM":     sfm_step,
    "PSO":     pso_step,
    "ACO":     aco_step,
    "APF":     apf_step,
    "RS-SSTO": rssto_step,
}


def _make_agents(positions: list[tuple[float, float]]) -> list[Agent]:
    return [Agent(x, y) for x, y in positions]


def run_single(
    name: str,
    step_fn,
    positions: list[tuple[float, float]],
    env: Environment,
    max_frames: int = MAX_FRAMES,
    verbose: bool = True,
) -> dict:
    """Run one algorithm to completion and return its metrics summary."""
    agents = _make_agents(positions)
    collector = MetricsCollector(len(agents))

    if name == "ACO":
        aco_init()

    t0 = time.perf_counter()

    for frame in range(1, max_frames + 1):
        step_fn(agents, env)
        collector.record_frame(agents, frame)

        if all(a.evacuated for a in agents):
            break

    elapsed = time.perf_counter() - t0
    result = collector.summary()
    result["Wall-clock (s)"] = round(elapsed, 3)

    if verbose:
        print(f"  {name:>8s}  |  Evac {result['Evacuated']:>3d}/{NUM_AGENTS}"
              f"  |  Time {result['Evacuation Time']:>5d}"
              f"  |  Throughput {result['Throughput']:.4f}"
              f"  |  Congestion {result['Congestion']:.4f}"
              f"  |  {elapsed:.2f}s")
    return result


def run_comparison(seed: int = 42, verbose: bool = True) -> dict[str, dict]:
    """Run all algorithms, return dict[algorithm_name] → metrics."""
    positions = generate_agent_positions(NUM_AGENTS, seed=seed)
    env = Environment(seed=seed)

    if verbose:
        print("=" * 80)
        print("  RS-SSTO Framework — Algorithm Comparison")
        print("=" * 80)
        print(f"  Agents: {NUM_AGENTS}   Map: {env.width}×{env.height}"
              f"   Obstacles: {len(env.obstacles)}")
        print("-" * 80)

    results: dict[str, dict] = {}
    for name, step_fn in ALGORITHMS.items():
        results[name] = run_single(name, step_fn, positions, env,
                                   verbose=verbose)

    if verbose:
        print("-" * 80)
        # Highlight winner
        best = max(results, key=lambda k: (
            results[k]["Evacuated"],
            results[k]["Throughput"],
            -results[k]["Evacuation Time"],
        ))
        print(f"  ★ Best algorithm: {best}  "
              f"({results[best]['Evacuated']} evacuated, "
              f"throughput {results[best]['Throughput']:.4f})")
        print("=" * 80)

    return results
