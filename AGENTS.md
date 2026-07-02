# AGENTS.md

This is a teaching repo for INSY 7970: Modern Software Development Tools and Practices for Data Science.

## Role Of This Repo

The repo is the instructor's running project example for the second half of the course.

It should grow lecture by lecture from a small API-backed command-line tool into a more complete data project with saved data, validation, tests, documentation, dashboards or reports, automation, and final handoff.

## Collaboration Expectations

When helping in this repo:

- Keep changes small and easy to review.
- Prefer clear, boring Python over clever abstractions.
- Preserve the separation between API boundary code and testable summary logic.
- Do not commit real API keys or `.env` files.
- Use `uv` for project commands.
- Keep examples teachable for early Python learners.
- Add or update tests when behavior changes.
- Explain the diff before broad rewrites.

## Current Teaching Premise

This version represents the first real API project step after students learned testable Python structure.

The current feature set should remain small:

- read a NASA API key from the environment
- fetch near-earth object data
- summarize the response
- print a terminal report
- test parsing and summary behavior using fixture data

Persistence, CSV output, dashboards, and automation come in later lecture iterations.
