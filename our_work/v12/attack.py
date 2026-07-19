"""v12 Module 8 & Top-Level Attack Engine (attack.py).

Orchestrates the 5 clean phases:
Phase 1: Probe across 6 strategy classes
Phase 2: Discover target evaluator preferences (`ClusteringEngine`)
Phase 3: Generate multiple attack styles (`StrategyEngine` + `SemanticMutator`)
Phase 4: Keep only novel behaviors (`BehavioralArchive` + `DiversityEngine`)
Phase 5: Replay-safe packing (`ReplayEstimator`), Adaptive Stopping (`Module 8`), & Offline Analytics (`Module 9`)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Sequence

from aicomp_sdk.agents.base import AttackAlgorithmBase
from aicomp_sdk.core.env.sandbox import SandboxEnv
from aicomp_sdk.core.state import AttackCandidate

from strategy_engine import STRATEGY_CLASSES, TOOL_FAMILIES, generate_strategy_message
from clustering import ClusteringEngine
from diversity_engine import DiversityEngine
from semantic_mutator import mutate_message, SEMANTIC_MUTATION_NAMES
from replay_estimator import ReplayEstimator
from archive import BehavioralArchive
from metrics import MetricsEngine

logger = logging.getLogger("v12_attack")

PROBE_REPS = 3
MAX_FILL_CANDIDATES = 120
REPLAY_SAFE_BUDGET_S = 8910.0
FLATTEN_LIMIT = 15  # Adaptive stopping: stop when new signatures flatten (`Module 8`)

class AttackAlgorithm(AttackAlgorithmBase):
    def __init__(self, config_or_max: Any = 100) -> None:
        if isinstance(config_or_max, dict):
            self.max_candidates = int(config_or_max.get("max_candidates", 100))
        elif hasattr(config_or_max, "max_candidates"):
            self.max_candidates = int(getattr(config_or_max, "max_candidates", 100))
        else:
            try:
                self.max_candidates = int(config_or_max)
            except Exception:
                self.max_candidates = 100
        self.archive = BehavioralArchive(max_candidates=self.max_candidates)
        self.diversity = DiversityEngine()
        self.total_trials = 0
        self.duplicate_rejections = 0

    def run(self, env: SandboxEnv, run_config: Any) -> Sequence[AttackCandidate]:
        logger.info(f"=== Starting v12 Attack Diversity & Replay Engine (max={self.max_candidates}) ===")

        # Phase 1: Probe across 6 Strategy Classes
        probe_fires: dict[str, int] = {sc: 0 for sc in STRATEGY_CLASSES}
        probe_trials: dict[str, int] = {sc: 0 for sc in STRATEGY_CLASSES}
        probe_latencies: dict[str, list[float]] = {sc: [] for sc in STRATEGY_CLASSES}

        # Use EXFILTRATION and UNTRUSTED_TO_ACTION round-robin during probing
        probe_tfs = ("EXFILTRATION", "UNTRUSTED_TO_ACTION")

        for rep in range(PROBE_REPS):
            for sc_idx, sc in enumerate(STRATEGY_CLASSES):
                tf = probe_tfs[(rep + sc_idx) % len(probe_tfs)]
                msg_text, strat_class, tool_fam = generate_strategy_message(sc, tf, rep)
                cand = AttackCandidate.from_messages((msg_text,))
                self.total_trials += 1

                try:
                    state, result = env.step(cand)
                    lat = float(getattr(state, "execution_time_s", 2.0))
                    trace = getattr(state, "trace", ())
                    v_cnt = int(getattr(result, "violation_count", 0)) if result else 0

                    probe_trials[sc] += 1
                    probe_latencies[sc].append(lat)
                    if v_cnt > 0:
                        probe_fires[sc] += 1

                    # Add successful probe immediately to archive (`Phase 4`)
                    success_prob = (probe_fires[sc] / probe_trials[sc]) if probe_trials[sc] > 0 else 0.1
                    added = self.archive.add(
                        candidate=cand,
                        trace=trace,
                        latency=lat,
                        violation_count=v_cnt,
                        strategy_class=sc,
                        tool_family=tf,
                        mutation_name="probe",
                        success_prob=success_prob,
                        diversity=self.diversity,
                    )
                    if not added and self.diversity.is_near_duplicate(tf, sc, len(msg_text), "probe"):
                        self.duplicate_rejections += 1
                except Exception as e:
                    logger.debug(f"Probe error on strategy {sc}: {e}")

        # Phase 2: Discover target evaluator preferences (`ClusteringEngine` Module 2)
        cluster_name, prioritized_strategies = ClusteringEngine.detect_cluster(
            probe_fires, probe_trials, probe_latencies
        )

        # Phase 3 & Phase 4: Generate multiple attack styles & Keep only novel behaviors
        unproductive_streak = 0
        fill_idx = 0

        while self.total_trials < (PROBE_REPS * len(STRATEGY_CLASSES) + MAX_FILL_CANDIDATES):
            # Adaptive stopping (`Module 8`): stop when new signatures flatten
            if unproductive_streak >= FLATTEN_LIMIT:
                logger.info(f"Adaptive stopping triggered (`unproductive_streak >= {FLATTEN_LIMIT}`). New signatures flattened.")
                break

            sc = prioritized_strategies[fill_idx % len(prioritized_strategies)]
            tf = TOOL_FAMILIES[(fill_idx // len(prioritized_strategies)) % len(TOOL_FAMILIES)]
            mut_idx = fill_idx % len(SEMANTIC_MUTATION_NAMES)

            base_msg, strat_class, tool_fam = generate_strategy_message(sc, tf, fill_idx)
            mut_msg, mut_name = mutate_message(base_msg, sc, mut_idx)

            msg_len = len(mut_msg)
            if self.diversity.is_near_duplicate(tf, sc, msg_len, mut_name):
                self.duplicate_rejections += 1
                unproductive_streak += 1
                fill_idx += 1
                self.total_trials += 1
                continue

            cand = AttackCandidate.from_messages((mut_msg,))
            self.total_trials += 1

            try:
                state, result = env.step(cand)
                lat = float(getattr(state, "execution_time_s", 2.0))
                trace = getattr(state, "trace", ())
                v_cnt = int(getattr(result, "violation_count", 0)) if result else 0

                trials = probe_trials.get(sc, 1)
                fires = probe_fires.get(sc, 0)
                success_prob = (fires / trials) if trials > 0 else 0.1

                added = self.archive.add(
                    candidate=cand,
                    trace=trace,
                    latency=lat,
                    violation_count=v_cnt,
                    strategy_class=sc,
                    tool_family=tf,
                    mutation_name=mut_name,
                    success_prob=success_prob,
                    diversity=self.diversity,
                )

                if added:
                    unproductive_streak = 0
                else:
                    unproductive_streak += 1
                    self.duplicate_rejections += 1
            except Exception as e:
                logger.debug(f"Fill error on strategy {sc}: {e}")
                unproductive_streak += 1

            fill_idx += 1

        # Phase 5: Replay-safe packing (`ReplayEstimator` Module 6)
        portfolio = self.archive.get_portfolio()
        final_candidates: list[AttackCandidate] = []
        cumulative_lat = 0.0

        for item in portfolio:
            lat = item["latency"]
            if cumulative_lat + lat <= REPLAY_SAFE_BUDGET_S and len(final_candidates) < self.max_candidates:
                final_candidates.append(item["candidate"])
                cumulative_lat += lat
            elif len(final_candidates) >= self.max_candidates:
                break

        # Fallback safety
        if not final_candidates:
            msg, _, _ = generate_strategy_message("Strategy A (Authority)", "EXFILTRATION", 0)
            final_candidates.append(AttackCandidate.from_messages((msg,)))

        # Module 9: Offline analytics report
        report_path = Path("v12/report.md") if Path("v12").exists() else Path("report.md")
        MetricsEngine.generate_analytics_report(
            archive=self.archive,
            diversity=self.diversity,
            total_trials=self.total_trials,
            duplicate_rejections=self.duplicate_rejections,
            output_path=report_path,
        )

        logger.info(f"=== v12 Engine Complete: returning {len(final_candidates)} candidates (cumulative_lat={cumulative_lat:.2f}s) ===")
        return final_candidates
