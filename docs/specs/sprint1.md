# Sprint 1: Command-Line NASA NEO Summary

## Goal

Create a small Python CLI that fetches near-Earth object data from NASA and prints a useful terminal summary for a requested date or short date range.

## Scope

- Package the project with a `src/` layout.
- Provide a `neo-monitor` command.
- Read the NASA API key from `NASA_API_KEY`.
- Support a local `.env` file for development.
- Fetch data from NASA's NEO Feed API.
- Summarize the response with object count, potentially hazardous count, closest approach, fastest object, and largest estimated diameter.
- Keep API access separate from parsing and summary logic.
- Include a realistic sample fixture for tests.

## Acceptance Criteria

- Running `uv run neo-monitor --start-date 2026-07-01 --end-date 2026-07-01` prints a readable summary.
- Missing API keys produce a clear error message.
- Unit tests exercise parsing and summary behavior without calling NASA.
- `README.md` explains setup, configuration, usage, and development checks.
- `.env.example` documents the required environment variable without exposing a real key.

## Out Of Scope

- Saving API responses to disk.
- CSV or JSON export.
- Charts, dashboards, or web views.
- Scheduled runs.
- Multi-command CLI structure.

## Notes

This sprint should leave the project small but real: it talks to an external API, uses normal project packaging, and has enough test coverage to support later changes.
