# pytest-smart-rerun

[![PyPI](https://img.shields.io/pypi/v/pytest-smart-rerun.svg)](https://pypi.org/project/pytest-smart-rerun/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`pytest-smart-rerun` is a lightweight Pytest plugin that retries flaky tests with configurable attempts and delays. It integrates directly with Pytest's hook system, requires no external dependencies, and works out of the box from the command line or via per-test decorators.

## Installation

```bash
pip install pytest-smart-rerun
```

For local development:

```bash
git clone https://github.com/Aki-07/pytest-smart-rerun.git
cd pytest-smart-rerun
pip install -e .
```

## Quick start

Retry all failing tests up to three times with a one second delay:

```bash
pytest --smart-rerun --smart-rerun-max=3 --smart-rerun-delay=1
```

Use the `smart_rerun` marker to target specific flaky tests:

```python
import pytest


@pytest.mark.smart_rerun(max=4, delay=0.5)
def test_eventually_consistent_service(client):
    response = client.read_state()
    assert response.status_code == 200
```

Combine both for a default retry policy with test-level overrides.

## CLI options

- `--smart-rerun`: enable smart reruns for the test session.
- `--smart-rerun-max=N`: set the total number of attempts per test (default: 2).
- `--smart-rerun-delay=SECONDS`: add a delay between retries (default: 0).
- `--smart-rerun-backoff=linear|exp|none`: apply linear or exponential backoff to delay intervals.
- `--smart-rerun-errors=name1,name2`: only retry failures whose exception names match the allow-list.
- `--smart-rerun-report=PATH`: write structured JSON analytics for downstream dashboards or triage tooling.
- `--smart-rerun-ai`: enable MCP-powered AI analysis to classify failures and adapt retry behaviour.
- `--smart-rerun-ai-report=PATH`: append AI classifications and suggested actions to a JSON artifact.

Invalid values raise a Pytest `UsageError`, keeping failure feedback obvious.

## Configuration via pytest.ini

All CLI options have config equivalents so you can bake defaults into your repository:

```ini
[pytest]
smart_rerun = true
smart_rerun_max = 3
smart_rerun_delay = 0.5
smart_rerun_backoff = exp
smart_rerun_errors = TimeoutError,ConnectionError
smart_rerun_report = reports/smart_rerun.json
smart_rerun_ai = true
smart_rerun_ai_endpoint = https://mcp.example.com/analyze
smart_rerun_ai_token = {{ env:SMART_RERUN_AI_TOKEN }}
smart_rerun_ai_report = reports/smart_rerun_ai.json
smart_rerun_ai_cache = .cache/smart_rerun_ai.json
smart_rerun_ai_redact = true
```

## Features

- Intelligent reruns driven purely by Pytest hooks—no external dependencies.
- Automatic attempt logging with rerun-aware, colourised terminal summaries ready for CI.
- Per-test overrides through `@pytest.mark.smart_rerun(max=..., delay=..., backoff=..., errors=...)`.
- Linear or exponential backoff strategies that cooperate with scripted delays.
- Exception-aware filtering so only flaky categories (e.g. timeouts) trigger reruns.
- Structured JSON analytics for dashboards or historical insights via `--smart-rerun-report`.
- AI-assisted classification that adjusts retry strategy on the fly (delay overrides, early exits, rich reporting).
- Works alongside existing Pytest plugins and respects fixture/state isolation.

## AI-powered smart reruns

Turn on the MCP-backed engine with either `--smart-rerun-ai` or `smart_rerun_ai = true`. When a test fails, the plugin gathers the stack trace, exception metadata, and retry configuration, then:

- Sends it to the configured MCP endpoint (or falls back to built-in heuristics when offline).
- Classifies the failure (`flaky-network`, `deterministic`, `environmental`, …) with a confidence score.
- Adapts the retry policy dynamically—e.g. `retry_with_delay(2s)` for network blips or `stop_retry` for logic bugs.
- Writes rich analytics into the main JSON report and, if configured, an AI-specific trail (`--smart-rerun-ai-report`).

Caching (`--smart-rerun-ai-cache`) avoids duplicate calls, `--smart-rerun-ai-redact` trims overly verbose traces before transmission, and environment variables such as `SMART_RERUN_AI_TOKEN` can feed credentials securely.

## Future roadmap

1. Natural-language retry policies that the MCP agent translates into structured plugin config.
2. Correlating repeated failures across repositories to suggest code-level fixes automatically.
3. Optional dashboards that visualise the JSON analytics over time for QA and release teams.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel
pip install -e .[test]
pytest -v
pytest --smart-rerun --smart-rerun-max=3 --smart-rerun-delay=1 -v
```

## Release workflow

1. `python -m build`
2. `python -m twine check dist/*`
3. `python -m twine upload dist/*`

Refer to [Publishing to PyPI](https://packaging.python.org/tutorials/packaging-projects/) for account setup and API tokens.

## License

MIT © 2025 Akilesh KR. See [LICENSE](LICENSE) for full text.
