# Near-Earth Object Monitor

A Python tool for collecting, summarizing, filtering, exporting, and visually exploring NASA near-Earth object close-approach data.

The CLI fetches data from NASA's Near Earth Object Web Service, prints readable terminal summaries and object tables, and can save raw and processed data artifacts for later inspection, testing, and reporting.

## Features

- Fetch near-Earth object data from NASA's NEO Feed API.
- Load the NASA API key from the environment or a local `.env` file.
- Summarize object counts, potentially hazardous objects, closest approach, fastest object, and largest estimated diameter.
- Save raw NASA JSON responses and processed object CSV files when requested.
- Print readable terminal summaries and object tables.
- Rank selected objects by closest approach, speed, or estimated size.
- Render ranked objects as a terminal bar chart with Rich.
- Explore NEO records in a local Streamlit browser dashboard.
- Print the installed CLI version.
- Validate the external NASA fields the project uses before creating internal records.
- Offer optional diagnostic logging without cluttering normal command output.
- Test API failures with mocked responses instead of calling NASA during test runs.
- Keep API access separate from summarizing logic so the core behavior is easy to test.

## Requirements

- Python 3.11 or newer
- `uv`
- A NASA API key
- Quarto and a TeX distribution such as TinyTeX to render PDF reports

NASA's `DEMO_KEY` is enough for quick local testing, but it is rate-limited. Request a personal key from <https://api.nasa.gov/> for regular use.

## Quick Start

```bash
git clone https://github.com/olearydj/near-earth-object-monitor.git
cd near-earth-object-monitor
uv sync
cp .env.example .env
```

On Windows PowerShell, replace the `cp` command with:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set your API key:

```bash
NASA_API_KEY=your_api_key_here
```

Run the CLI:

```bash
uv run neo-monitor --start-date 2026-07-01 --end-date 2026-07-01
```

The command prints a summary containing the requested date range, the number of
objects observed, and the closest, fastest, and largest objects in the feed.

## Development Check

Run the project's lint and test contract with one command:

```bash
bash scripts/check.sh
```

`scripts/hello.sh` is a small Bash example that demonstrates sequencing, a
loop, and a conditional without changing project files.

Run the local browser dashboard:

```bash
uv run streamlit run src/neo_monitor/dashboard.py
```

The dashboard uses the same `NASA_API_KEY` configuration and trusted project
logic as the CLI. It provides an interactive comparison chart, ranked view,
detail table, and explicit downloads for raw JSON and selected CSV rows.

## Usage

Show the complete command reference and examples:

```bash
uv run neo-monitor --help
```

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

When `--save-raw` is supplied, the original response is saved before it is
validated and summarized. That keeps evidence available if the outside data is
not usable.

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

Rank and limit the rows written to a listing or CSV file:

```bash
uv run neo-monitor \
  --list-objects \
  --sort-by fastest \
  --top 5
```

Render the same ranked rows as a Rich terminal bar chart:

```bash
uv run neo-monitor \
  --bar-chart \
  --sort-by largest \
  --top 5
```

`--sort-by` accepts `closest`, `fastest`, or `largest`. Chart bars are scaled
only to the selected rows, so the exact value beside each bar remains the
evidence to compare across runs. `--bar-chart` requires Rich output and cannot
be combined with `--plain`.

Use plain text output when styled terminal output is not helpful:

```bash
uv run neo-monitor --start-date 2026-07-01 --end-date 2026-07-01 --plain
```

Print the installed CLI version:

```bash
uv run neo-monitor --version
```

Show operational messages in the terminal while the command runs:

```bash
uv run neo-monitor --start-date 2026-07-01 --verbose
```

Write more detailed diagnostic messages to a file:

```bash
uv run neo-monitor \
  --start-date 2026-07-01 \
  --log-file logs/neo-monitor.log
```

`--verbose` writes `INFO` and higher messages to stderr. `--log-file` includes
additional `DEBUG` detail in the named file. Use both options to see the
terminal messages while saving the fuller log.

## Dashboard

Start the local dashboard after configuring `NASA_API_KEY`:

```bash
uv run streamlit run src/neo_monitor/dashboard.py
```

Choose a date range, a hazardous-only filter if useful, and a ranking. Select
**Load near-Earth object data** to make one request. The dashboard shows a
comparison chart with miss distance, velocity, estimated diameter, and
hazardous status, plus a ranked view and the selected rows behind the charts.

The command line remains the better interface for repeatable runs,
automation, and writing artifacts to named paths. The dashboard is for a
person who wants to explore a requested result in a browser.

Check local project setup without calling NASA:

```bash
uv run neo-monitor --project-info
```

## Configuration

Set `NASA_API_KEY` in your shell or in a local `.env` file.

```bash
export NASA_API_KEY=your_api_key_here
```

On Windows PowerShell, use:

```powershell
$env:NASA_API_KEY = "your_api_key_here"
```

The `.env` file is ignored by Git so API keys do not get committed.

## Outputs and Documentation

- Raw JSON is a readable, credential-sanitized copy of the NASA response. The
  project redacts API-key values echoed in provider link metadata while
  preserving analytical fields for provenance and later troubleshooting.
- Processed CSV contains the smaller, validated record used by the project.
  See the [data dictionary](docs/data-dictionary.md) for fields, units, and
  transformation rules.
- Start with the [documentation map](docs/index.md) for architecture artifacts,
  sprint specifications, and maintainer-facing references.
- Runtime diagnostics go to the terminal with `--verbose` or to a requested
  file with `--log-file`. Logs are ignored by Git and must not contain API keys
  or private data.

## Quarto Reports

The repository includes `reports/hello-quarto.qmd`, a small Python report
adapted from Posit's Hello, Quarto tutorial. It uses the bundled Plotnine
Palmer Penguins data so the example does not need a live API or downloaded
data file.

`reports/neo-report.qmd` is the project report. It requests the current calendar
week from NASA, saves a credential-sanitized response and acquisition metadata
under `data/raw/`, validates the response through the shared project workflow,
and renders an academic-style PDF containing an abstract, citations, cross-
references, computed prose, tables, figures, limitations, and provenance.

`reports/neo-report-agu.qmd` is a prepared classroom variant of the same report
body using the American Geophysical Union format. It exists to make a brief
before-and-after demonstration possible; `reports/neo-report.qmd` remains the
authoritative report source.

Install Quarto globally with Homebrew, Scoop, or the official installer. Quarto
is a separate CLI application and is not installed by `uv`. Restore and
activate the project's Python environment so Quarto's Jupyter engine can use
the report dependencies:

```bash
uv sync
source .venv/bin/activate
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Verify the publishing tools and install TinyTeX if needed:

```bash
quarto check
quarto install tinytex
```

Render the example directly with the global Quarto CLI:

```bash
quarto render reports/hello-quarto.qmd --to pdf
```

Render the weekly NEO report after configuring `NASA_API_KEY`:

```bash
quarto render reports/neo-report.qmd --to pdf
```

Render the prepared AGU variant with the extension included in this repository:

```bash
quarto render reports/neo-report-agu.qmd --to agu-pdf
```

For an existing project that does not yet contain the extension, add it with
`quarto add quarto-journals/agu`.

The first render for a calendar week requests and saves the response. Later
renders reuse that saved evidence. Set `NEO_REPORT_REFRESH=1` when a new request
should replace the saved response for the same week.

The generated PDFs are ignored because they can be rebuilt from the committed
source, saved input, and locked Python environment.

## Troubleshooting

**Quarto cannot import `plotnine`**

Activate the project's `.venv` before rendering. If `quarto check jupyter`
still reports a Python path outside `.venv`, remove any existing
`QUARTO_PYTHON` override from that shell and check again.

**`NASA_API_KEY is required`**

Copy `.env.example` to `.env`, add a key, and run
`uv run neo-monitor --project-info`. The status command reports whether a key is
configured without displaying its value or calling NASA.

**NASA rejects or rate-limits a request**

Confirm the date range and key. `DEMO_KEY` is intentionally rate-limited; use a
personal key for regular work. Add `--verbose` or `--log-file logs/neo.log` for
diagnostic context.

**NASA data cannot be used**

The project validates the external fields it depends on. Add
`--save-raw data/raw/failed-response.json` to preserve the original response
before validation so the mismatch can be inspected.

**No rows match a filter**

The unfiltered summary can still contain objects even when a row-level filter
selects none. Relax `--hazardous-only`, `--min-diameter-meters`, or
`--max-miss-distance-lunar` and rerun the command.

## Development

Install dependencies:

```bash
uv sync
```

Run tests:

```bash
uv run python -m pytest
```

Inspect which source lines the tests exercise:

```bash
uv run pytest --cov=neo_monitor --cov-report=term-missing
```

Run code quality checks and verify the diff:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src
git diff --check
```

## Project Structure

```text
.
├── _quarto.yml             # Quarto project root and extension discovery
├── src/
│   └── neo_monitor/
│       ├── __main__.py     # python -m neo_monitor entry point
│       ├── api.py          # NASA API client
│       ├── cli.py          # command-line interface
│       ├── dashboard.py    # Streamlit browser interface
│       ├── display.py      # terminal presentation helpers
│       ├── logging_config.py # optional diagnostic logging
│       ├── metadata.py     # setup and project information
│       ├── output.py       # file output helpers
│       ├── summarize.py    # data transformation and summary logic
│       └── workflow.py     # shared request-to-result coordination
├── docs/
│   ├── data-dictionary.md  # processed data fields and derivations
│   ├── index.md            # documentation map
│   └── specs/              # completed sprint specifications
├── reports/
│   ├── hello-quarto.qmd    # reproducible Python and Quarto starter
│   ├── neo-report.qmd      # current-week NEO monitoring report
│   ├── neo-report-agu.qmd  # prepared AGU classroom variant
│   └── references.bib      # report bibliography
├── _extensions/
│   └── quarto-journals/agu/ # vendored AGU publication format
├── tests/
│   ├── fixtures/
│   └── test_*.py           # executable behavior examples
├── data/
│   ├── raw/                # generated raw API responses, ignored by Git
│   └── processed/          # generated processed outputs, ignored by Git
├── .env.example
├── AGENTS.md
├── LICENSE
├── pyproject.toml
└── README.md
```

Generated data files belong under `data/raw/` and `data/processed/`. Those
folders are ignored by Git because they can be recreated from documented
commands. Small stable examples used by tests belong under `tests/fixtures/`.

## Data Source

Data comes from NASA's Near Earth Object Web Service:

<https://api.nasa.gov/>

NASA is the source of names, approach dates, hazard flags, estimated diameter
ranges, miss distances, and relative velocities. The project-specific
derivations are documented in the [data dictionary](docs/data-dictionary.md).

## License

This project is available under the [MIT License](LICENSE).
