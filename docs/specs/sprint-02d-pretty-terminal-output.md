# Sprint 02D: Pretty Terminal Output

Near-Earth Object Monitor can produce useful terminal output, but users need output that is easier to scan as the project adds summaries, object lists, filters, and exports.

## Context

A user needs terminal output that is readable at a glance. Plain text is reliable, but as the project grows it becomes harder to scan important values, distinguish hazardous objects, and compare records. Better terminal presentation can make the CLI more useful without changing the data model.

This sprint should improve the command-line experience with richer formatting while keeping the data extraction and API logic independent from presentation details.

## User Features: What

- A user sees a more readable summary display.
- A user sees object listings in a clean table when listing mode is used.
- A user can quickly identify potentially hazardous objects.
- A user still has access to plain output if needed for copying, logs, or environments that do not render styled output well.
- A developer can test the data and formatting behavior without calling NASA.

## Implementation Plan: How

- Add `rich` as a runtime dependency.
- Keep Rich-specific code near the presentation layer.
- Do not put Rich objects in API, extraction, filtering, or summary logic.
- Preserve or add a plain-output path for predictable text output.
- Keep tests focused on core data behavior and simple output expectations; do not over-test terminal styling internals.
- Update `README.md` examples only where the commands or user-visible behavior changes.

## Tasks

- Add `rich` as a project dependency.
- Format the summary in a readable Rich panel or table.
- Format object listings as a Rich table.
- Visually mark potentially hazardous objects in listing output.
- Add a plain-output option if needed.
- Make sure output still works in non-interactive terminals.
- Add or update tests for plain output and core formatting paths.
- Update `README.md` to mention the improved terminal display.
- Verify:
  - `uv run python -m pytest`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src`

## Out Of Scope

- A text user interface.
- Interactive terminal prompts.
- Charts.
- Dashboard behavior.
- Changing summary calculations.
- Styling generated CSV or JSON files.
