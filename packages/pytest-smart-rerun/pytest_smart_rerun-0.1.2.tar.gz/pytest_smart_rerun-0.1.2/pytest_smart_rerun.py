"""
pytest-smart-rerun: lightweight Pytest plugin for retrying flaky tests.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import time
import urllib.error
import urllib.request
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

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
    backoff: str
    error_filters: Tuple[str, ...]


@dataclass
class SmartRerunAIConfig:
    enabled: bool
    endpoint: Optional[str]
    api_key: Optional[str]
    timeout: float
    cache_path: Optional[Path]
    report_path: Optional[Path]
    redact: bool


@dataclass
class SmartRerunAIResult:
    category: str
    confidence: float
    suggested_action: str
    delay_override: Optional[float] = None
    notes: Optional[str] = None


class SmartRerunAIClient:
    """Handles communication with MCP endpoints (or heuristic fallback) plus caching."""

    def __init__(
        self,
        config: SmartRerunAIConfig,
        terminal_reporter,
    ) -> None:
        self.config = config
        self.terminal_reporter = terminal_reporter
        self._cache: Dict[str, dict] = {}
        self._cache_loaded = False
        if config.enabled and config.cache_path:
            self._load_cache()

    def analyze_failure(self, payload: dict) -> Optional[SmartRerunAIResult]:
        if not self.config.enabled:
            return None

        cache_key = self._cache_key(payload)
        cached = self._cache.get(cache_key)
        if cached:
            return self._build_result(cached, source="cache")

        if self.config.endpoint:
            response = self._call_remote(payload)
        else:
            response = self._heuristic_response(payload)

        if response is None:
            return None

        self._cache[cache_key] = response
        self._persist_cache()
        return self._build_result(response, source="fresh")

    def _call_remote(self, payload: dict) -> Optional[dict]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        request = urllib.request.Request(
            self.config.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                data = response.read().decode("utf-8")
                return json.loads(data or "{}")
        except urllib.error.URLError as exc:
            self._notify(f"MCP request failed: {exc}", level="red")
        except json.JSONDecodeError as exc:
            self._notify(f"MCP response was not valid JSON: {exc}", level="red")
        return None

    @staticmethod
    def _heuristic_response(payload: dict) -> dict:
        """Fallback heuristic when no endpoint is configured."""
        failures = payload.get("failures", [])
        category = "unknown"
        confidence = 0.25
        suggestion = "retry_with_delay(1s)"
        delay = 1.0
        notes: List[str] = []

        for failure in failures:
            exc = (failure.get("exception") or "").lower()
            message = (failure.get("message") or "").lower()
            if "timeout" in exc or "timeout" in message:
                category = "flaky-network"
                confidence = 0.85
                suggestion = "retry_with_delay(2s)"
                delay = 2.0
                notes.append("Detected timeout signature; suggesting cautious retry.")
                break
            if "connection" in exc or "connection" in message:
                category = "environmental"
                confidence = 0.7
                suggestion = "retry_with_delay(1.5s)"
                delay = 1.5
                notes.append("Connection failure is often transient in CI.")
                break
            if "assert" in exc or "assert" in message:
                category = "deterministic"
                confidence = 0.9
                suggestion = "stop_retry"
                delay = 0.0
                notes.append("Assertion-based failure likely deterministic.")
                break
            if "valueerror" in exc or "typeerror" in exc:
                category = "deterministic"
                confidence = 0.8
                suggestion = "stop_retry"
                delay = 0.0
                notes.append("Immediate data validation failure.")
                break
        else:
            notes.append("No heuristics matched; defaulting to cautious retry.")

        return {
            "category": category,
            "confidence": confidence,
            "suggested_action": suggestion,
            "delay_override": delay,
            "notes": notes,
        }

    def _build_result(self, response: dict, source: str) -> SmartRerunAIResult:
        category = str(response.get("category", "unknown"))
        confidence = float(response.get("confidence", 0.0))
        suggested_action = str(response.get("suggested_action", "retry_with_delay(1s)"))
        delay_override = response.get("delay_override")
        if isinstance(delay_override, str):
            try:
                delay_override = float(delay_override)
            except ValueError:
                delay_override = None
        elif isinstance(delay_override, (int, float)):
            delay_override = float(delay_override)
        else:
            delay_override = None

        notes = response.get("notes")
        if isinstance(notes, list):
            notes = " ".join(str(n) for n in notes if n)
        elif isinstance(notes, dict):
            notes = json.dumps(notes)
        elif notes is not None:
            notes = str(notes)

        if source == "cache":
            self._notify("AI analysis served from cache", level="blue")

        return SmartRerunAIResult(
            category=category,
            confidence=confidence,
            suggested_action=suggested_action,
            delay_override=delay_override,
            notes=notes,
        )

    def _cache_key(self, payload: dict) -> str:
        fingerprint = payload.get("fingerprint")
        if not fingerprint:
            fingerprint = json.dumps(payload.get("failures", []), sort_keys=True)
        return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()

    def _load_cache(self) -> None:
        if self._cache_loaded or not self.config.cache_path:
            return
        try:
            if self.config.cache_path.exists():
                data = json.loads(self.config.cache_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    self._cache = data
        except (OSError, json.JSONDecodeError) as exc:
            self._notify(f"Could not load AI cache: {exc}", level="red")
        finally:
            self._cache_loaded = True

    def _persist_cache(self) -> None:
        if not self.config.cache_path:
            return
        try:
            self.config.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.config.cache_path.write_text(json.dumps(self._cache, indent=2), encoding="utf-8")
        except OSError as exc:
            self._notify(f"Failed to persist AI cache: {exc}", level="red")

    def flush(self) -> None:
        self._persist_cache()

    def _notify(self, message: str, *, level: str = "yellow") -> None:
        if self.terminal_reporter is None:
            warnings.warn(message, RuntimeWarning, stacklevel=3)
            return
        kwargs = {level: True} if level in {"red", "green", "yellow", "blue"} else {}
        self.terminal_reporter.write_line(f"[smart-rerun AI] {message}", **kwargs)

class SmartRerunPlugin:
    """Coordinates retry attempts for flaky tests."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.enabled_flag = self._resolve_enabled_flag()
        self.default_max_attempts = self._resolve_int_option("smart_rerun_max", default=2)
        self.default_delay = self._resolve_float_option("smart_rerun_delay", default=0.0)
        self.backoff_mode = self._resolve_backoff_option()
        self.retry_error_names = self._resolve_error_filters()
        self.report_path = self._resolve_report_path()
        self.ai_config = self._resolve_ai_config()
        self.terminal_reporter = config.pluginmanager.get_plugin("terminalreporter")
        self._report_entries: List[dict] = []
        self._ai_entries: List[dict] = []
        self._session_stats = {
            "total": 0,
            "retried": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "retried_passed": 0,
            "retried_failed": 0,
        }
        self.ai_client = SmartRerunAIClient(self.ai_config, self.terminal_reporter)

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
        attempt_records: List[dict] = []
        final_outcome = "passed"
        latest_ai_result: Optional[SmartRerunAIResult] = None
        for attempt in range(1, settings.max_attempts + 1):
            self._log_attempt(item, attempt, settings.max_attempts)
            item.ihook.pytest_runtest_logstart(nodeid=nodeid, location=item.location)
            reports = runtestprotocol(item, nextitem=nextitem, log=False)

            failures = self._collect_failure_info(reports)
            should_retry = self._should_retry(failures, settings)
            ai_result = self._maybe_analyze_with_ai(
                item=item,
                attempt=attempt,
                settings=settings,
                failures=failures,
                reports=reports,
            )
            final_outcome = self._final_outcome(reports)

            ai_delay_override: Optional[float] = None
            if ai_result is not None:
                latest_ai_result = ai_result
                ai_delay_override = ai_result.delay_override
                self._handle_ai_outcome(ai_result)
                if ai_result.suggested_action == "stop_retry":
                    should_retry = False
                elif ai_result.suggested_action.startswith("retry_with_delay"):
                    should_retry = True
                    if ai_delay_override is None:
                        ai_delay_override = self._extract_delay_from_suggestion(
                            ai_result.suggested_action
                        )
                elif ai_result.suggested_action == "skip_test":
                    should_retry = False

            if failures:
                attempt_records.append(
                    {
                        "attempt": attempt,
                        "stage_failures": failures,
                        "outcome": final_outcome,
                    }
                )

            if should_retry and attempt < settings.max_attempts:
                self._mark_reports_as_rerun(reports, attempt, settings.max_attempts)
                self._emit_reports(item, reports)
                item.ihook.pytest_runtest_logfinish(nodeid=nodeid, location=item.location)
                delay_seconds = self._next_delay(settings, attempt + 1)
                if ai_delay_override is not None:
                    delay_seconds = ai_delay_override
                if delay_seconds > 0:
                    self._log_backoff(item, attempt + 1, delay_seconds, settings.backoff)
                    time.sleep(delay_seconds)
                continue

            self._emit_reports(item, reports)
            item.ihook.pytest_runtest_logfinish(nodeid=nodeid, location=item.location)
            break

        self._record_test_result(
            nodeid=nodeid,
            attempts_run=attempt,
            final_outcome=final_outcome,
            attempt_records=attempt_records,
            settings=settings,
            ai_result=latest_ai_result,
        )
        return True

    def pytest_report_teststatus(self, report: TestReport):
        if report.outcome == "rerun":
            return "rerun", "R", ("RERUN", {"yellow": True})

    def pytest_terminal_summary(self, terminalreporter) -> None:
        total = self._session_stats["total"]
        if total == 0:
            return

        terminalreporter.section("smart rerun summary", sep="=")
        stats = self._session_stats
        terminalreporter.write_line(f"monitored tests: {total}", bold=True)

        if stats["retried"] == 0:
            terminalreporter.write_line("no retries were triggered 🎉", green=True)
        else:
            terminalreporter.write_line(
                f"retries: {stats['retried']} "
                f"(passed after retry: {stats['retried_passed']}, "
                f"failed after retries: {stats['retried_failed']})",
                yellow=True,
            )

        if stats["failed"] > 0:
            terminalreporter.write_line(
                f"final failures: {stats['failed']}", red=True
            )
        if stats["skipped"] > 0:
            terminalreporter.write_line(f"skipped: {stats['skipped']}", cyan=True)

        reruns = terminalreporter.stats.get("rerun")
        if reruns:
            terminalreporter.write_line("rerun details:", bold=True)
            for report in reruns:
                terminalreporter.write_line(f" - {report.nodeid}", yellow=True)

        if self.report_path and self._report_entries:
            terminalreporter.write_line(
                f"analytics report written to {self.report_path}", blue=True
            )
        if self.ai_config.report_path and self._ai_entries:
            terminalreporter.write_line(
                f"AI insights appended to {self.ai_config.report_path}", blue=True
            )
        if self._ai_entries:
            terminalreporter.write_line("AI classifications:", bold=True)
            for entry in self._ai_entries:
                terminalreporter.write_line(
                    f" - {entry['nodeid']} -> {entry['category']}"
                    f" ({entry['confidence']:.2f}) action={entry['suggested_action']}",
                    cyan=True,
                )

    def pytest_sessionfinish(self, session, exitstatus) -> None:
        if self.report_path and self._report_entries:
            self._write_report()
        if self.ai_config.enabled:
            self.ai_client.flush()

    # ----------------------------
    # Helper methods
    # ----------------------------

    def _settings_for(self, item: Item) -> SmartRerunSettings:
        marker = item.get_closest_marker("smart_rerun")

        enabled = bool(self.enabled_flag)
        max_attempts = self.default_max_attempts
        delay = self.default_delay
        backoff = self.backoff_mode
        error_filters: Sequence[str] = self.retry_error_names

        if marker is not None:
            default_enabled = enabled if enabled else True
            enabled = marker.kwargs.get("enabled", default_enabled)
            if marker.args:
                if len(marker.args) > 1:
                    raise pytest.UsageError(
                        f"smart_rerun marker on {item.nodeid} accepts at most one positional argument."
                    )
                # Positional argument is treated as max attempts.
                max_attempts = marker.args[0]
            max_attempts = marker.kwargs.get("max", max_attempts)
            delay = marker.kwargs.get("delay", delay)
            backoff = marker.kwargs.get("backoff", backoff)
            if "errors" in marker.kwargs:
                error_filters = self._parse_error_filters(marker.kwargs["errors"])

        max_attempts = self._coerce_int(max_attempts, field="max_attempts", item=item)
        delay = self._coerce_float(delay, field="delay", item=item)
        backoff = self._coerce_backoff(backoff, item=item)
        error_filters = tuple(self._parse_error_filters(error_filters))

        if enabled not in (True, False):
            raise pytest.UsageError(
                f"smart_rerun enabled flag for {item.nodeid} must be either True or False."
            )

        if enabled:
            self._validate_attempts(max_attempts, source=item.nodeid)
            self._validate_delay(delay, source=item.nodeid)

        return SmartRerunSettings(
            enabled=bool(enabled),
            max_attempts=max_attempts,
            delay=delay,
            backoff=backoff,
            error_filters=error_filters,
        )

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

    def _record_test_result(
        self,
        *,
        nodeid: str,
        attempts_run: int,
        final_outcome: str,
        attempt_records: Sequence[dict],
        settings: SmartRerunSettings,
        ai_result: Optional[SmartRerunAIResult],
    ) -> None:
        had_retry = attempts_run > 1
        self._session_stats["total"] += 1
        if final_outcome == "passed":
            self._session_stats["passed"] += 1
            if had_retry:
                self._session_stats["retried_passed"] += 1
        elif final_outcome == "failed":
            self._session_stats["failed"] += 1
            if had_retry:
                self._session_stats["retried_failed"] += 1
        elif final_outcome == "skipped":
            self._session_stats["skipped"] += 1

        if had_retry:
            self._session_stats["retried"] += 1

        report_entry = {
            "nodeid": nodeid,
            "attempts": attempts_run,
            "max_attempts": settings.max_attempts,
            "backoff": settings.backoff,
            "base_delay": settings.delay,
            "error_filters": list(settings.error_filters),
            "final_outcome": final_outcome,
            "reruns": list(attempt_records),
        }

        if ai_result is not None:
            report_entry["ai"] = {
                "category": ai_result.category,
                "confidence": ai_result.confidence,
                "suggested_action": ai_result.suggested_action,
                "delay_override": ai_result.delay_override,
                "notes": ai_result.notes,
            }
            self._ai_entries.append(
                {
                    "nodeid": nodeid,
                    "category": ai_result.category,
                    "confidence": ai_result.confidence,
                    "suggested_action": ai_result.suggested_action,
                    "notes": ai_result.notes,
                }
            )

        if self.report_path:
            self._report_entries.append(report_entry)

        if self.ai_config.report_path and ai_result is not None:
            ai_entry = dict(report_entry)
            ai_entry.pop("reruns", None)
            self._append_ai_report(ai_entry)

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

    def _collect_failure_info(self, reports: Iterable[TestReport]) -> List[dict]:
        failures: List[dict] = []
        for report in reports:
            if not report.failed:
                continue
            failures.append(
                {
                    "stage": report.when,
                    "exception": self._exception_name(report),
                    "message": self._failure_message(report),
                }
            )
        return failures

    def _should_retry(self, failures: Sequence[dict], settings: SmartRerunSettings) -> bool:
        if not failures:
            return False

        retry_candidates = [
            failure for failure in failures if failure["stage"] in {"setup", "call"}
        ]
        if not retry_candidates:
            return False

        if not settings.error_filters:
            return True

        for failure in retry_candidates:
            if self._matches_error_filter(failure, settings.error_filters):
                return True
        return False

    @staticmethod
    def _final_outcome(reports: Iterable[TestReport]) -> str:
        for report in reversed(list(reports)):
            if report.when in {"call", "setup", "teardown"}:
                return report.outcome
        return "passed"

    @staticmethod
    def _failure_message(report: TestReport) -> str:
        longreprtext = getattr(report, "longreprtext", None)
        if longreprtext:
            return longreprtext.strip()
        longrepr = getattr(report, "longrepr", None)
        if longrepr:
            return str(longrepr)
        return report.outcome

    @staticmethod
    def _exception_name(report: TestReport) -> str:
        longrepr = getattr(report, "longrepr", None)
        if longrepr is None:
            return ""
        reprcrash = getattr(longrepr, "reprcrash", None)
        if reprcrash:
            excname = getattr(reprcrash, "excname", None)
            if excname:
                return excname
            message = getattr(reprcrash, "message", "")
            if message:
                return message.split(":", 1)[0].strip()
        return ""

    @staticmethod
    def _matches_error_filter(failure: dict, filters: Sequence[str]) -> bool:
        exception_name = failure.get("exception", "") or ""
        message = failure.get("message", "") or ""
        exc_lower = exception_name.lower()
        msg_lower = message.lower()
        for raw_filter in filters:
            candidate = raw_filter.lower()
            if not candidate:
                continue
            if exc_lower.endswith(candidate) or exc_lower == candidate:
                return True
            if candidate in msg_lower:
                return True
        return False

    @staticmethod
    def _next_delay(settings: SmartRerunSettings, next_attempt: int) -> float:
        if settings.delay <= 0:
            return 0.0
        if settings.backoff == "linear":
            return settings.delay * max(1, next_attempt - 1)
        if settings.backoff == "exp":
            exponent = max(0, next_attempt - 2)
            return settings.delay * (2 ** exponent)
        return settings.delay

    def _log_backoff(
        self, item: Item, attempt: int, delay_seconds: float, backoff: str
    ) -> None:
        if self.terminal_reporter is None:
            return
        strategy = "constant" if backoff == "none" else backoff
        self.terminal_reporter.write_line(
            f"[smart-rerun] waiting {delay_seconds:.3f}s before attempt {attempt} ({strategy} backoff)"
        )

    def _maybe_analyze_with_ai(
        self,
        *,
        item: Item,
        attempt: int,
        settings: SmartRerunSettings,
        failures: Sequence[dict],
        reports: Sequence[TestReport],
    ) -> Optional[SmartRerunAIResult]:
        if not failures or not self.ai_config.enabled:
            return None

        environment = {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pytest": pytest.__version__,
        }
        payload = {
            "nodeid": item.nodeid,
            "attempt": attempt,
            "max_attempts": settings.max_attempts,
            "failures": failures,
            "environment": environment,
            "config": {
                "delay": settings.delay,
                "backoff": settings.backoff,
                "error_filters": list(settings.error_filters),
            },
            "fingerprint": self._ai_fingerprint(item, failures),
        }

        if self.ai_config.redact:
            payload = self._redact_payload(payload)

        result = self.ai_client.analyze_failure(payload)
        if result is None:
            return None

        self._notify_ai_summary(item.nodeid, result)
        return result

    def _handle_ai_outcome(self, result: SmartRerunAIResult) -> None:
        if not self.terminal_reporter:
            return
        action = result.suggested_action
        message = (
            f"AI classification: {result.category} (confidence {result.confidence:.2f}) -> {action}"
        )
        self.terminal_reporter.write_line(f"[smart-rerun AI] {message}", cyan=True)
        if result.notes:
            self.terminal_reporter.write_line(
                f"[smart-rerun AI] notes: {result.notes}", blue=True
            )

    @staticmethod
    def _extract_delay_from_suggestion(action: str) -> Optional[float]:
        if "(" not in action or ")" not in action:
            return None
        try:
            inside = action.split("(", 1)[1].split(")", 1)[0]
            if inside.endswith("s"):
                inside = inside[:-1]
            return float(inside)
        except (IndexError, ValueError):
            return None

    def _ai_fingerprint(self, item: Item, failures: Sequence[dict]) -> str:
        key_parts = [item.nodeid]
        for failure in failures:
            key_parts.append(failure.get("stage", ""))
            key_parts.append(failure.get("exception", ""))
            key_parts.append(failure.get("message", ""))
        return "|".join(key_parts)

    @staticmethod
    def _redact_payload(payload: dict) -> dict:
        redacted = dict(payload)
        failures = []
        for failure in payload.get("failures", []):
            trimmed = dict(failure)
            message = trimmed.get("message")
            if isinstance(message, str) and len(message) > 512:
                trimmed["message"] = message[:512] + "... [redacted]"
            failures.append(trimmed)
        redacted["failures"] = failures
        return redacted

    def _notify_ai_summary(self, nodeid: str, result: SmartRerunAIResult) -> None:
        if self.terminal_reporter is None:
            return
        self.terminal_reporter.write_line(
            f"[smart-rerun AI] {nodeid} categorised as {result.category}"
        )

    @staticmethod
    def _mark_reports_as_rerun(
        reports: Iterable[TestReport], attempt: int, max_attempts: int
    ) -> None:
        for report in reports:
            if report.failed:
                report.outcome = "rerun"
                report.wasxfail = ""
                report.longrepr = f"RERUN (attempt {attempt}/{max_attempts})"

    def _resolve_enabled_flag(self) -> bool:
        cli_enabled = self.config.getoption("smart_rerun")
        if cli_enabled:
            return True
        ini_enabled = self._get_ini_bool("smart_rerun")
        return ini_enabled

    def _resolve_int_option(self, name: str, default: int) -> int:
        cli_value = self.config.getoption(name)
        if cli_value is not None:
            return cli_value
        ini_value = str(self.config.getini(name)).strip()
        if ini_value == "":
            return default
        try:
            return int(ini_value)
        except (TypeError, ValueError):
            raise pytest.UsageError(
                f"pytest.ini option {name} must be an integer, got {ini_value!r}"
            ) from None

    def _resolve_float_option(self, name: str, default: float) -> float:
        cli_value = self.config.getoption(name)
        if cli_value is not None:
            return float(cli_value)
        ini_value = str(self.config.getini(name)).strip()
        if ini_value == "":
            return default
        try:
            return float(ini_value)
        except (TypeError, ValueError):
            raise pytest.UsageError(
                f"pytest.ini option {name} must be a number, got {ini_value!r}"
            ) from None

    def _resolve_backoff_option(self) -> str:
        cli_value = self.config.getoption("smart_rerun_backoff")
        if cli_value:
            return cli_value
        ini_value = str(self.config.getini("smart_rerun_backoff")).strip().lower()
        if ini_value in {"", "none"}:
            return "none"
        if ini_value not in {"linear", "exp"}:
            raise pytest.UsageError(
                "pytest.ini option smart_rerun_backoff must be one of: none, linear, exp."
            )
        return ini_value

    def _resolve_error_filters(self) -> Tuple[str, ...]:
        cli_value = self.config.getoption("smart_rerun_errors")
        if cli_value is None:
            ini_value = self.config.getini("smart_rerun_errors")
            return tuple(self._parse_error_filters(ini_value))
        return tuple(self._parse_error_filters(cli_value))

    def _resolve_report_path(self) -> Optional[Path]:
        cli_value = self.config.getoption("smart_rerun_report")
        if cli_value:
            return Path(cli_value)
        ini_value = str(self.config.getini("smart_rerun_report")).strip()
        if ini_value:
            return Path(ini_value)
        return None

    def _resolve_ai_config(self) -> SmartRerunAIConfig:
        enabled = self._interpret_bool(self.config.getoption("smart_rerun_ai"))
        if not enabled:
            enabled = self._interpret_bool(self.config.getini("smart_rerun_ai"))

        endpoint = self.config.getoption("smart_rerun_ai_endpoint")
        if not endpoint:
            endpoint = str(self.config.getini("smart_rerun_ai_endpoint")).strip() or None

        api_key = self.config.getoption("smart_rerun_ai_token")
        if not api_key:
            api_key = os.getenv("SMART_RERUN_AI_TOKEN")
            if not api_key:
                api_key = str(self.config.getini("smart_rerun_ai_token")).strip() or None

        timeout_opt = self.config.getoption("smart_rerun_ai_timeout")
        if timeout_opt is None:
            timeout_ini = str(self.config.getini("smart_rerun_ai_timeout")).strip()
            timeout_opt = float(timeout_ini) if timeout_ini else 5.0
        timeout = float(timeout_opt)

        cache = self.config.getoption("smart_rerun_ai_cache")
        if not cache:
            cache = str(self.config.getini("smart_rerun_ai_cache")).strip() or None
        cache_path = Path(cache) if cache else None

        report = self.config.getoption("smart_rerun_ai_report")
        if not report:
            report = str(self.config.getini("smart_rerun_ai_report")).strip() or None
        report_path = Path(report) if report else None

        redact = self._interpret_bool(self.config.getoption("smart_rerun_ai_redact"))
        if not redact:
            redact = self._interpret_bool(self.config.getini("smart_rerun_ai_redact"))

        return SmartRerunAIConfig(
            enabled=enabled,
            endpoint=endpoint,
            api_key=api_key,
            timeout=timeout,
            cache_path=cache_path,
            report_path=report_path,
            redact=redact,
        )

    def _get_ini_bool(self, name: str) -> bool:
        raw_value = self.config.getini(name)
        return self._interpret_bool(raw_value)

    @staticmethod
    def _interpret_bool(value: object) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _parse_error_filters(value: object) -> Tuple[str, ...]:
        if value is None:
            return ()
        if isinstance(value, (list, tuple, set)):
            items = value
        else:
            items = str(value).split(",")
        return tuple(
            part.strip() for part in items if isinstance(part, str) and part.strip()
        )

    @staticmethod
    def _coerce_backoff(value: object, item: Item) -> str:
        if value is None:
            return "none"
        normalized = str(value).strip().lower()
        if normalized in {"none", ""}:
            return "none"
        if normalized not in {"linear", "exp"}:
            raise pytest.UsageError(
                f"smart_rerun backoff for {item.nodeid} must be one of: none, linear, exp."
            )
        return normalized

    def _write_report(self) -> None:
        if self.report_path is None:
            return
        payload = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "results": self._report_entries,
        }
        path = Path(self.report_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as exc:
            message = f"[smart-rerun] failed to write report to {path}: {exc}"
            if self.terminal_reporter is not None:
                self.terminal_reporter.write_line(message, red=True)
            else:
                warnings.warn(message, RuntimeWarning, stacklevel=2)

    def _append_ai_report(self, entry: dict) -> None:
        path = self.ai_config.report_path
        if path is None:
            return
        try:
            existing = []
            if path.exists():
                existing = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(existing, list):
                    existing = []
            existing.append(entry)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        except (OSError, json.JSONDecodeError) as exc:
            message = f"[smart-rerun AI] failed to update AI report {path}: {exc}"
            if self.terminal_reporter is not None:
                self.terminal_reporter.write_line(message, red=True)
            else:
                warnings.warn(message, RuntimeWarning, stacklevel=2)


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
        default=None,
        metavar="N",
        help="Maximum number of total attempts per test when smart rerun is enabled (default: 2).",
    )
    group.addoption(
        "--smart-rerun-delay",
        action="store",
        type=float,
        dest="smart_rerun_delay",
        default=None,
        metavar="SECONDS",
        help="Delay in seconds between retry attempts (default: 0).",
    )
    group.addoption(
        "--smart-rerun-backoff",
        action="store",
        dest="smart_rerun_backoff",
        choices=("linear", "exp", "none"),
        default=None,
        help="Backoff strategy applied to delays between retries (options: none, linear, exp).",
    )
    group.addoption(
        "--smart-rerun-errors",
        action="store",
        dest="smart_rerun_errors",
        default=None,
        help="Comma-separated list of exception names that qualify for smart reruns.",
    )
    group.addoption(
        "--smart-rerun-report",
        action="store",
        dest="smart_rerun_report",
        default=None,
        metavar="PATH",
        help="File path to write JSON analytics for smart reruns.",
    )
    group.addoption(
        "--smart-rerun-ai",
        action="store_true",
        dest="smart_rerun_ai",
        default=False,
        help="Enable MCP-assisted AI analysis for failures.",
    )
    group.addoption(
        "--smart-rerun-ai-endpoint",
        action="store",
        dest="smart_rerun_ai_endpoint",
        default=None,
        help="MCP endpoint URL used for AI analysis (HTTPS).",
    )
    group.addoption(
        "--smart-rerun-ai-token",
        action="store",
        dest="smart_rerun_ai_token",
        default=None,
        help="API token used when authenticating against the MCP endpoint.",
    )
    group.addoption(
        "--smart-rerun-ai-timeout",
        action="store",
        dest="smart_rerun_ai_timeout",
        default=None,
        help="Timeout (seconds) for MCP requests (default: 5).",
    )
    group.addoption(
        "--smart-rerun-ai-cache",
        action="store",
        dest="smart_rerun_ai_cache",
        default=None,
        help="Path to cache AI analysis responses for offline reuse.",
    )
    group.addoption(
        "--smart-rerun-ai-report",
        action="store",
        dest="smart_rerun_ai_report",
        default=None,
        help="Optional JSON file to append AI classifications per test.",
    )
    group.addoption(
        "--smart-rerun-ai-redact",
        action="store_true",
        dest="smart_rerun_ai_redact",
        default=False,
        help="Redact failure payloads before sending to the MCP endpoint.",
    )

    parser.addini("smart_rerun", "Enable smart reruns by default.", default="false")
    parser.addini("smart_rerun_max", "Default maximum attempts for smart reruns.", default="2")
    parser.addini("smart_rerun_delay", "Default base delay in seconds between attempts.", default="0.0")
    parser.addini("smart_rerun_backoff", "Delay backoff strategy: none, linear, exp.", default="none")
    parser.addini(
        "smart_rerun_errors",
        "Comma-separated exception names that qualify for smart reruns.",
        default="",
    )
    parser.addini(
        "smart_rerun_report",
        "Output path for smart rerun analytics report.",
        default="",
    )
    parser.addini("smart_rerun_ai", "Enable smart rerun AI analysis by default.", default="false")
    parser.addini("smart_rerun_ai_endpoint", "Default MCP endpoint for smart rerun AI.", default="")
    parser.addini("smart_rerun_ai_token", "API token for MCP endpoint.", default="")
    parser.addini("smart_rerun_ai_timeout", "Timeout in seconds for AI requests.", default="5.0")
    parser.addini("smart_rerun_ai_cache", "Cache file for AI analysis responses.", default="")
    parser.addini("smart_rerun_ai_report", "AI-focused analytics output path.", default="")
    parser.addini(
        "smart_rerun_ai_redact",
        "Redact payloads before they are sent to MCP endpoints.",
        default="false",
    )


def pytest_configure(config: Config) -> None:
    config.addinivalue_line(
        "markers",
        "smart_rerun(max=2, delay=0.0, backoff='none', errors=(), enabled=True): customize smart rerun behaviour for a test.",
    )
    plugin = SmartRerunPlugin(config)
    config._smart_rerun_plugin = plugin  # type: ignore[attr-defined]
    config.pluginmanager.register(plugin, "smart-rerun-plugin")


def pytest_unconfigure(config: Config) -> None:
    plugin = getattr(config, "_smart_rerun_plugin", None)
    if plugin is not None:
        config.pluginmanager.unregister(plugin)
        delattr(config, "_smart_rerun_plugin")
