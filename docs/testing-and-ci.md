# Testing and CI

## Local Tests

Install the package with test dependencies:

```bash
python -m pip install -e ".[test]"
```

Run tests:

```bash
python -m pytest
```

The project requires Python 3.10 or newer in `pyproject.toml`.

## CI

GitHub Actions workflow:

```text
.github/workflows/tests.yml
```

The workflow runs on:

- pull requests
- pushes to `main`
- pushes to `master`

It tests Python 3.10 and 3.11 by installing the package with `.[test]` and running `python -m pytest`.

## Current Test Coverage

The test suite covers:

- document iteration, extension filtering, empty documents, and unsupported extensions
- prompt loading and prompt override directories
- JSON extraction from model responses
- intake-agent fallback behavior
- capability matching
- collaboration risk detection
- VISS rubric assessment parsing and fallback behavior
- scorecard behavior
- folder analysis orchestration and per-document failures
- CLI defaults and output writing
- profile summary rendering

## Adding Tests

Guidelines:

- Prefer unit tests with fake `run_chat` callables instead of live model calls.
- Test prompt contracts by checking required filenames and key fields, not generated prose.
- Keep CLI tests focused on argument behavior and output files.
- Add regression tests when changing dataclass fields or JSON schemas.
- Add one test for every new deterministic agent or fallback path.

## Model Calls In Tests

Tests should not call the real LiteLLM proxy or OpenAI API. For model-backed agents, pass fake functions that return deterministic JSON strings.

Example:

```python
def fake_run_chat(messages, temperature):
    return '{"title": "Example EOI", "software_objectives": ["Build a workflow"]}'
```

