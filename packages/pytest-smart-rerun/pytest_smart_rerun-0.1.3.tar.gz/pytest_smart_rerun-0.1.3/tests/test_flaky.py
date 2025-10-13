import json
from pathlib import Path

import pytest

pytest_plugins = ("pytester",)

_counter = {"attempts": 0}


@pytest.mark.smart_rerun(max=3, delay=0)
def test_flaky_counter_passes_on_second_attempt():
    _counter["attempts"] += 1
    if _counter["attempts"] < 2:
        pytest.fail("Intentional flaky failure")
    assert True


def test_regular_behavior_without_marker():
    assert 1 + 1 == 2


def test_error_filter_and_report_generation(pytester):
    test_file = pytester.makepyfile(
        """
        import pytest
        attempts = {"count": 0}


        @pytest.mark.smart_rerun(max=3, delay=0, errors=["TimeoutError"])
        def test_filtered_retry():
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise TimeoutError("temporary blip")
        """
    )
    report_path = pytester.path / "smart_report.json"
    result = pytester.runpytest(
        "--smart-rerun",
        "--smart-rerun-report",
        str(report_path),
    )
    outcomes = result.parseoutcomes()
    assert outcomes.get("passed") == 1
    assert outcomes.get("rerun") == 1

    data = json.loads(report_path.read_text())
    assert data["results"][0]["nodeid"].endswith("test_filtered_retry")
    assert data["results"][0]["final_outcome"] == "passed"


def test_linear_backoff_collects_sleep_intervals(pytester):
    test_file = pytester.makepyfile(
        """
        import pytest
        from pathlib import Path
        import pytest_smart_rerun

        sleep_calls = []

        def fake_sleep(value):
            sleep_calls.append(round(value, 2))


        pytest_smart_rerun.time.sleep = fake_sleep

        attempts = {"count": 0}


        @pytest.mark.smart_rerun(max=3, delay=0.5, backoff="linear")
        def test_linear_backoff():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise TimeoutError("still flaky")
            Path("sleep_calls.json").write_text(str(sleep_calls))
        """
    )
    result = pytester.runpytest("--smart-rerun")
    outcomes = result.parseoutcomes()
    assert outcomes.get("passed") == 1
    assert outcomes.get("rerun") == 2

    sleep_file = Path(pytester.path) / "sleep_calls.json"
    sleep_calls = sleep_file.read_text()
    assert "0.5" in sleep_calls and "1.0" in sleep_calls


def test_ai_retry_hint_for_timeouts(pytester):
    pytester.makepyfile(
        """
        import pytest
        attempts = {"count": 0}


        @pytest.mark.smart_rerun(max=2, delay=0.1)
        def test_ai_timeout_retry():
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise TimeoutError("network hiccup")
        """
    )
    ai_report = pytester.path / "ai_report.json"
    result = pytester.runpytest(
        "--smart-rerun",
        "--smart-rerun-ai",
        "--smart-rerun-ai-report",
        str(ai_report),
    )
    outcomes = result.parseoutcomes()
    assert outcomes.get("passed") == 1
    assert outcomes.get("rerun") == 1

    data = json.loads(ai_report.read_text())
    categories = {
        entry["ai"]["category"]
        for entry in data
        if isinstance(entry, dict) and entry.get("ai")
    }
    assert "flaky-network" in categories


def test_ai_stops_retry_for_deterministic_failures(pytester):
    pytester.makepyfile(
        """
        import pytest


        @pytest.mark.smart_rerun(max=3, delay=0)
        def test_ai_deterministic_failure():
            assert False, "permanent logic bug"
        """
    )
    result = pytester.runpytest("--smart-rerun", "--smart-rerun-ai")
    outcomes = result.parseoutcomes()
    assert outcomes.get("failed") == 1
    assert outcomes.get("rerun") is None
