from __future__ import annotations

import argparse
import os
from datetime import date

from dotenv import load_dotenv

from neo_monitor.api import NasaApiError, fetch_neo_feed
from neo_monitor.summarize import format_summary, summarize_feed


def parse_args() -> argparse.Namespace:
    # argparse handles command-line parsing, help text, and error messages. The
    # rest of the program can work with normal Python values instead of raw
    # strings from the terminal.
    parser = argparse.ArgumentParser(
        description="Summarize NASA near-earth object close-approach data."
    )
    parser.add_argument(
        "--start-date",
        type=_date_arg,
        default=date.today(),
        help="first date to request, in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--end-date",
        type=_date_arg,
        default=None,
        help="last date to request, in YYYY-MM-DD format",
    )
    return parser.parse_args()


def main() -> None:
    # load_dotenv reads a local .env file if one exists. Environment variables
    # are still the source of truth, so the same code works in a shell, a CI
    # job, or a hosted environment.
    load_dotenv()
    args = parse_args()

    api_key = os.environ.get("NASA_API_KEY", "")
    if not api_key:
        raise SystemExit(
            "NASA_API_KEY is required. Copy .env.example to .env and add a key."
        )

    try:
        # The CLI coordinates the workflow: read configuration, fetch data,
        # summarize it, and print the result. The detailed API and summary logic
        # live in smaller functions that are easier to test.
        feed = fetch_neo_feed(
            api_key=api_key,
            start_date=args.start_date,
            end_date=args.end_date,
        )
    except NasaApiError as exc:
        raise SystemExit(str(exc)) from exc

    end_date = args.end_date or args.start_date
    label = args.start_date.isoformat()
    if end_date != args.start_date:
        label = f"{args.start_date.isoformat()} to {end_date.isoformat()}"

    summary = summarize_feed(feed)
    print(format_summary(summary, label))


def _date_arg(value: str) -> date:
    # argparse calls this function for each date argument. Raising
    # ArgumentTypeError gives the user a normal CLI error instead of a traceback.
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"{value!r} is not a valid YYYY-MM-DD date"
        ) from exc
