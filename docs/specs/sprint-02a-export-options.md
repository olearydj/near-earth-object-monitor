# Sprint 02A: Export Options

Near-Earth Object Monitor can fetch NASA data and print a terminal summary. The next step is to make each run leave behind durable artifacts that can be inspected, reused, tested, and documented.

## Context

A user needs to keep and reuse the data from a successful API call. The current command answers a question once, but after the terminal output disappears there is no raw response to inspect, no processed artifact for later analysis, and no clear data trail for a report or dashboard.

This sprint should turn the first working API-backed command into a reproducible data workflow. Keep the feature narrow: save the original NASA response when requested, save a small processed output when requested, and preserve the current terminal summary behavior.

## User Features: What

- A user can keep the existing terminal summary workflow unchanged.
- A user can provide an output path for saving the raw NASA JSON response.
- A user can provide an output path for saving processed near-earth object rows as CSV.
- A user can save both raw and processed outputs in one run.
- A user can use conventional folders such as `data/raw/` and `data/processed/`.
- A user gets parent output folders created automatically when reasonable.
- A user gets a clear error if an output file cannot be written.
- A developer can test output writing without calling the live NASA API.
- A future report or dashboard can use the processed output instead of calling NASA directly.

## Implementation Plan: How

- Keep live API access in `src/neo_monitor/api.py`.
- Keep command-line orchestration in `src/neo_monitor/cli.py`.
- Keep object extraction and summary logic in `src/neo_monitor/summarize.py`.
- Add a small file-output module only if it keeps the CLI from becoming crowded.
- Use `pathlib.Path` for output paths.
- Use Python's standard `json` and `csv` libraries.
- Save raw JSON with stable, readable formatting.
- Save processed CSV from extracted `NeoObject` values, not by flattening the whole NASA response.
- Keep generated data out of Git by default unless it is intentional fixture data.
- Use temporary directories in tests so tests do not write into the project tree.

## Tasks

- Add CLI options for saving raw JSON and processed CSV.
- Write the raw NASA response to the requested JSON path.
- Write extracted near-earth object rows to the requested CSV path.
- Create parent folders for requested output paths when needed.
- Keep the existing printed terminal summary.
- Add tests for raw JSON output using fixture data.
- Add tests for processed CSV output using fixture data.
- Update `README.md` with examples that save raw and processed artifacts.
- Confirm `.gitignore` covers generated `data/raw/` and `data/processed/` outputs.
- Verify:
  - `uv run python -m pytest`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src`

## Out Of Scope

- Databases.
- Caching behavior.
- Scheduled collection.
- Dashboard or report generation.
- Pandas dependency.
- Saving every possible flattened NASA field.
- Changing the current summary calculations.
