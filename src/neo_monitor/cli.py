from __future__ import annotations

import argparse
import os
from datetime import date

from dotenv import load_dotenv

from neo_monitor.api import NasaApiError, fetch_neo_feed
from neo_monitor.summarize import format_summary, summarize_feed


def parse_args() -> argparse.Namespace:
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
    load_dotenv()
    args = parse_args()

    api_key = os.environ.get("NASA_API_KEY", "")
    if not api_key:
        raise SystemExit(
            "NASA_API_KEY is required. Copy .env.example to .env and add a key."
        )

    try:
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
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"{value!r} is not a valid YYYY-MM-DD date"
        ) from exc
