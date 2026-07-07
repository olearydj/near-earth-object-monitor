# Sprint 02C: Filter Mode

Near-Earth Object Monitor can summarize and list near-earth objects. Users now need a way to focus the output on records that match their question.

## Context

A user needs to focus on relevant records instead of scanning every object in a date range. The object list is useful, but it can become noisy. Common questions include "which objects are potentially hazardous?", "which objects are large enough to care about?", and "which objects passed especially close?"

This sprint should add a small set of filters that work on the processed object data. Filters should be understandable from the command line, testable with fixture data, and reusable for both display and export behavior.

## User Features: What

- A user can list only potentially hazardous objects.
- A user can require a minimum estimated diameter in meters.
- A user can require a maximum miss distance in lunar distances.
- A user can combine supported filters.
- A user gets clear behavior when no objects match the filters.
- A user can apply filters consistently to terminal listing and processed export output when those modes are used.
- A developer can test filtering behavior without calling NASA.

## Implementation Plan: How

- Keep filtering logic in pure functions that accept `NeoObject` values and return filtered lists.
- Keep CLI parsing in `src/neo_monitor/cli.py`.
- Apply filters after extracting objects from the NASA response.
- Use filter names that read clearly in `--help`.
- Prefer a few high-value filters over a large query language.
- Keep the existing summary behavior stable unless filtered summaries are explicitly requested.
- Add tests for individual filters and combined filters.

## Tasks

- Add a pure function for filtering extracted objects.
- Add a CLI option for hazardous-only filtering.
- Add a CLI option for minimum diameter in meters.
- Add a CLI option for maximum miss distance in lunar distances.
- Apply filters to object listing mode.
- Apply filters to processed CSV export if export behavior exists.
- Print or return a clear message when a filtered list is empty.
- Add tests for each filter and for one combined-filter case.
- Update `README.md` with filter examples.
- Verify:
  - `uv run python -m pytest`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src`

## Out Of Scope

- A general query language.
- Filtering on every NASA field.
- Sorting.
- Pagination.
- Interactive prompts.
- Changing API request parameters beyond the existing date range.
