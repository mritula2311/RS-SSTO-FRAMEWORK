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

    # ── per-frame update ─────────────────────────────────────────────────
    def record_frame(self, agents: list, frame: int) -> None:
        """Call once per frame to accumulate data."""
        active = [a for a in agents if not a.evacuated]
        if not active:
            return

        # Average speed
        speeds = [float(np.linalg.norm(a.vel)) for a in active]
        self.frame_speeds.append(float(np.mean(speeds)))

        # Congestion: fraction of agent-pairs within 15 px
        crowd_radius = 15.0
        n = len(active)
        crowded_pairs = 0
        total_pairs   = max(n * (n - 1) // 2, 1)
        for i in range(n):
            for j in range(i + 1, n):
                if float(np.linalg.norm(active[i].pos - active[j].pos)) < crowd_radius:
                    crowded_pairs += 1
        self.frame_congestion.append(crowded_pairs / total_pairs)

        # Track newly evacuated
        newly_evacuated = sum(1 for a in agents if a.evacuated) - len(self.evacuated_at_frame)
        for _ in range(newly_evacuated):
            self.evacuated_at_frame.append(frame)

        self.final_frame = frame

    # ── summary ──────────────────────────────────────────────────────────
    def summary(self) -> dict:
        evacuated_count = len(self.evacuated_at_frame)
        evac_time = max(self.evacuated_at_frame) if self.evacuated_at_frame else self.final_frame
        return {
            "Evacuated":        evacuated_count,
            "Evacuation Time":  evac_time,
            "Avg Speed":        round(float(np.mean(self.frame_speeds)) if self.frame_speeds else 0, 3),
            "Congestion":       round(float(np.mean(self.frame_congestion)) if self.frame_congestion else 0, 4),
            "Throughput":       round(evacuated_count / max(evac_time, 1), 4),
            "Efficiency %":     round(100 * evacuated_count / self.total_agents, 1),
        }
