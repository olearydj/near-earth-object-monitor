# Sprint 01: First NASA NEO Summary

Near-Earth Object Monitor is a small Python command-line tool for summarizing NASA near-Earth object data.

## Context

Build the first useful version of the project. Keep the scope narrow: one command, one API, one terminal summary, and enough structure to support later changes.

## User Features: What

- A user can run `neo-monitor` from the command line.
- A user can request NASA near-Earth object data for one date or a short date range.
- A user can provide a NASA API key with `NASA_API_KEY`.
- A user can keep local configuration in a `.env` file that is not committed.
- A user sees a readable terminal summary with:
  - total object count
  - potentially hazardous object count
  - closest approach
  - fastest object
  - largest estimated diameter
- A user gets a clear message when the API key is missing or the API request fails.
- A developer can run tests without calling the live NASA API.
- A developer can run formatting, linting, type checking, and package build checks.

## Implementation Plan: How

- Use a `src/` package layout with import package `neo_monitor`.
- Use `uv` for environment management, command execution, locking, and building.
- Use `uv_build` as the build backend.
- Use `requests` for the NASA API request.
- Use `python-dotenv` so local `.env` files work during development.
- Keep live API access in `src/neo_monitor/api.py`.
- Keep command-line parsing and orchestration in `src/neo_monitor/cli.py`.
- Keep data extraction, calculations, and terminal formatting in `src/neo_monitor/summarize.py`.
- Represent the extracted object data and final summary with dataclasses.
- Keep summary logic as pure functions where practical.
- Use pytest fixture data for unit tests.
- Use Ruff for formatting and linting.
- Use mypy for static type checks.

## Tasks

- Create project metadata in `pyproject.toml`.
- Configure the `neo-monitor` console script.
- Add `.env.example` with `NASA_API_KEY`.
- Add `.gitignore` entries for local secrets, environments, caches, and generated data.
- Implement the NASA NEO Feed API client.
- Implement CLI arguments for `--start-date` and `--end-date`.
- Load `NASA_API_KEY` from the environment after reading `.env`.
- Extract the subset of API fields needed for the summary.
- Calculate total objects, hazardous objects, closest approach, fastest object, and largest estimated diameter.
- Format the summary for terminal output.
- Add fixture-based tests for extraction, summarizing, and formatting behavior.
- Document setup, configuration, usage, and development checks in `README.md`.
- Add `AGENTS.md` with project guidance for coding agents.
- Verify:
  - `uv build`
  - `uv run python -m pytest`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src`

## Out Of Scope

- Saving API responses to disk.
- CSV or JSON export.
- Charts, dashboards, reports, or web views.
- Scheduled runs.
- Multiple CLI subcommands.
- Database storage.
