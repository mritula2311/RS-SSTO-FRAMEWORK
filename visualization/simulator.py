"""
Pygame Real-Time Simulator
===========================
Renders one algorithm at a time in a pygame window.
Agents are drawn as circles, exit as green, hazard as red, obstacles grey.
Press SPACE to pause/resume, ESC to skip current algorithm.
"""

from __future__ import annotations
import sys
import os
import collections
import numpy as np
from typing import Iterable, Sequence

try:
    import pygame
except ImportError:
    pygame = None  # graceful fallback for headless runs

try:
    import imageio
except ImportError:
    imageio = None

from config import (
    MAP_WIDTH, MAP_HEIGHT, FPS, NUM_AGENTS, MAX_FRAMES,
    COL_BG, COL_AGENT, COL_EXIT, COL_HAZARD, COL_OBS, COL_TEXT,
    EXIT_RADIUS, HAZARD_RADIUS,
)
from utils.math_utils import clamp_speed
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

ALGO_MAP = {name.lower(): (name, fn) for name, fn in ALGORITHMS}

TRAIL_LEN = 25  # number of past positions to show per agent
GHOST_LEN = 40  # trail length retained for evacuated agents (ghost)
MAX_STEP_SCALE = 0.85  # damp velocities slightly to avoid tunnelling


def _normalise_format(fmt: str) -> list[str]:
    fmt = fmt.lower()
    if fmt == "both":
        return ["gif", "mp4"]
    if fmt in ("gif", "mp4"):
        return [fmt]
    return []


class FrameRecorder:
    """Stream frames to gif/mp4 using imageio."""

    def __init__(self, out_dir: str, base_name: str, formats: Sequence[str], fps: int):
        self.writers = []
        self.paths = []
        if imageio is None:
            return
        os.makedirs(out_dir, exist_ok=True)
        for fmt in formats:
            fname = f"{base_name}.{fmt}"
            path = os.path.join(out_dir, fname)
            try:
                if fmt == "mp4":
                    writer = imageio.get_writer(path, fps=fps, codec="libx264")
                else:
                    writer = imageio.get_writer(path, fps=fps)
                self.writers.append(writer)
                self.paths.append(path)
            except Exception:
                # Skip writer if backend unavailable
                continue

    def append(self, surface):
        if not self.writers:
            return
        # pygame array3d returns (w, h, 3); transpose to (h, w, 3)
        frame = pygame.surfarray.array3d(surface)
        frame = np.transpose(frame, (1, 0, 2))
        for w in self.writers:
            w.append_data(frame)

    def close(self):
        for w in self.writers:
            try:
                w.close()
            except Exception:
                pass



def _panic_color(panic: float) -> tuple[int, int, int]:
    """Map panic level 0-1 to a blue→orange→red gradient."""
    p = float(np.clip(panic, 0.0, 1.0))
    # simple two-stage lerp: blue (calm) to orange, then to red
    if p < 0.5:
        t = p / 0.5
        r = int(30 + t * (255 - 30))
        g = int(144 + t * (140 - 144))
        b = int(255 - t * 165)
    else:
        t = (p - 0.5) / 0.5
        r = 255
        g = int(140 - t * 140)
        b = int(90 - t * 90)
    return (r, g, b)


def _line_intersects_hazard(p1: np.ndarray, p2: np.ndarray, centre: np.ndarray, radius: float) -> bool:
    """Check if line segment p1-p2 passes through (or close to) hazard circle."""
    # Closest-point-on-segment distance to circle centre
    seg = p2 - p1
    seg_len_sq = float(np.dot(seg, seg))
    if seg_len_sq < 1e-8:
        return float(np.linalg.norm(p1 - centre)) <= radius
    t = float(np.dot(centre - p1, seg) / seg_len_sq)
    t = max(0.0, min(1.0, t))
    closest = p1 + t * seg
    return float(np.linalg.norm(closest - centre)) <= radius


def _resolve_obstacle_collisions(agents: Iterable, env) -> int:
    """Push agents out of obstacles if they penetrated after a step. Returns count of fixes."""
    fixed = 0
    for a in agents:
        if a.evacuated:
            continue
        for obs in env.obstacles:
            if obs.contains(a.pos):
                fixed += 1
                # Compute distance to each side and push out the minimal axis
                left_dist   = a.pos[0] - obs.x
                right_dist  = (obs.x + obs.w) - a.pos[0]
                top_dist    = a.pos[1] - obs.y
                bottom_dist = (obs.y + obs.h) - a.pos[1]
                min_axis = min(left_dist, right_dist, top_dist, bottom_dist)
                eps = 0.5
                if min_axis == left_dist:
                    a.pos[0] = obs.x - eps
                    a.vel[0] = 0
                elif min_axis == right_dist:
                    a.pos[0] = obs.x + obs.w + eps
                    a.vel[0] = 0
                elif min_axis == top_dist:
                    a.pos[1] = obs.y - eps
                    a.vel[1] = 0
                else:
                    a.pos[1] = obs.y + obs.h + eps
                    a.vel[1] = 0
    return fixed


def _maybe_unstick(agents: Iterable, env, rng: np.random.Generator) -> int:
    """Nudge agents that have stalled in place for many frames. Returns count of nudges."""
    nudges = 0
    for a in agents:
        if a.evacuated:
            continue
        speed = float(np.linalg.norm(a.vel))
        if speed < 0.05:
            a.stuck_frames += 1
        else:
            a.stuck_frames = 0

        if a.stuck_frames >= 30:
            # Nudge toward goal, slight random jitter, avoid hazard line if necessary
            goal_dir = a.goal - a.pos
            norm = float(np.linalg.norm(goal_dir))
            if norm > 1e-6:
                goal_dir /= norm
            jitter = rng.normal(0, 0.05, size=2)
            nudge = goal_dir * 0.6 + jitter
            # If the direct line crosses hazard, add perpendicular detour
            if _line_intersects_hazard(a.pos, a.pos + nudge * 40, env.hazard_pos, env.hazard_radius * 1.05):
                perp = np.array([-goal_dir[1], goal_dir[0]])
                nudge += perp * 0.4
            a.vel = clamp_speed(nudge, a.max_speed * 0.6)
            a.stuck_frames = 0
            nudges += 1
    return nudges


def _resolve_hazard_overlap(agents: Iterable, env) -> int:
    """Push agents out of hazard if they drift inside. Returns count of fixes."""
    fixed = 0
    centre = env.hazard_pos
    radius = env.hazard_radius
    for a in agents:
        if a.evacuated:
            continue
        diff = a.pos - centre
        dist = float(np.linalg.norm(diff))
        if dist < radius:
            fixed += 1
            if dist < 1e-6:
                diff = np.array([1.0, 0.0])
                dist = 1.0
            dir_vec = diff / dist
            a.pos = centre + dir_vec * (radius + 1.0)
            a.vel = clamp_speed(dir_vec * a.max_speed * 0.5, a.max_speed)
    return fixed


def _draw(screen, agents, trails, ghosts, env, algo_name, frame, font, offset_x: int = 0):
    """Draw one frame with trails, velocity arrows, route hints, and evacuated ghosts."""
    # Hazard zone
    pygame.draw.circle(
        screen, COL_HAZARD,
        (int(offset_x + env.hazard_pos[0]), int(env.hazard_pos[1])),
        int(env.hazard_radius), 2,
    )

    # Obstacles
    for obs in env.obstacles:
        # obstacles store rect as tuple, so wrap as pygame.Rect then shift
        r = pygame.Rect(obs.rect)
        r.move_ip(offset_x, 0)
        pygame.draw.rect(screen, COL_OBS, r)

    # Exit
    ex = env.exit
    pygame.draw.circle(
        screen, COL_EXIT,
        (int(offset_x + ex.pos[0]), int(ex.pos[1])),
        int(ex.radius), 0,
    )

    # Evacuated ghosts (faded trails)
    for ghost_trail in ghosts:
        if len(ghost_trail) > 1:
            pygame.draw.lines(
                screen, (90, 120, 160), False,
                [(int(offset_x + px), int(py)) for (px, py) in ghost_trail], 1,
            )

    # Agents
    total_panic = 0.0
    active_agents = 0
    for idx, a in enumerate(agents):
        if a.evacuated:
            continue
        active_agents += 1
        p_level = float(getattr(a, "panic", 0.0))
        total_panic += p_level
        colour = _panic_color(p_level)

        # Trail
        trail = trails[idx]
        if len(trail) > 1:
            pygame.draw.lines(
                screen, (180, 200, 220), False,
                [(int(offset_x + px), int(py)) for (px, py) in trail], 1,
            )

        # Planned route line to exit (green if clear; amber if blocked by hazard)
        ex = env.exit
        line_colour = (60, 200, 110)
        if _line_intersects_hazard(a.pos, ex.pos, env.hazard_pos, env.hazard_radius * 1.05):
            line_colour = (255, 170, 60)
        pygame.draw.line(
            screen, line_colour,
            (int(offset_x + a.pos[0]), int(a.pos[1])),
            (int(offset_x + ex.pos[0]), int(ex.pos[1])), 1,
        )

        # Agent body
        pygame.draw.circle(
            screen, colour,
            (int(offset_x + a.pos[0]), int(a.pos[1])),
            int(a.radius),
        )

        # Velocity arrow (scaled)
        vel = a.vel
        arrow_scale = 6.0
        end_pos = a.pos + vel * arrow_scale
        pygame.draw.line(
            screen, (255, 255, 255),
            (int(offset_x + a.pos[0]), int(a.pos[1])),
            (int(offset_x + end_pos[0]), int(end_pos[1])), 2,
        )

    # HUD
    active = sum(1 for a in agents if not a.evacuated)
    evacuated = sum(1 for a in agents if a.evacuated)
    avg_panic = (total_panic / active) if active > 0 else 0.0
    hud = font.render(
        f"{algo_name}  |  Frame {frame}  |  Active {active}  |  Evacuated {evacuated}/{NUM_AGENTS}  |  Avg panic {avg_panic:.2f}",
        True, COL_TEXT,
    )
    screen.blit(hud, (10 + offset_x, 8))

    legend = [
        "Colour = panic (blue→orange→red)",
        "Line to exit: green=clear, amber=hazard avoidance",
        "White arrow = velocity",
        "Faint line = recent trail",
        "Faded lines = evacuated paths",
    ]
    for i, text in enumerate(legend):
        lbl = font.render(text, True, (220, 220, 220))
        screen.blit(lbl, (10 + offset_x, 28 + i * 16))


def run_visual(
    seed: int = 42,
    record: bool = False,
    record_format: str = "mp4",
    record_dir: str | None = None,
) -> dict[str, dict]:
    """
    Run all algorithms sequentially with pygame visualisation.
    Optionally record each algorithm run to GIF/MP4 via imageio.
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
    rng = np.random.default_rng(seed + 99)
    env = Environment(seed=seed)
    all_results: dict[str, dict] = {}
    out_dir = record_dir or os.path.join(os.path.dirname(__file__), "..", "output", "animations")
    formats = _normalise_format(record_format)
    if record and imageio is None:
        print("[WARN] imageio not installed; recording disabled.")
        record = False

    for algo_name, step_fn in ALGORITHMS:
        agents = [Agent(x, y) for x, y in positions]
        trails = [collections.deque(maxlen=TRAIL_LEN) for _ in agents]
        ghosts = []
        for idx, ag in enumerate(agents):
            trails[idx].append(tuple(ag.pos))
        collector = MetricsCollector(len(agents))
        if algo_name == "ACO":
            aco_init()

        # per-run counters for HUD logging
        total_collision_fixes = 0
        total_hazard_fixes = 0
        total_nudges = 0
        recent_messages: collections.deque[str] = collections.deque(maxlen=4)

        paused = False
        done   = False

        recorder = FrameRecorder(out_dir, algo_name.replace(" ", "_").lower(), formats, fps=FPS) if record else None
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
                # Damp velocity slightly to avoid tunnelling
                for a in agents:
                    a.vel = clamp_speed(a.vel, a.max_speed * MAX_STEP_SCALE)

                cfix = _resolve_obstacle_collisions(agents, env)
                hfix = _resolve_hazard_overlap(agents, env)
                nudges = _maybe_unstick(agents, env, rng)
                total_collision_fixes += cfix
                total_hazard_fixes += hfix
                total_nudges += nudges
                if cfix:
                    recent_messages.append(f"{cfix} obstacle pushes")
                if hfix:
                    recent_messages.append(f"{hfix} hazard pushes")
                if nudges:
                    recent_messages.append(f"{nudges} unsticks")
                collector.record_frame(agents, frame)
                for idx, ag in enumerate(agents):
                    trails[idx].append(tuple(ag.pos))
                    if ag.evacuated:
                        # move recent trail to ghosts once per agent
                        if len(trails[idx]) > 0:
                            ghosts.append(collections.deque(trails[idx], maxlen=GHOST_LEN))
                        trails[idx].clear()

            screen.fill(COL_BG)
            _draw(screen, agents, trails, ghosts, env, algo_name, frame, font, offset_x=0)
            # HUD extension: recent events
            for i, msg in enumerate(recent_messages):
                lbl = font.render(f"Event: {msg}", True, (200, 200, 200))
                screen.blit(lbl, (10, 110 + i * 16))
            pygame.display.flip()
            if recorder:
                recorder.append(screen)
            clock.tick(FPS)

            if all(a.evacuated for a in agents):
                # Pause briefly so user sees the final state
                pygame.time.wait(600)
                break

        if recorder:
            recorder.close()

        result = collector.summary()
        all_results[algo_name] = result
        print(f"  {algo_name:>8s}  Evacuated {result['Evacuated']}/{NUM_AGENTS}"
              f"  Time {result['Evacuation Time']}"
              f"  Throughput {result['Throughput']:.4f}")

    pygame.quit()
    return all_results


def run_visual_split(
    algo_names: list[str],
    seed: int = 42,
    record: bool = False,
    record_format: str = "mp4",
    record_dir: str | None = None,
) -> dict[str, dict]:
    """Run two algorithms side-by-side in one window for direct comparison."""
    if pygame is None:
        print("[WARN] pygame not installed — falling back to headless mode.")
        from metrics.comparison import run_comparison
        return run_comparison(seed=seed)

    resolved = []
    for name in algo_names:
        key = name.lower()
        if key in ALGO_MAP:
            resolved.append(ALGO_MAP[key])
    if len(resolved) < 2:
        print("[WARN] Could not resolve both algorithms; using PSO vs RS-SSTO")
        resolved = [ALGO_MAP["pso"], ALGO_MAP["rs-ssto"]]

    (name_a, fn_a), (name_b, fn_b) = resolved[:2]

    pygame.init()
    width = MAP_WIDTH * 2 + 16
    height = MAP_HEIGHT
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Split View: {name_a} vs {name_b}")
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("consolas", 16)
    out_dir = record_dir or os.path.join(os.path.dirname(__file__), "..", "output", "animations")
    formats = _normalise_format(record_format)
    if record and imageio is None:
        print("[WARN] imageio not installed; split recording disabled.")
        record = False
    recorder = FrameRecorder(out_dir, f"split_{name_a}_{name_b}".replace(" ", "_"), formats, fps=FPS) if record else None

    positions = generate_agent_positions(NUM_AGENTS, seed=seed)
    rng = np.random.default_rng(seed + 101)
    env_a = Environment(seed=seed)
    env_b = Environment(seed=seed)

    agents_a = [Agent(x, y) for x, y in positions]
    agents_b = [Agent(x, y) for x, y in positions]
    trails_a = [collections.deque(maxlen=TRAIL_LEN) for _ in agents_a]
    trails_b = [collections.deque(maxlen=TRAIL_LEN) for _ in agents_b]
    ghosts_a = []
    ghosts_b = []
    for idx, ag in enumerate(agents_a):
        trails_a[idx].append(tuple(ag.pos))
    for idx, ag in enumerate(agents_b):
        trails_b[idx].append(tuple(ag.pos))

    collector_a = MetricsCollector(len(agents_a))
    collector_b = MetricsCollector(len(agents_b))

    total_collision_fixes_a = 0
    total_collision_fixes_b = 0
    total_hazard_fixes_a = 0
    total_hazard_fixes_b = 0
    total_nudges_a = 0
    total_nudges_b = 0
    recent_messages: collections.deque[str] = collections.deque(maxlen=4)

    if name_a == "ACO":
        aco_init()
    if name_b == "ACO":
        aco_init()

    paused = False
    done   = False

    for frame in range(1, MAX_FRAMES + 1):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return {name_a: collector_a.summary(), name_b: collector_b.summary()}
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    done = True
                if ev.key == pygame.K_SPACE:
                    paused = not paused

        if done:
            break

        if not paused:
            fn_a(agents_a, env_a)
            fn_b(agents_b, env_b)
            for a in agents_a:
                a.vel = clamp_speed(a.vel, a.max_speed * MAX_STEP_SCALE)
            for a in agents_b:
                a.vel = clamp_speed(a.vel, a.max_speed * MAX_STEP_SCALE)
            cfix_a = _resolve_obstacle_collisions(agents_a, env_a)
            cfix_b = _resolve_obstacle_collisions(agents_b, env_b)
            hfix_a = _resolve_hazard_overlap(agents_a, env_a)
            hfix_b = _resolve_hazard_overlap(agents_b, env_b)
            nudges_a = _maybe_unstick(agents_a, env_a, rng)
            nudges_b = _maybe_unstick(agents_b, env_b, rng)
            total_collision_fixes_a += cfix_a
            total_collision_fixes_b += cfix_b
            total_hazard_fixes_a += hfix_a
            total_hazard_fixes_b += hfix_b
            total_nudges_a += nudges_a
            total_nudges_b += nudges_b
            if cfix_a or cfix_b:
                recent_messages.append(f"pushes A:{cfix_a} B:{cfix_b}")
            if hfix_a or hfix_b:
                recent_messages.append(f"hazard A:{hfix_a} B:{hfix_b}")
            if nudges_a or nudges_b:
                recent_messages.append(f"unstick A:{nudges_a} B:{nudges_b}")
            collector_a.record_frame(agents_a, frame)
            collector_b.record_frame(agents_b, frame)
            for idx, ag in enumerate(agents_a):
                trails_a[idx].append(tuple(ag.pos))
                if ag.evacuated:
                    ghosts_a.append(collections.deque(trails_a[idx], maxlen=GHOST_LEN))
                    trails_a[idx].clear()
            for idx, ag in enumerate(agents_b):
                trails_b[idx].append(tuple(ag.pos))
                if ag.evacuated:
                    ghosts_b.append(collections.deque(trails_b[idx], maxlen=GHOST_LEN))
                    trails_b[idx].clear()

        screen.fill(COL_BG)
        _draw(screen, agents_a, trails_a, ghosts_a, env_a, name_a, frame, font, offset_x=0)
        _draw(screen, agents_b, trails_b, ghosts_b, env_b, name_b, frame, font, offset_x=MAP_WIDTH + 8)
        for i, msg in enumerate(recent_messages):
            lbl = font.render(f"Event: {msg}", True, (200, 200, 200))
            screen.blit(lbl, (10, MAP_HEIGHT - 80 + i * 16))
        pygame.display.flip()
        if recorder:
            recorder.append(screen)
        clock.tick(FPS)

        if all(a.evacuated for a in agents_a) and all(b.evacuated for b in agents_b):
            pygame.time.wait(600)
            break

    result_a = collector_a.summary()
    result_b = collector_b.summary()
    both = {name_a: result_a, name_b: result_b}
    print(f"  {name_a:>8s}  Evacuated {result_a['Evacuated']}/{NUM_AGENTS}  Time {result_a['Evacuation Time']}  Throughput {result_a['Throughput']:.4f}")
    print(f"  {name_b:>8s}  Evacuated {result_b['Evacuated']}/{NUM_AGENTS}  Time {result_b['Evacuation Time']}  Throughput {result_b['Throughput']:.4f}")

    if recorder:
        recorder.close()

    pygame.quit()
    return both
