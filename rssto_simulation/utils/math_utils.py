"""Shared mathematical utilities for force-based motion."""

from __future__ import annotations

import numpy as np


def normalize(vec: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm < eps:
        return np.zeros_like(vec)
    return vec / norm


def pairwise_neighbors(positions: np.ndarray, radius: float) -> list[list[int]]:
    """Return neighbor index list for each position within radius."""
    n = len(positions)
    neighbors: list[list[int]] = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if np.linalg.norm(positions[i] - positions[j]) <= radius:
                neighbors[i].append(j)
                neighbors[j].append(i)
    return neighbors
