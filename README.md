# Near-Earth Object Monitor

A Python command-line tool for summarizing NASA near-Earth object close-approach data.

The CLI fetches data from NASA's Near Earth Object Web Service and prints a compact terminal summary for a date or short date range.

## Features

- Fetch near-Earth object data from NASA's NEO Feed API.
- Load the NASA API key from the environment or a local `.env` file.
- Summarize object counts, potentially hazardous objects, closest approach, fastest object, and largest estimated diameter.
- Keep API access separate from summarizing logic so the core behavior is easy to test.

## Requirements

- Python 3.11 or newer
- `uv`
- A NASA API key

NASA's `DEMO_KEY` is enough for quick local testing, but it is rate-limited. Request a personal key from <https://api.nasa.gov/> for regular use.

## Quick Start

```bash
git clone <repo-url>
cd near-earth-object-monitor
uv sync
cp .env.example .env
```

Edit `.env` and set your API key:

```bash
NASA_API_KEY=your_api_key_here
```

Run the CLI:

```bash
uv run neo-monitor --start-date 2026-07-01 --end-date 2026-07-01
```

## Usage

Summarize one day:

```bash
uv run neo-monitor --start-date 2026-07-01 --end-date 2026-07-01
```

Summarize a short date range:

```bash
uv run neo-monitor --start-date 2026-07-01 --end-date 2026-07-03
```

The CLI currently prints summaries only. It does not write API responses or reports to disk.

## Configuration

Set `NASA_API_KEY` in your shell or in a local `.env` file.

```bash
export NASA_API_KEY=your_api_key_here
```

The `.env` file is ignored by Git so API keys do not get committed.

## Development

Install dependencies:

```bash
uv sync
```

Run tests:

```bash
uv run python -m pytest
```

Run code quality checks:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src
```

## Project Structure

```text
.
├── src/
│   └── neo_monitor/
│       ├── api.py          # NASA API client
│       ├── cli.py          # command-line interface
│       └── summarize.py    # data transformation and summary logic
├── tests/
│   ├── fixtures/
│   └── test_summarize.py
├── .env.example
├── pyproject.toml
└── README.md
```

## Data Source

Data comes from NASA's Near Earth Object Web Service:

<https://api.nasa.gov/>
