# AGENTS.md

## Project Context

Near-Earth Object Monitor is a small Python CLI that fetches NASA NEO Feed data and prints a terminal summary.

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

## Checks

Run these before committing:

```bash
uv run python -m pytest
uv run ruff format --check .
uv run ruff check .
uv run mypy src
```
