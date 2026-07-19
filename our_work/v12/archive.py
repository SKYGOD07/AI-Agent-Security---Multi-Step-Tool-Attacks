"""v12 Module 7: Behavioral & Semantic Novelty Archive (archive.py).

Hashes semantic behavior instead of raw prompt text (`compute_semantic_signature`).
Two prompts with identical tool sequence, strategy class, and action parameters are treated as duplicates.
Retains candidates that maximize Expected Yield and provide behavioral diversity.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Sequence
from diversity_engine import DiversityEngine
from replay_estimator import ReplayEstimator

logger = logging.getLogger("v12_archive")

class BehavioralArchive:
    def __init__(self, max_candidates: int = 100) -> None:
        self.max_candidates = max_candidates
        # Map semantic_sig -> dict containing candidate info
        self.entries: dict[str, dict[str, Any]] = {}
        self.family_counts: dict[str, int] = {}

    @staticmethod
    def _extract_tool_seq(trace: Sequence[Any]) -> str:
        if not trace:
            return ""
        names: list[str] = []
        for step in trace:
            if hasattr(step, "tool_name"):
                names.append(str(getattr(step, "tool_name", "")))
            elif isinstance(step, dict) and "tool_name" in step:
                names.append(str(step["tool_name"]))
            else:
                names.append(str(step))
        return "->".join(names)

    @classmethod
    def compute_semantic_signature(
        cls,
        messages: Sequence[str],
        trace: Sequence[Any],
        strategy_class: str,
        tool_family: str,
    ) -> str:
        """Computes semantic behavior signature ignoring cosmetic wrapper text (`Module 7`)."""
        tool_seq = cls._extract_tool_seq(trace) or tool_family
        # Extract core action payload indicators (URLs, commands, file paths) to hash semantic intent
        combined_text = " ".join(str(m) for m in messages)
        payload_tokens: list[str] = []
        for word in combined_text.split():
            if any(k in word for k in ("http://", "url=", "command=", "path=", "user=", "role=")):
                payload_tokens.append(word)
        payload_str = "|".join(payload_tokens) if payload_tokens else combined_text[:100]
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()[:12]
        return f"{tool_seq}|{strategy_class}|{tool_family}|{payload_hash}"

    def add(
        self,
        candidate: Any,
        trace: Sequence[Any],
        latency: float,
        violation_count: int,
        strategy_class: str,
        tool_family: str,
        mutation_name: str,
        success_prob: float,
        diversity: DiversityEngine,
    ) -> bool:
        """Adds candidate if novel semantic signature or strictly higher yield efficiency (`Module 7`)."""
        messages = getattr(candidate, "user_messages", ())
        if not messages:
            return False

        # Check similarity check from diversity engine first (`Module 3`)
        msg_len = sum(len(str(m)) for m in messages)
        if diversity.is_near_duplicate(tool_family, strategy_class, msg_len, mutation_name):
            return False

        sem_sig = self.compute_semantic_signature(messages, trace, strategy_class, tool_family)
        fam_count = self.family_counts.get(tool_family, 0)

        exp_yield, yield_eff = ReplayEstimator.calculate_expected_yield(
            tool_family=tool_family,
            strategy_class=strategy_class,
            msg_len=msg_len,
            latency=latency,
            violation_count=violation_count,
            success_prob=success_prob,
            archive_family_count=fam_count,
            diversity=diversity,
        )

        if sem_sig in self.entries:
            existing = self.entries[sem_sig]
            # If our new yield efficiency is higher, or latency is lower with same yield, replace
            if yield_eff > existing["yield_efficiency"] * 1.05 or (
                abs(yield_eff - existing["yield_efficiency"]) < 1e-4 and latency < existing["latency"]
            ):
                self.entries[sem_sig] = {
                    "candidate": candidate,
                    "trace": trace,
                    "latency": latency,
                    "violation_count": violation_count,
                    "strategy_class": strategy_class,
                    "tool_family": tool_family,
                    "mutation_name": mutation_name,
                    "expected_yield": exp_yield,
                    "yield_efficiency": yield_eff,
                    "msg_len": msg_len,
                }
                diversity.record_candidate(tool_family, strategy_class, msg_len, mutation_name)
                return True
            return False

        # Brand new semantic signature
        self.entries[sem_sig] = {
            "candidate": candidate,
            "trace": trace,
            "latency": latency,
            "violation_count": violation_count,
            "strategy_class": strategy_class,
            "tool_family": tool_family,
            "mutation_name": mutation_name,
            "expected_yield": exp_yield,
            "yield_efficiency": yield_eff,
            "msg_len": msg_len,
        }
        self.family_counts[tool_family] = fam_count + 1
        diversity.record_candidate(tool_family, strategy_class, msg_len, mutation_name)
        return True

    def get_portfolio(self) -> list[dict[str, Any]]:
        """Returns all entries sorted strictly descending by Yield Efficiency (`Module 6`)."""
        return sorted(list(self.entries.values()), key=lambda x: x["yield_efficiency"], reverse=True)
