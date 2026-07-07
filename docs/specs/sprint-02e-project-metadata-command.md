# Sprint 02E: Project Metadata Command

Near-Earth Object Monitor is becoming a larger project with configuration, external API access, generated outputs, and development checks. Users need a quick way to understand whether the project is installed and configured well enough to run.

## Context

A user needs to understand the project state before trying a data run. If the API key is missing, the package version is unclear, or the expected output folders are not obvious, troubleshooting becomes harder than it needs to be. A small metadata command can make setup and handoff easier.

This sprint should add a lightweight project information command or option. It should help users and reviewers inspect configuration status without exposing secrets or requiring a live NASA API call.

## User Features: What

- A user can display the project version or package name.
- A user can check whether the expected NASA API key environment variable is present without printing the key.
- A user can see the default or recommended data folders.
- A user can see the core commands for running checks or where to find them in the README.
- A user can run the metadata command without calling the live NASA API.
- A reviewer can use the command as a quick setup sanity check.

## Implementation Plan: How

- Keep the metadata behavior small and predictable.
- Avoid adding a large subcommand framework unless the CLI already needs one.
- Read package metadata with standard Python tools if practical.
- Report whether `NASA_API_KEY` is configured, but never print its value.
- Keep the command independent from live API calls.
- Add tests that check the metadata output with controlled environment variables.

## Tasks

- Add a CLI option or subcommand for project metadata.
- Display project/package name and version if available.
- Display whether `NASA_API_KEY` is set.
- Display recommended data output folders.
- Display or reference the standard development check commands.
- Add tests for metadata output without an API key.
- Add tests for metadata output with a fake API key set in the test environment.
- Update `README.md` with the metadata command.
- Verify:
  - `uv run python -m pytest`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src`

## Out Of Scope

- Calling NASA to verify whether the API key is valid.
- Printing secret values.
- Interactive setup repair.
- Full health-check framework.
- Dependency vulnerability auditing.
- CI configuration.
