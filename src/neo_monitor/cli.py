from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from neo_monitor.api import NasaApiError, fetch_neo_feed
from neo_monitor.display import print_rich_object_listing, print_rich_summary
from neo_monitor.metadata import (
    build_project_metadata,
    format_project_metadata,
    package_version,
)
from neo_monitor.output import OutputWriteError, write_objects_csv, write_raw_json
from neo_monitor.summarize import (
    extract_objects,
    filter_objects,
    format_object_listing,
    format_summary,
    summarize_objects,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    # argparse handles command-line parsing, help text, and error messages. The
    # rest of the program can work with normal Python values instead of raw
    # strings from the terminal.
    parser = argparse.ArgumentParser(
        prog="neo-monitor",
        description="Summarize NASA near-earth object close-approach data.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {package_version()}",
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
    parser.add_argument(
        "--save-raw",
        type=Path,
        default=None,
        metavar="PATH",
        help="write the raw NASA JSON response to PATH",
    )
    parser.add_argument(
        "--save-processed-csv",
        type=Path,
        default=None,
        metavar="PATH",
        help="write extracted near-earth object rows to PATH as CSV",
    )
    parser.add_argument(
        "--list-objects",
        action="store_true",
        help="print a row-level listing of extracted near-earth objects",
    )
    parser.add_argument(
        "--hazardous-only",
        action="store_true",
        help="include only potentially hazardous objects in row-level outputs",
    )
    parser.add_argument(
        "--min-diameter-meters",
        type=_nonnegative_float_arg,
        default=None,
        metavar="METERS",
        help="minimum estimated diameter for row-level outputs",
    )
    parser.add_argument(
        "--max-miss-distance-lunar",
        type=_nonnegative_float_arg,
        default=None,
        metavar="LD",
        help="maximum miss distance in lunar distances for row-level outputs",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="print plain text instead of styled terminal output",
    )
    parser.add_argument(
        "--project-info",
        action="store_true",
        help="print project setup information and exit without calling NASA",
    )
    return parser.parse_args(argv)


def main() -> None:
    # load_dotenv reads a local .env file if one exists. Environment variables
    # are still the source of truth, so the same code works in a shell, a CI
    # job, or a hosted environment.
    load_dotenv()
    args = parse_args()

    api_key = os.environ.get("NASA_API_KEY", "")
    if args.project_info:
        print(format_project_metadata(build_project_metadata(api_key)))
        return

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

    objects = extract_objects(feed)
    summary = summarize_objects(objects)
    filtered_objects = filter_objects(
        objects,
        hazardous_only=args.hazardous_only,
        min_diameter_meters=args.min_diameter_meters,
        max_miss_distance_lunar=args.max_miss_distance_lunar,
    )

    try:
        if args.save_raw is not None:
            write_raw_json(feed, args.save_raw)
        if args.save_processed_csv is not None:
            write_objects_csv(filtered_objects, args.save_processed_csv)
    except OutputWriteError as exc:
        raise SystemExit(str(exc)) from exc

    if args.plain:
        print(format_summary(summary, label))
        if args.list_objects:
            print()
            print(format_object_listing(filtered_objects))
    else:
        console = Console()
        print_rich_summary(console, summary, label)
        if args.list_objects:
            print_rich_object_listing(console, filtered_objects)


def _date_arg(value: str) -> date:
    # argparse calls this function for each date argument. Raising
    # ArgumentTypeError gives the user a normal CLI error instead of a traceback.
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"{value!r} is not a valid YYYY-MM-DD date"
        ) from exc


def _nonnegative_float_arg(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not a number") from exc

    if parsed < 0:
        raise argparse.ArgumentTypeError(f"{value!r} must be nonnegative")
    return parsed
