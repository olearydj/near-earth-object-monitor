# Near-Earth Object Monitor

A Python command-line tool for collecting, summarizing, filtering, and exporting NASA near-Earth object close-approach data.

The CLI fetches data from NASA's Near Earth Object Web Service, prints readable terminal summaries and object tables, and can save raw and processed data artifacts for later inspection, testing, and reporting.

## Features

- Fetch near-Earth object data from NASA's NEO Feed API.
- Load the NASA API key from the environment or a local `.env` file.
- Summarize object counts, potentially hazardous objects, closest approach, fastest object, and largest estimated diameter.
- Save raw NASA JSON responses and processed object CSV files when requested.
- Print readable terminal summaries and object tables.
- Print the installed CLI version.
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

Save the raw NASA response and processed object rows:

```bash
uv run neo-monitor \
  --start-date 2026-07-01 \
  --end-date 2026-07-01 \
  --save-raw data/raw/neo-2026-07-01.json \
  --save-processed-csv data/processed/neo-objects-2026-07-01.csv
```

Print a row-level listing of the extracted objects:

```bash
uv run neo-monitor --start-date 2026-07-01 --end-date 2026-07-01 --list-objects
```

Filter row-level output to potentially hazardous objects:

```bash
uv run neo-monitor \
  --start-date 2026-07-01 \
  --end-date 2026-07-01 \
  --list-objects \
  --hazardous-only
```

Filters apply to row-level listing and processed CSV export. The terminal
summary still reports the full requested date range.

Filter row-level output by size or miss distance:

```bash
uv run neo-monitor \
  --start-date 2026-07-01 \
  --end-date 2026-07-03 \
  --list-objects \
  --min-diameter-meters 100 \
  --max-miss-distance-lunar 2
```

Use plain text output when styled terminal output is not helpful:

```bash
uv run neo-monitor --start-date 2026-07-01 --end-date 2026-07-01 --plain
```

Print the installed CLI version:

```bash
uv run neo-monitor --version
```

Check local project setup without calling NASA:

```bash
uv run neo-monitor --project-info
```

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
│       ├── __main__.py     # python -m neo_monitor entry point
│       ├── api.py          # NASA API client
│       ├── cli.py          # command-line interface
│       ├── display.py      # terminal presentation helpers
│       ├── metadata.py     # setup and handoff information
│       ├── output.py       # file output helpers
│       └── summarize.py    # data transformation and summary logic
├── tests/
│   ├── fixtures/
│   ├── test_metadata.py
│   └── test_summarize.py
├── data/
│   ├── raw/                # generated raw API responses, ignored by Git
│   └── processed/          # generated processed outputs, ignored by Git
├── .env.example
├── pyproject.toml
└── README.md
```

Generated data files belong under `data/raw/` and `data/processed/`. Those
folders are ignored by Git because they can be recreated from documented
commands. Small stable examples used by tests belong under `tests/fixtures/`.

## Data Source

Data comes from NASA's Near Earth Object Web Service:

<https://api.nasa.gov/>
