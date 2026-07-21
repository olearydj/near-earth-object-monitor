"""Command-line interface for repeatable NEO data requests and exports."""

from __future__ import annotations

import argparse
import logging
import os
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from neo_monitor.api import NasaApiError
from neo_monitor.display import (
    print_rich_bar_chart,
    print_rich_object_listing,
    print_rich_summary,
)
from neo_monitor.logging_config import LoggingSetupError, configure_logging
from neo_monitor.metadata import (
    build_project_metadata,
    format_project_metadata,
    package_version,
)
from neo_monitor.output import OutputWriteError, write_objects_csv, write_raw_json
from neo_monitor.summarize import (
    NeoDataValidationError,
    format_object_listing,
    format_summary,
)
from neo_monitor.workflow import (
    MonitorRequest,
    build_monitor_result,
    fetch_monitor_feed,
)


logger = logging.getLogger(__name__)
CLI_HELP_EPILOG = """examples:
  neo-monitor --start-date 2026-07-01 --end-date 2026-07-03
  neo-monitor --list-objects --sort-by closest --top 5
  neo-monitor --save-raw data/raw/feed.json --save-processed-csv data/processed/neos.csv
  neo-monitor --project-info

configuration:
  Set NASA_API_KEY in the environment or in a local .env file.
  Run neo-monitor --project-info to check setup without calling NASA.
"""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse and validate command-line options.

    Args:
        argv: Arguments without the program name. Uses ``sys.argv`` when omitted.

    Returns:
        Validated options ready for the command workflow.

    Raises:
        SystemExit: If argparse handles ``--help`` or finds invalid options.
    """

    # argparse handles command-line parsing, help text, and error messages. The
    # rest of the program can work with normal Python values instead of raw
    # strings from the terminal.
    parser = argparse.ArgumentParser(
        prog="neo-monitor",
        description="Summarize NASA near-earth object close-approach data.",
        epilog=CLI_HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        help="first date to request, in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--end-date",
        type=_date_arg,
        default=None,
        help="last date to request, in YYYY-MM-DD format (default: start date)",
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
        "--sort-by",
        choices=("closest", "fastest", "largest"),
        default=None,
        help="rank row-level results by the selected measure",
    )
    parser.add_argument(
        "--top",
        type=_positive_int_arg,
        default=None,
        metavar="N",
        help="keep the first N ranked rows for listings and CSV export",
    )
    parser.add_argument(
        "--bar-chart",
        action="store_true",
        help="render ranked rows as a Rich bar chart (requires --sort-by)",
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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="write operational INFO messages to stderr",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        metavar="PATH",
        help="write detailed DEBUG logs to PATH",
    )

    args = parser.parse_args(argv)
    if args.end_date is not None and args.end_date < args.start_date:
        parser.error("--end-date cannot be before --start-date")
    if args.top is not None and args.sort_by is None:
        parser.error("--top requires --sort-by")
    if args.bar_chart and args.sort_by is None:
        parser.error("--bar-chart requires --sort-by")
    if args.bar_chart and args.plain:
        parser.error("--bar-chart cannot be used with --plain")
    if args.sort_by is not None and not (
        args.list_objects or args.bar_chart or args.save_processed_csv is not None
    ):
        parser.error(
            "--sort-by requires --list-objects, --bar-chart, or --save-processed-csv"
        )
    return args


def main() -> None:
    """Run one CLI request and translate expected failures into concise errors."""

    # load_dotenv reads a local .env file if one exists. Environment variables
    # are still the source of truth, so the same code works in a shell, a CI
    # job, or a hosted environment.
    load_dotenv()
    args = parse_args()

    try:
        configure_logging(verbose=args.verbose, log_file=args.log_file)
    except LoggingSetupError as exc:
        raise SystemExit(str(exc)) from exc

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
        request = MonitorRequest(
            start_date=args.start_date,
            end_date=args.end_date,
            hazardous_only=args.hazardous_only,
            min_diameter_meters=args.min_diameter_meters,
            max_miss_distance_lunar=args.max_miss_distance_lunar,
            sort_by=args.sort_by,
            top=args.top,
        )
        feed = fetch_monitor_feed(api_key, request)
    except (NasaApiError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    try:
        if args.save_raw is not None:
            write_raw_json(feed, args.save_raw)
            logger.info("Saved raw NASA response to %s.", args.save_raw)
    except OutputWriteError as exc:
        raise SystemExit(str(exc)) from exc

    try:
        result = build_monitor_result(
            feed,
            request,
        )
    except (NeoDataValidationError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    try:
        if args.save_processed_csv is not None:
            write_objects_csv(result.selected_objects, args.save_processed_csv)
            logger.info("Saved processed object rows to %s.", args.save_processed_csv)
    except OutputWriteError as exc:
        raise SystemExit(str(exc)) from exc

    if args.plain:
        print(format_summary(result.summary, result.label))
        if args.list_objects:
            print()
            print(format_object_listing(result.selected_objects))
    else:
        console = Console()
        print_rich_summary(console, result.summary, result.label)
        if args.list_objects:
            print_rich_object_listing(console, result.selected_objects)
        if args.bar_chart:
            print_rich_bar_chart(console, result.selected_objects, args.sort_by)


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


def _positive_int_arg(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not a whole number") from exc

    if parsed < 1:
        raise argparse.ArgumentTypeError(f"{value!r} must be at least 1")
    return parsed
