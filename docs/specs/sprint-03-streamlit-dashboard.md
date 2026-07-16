# Sprint 03: Streamlit NEO Dashboard

Near-Earth Object Monitor is a reliable command-line data tool. It can fetch, validate, summarize, filter, rank, and export NASA near-Earth object data, but a non-technical user has no way to explore those results in a browser.

## Context

Build one small Streamlit dashboard that gives a person a browser-facing way to explore NEO data. The dashboard should be a new presentation layer over the existing project, not a rewrite of the CLI and not a separate copy of the NASA/API/validation workflow.

The useful payoff is visual exploration. A person should be able to see relationships among an object's miss distance, speed, estimated diameter, and hazardous status, then inspect the rows behind the visual. The dashboard should also preserve the course project's existing trust-boundary work: external data is still validated before use, API failures are still explained clearly, and logs remain operational evidence on the host machine.

This sprint is the prepared example for Lecture 07B, "Web Interfaces and Data Dashboards." It should remain small enough to review as a completed increment. The CLI remains a supported interface for repeatable runs and automation.

## User Features: What

- A user can start a local Streamlit NEO dashboard through a documented command.
- A user can choose a start date and end date before requesting NEO data.
- A user can choose a small set of existing exploration options:
  - potentially hazardous objects only;
  - ranking by closest approach, speed, or estimated diameter;
  - an optional limit on the number of ranked rows.
- A user explicitly submits a request; changing a control does not automatically call NASA.
- A user sees a concise summary of the requested NEO data.
- A user sees a central comparison visualization that makes the following fields visible together:
  - miss distance in lunar distances;
  - velocity in kilometers per hour;
  - estimated diameter;
  - potentially hazardous status.
- A user can inspect the selected objects in a readable table, including the values represented in the visualization.
- A user can use a secondary ranked view when it helps compare the selected metric.
- A user can download the raw NASA JSON response and the selected processed rows without the dashboard silently writing user-requested data to an arbitrary server path.
- A user sees a clear in-page message when the API key is missing, a request fails, incoming NASA data is invalid, or no objects match the selected filters.
- A developer retains the existing CLI behavior and can run the existing project checks without calling NASA during routine tests.

## Implementation Plan: How

- Add Streamlit as a runtime dependency and document one explicit local launch command, such as `uv run streamlit run src/neo_monitor/dashboard.py`.
- Add a small dashboard module that owns only browser controls, page layout, user-facing status/error messages, and browser-specific presentation.
- Do not put Streamlit imports or objects in `api.py`, `summarize.py`, or other reusable core-data modules.
- Do not call the CLI from the dashboard and do not add dashboard concerns to `argparse`.
- Extract the current shared fetch-to-result coordination into a small reusable workflow module if needed. It should accept normal Python values, use the existing API and summary functions, and return normal Python/dataclass results that both interfaces can consume.
- Keep raw NASA data available to the calling interface before validation/transformation. The CLI can continue to save it to a requested path; the dashboard should offer it as an explicit download.
- Keep `NeoObject`, Pydantic validation, filtering, ranking, and summary calculations as the trusted project logic. The dashboard must call those existing behaviors rather than recalculate fields independently.
- Build the primary visualization from the extracted `NeoObject` records. Use a chart type that can show distance, velocity, diameter, hazardous status, and object details without hiding the underlying values. Tooltips or a nearby table should expose the precise values.
- Label axes, units, colors, sizes, and any ranking direction clearly. In particular, a closer approach means a lower miss-distance value; do not use a visual encoding that implies the largest bar is the closest object without explanation.
- Keep the initial dashboard to one page and one complete user path. Do not add accounts, a database, a custom JavaScript frontend, or a new program-facing NEO API.
- Load `NASA_API_KEY` from the existing environment / local `.env` development pattern. Do not add a text field for secrets and do not display the key.
- Use a form or equivalent explicit submission control so Streamlit reruns do not cause surprise NASA requests.
- Continue to log operational details on the machine running Streamlit. Do not expose verbose/log-file controls as dashboard settings; browser users need concise status and error messages instead.
- Use a stable fixture-backed or saved-data path for the lecture demonstration if a live NASA request would make the demonstration depend on credentials, rate limits, or current upstream behavior.
- Add focused tests for any extracted shared workflow using existing fixture data and mocked API behavior. A manual dashboard smoke run is sufficient for the initial browser layer; do not turn this sprint into a deep Streamlit-testing unit.
- Update `README.md` with dashboard setup, launch, expected configuration, the difference between CLI and dashboard use, and the standard project checks.

## Tasks

- Add `streamlit` and any minimal, justified chart dependency to `pyproject.toml`.
- Add a documented dashboard launch command.
- Create the dashboard module and one-page layout.
- Add date-range controls and an explicit submit action.
- Reuse or extract shared workflow coordination so the dashboard and CLI use the same fetch, validation, summary, filter, and rank logic.
- Add hazardous-only, ranking, and row-limit controls using the project’s existing semantics.
- Display summary values and a clear no-matches state.
- Add the primary NEO comparison visualization with units, legend, and precise details available on hover or in the table.
- Add a secondary ranked comparison view only if it materially helps users inspect the selected ranking.
- Display selected objects in a readable browser table.
- Add explicit raw-JSON and processed-row download controls.
- Handle missing configuration, API failures, validation failures, invalid date ranges, and empty filtered results with understandable in-page messages.
- Keep host-side logging useful and avoid printing secrets in dashboard output or logs.
- Add or update fixture-backed tests for extracted shared workflow behavior.
- Manually run the dashboard through one successful request, one no-matches result, and one handled failure path.
- Update `README.md` and this project’s agent guidance if the final module responsibilities change.
- Verify:
  - `uv run python -m pytest`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run streamlit run src/neo_monitor/dashboard.py`

## Acceptance Checks

- The existing `neo-monitor` and `neo` commands continue to work without changed required arguments or changed summary/filter/ranking meanings.
- The dashboard does not import or invoke `cli.main()`.
- A dashboard request reaches the existing NASA boundary and existing Pydantic validation rather than a duplicate implementation.
- A chart and its supporting table agree on the selected rows and displayed values.
- The dashboard explains a missing key, failed request, invalid data, invalid date range, and no-matches result without a Python traceback reaching the user.
- A dashboard interaction does not reveal `NASA_API_KEY`.
- Routine automated tests use fixture or mocked data rather than a live NASA request.

## Out Of Scope

- Replacing or removing the command-line interface.
- Teaching or building a custom HTML/CSS/JavaScript frontend.
- Building a new program-facing NEO API or a FastAPI service.
- User accounts, authentication, or multi-user authorization.
- Deploying the dashboard to a cloud platform.
- Remote-access or SSH setup.
- A database, scheduled collection, or long-term dashboard persistence.
- A multipage dashboard, map, or advanced analytics workspace.
- Deep automated testing of Streamlit widgets or layout.
