"""
pytest-smart-rerun: lightweight Pytest plugin for retrying flaky tests.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable, Optional

import pytest
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import runtestprotocol


@dataclass
class SmartRerunSettings:
    enabled: bool
    max_attempts: int
    delay: float


class SmartRerunPlugin:
    """Coordinates retry attempts for flaky tests."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.enabled_flag = config.getoption("smart_rerun")
        self.default_max_attempts = config.getoption("smart_rerun_max")
        self.default_delay = config.getoption("smart_rerun_delay")
        self.terminal_reporter = config.pluginmanager.get_plugin("terminalreporter")

        if self.default_max_attempts < 1:
            raise pytest.UsageError("--smart-rerun-max must be >= 1")
        if self.default_delay < 0:
            raise pytest.UsageError("--smart-rerun-delay must be >= 0")

    # ----------------------------
    # Hook implementations
    # ----------------------------

    def pytest_collection_modifyitems(self, items: Iterable[Item]) -> None:
        # Ensure marker validation happens early so the user sees clear errors.
        for item in items:
            marker = item.get_closest_marker("smart_rerun")
            if marker is None:
                continue
            max_value = self._extract_marker_max(marker, item)
            delay_value = self._extract_marker_delay(marker)
            enabled_value = marker.kwargs.get("enabled", True)
            if max_value is not None:
                coerced_max = self._coerce_int(max_value, field="marker max", item=item)
                self._validate_attempts(coerced_max, source=f"marker on {item.nodeid}")
            coerced_delay = self._coerce_float(delay_value, field="marker delay", item=item)
            self._validate_delay(coerced_delay, source=f"marker on {item.nodeid}")
            if enabled_value not in (True, False):
                raise pytest.UsageError(
                    f"smart_rerun marker on {item.nodeid} must set enabled to True/False if provided."
                )

    def pytest_runtest_protocol(self, item: Item, nextitem: Optional[Item]) -> Optional[bool]:
        settings = self._settings_for(item)
        if not settings.enabled or settings.max_attempts <= 1:
            return None

        nodeid = item.nodeid
        for attempt in range(1, settings.max_attempts + 1):
            self._log_attempt(item, attempt, settings.max_attempts)
            item.ihook.pytest_runtest_logstart(nodeid=nodeid, location=item.location)
            reports = runtestprotocol(item, nextitem=nextitem, log=False)

            failure_detected = self._should_retry(reports)
            if failure_detected and attempt < settings.max_attempts:
                self._mark_reports_as_rerun(reports, attempt, settings.max_attempts)
                self._emit_reports(item, reports)
                item.ihook.pytest_runtest_logfinish(nodeid=nodeid, location=item.location)
                if settings.delay:
                    time.sleep(settings.delay)
                continue

            self._emit_reports(item, reports)
            item.ihook.pytest_runtest_logfinish(nodeid=nodeid, location=item.location)
            break
        return True

    def pytest_report_teststatus(self, report: TestReport):
        if report.outcome == "rerun":
            return "rerun", "R", ("RERUN", {"yellow": True})

    def pytest_terminal_summary(self, terminalreporter) -> None:
        reruns = terminalreporter.stats.get("rerun")
        if not reruns:
            return
        terminalreporter.section("smart rerun summary", sep="=")
        for report in reruns:
            terminalreporter.line(f"{report.nodeid} - retried")

    # ----------------------------
    # Helper methods
    # ----------------------------

    def _settings_for(self, item: Item) -> SmartRerunSettings:
        marker = item.get_closest_marker("smart_rerun")

        enabled = bool(self.enabled_flag)
        max_attempts = self.default_max_attempts
        delay = self.default_delay

        if marker is not None:
            enabled = marker.kwargs.get("enabled", True)
            if marker.args:
                if len(marker.args) > 1:
                    raise pytest.UsageError(
                        f"smart_rerun marker on {item.nodeid} accepts at most one positional argument."
                    )
                # Positional argument is treated as max attempts.
                max_attempts = marker.args[0]
            max_attempts = marker.kwargs.get("max", max_attempts)
            delay = marker.kwargs.get("delay", delay)

        max_attempts = self._coerce_int(max_attempts, field="max_attempts", item=item)
        delay = self._coerce_float(delay, field="delay", item=item)

        if enabled not in (True, False):
            raise pytest.UsageError(
                f"smart_rerun enabled flag for {item.nodeid} must be either True or False."
            )

        if enabled:
            self._validate_attempts(max_attempts, source=item.nodeid)
            self._validate_delay(delay, source=item.nodeid)

        return SmartRerunSettings(enabled=bool(enabled), max_attempts=max_attempts, delay=delay)

    def _log_attempt(self, item: Item, attempt: int, max_attempts: int) -> None:
        if self.terminal_reporter is None:
            return
        prefix = "retrying" if attempt > 1 else "running"
        self.terminal_reporter.write_line(
            f"[smart-rerun] {prefix} {item.nodeid} (attempt {attempt}/{max_attempts})"
        )

    @staticmethod
    def _emit_reports(item: Item, reports: Iterable[TestReport]) -> None:
        for report in reports:
            item.ihook.pytest_runtest_logreport(report=report)

    @staticmethod
    def _validate_attempts(value: int, source: str) -> None:
        if value < 1:
            raise pytest.UsageError(f"{source}: max attempts must be >= 1.")

    @staticmethod
    def _validate_delay(value: float, source: str) -> None:
        if value < 0:
            raise pytest.UsageError(f"{source}: delay must be >= 0 seconds.")

    @staticmethod
    def _coerce_int(value: object, field: str, item: Item) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            raise pytest.UsageError(
                f"smart_rerun {field} for {item.nodeid} must be an integer."
            ) from None

    @staticmethod
    def _coerce_float(value: object, field: str, item: Item) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            raise pytest.UsageError(
                f"smart_rerun {field} for {item.nodeid} must be a number."
            ) from None

    @staticmethod
    def _extract_marker_max(marker: pytest.Mark, item: Item) -> int:
        if marker.args:
            if len(marker.args) > 1:
                raise pytest.UsageError(
                    f"smart_rerun marker on {item.nodeid} accepts at most one positional argument."
                )
            return marker.args[0]
        return marker.kwargs.get("max")

    @staticmethod
    def _extract_marker_delay(marker: pytest.Mark) -> float:
        return marker.kwargs.get("delay", 0.0)

    @staticmethod
    def _should_retry(reports: Iterable[TestReport]) -> bool:
        for report in reports:
            if report.failed and report.when in {"setup", "call"}:
                return True
        return False

    @staticmethod
    def _mark_reports_as_rerun(
        reports: Iterable[TestReport], attempt: int, max_attempts: int
    ) -> None:
        for report in reports:
            if report.failed:
                report.outcome = "rerun"
                report.wasxfail = ""
                report.longrepr = f"RERUN (attempt {attempt}/{max_attempts})"


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("smart-rerun")
    group.addoption(
        "--smart-rerun",
        action="store_true",
        dest="smart_rerun",
        help="Enable intelligent retries for flaky tests.",
    )
    group.addoption(
        "--smart-rerun-max",
        action="store",
        type=int,
        dest="smart_rerun_max",
        default=2,
        metavar="N",
        help="Maximum number of total attempts per test when smart rerun is enabled (default: 2).",
    )
    group.addoption(
        "--smart-rerun-delay",
        action="store",
        type=float,
        dest="smart_rerun_delay",
        default=0.0,
        metavar="SECONDS",
        help="Delay in seconds between retry attempts (default: 0).",
    )


def pytest_configure(config: Config) -> None:
    config.addinivalue_line(
        "markers",
        "smart_rerun(max=2, delay=0.0, enabled=True): customize smart rerun behaviour for a test.",
    )
    plugin = SmartRerunPlugin(config)
    config._smart_rerun_plugin = plugin  # type: ignore[attr-defined]
    config.pluginmanager.register(plugin, "smart-rerun-plugin")


def pytest_unconfigure(config: Config) -> None:
    plugin = getattr(config, "_smart_rerun_plugin", None)
    if plugin is not None:
        config.pluginmanager.unregister(plugin)
        delattr(config, "_smart_rerun_plugin")
