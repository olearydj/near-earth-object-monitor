# Sprint 2: Saved Data And Repeatable Runs

## Goal

Add a persistence layer so API responses and processed summaries can be saved, inspected, and reused across runs.

## Proposed Scope

- Add an output directory option.
- Save raw NASA API responses as JSON.
- Save processed summary rows as CSV.
- Use `pathlib` for cross-platform file paths.
- Add command-line options for choosing whether to fetch fresh data or reuse saved data.
- Expand tests to cover file-writing behavior with temporary directories.

## Acceptance Criteria

- A user can run the CLI for a date range and save the raw response.
- A user can generate a CSV summary from saved data.
- Re-running tests does not depend on the network or a real API key.
- File paths work on macOS, Windows, and Linux.
- The README documents the new workflow.

## Out Of Scope

- Database storage.
- Hosted dashboards.
- Authentication beyond `NASA_API_KEY`.
- Long-running scheduling or automation.

## Open Questions

- Should the default output format be one JSON file per API response or one JSON file per requested date?
- Should CSV output represent one row per object, one row per day, or one row per command run?
- Should the CLI stay as one command with options or move to subcommands such as `fetch` and `summarize`?
