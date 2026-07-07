# Sprint 02B: Object Listing Mode

Near-Earth Object Monitor currently gives a high-level summary. Users also need a way to see the individual objects behind that summary without opening raw NASA JSON by hand.

## Context

A user needs to see the individual near-earth object records, not only aggregate statistics. The summary answers "how many, closest, fastest, largest," but it does not show the list of objects that produced those answers. A useful project workflow should let the user inspect the processed records directly.

This sprint should add a listing mode that presents extracted near-earth objects in a predictable, reviewable shape. Keep the feature focused on the fields the project already extracts.

## User Features: What

- A user can ask the CLI to list individual near-earth objects for the requested date range.
- A user sees one row per extracted object.
- A user sees the most important fields for each object:
  - approach date
  - name
  - hazardous flag
  - estimated diameter in meters
  - miss distance in kilometers
  - miss distance in lunar distances
  - velocity in kilometers per hour
- A user can still run the original summary behavior.
- A user can combine listing behavior with processed CSV export if that was added in Sprint 02A.
- A developer can test listing behavior with fixture data and without calling NASA.

## Implementation Plan: How

- Reuse `extract_objects()` rather than parsing the NASA response again.
- Keep extracted object data in the existing `NeoObject` shape unless a small change is clearly needed.
- Keep display formatting separate from object extraction.
- Keep the initial listing deterministic by using the current object ordering from extraction.
- Add one simple CLI option for listing objects.
- Avoid adding filtering or sorting in this sprint unless needed to keep the output usable.
- Keep tests focused on the listing output and object fields.

## Tasks

- Add a CLI option that enables object listing mode.
- Format extracted objects as a readable terminal table or simple aligned text.
- Preserve the current summary output as the default command behavior.
- Ensure listing mode works for one-day and short-range requests.
- Add tests for listing output using fixture data.
- Update `README.md` with a listing-mode example.
- Verify:
  - `uv run python -m pytest`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src`

## Out Of Scope

- Filtering.
- Sorting controls.
- Rich terminal styling.
- Pagination.
- Interactive selection.
- Adding many more NASA fields.
- Changing the raw NASA API request.
