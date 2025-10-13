"""Command-line analytics toolkit for pytest-smart-rerun JSON reports."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class AggregatedStats:
    total_tests: int
    total_attempts: int
    retried_tests: int
    outcomes: Dict[str, int]
    ai_categories: Dict[str, Dict[str, float]]
    max_attempts: int

    @property
    def average_attempts(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.total_attempts / self.total_tests


def load_reports(paths: Iterable[Path]) -> List[dict]:
    reports: List[dict] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Report file not found: {path}")
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and "results" in data:
            reports.append(data)
        elif isinstance(data, list):
            # AI report format (list of entries)
            reports.append({"generated_at": None, "results": data})
        else:
            raise ValueError(f"Unrecognized report format in {path}")
    return reports


def aggregate_reports(reports: List[dict]) -> AggregatedStats:
    total_tests = 0
    total_attempts = 0
    retried_tests = 0
    outcomes_counter: Counter[str] = Counter()
    ai_category_counter: Counter[str] = Counter()
    ai_confidence_totals: Dict[str, float] = defaultdict(float)
    ai_counts: Counter[str] = Counter()
    max_attempts = 0

    for report in reports:
        for entry in report.get("results", []):
            total_tests += 1
            attempts = int(entry.get("attempts", 1))
            total_attempts += attempts
            max_attempts = max(max_attempts, attempts, int(entry.get("max_attempts", attempts)))
            if attempts > 1:
                retried_tests += 1

            outcome = entry.get("final_outcome", "unknown")
            outcomes_counter[outcome] += 1

            ai_data = entry.get("ai")
            if isinstance(ai_data, dict):
                category = ai_data.get("category", "unclassified")
                confidence = float(ai_data.get("confidence", 0.0))
                ai_category_counter[category] += 1
                ai_confidence_totals[category] += confidence
                ai_counts[category] += 1

    ai_categories: Dict[str, Dict[str, float]] = {}
    for category, count in ai_category_counter.items():
        confidence_total = ai_confidence_totals.get(category, 0.0)
        avg_confidence = confidence_total / ai_counts[category] if ai_counts[category] else 0.0
        ai_categories[category] = {
            "count": count,
            "avg_confidence": round(avg_confidence, 2),
        }

    return AggregatedStats(
        total_tests=total_tests,
        total_attempts=total_attempts,
        retried_tests=retried_tests,
        outcomes=dict(outcomes_counter),
        ai_categories=ai_categories,
        max_attempts=max_attempts,
    )


def format_table(stats: AggregatedStats) -> str:
    lines = [
        "Smart Rerun Analytics",
        "======================",
        f"Total tests analysed: {stats.total_tests}",
        f"Tests with retries:   {stats.retried_tests}",
        f"Average attempts:     {stats.average_attempts:.2f}",
        f"Max attempts seen:    {stats.max_attempts}",
        "",
        "Final outcomes:",
    ]
    if stats.outcomes:
        for outcome, count in sorted(stats.outcomes.items()):
            lines.append(f"  - {outcome}: {count}")
    else:
        lines.append("  (none)")

    lines.append("")
    lines.append("AI classifications:")
    if stats.ai_categories:
        for category, data in sorted(stats.ai_categories.items()):
            lines.append(
                f"  - {category}: {data['count']} (avg confidence {data['avg_confidence']:.2f})"
            )
    else:
        lines.append("  (no AI data)")
    return "\n".join(lines)


def format_json(stats: AggregatedStats) -> str:
    payload = {
        "total_tests": stats.total_tests,
        "retried_tests": stats.retried_tests,
        "average_attempts": round(stats.average_attempts, 4),
        "max_attempts": stats.max_attempts,
        "outcomes": stats.outcomes,
        "ai_categories": stats.ai_categories,
    }
    return json.dumps(payload, indent=2)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate pytest-smart-rerun JSON analytics into human-readable summaries.",
    )
    parser.add_argument(
        "reports",
        nargs="+",
        type=Path,
        help="One or more JSON report file paths produced by pytest-smart-rerun.",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Output format (default: table).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    reports = load_reports(args.reports)
    stats = aggregate_reports(reports)
    if args.format == "json":
        print(format_json(stats))
    else:
        print(format_table(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
