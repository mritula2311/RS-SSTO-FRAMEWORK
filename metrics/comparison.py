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
from utils.math_utils import clamp_speed

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


def _resolve_obstacle_collisions(agents, env):
    for a in agents:
        if a.evacuated:
            continue
        for obs in env.obstacles:
            if obs.contains(a.pos):
                left   = a.pos[0] - obs.x
                right  = (obs.x + obs.w) - a.pos[0]
                top    = a.pos[1] - obs.y
                bottom = (obs.y + obs.h) - a.pos[1]
                m = min(left, right, top, bottom)
                eps = 0.5
                if m == left:
                    a.pos[0] = obs.x - eps
                    a.vel[0] = 0
                elif m == right:
                    a.pos[0] = obs.x + obs.w + eps
                    a.vel[0] = 0
                elif m == top:
                    a.pos[1] = obs.y - eps
                    a.vel[1] = 0
                else:
                    a.pos[1] = obs.y + obs.h + eps
                    a.vel[1] = 0


def _resolve_hazard_overlap(agents, env):
    centre = env.hazard_pos
    radius = env.hazard_radius
    for a in agents:
        if a.evacuated:
            continue
        diff = a.pos - centre
        dist = float(np.linalg.norm(diff))
        if dist < radius:
            if dist < 1e-6:
                diff = np.array([1.0, 0.0])
                dist = 1.0
            dir_vec = diff / dist
            a.pos = centre + dir_vec * (radius + 1.0)
            a.vel = clamp_speed(dir_vec * a.max_speed * 0.5, a.max_speed)


def _maybe_unstick(agents, env, rng):
    for a in agents:
        if a.evacuated:
            continue
        speed = float(np.linalg.norm(a.vel))
        if speed < 0.05:
            a.stuck_frames += 1
        else:
            a.stuck_frames = 0
        if a.stuck_frames >= 30:
            goal_dir = a.goal - a.pos
            norm = float(np.linalg.norm(goal_dir))
            if norm > 1e-6:
                goal_dir /= norm
            jitter = rng.normal(0, 0.05, size=2)
            nudge = goal_dir * 0.6 + jitter
            a.vel = clamp_speed(nudge, a.max_speed * 0.6)
            a.stuck_frames = 0


def _make_agents(positions: list[tuple[float, float]]) -> list[Agent]:
    return [Agent(x, y) for x, y in positions]


def run_single(
    name: str,
    step_fn,
    positions: list[tuple[float, float]],
    env: Environment,
    max_frames: int = MAX_FRAMES,
    verbose: bool = True,
    record_positions: bool = False,
):
    """Run one algorithm to completion and return its metrics summary."""
    agents = _make_agents(positions)
    collector = MetricsCollector(len(agents))
    traces: list[np.ndarray] | None = [] if record_positions else None
    rng = np.random.default_rng(1234)

    if name == "ACO":
        aco_init()

    t0 = time.perf_counter()

    for frame in range(1, max_frames + 1):
        step_fn(agents, env)
        # post-step safety: damp speed, resolve collisions/hazard, unstick, clamp bounds
        for a in agents:
            a.vel = clamp_speed(a.vel, a.max_speed * 0.9)
            a.pos[0] = np.clip(a.pos[0], 0, env.width)
            a.pos[1] = np.clip(a.pos[1], 0, env.height)
        _resolve_obstacle_collisions(agents, env)
        _resolve_hazard_overlap(agents, env)
        _maybe_unstick(agents, env, rng)

        collector.record_frame(agents, frame)
        if traces is not None:
            traces.append(np.array([a.pos.copy() for a in agents]))

        if all(a.evacuated for a in agents):
            break

    elapsed = time.perf_counter() - t0
    result = collector.summary()
    result["Wall-clock (s)"] = round(elapsed, 3)

    if verbose:
        print(f"  {name:>8s}  |  Evac {result['Evacuated']:>3d}/{NUM_AGENTS}"
              f"  |  Time {result['Evac Time']:>5d}"
              f"  |  Throughput {result['Throughput']:.4f}"
              f"  |  Congestion {result['Congestion']:.4f}"
              f"  |  {elapsed:.2f}s")
    return (result, traces) if traces is not None else result


def run_comparison(seed: int = 42, verbose: bool = True, record_positions: bool = False):
    """Run all algorithms, return dict[algorithm_name] → metrics.

    When record_positions is True, also returns (results, traces, env).
    traces is a dict mapping algorithm → list of np.ndarray frames.
    """
    positions = generate_agent_positions(NUM_AGENTS, seed=seed)
    env = Environment(seed=seed)

    if verbose:
        print("=" * 80)
        print(f"  RS-SSTO Framework — Algorithm Comparison")
        print("=" * 80)
        print(f"  Agents: {NUM_AGENTS}   Map: {env.width}×{env.height}"
              f"   Obstacles: {len(env.obstacles)}   Exit Radius: {int(env.exit.radius)}px")
        print("-" * 80)

    results: dict[str, dict] = {}
    traces: dict[str, list[np.ndarray]] = {} if record_positions else {}
    for name, step_fn in ALGORITHMS.items():
        run_out = run_single(name, step_fn, positions, env,
                             verbose=verbose,
                             record_positions=record_positions)
        if record_positions:
            res, pos_trace = run_out
            results[name] = res
            traces[name] = pos_trace
        else:
            results[name] = run_out

    if verbose:
        print("-" * 80)
        # Highlight winner
        best = max(results, key=lambda k: (
            results[k]["Evacuated"],
            results[k]["Throughput"],
            -results[k]["Evac Time"],
        ))
        print(f"  ★ Best algorithm: {best}  "
              f"({results[best]['Evacuated']} evacuated, "
              f"throughput {results[best]['Throughput']:.4f})")
        print("=" * 80)

    if record_positions:
        return results, traces, env
    return results
