"""v12 Module 9: Offline Analytics & Reporting Engine (metrics.py).

Computes real-time and summary statistics across the generated portfolio:
- Candidate count
- Strategy distribution
- Tool distribution
- Mutation distribution
- Duplicate %
- Average replay latency
- Coverage score
- Novelty score
Writes full diagnostic report to report.md.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from archive import BehavioralArchive
from diversity_engine import DiversityEngine

logger = logging.getLogger("v12_metrics")

class MetricsEngine:
    @staticmethod
    def generate_analytics_report(
        archive: BehavioralArchive,
        diversity: DiversityEngine,
        total_trials: int,
        duplicate_rejections: int,
        output_path: str | Path | None = None,
    ) -> str:
        """Generates comprehensive offline analytics summary and writes to report.md (`Module 9`)."""
        portfolio = archive.get_portfolio()
        count = len(portfolio)

        strat_dist: dict[str, int] = {}
        tool_dist: dict[str, int] = {}
        mut_dist: dict[str, int] = {}
        total_lat = 0.0
        total_yield = 0.0

        for item in portfolio:
            sc = item["strategy_class"]
            tf = item["tool_family"]
            mut = item["mutation_name"]
            lat = item["latency"]
            yd = item["expected_yield"]

            strat_dist[sc] = strat_dist.get(sc, 0) + 1
            tool_dist[tf] = tool_dist.get(tf, 0) + 1
            mut_dist[mut] = mut_dist.get(mut, 0) + 1
            total_lat += lat
            total_yield += yd

        avg_lat = (total_lat / count) if count > 0 else 0.0
        avg_yield = (total_yield / count) if count > 0 else 0.0
        dup_pct = (duplicate_rejections / total_trials * 100.0) if total_trials > 0 else 0.0

        # Coverage score: distinct tool families + distinct strategies represented
        distinct_tools = len([tf for tf, c in tool_dist.items() if c > 0])
        distinct_strats = len([sc for sc, c in strat_dist.items() if c > 0])
        coverage_score = (distinct_tools / 4.0 * 50.0) + (distinct_strats / 6.0 * 50.0)

        # Novelty score: percentage of candidates with unique semantic signatures vs total trials
        novelty_score = (count / max(1, total_trials)) * 100.0

        lines = [
            "# v12 Attack Engine Offline Analytics Report (`Module 9`)",
            "",
            "## Executive Summary",
            f"- **Total Portfolio Candidates (`Candidate count`)**: `{count}`",
            f"- **Total Generation Trials**: `{total_trials}`",
            f"- **Duplicate Rejection Rate (`Duplicate %`)**: `{dup_pct:.2f}%` (`{duplicate_rejections}/{total_trials}` rejected as semantic/feature duplicates)",
            f"- **Average Replay Latency (`Average replay latency`)**: `{avg_lat:.2f}s`",
            f"- **Average Expected Yield**: `{avg_yield:.2f}`",
            f"- **Coverage Score (`Coverage score`)**: `{coverage_score:.1f} / 100.0` (`{distinct_tools}/4` tool families, `{distinct_strats}/6` strategies)",
            f"- **Novelty Score (`Novelty score`)**: `{novelty_score:.1f} / 100.0`",
            "",
            "## Strategy Distribution (`Strategy distribution`)",
        ]
        for sc, c in sorted(strat_dist.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **`{sc}`**: `{c}` (`{c/max(1,count)*100:.1f}%`)")

        lines.extend([
            "",
            "## Tool Family Distribution (`Tool distribution`)",
        ])
        for tf, c in sorted(tool_dist.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **`{tf}`**: `{c}` (`{c/max(1,count)*100:.1f}%`)")

        lines.extend([
            "",
            "## Mutation Distribution (`Mutation distribution`)",
        ])
        for mut, c in sorted(mut_dist.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **`{mut}`**: `{c}` (`{c/max(1,count)*100:.1f}%`)")

        report_content = "\n".join(lines)
        logger.info(f"Analytics generated:\n{report_content[:500]}...")

        if output_path:
            try:
                p = Path(output_path)
                p.parent.mkdir(parents=True, exist_ok=True)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(report_content)
                logger.info(f"Report written to {p}")
            except Exception as e:
                logger.warning(f"Could not write report to {output_path}: {e}")

        return report_content
