"""v12 Module 2: Behavior Clustering Engine (clustering.py).

Discovers target model behavior clusters online from front-end probe statistics across the 6 strategy classes:
- Cluster A (Authority/Emergency-Responsive): Authority & Emergency convert best.
- Cluster B (Workflow/Reasoning-Responsive): Workflow & Reasoning convert best.
- Cluster C (Maintenance/Debug-Responsive): Maintenance & Debug convert best.
Maps the discovered cluster to an adaptive policy prioritizing the most responsive strategy classes.
"""

from __future__ import annotations

import logging
from typing import Any, Sequence
from strategy_engine import STRATEGY_CLASSES, TOOL_FAMILIES

logger = logging.getLogger("v12_clustering")

class ClusteringEngine:
    @staticmethod
    def detect_cluster(
        probe_fires: dict[str, int],
        probe_trials: dict[str, int],
        probe_latencies: dict[str, list[float]],
    ) -> tuple[str, list[str]]:
        """Discovers behavior cluster and returns (cluster_name, prioritized_strategies)."""
        rates: dict[str, float] = {}
        for s in STRATEGY_CLASSES:
            trials = probe_trials.get(s, 0)
            fires = probe_fires.get(s, 0)
            rates[s] = (fires / trials) if trials > 0 else 0.0

        # Group conversion rates into behavioral clusters
        auth_score = rates.get("Strategy A (Authority)", 0.0) + rates.get("Strategy D (Emergency)", 0.0)
        work_score = rates.get("Strategy B (Workflow)", 0.0) + rates.get("Strategy C (Reasoning chain)", 0.0)
        maint_score = rates.get("Strategy E (Maintenance)", 0.0) + rates.get("Strategy F (Debug)", 0.0)

        # Sort all strategies by empirical fire rate, then by lowest latency
        def _strat_sort_key(s: str) -> tuple[float, float]:
            r = rates.get(s, 0.0)
            lats = probe_latencies.get(s, [])
            med_lat = sorted(lats)[len(lats) // 2] if lats else 24.0
            return (r, -med_lat)

        sorted_strats = sorted(list(STRATEGY_CLASSES), key=_strat_sort_key, reverse=True)

        if auth_score > work_score and auth_score > maint_score and auth_score > 0.0:
            cluster_name = "Cluster A (Authority/Emergency-Responsive)"
            # Prioritize Authority & Emergency first, followed by remaining sorted strategies
            prioritized = [
                "Strategy A (Authority)",
                "Strategy D (Emergency)",
                "Strategy B (Workflow)",
                "Strategy C (Reasoning chain)",
                "Strategy E (Maintenance)",
                "Strategy F (Debug)",
            ]
        elif work_score >= auth_score and work_score > maint_score and work_score > 0.0:
            cluster_name = "Cluster B (Workflow/Reasoning-Responsive)"
            prioritized = [
                "Strategy B (Workflow)",
                "Strategy C (Reasoning chain)",
                "Strategy E (Maintenance)",
                "Strategy A (Authority)",
                "Strategy D (Emergency)",
                "Strategy F (Debug)",
            ]
        elif maint_score >= auth_score and maint_score >= work_score and maint_score > 0.0:
            cluster_name = "Cluster C (Maintenance/Debug-Responsive)"
            prioritized = [
                "Strategy E (Maintenance)",
                "Strategy F (Debug)",
                "Strategy A (Authority)",
                "Strategy B (Workflow)",
                "Strategy C (Reasoning chain)",
                "Strategy D (Emergency)",
            ]
        else:
            cluster_name = "Cluster Balanced (Empirical-Sorted Policy)"
            prioritized = sorted_strats

        logger.info(f"Clustering engine detected: {cluster_name} -> prioritized strategies: {prioritized[:3]}")
        return cluster_name, prioritized
