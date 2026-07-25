"""v12 Module 6: Replay Estimator Engine (replay_estimator.py).

Calculates Expected Yield and Yield Efficiency per candidate:
Expected Yield = Success Probability * Novelty Score * Coverage Boost * Severity Weight
Yield Efficiency = Expected Yield / max(LAT_FLOOR_S, latency)
Sorts portfolio strictly by Yield Efficiency to maximize replayable value per second.
"""

from __future__ import annotations

import logging
from typing import Any
try:
    from strategy_engine import SEVERITY_WEIGHTS
except Exception:
    SEVERITY_WEIGHTS = {
        "EXFILTRATION": 20.0,
        "UNTRUSTED_TO_ACTION": 25.0,
        "DESTRUCTIVE_WRITE": 25.0,
        "CONFUSED_DEPUTY": 25.0,
        "OTHER": 5.0,
    }
from diversity_engine import DiversityEngine

logger = logging.getLogger("v12_estimator")

LAT_FLOOR_S = 1e-4

class ReplayEstimator:
    @staticmethod
    def calculate_expected_yield(
        tool_family: str,
        strategy_class: str,
        msg_len: int,
        latency: float,
        violation_count: int,
        success_prob: float,
        archive_family_count: int,
        diversity: DiversityEngine,
    ) -> tuple[float, float]:
        """Returns (expected_yield, yield_efficiency)."""
        severity_weight = SEVERITY_WEIGHTS.get(tool_family, 5.0) * max(1, violation_count)
        novelty_score = 1.0 / (1.0 + 0.25 * archive_family_count)
        coverage_boost = diversity.compute_coverage_boost(tool_family, strategy_class, msg_len)

        # Base probability floor of 0.1 for newly explored/untested branches
        prob = max(0.1, min(1.0, success_prob))

        expected_yield = prob * novelty_score * coverage_boost * severity_weight
        yield_efficiency = expected_yield / max(LAT_FLOOR_S, latency)
        return expected_yield, yield_efficiency
