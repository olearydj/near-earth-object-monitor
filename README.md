# Near-Earth Object Monitor

A small teaching project for INSY 7970.

The project fetches near-earth object close-approach data from NASA's public API, summarizes the response, and prints a short terminal report.

This is the "tomorrow" version of the project: real API, real package layout, small surface area.

Future iterations will add saved raw data, processed CSV output, richer command-line options, validation, documentation, dashboards, and automation.

## What It Demonstrates

- `src/` project layout
- runtime vs development dependencies
- API key handling with environment variables
- `.env.example` without committing real secrets
- API boundary code separated from testable summary logic
- tests that use fixture data instead of a live API call
- a small command-line report

## Setup

Create the environment:

```bash
uv sync --group dev
```

Copy the example environment file:

```bash
cp .env.example .env
```

For quick testing, `DEMO_KEY` works with NASA's API but is rate-limited.

For regular work, request a free API key from NASA and put it in `.env`:

```text
NASA_API_KEY=your_key_here
```

Do not commit `.env`.

## Run

Run for today:

```bash
uv run neo-monitor
```

Run for a specific date:

```bash
uv run neo-monitor --start-date 2026-07-02
```

Run for a short date range:

```bash
uv run neo-monitor --start-date 2026-07-01 --end-date 2026-07-02
```

## Check

```bash
uv run python -m pytest
uv run ruff format --check .
uv run ruff check .
uv run mypy src
```

## Notes

NASA's NEO feed endpoint:

```text
https://api.nasa.gov/neo/rest/v1/feed
```

The API returns nested JSON. The project keeps the live API request in `api.py` and the testable parsing/summarizing code in `summarize.py`.
