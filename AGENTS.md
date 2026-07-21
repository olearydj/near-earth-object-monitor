# AGENTS.md

## Project Context

Near-Earth Object Monitor is a small Python project that fetches and validates
NASA NEO Feed data. It provides a repeatable CLI and a local Streamlit dashboard
over the same trusted workflow.

The project uses a `src/` layout, `uv`, `requests`, `python-dotenv`, Streamlit, `pytest`, Ruff, and mypy.

## Working Guidelines

- Keep command-line behavior small, explicit, and predictable.
- Keep NASA API access in `src/neo_monitor/api.py`.
- Keep command-line orchestration in `src/neo_monitor/cli.py`.
- Keep browser-specific controls and display in `src/neo_monitor/dashboard.py`.
- Keep shared request-to-result coordination in `src/neo_monitor/workflow.py` so the CLI and dashboard use the same trusted project logic.
- Keep parsing, calculations, and formatting helpers in `src/neo_monitor/summarize.py`.
- Prefer pure functions for summary logic.
- Use fixture data for unit tests; unit tests should not call the live NASA API.
- Do not commit `.env`, real API keys, generated data, caches, or `.venv`.
- Add or update tests when behavior changes.
- Add concise docstrings to public modules, classes, and functions. Describe the
  contract, important transformations, and failures rather than restating code.
- Update `README.md` when setup, commands, configuration, or user-visible
  behavior changes.
- Update `docs/data-dictionary.md` when processed fields, units, provenance, or
  transformation rules change.

## Documentation Map

- `README.md`: user and developer entry point; setup, usage, and troubleshooting.
- `docs/index.md`: durable documentation map and maintainer orientation.
- `docs/data-dictionary.md`: processed CSV schema and derivation rules.
- `docs/specs/`: completed sprint requirements and design constraints.
- `tests/`: executable examples of expected behavior and failure handling.
- `logs/` and generated data folders: local runtime evidence, never source of
  truth and never committed.

Keep durable project facts in the files above. Session state and temporary task
notes do not belong in this file.

## Checks

Run these before committing:

```bash
uv run python -m pytest
uv run ruff format --check .
uv run ruff check .
uv run mypy src
```
