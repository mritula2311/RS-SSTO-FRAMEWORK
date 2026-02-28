"""Comparison orchestration for all algorithms."""

from __future__ import annotations

import pandas as pd


def build_comparison_table(results: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(results)
    ordered_cols = ["Algorithm", "EvacuationTime", "AverageSpeed", "Congestion", "Throughput"]
    return df[ordered_cols].sort_values(by="EvacuationTime").reset_index(drop=True)
