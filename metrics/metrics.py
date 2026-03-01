"""
Metrics Module
==============
Calculates performance metrics for each algorithm run.

Metrics tracked:
  - Evacuation Time   (frames until all agents evacuated or timeout)
  - Average Speed     (mean speed of agents per frame)
  - Congestion Level  (fraction of agent-pairs within crowding radius)
  - Throughput        (agents evacuated / time)
  - Evacuated Count   (total agents that reached the exit)
"""

from __future__ import annotations
import numpy as np


class MetricsCollector:
    """Accumulates per-frame data and computes summary statistics."""

    def __init__(self, total_agents: int):
        self.total_agents = total_agents
        self.frame_speeds: list[float]  = []
        self.frame_congestion: list[float] = []
        self.evacuated_at_frame: list[int] = []
        self.final_frame: int = 0
        # Exit parameters for congestion calculation
        from config import EXIT_RADIUS
        self.exit_radius = EXIT_RADIUS

    # ── per-frame update ─────────────────────────────────────────────────
    def record_frame(self, agents: list, frame: int) -> None:
        """Call once per frame to accumulate data."""
        active = [a for a in agents if not a.evacuated]
        if not active:
            return

        # Average speed
        speeds = [float(np.linalg.norm(a.vel)) for a in active]
        self.frame_speeds.append(float(np.mean(speeds)))

        # Congestion: density of agents near exit (agents per unit area)
        # Count agents within 3x exit radius (exit vicinity zone)
        from config import EXIT_POS
        exit_pos = np.array(EXIT_POS, dtype=float)
        exit_vicinity_radius = self.exit_radius * 3.0
        agents_near_exit = sum(
            1 for a in active
            if float(np.linalg.norm(a.pos - exit_pos)) < exit_vicinity_radius
        )
        # Area of exit vicinity zone
        exit_area = np.pi * (exit_vicinity_radius ** 2)
        # Density: agents per 1000 square pixels (normalized)
        density = (agents_near_exit / exit_area) * 1000.0
        self.frame_congestion.append(density)

        # Track newly evacuated
        newly_evacuated = sum(1 for a in agents if a.evacuated) - len(self.evacuated_at_frame)
        for _ in range(newly_evacuated):
            self.evacuated_at_frame.append(frame)

        self.final_frame = frame

    # ── summary ──────────────────────────────────────────────────────────
    def summary(self) -> dict:
        evacuated_count = len(self.evacuated_at_frame)
        evac_time = max(self.evacuated_at_frame) if self.evacuated_at_frame else self.final_frame
        avg_time = round(float(np.mean(self.evacuated_at_frame)) if self.evacuated_at_frame else evac_time, 1)
        return {
            "Total Agents":     self.total_agents,
            "Evacuated":        evacuated_count,
            "Evac Time":        evac_time,
            "Avg Time":         avg_time,
            "Throughput":       round(evacuated_count / max(evac_time, 1), 4),
            "Congestion":       round(float(np.mean(self.frame_congestion)) if self.frame_congestion else 0, 4),
            "Efficiency":       round(100 * evacuated_count / self.total_agents, 1),
        }
