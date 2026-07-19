"""v12 Module 3 & 5: Replay Diversity & Coverage Optimizer Engine (diversity_engine.py).

Tracks multi-dimensional portfolio statistics across:
- Tool families (EXFILTRATION, UNTRUSTED_TO_ACTION, DESTRUCTIVE_WRITE, CONFUSED_DEPUTY)
- Strategy classes (Strategy A through Strategy F)
- Prompt length and structure buckets
Rejects near-duplicate candidates and boosts candidates targeting under-represented dimensions.
"""

from __future__ import annotations

import logging
from typing import Any, Final
from strategy_engine import STRATEGY_CLASSES, TOOL_FAMILIES

logger = logging.getLogger("v12_diversity")

class DiversityEngine:
    def __init__(self) -> None:
        self.tool_counts: dict[str, int] = {tf: 0 for tf in TOOL_FAMILIES}
        self.tool_counts["OTHER"] = 0
        self.strategy_counts: dict[str, int] = {sc: 0 for sc in STRATEGY_CLASSES}
        self.len_bucket_counts: dict[str, int] = {"short": 0, "medium": 0, "long": 0}
        self.seen_feature_vectors: set[str] = set()

    def _len_bucket(self, msg_len: int) -> str:
        if msg_len < 150:
            return "short"
        elif msg_len < 300:
            return "medium"
        return "long"

    def compute_feature_vector(self, tool_family: str, strategy_class: str, msg_len: int, mutation_name: str) -> str:
        """Computes multi-dimensional feature representation for similarity rejection (`Module 3`)."""
        bucket = self._len_bucket(msg_len)
        return f"{tool_family}|{strategy_class}|{bucket}|{mutation_name}"

    def is_near_duplicate(self, tool_family: str, strategy_class: str, msg_len: int, mutation_name: str) -> bool:
        """Returns True if an identical feature vector is already heavily represented (`Module 3`)."""
        vec = self.compute_feature_vector(tool_family, strategy_class, msg_len, mutation_name)
        # If this exact vector is already seen and the tool family is over-represented, reject
        if vec in self.seen_feature_vectors and self.tool_counts.get(tool_family, 0) >= 10:
            return True
        return False

    def record_candidate(self, tool_family: str, strategy_class: str, msg_len: int, mutation_name: str) -> None:
        """Records statistics for coverage tracking (`Module 5`)."""
        self.tool_counts[tool_family] = self.tool_counts.get(tool_family, 0) + 1
        self.strategy_counts[strategy_class] = self.strategy_counts.get(strategy_class, 0) + 1
        bucket = self._len_bucket(msg_len)
        self.len_bucket_counts[bucket] = self.len_bucket_counts.get(bucket, 0) + 1
        vec = self.compute_feature_vector(tool_family, strategy_class, msg_len, mutation_name)
        self.seen_feature_vectors.add(vec)

    def compute_coverage_boost(self, tool_family: str, strategy_class: str, msg_len: int) -> float:
        """Calculates coverage multiplier: inverse representation across tool and strategy dimensions (`Module 5`)."""
        tf_count = self.tool_counts.get(tool_family, 0)
        sc_count = self.strategy_counts.get(strategy_class, 0)
        bucket = self._len_bucket(msg_len)
        b_count = self.len_bucket_counts.get(bucket, 0)

        boost_tf = 1.0 + (3.0 / (tf_count + 1.0))
        boost_sc = 1.0 + (2.0 / (sc_count + 1.0))
        boost_b = 1.0 + (1.0 / (b_count + 1.0))
        return boost_tf * boost_sc * boost_b
