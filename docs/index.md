# NEO Monitor Documentation

This directory holds durable documentation that is too detailed for the
project README. The README remains the entry point for installation, everyday
commands, and troubleshooting.

## Find What You Need

| Need | Source |
| --- | --- |
| Install, configure, or run the project | [`README.md`](../README.md) |
| Understand processed fields and units | [`data-dictionary.md`](data-dictionary.md) |
| Review the CLI and dashboard architecture | [`neo-v04-architecture.png`](neo-v04-architecture.png) |
| Inspect the interactive architecture artifact | [`neo-v04-architecture.html`](neo-v04-architecture.html) |
| Understand why a feature was built | [`specs/`](specs/) |
| See expected behavior and failure handling | [`tests/`](../tests/) |
| Orient a coding agent | [`AGENTS.md`](../AGENTS.md) |

## Code Reference

Public modules, classes, and functions carry type hints and docstrings so tools
such as Python's `help()` and pdoc can generate an API reference from the code.
Generated reference sites are views of the source, not hand-maintained copies,
and are therefore not committed here.

## Evidence Versus Documentation

The `data/raw/`, `data/processed/`, and `logs/` directories contain generated
evidence from particular runs. They are useful for inspection and diagnosis,
but they are ignored by Git and do not define the project's intended behavior.
The README, this directory, source docstrings, and tests are the durable record.

When behavior changes, update the smallest authoritative document and link to
it rather than repeating the same explanation in several places.
