import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from smart_rerun_report import aggregate_reports, format_json, format_table, main


def sample_report(tmp_path: Path) -> Path:
    payload = {
        "generated_at": "2025-01-01T00:00:00Z",
        "results": [
            {
                "nodeid": "tests/test_one.py::test_passed_after_retry",
                "attempts": 2,
                "max_attempts": 3,
                "backoff": "linear",
                "base_delay": 0.5,
                "error_filters": ["TimeoutError"],
                "final_outcome": "passed",
                "ai": {
                    "category": "flaky-network",
                    "confidence": 0.9,
                    "suggested_action": "retry_with_delay(2s)",
                    "delay_override": 2.0,
                    "notes": "Detected timeout signature.",
                },
            },
            {
                "nodeid": "tests/test_two.py::test_failed",
                "attempts": 1,
                "max_attempts": 2,
                "backoff": "none",
                "base_delay": 0.0,
                "error_filters": [],
                "final_outcome": "failed",
            },
        ],
    }
    path = tmp_path / "report.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_aggregate_reports(tmp_path: Path):
    report_path = sample_report(tmp_path)
    reports = [json.loads(report_path.read_text())]
    stats = aggregate_reports(reports)

    assert stats.total_tests == 2
    assert stats.retried_tests == 1
    assert pytest.approx(stats.average_attempts, 0.01) == 1.5
    assert stats.outcomes["passed"] == 1
    assert stats.outcomes["failed"] == 1
    assert stats.ai_categories["flaky-network"]["count"] == 1


def test_format_outputs(tmp_path: Path):
    report_path = sample_report(tmp_path)
    reports = [json.loads(report_path.read_text())]
    stats = aggregate_reports(reports)

    table_output = format_table(stats)
    assert "Total tests analysed: 2" in table_output
    assert "flaky-network" in table_output

    json_output = format_json(stats)
    data = json.loads(json_output)
    assert data["total_tests"] == 2
    assert data["ai_categories"]["flaky-network"]["count"] == 1


def test_cli_main_outputs_table(tmp_path: Path, capsys):
    report_path = sample_report(tmp_path)
    exit_code = main([str(report_path)])
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Smart Rerun Analytics" in output
    assert "flaky-network" in output
