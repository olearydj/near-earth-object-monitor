"""Shared NEO request-to-result workflow for command-line and browser clients."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from neo_monitor.api import fetch_neo_feed
from neo_monitor.summarize import (
    NeoObject,
    NeoSummary,
    SortBy,
    extract_objects,
    filter_objects,
    rank_objects,
    summarize_objects,
)


@dataclass(frozen=True)
class MonitorRequest:
    """User-selected options shared by the CLI and dashboard.

    A request describes dates and row-level selection. Validation here keeps
    interface-specific code from creating impossible workflow states.
    """

    start_date: date
    end_date: date | None = None
    hazardous_only: bool = False
    min_diameter_meters: float | None = None
    max_miss_distance_lunar: float | None = None
    sort_by: SortBy | None = None
    top: int | None = None

    def __post_init__(self) -> None:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end date cannot be before start date")
        if self.top is not None and self.top < 1:
            raise ValueError("top must be at least 1")
        if self.top is not None and self.sort_by is None:
            raise ValueError("top requires a ranking")


@dataclass(frozen=True)
class MonitorResult:
    """Raw evidence and derived values for one completed request.

    ``summary`` and ``objects`` describe the full validated feed;
    ``selected_objects`` reflects the request's filters, ranking, and limit.
    """

    raw_feed: dict[str, Any]
    label: str
    summary: NeoSummary
    objects: tuple[NeoObject, ...]
    selected_objects: tuple[NeoObject, ...]


def fetch_monitor_feed(api_key: str, request: MonitorRequest) -> dict[str, Any]:
    """Fetch raw NASA data for a shared request without transforming it.

    Raises:
        NasaApiError: Propagated from the external API boundary when the request
        or response is unusable.
    """

    return fetch_neo_feed(
        api_key=api_key,
        start_date=request.start_date,
        end_date=request.end_date,
    )


def build_monitor_result(
    feed: dict[str, Any], request: MonitorRequest
) -> MonitorResult:
    """Validate, summarize, select, and optionally rank one NASA feed.

    Args:
        feed: Decoded raw NASA response retained in the returned result.
        request: Date label and row-level selection requested by the interface.

    Returns:
        A result that keeps raw evidence, the unfiltered summary, all trusted
        records, and the selected records distinct.

    Raises:
        NeoDataValidationError: If required NASA fields cannot create trusted
        project records.
        ValueError: If ranking or request constraints are invalid.
    """

    objects = tuple(extract_objects(feed))
    selected_objects = tuple(
        filter_objects(
            objects,
            hazardous_only=request.hazardous_only,
            min_diameter_meters=request.min_diameter_meters,
            max_miss_distance_lunar=request.max_miss_distance_lunar,
        )
    )
    if request.sort_by is not None:
        selected_objects = tuple(
            rank_objects(selected_objects, request.sort_by, request.top)
        )

    end_date = request.end_date or request.start_date
    label = request.start_date.isoformat()
    if end_date != request.start_date:
        label = f"{request.start_date.isoformat()} to {end_date.isoformat()}"

    return MonitorResult(
        raw_feed=feed,
        label=label,
        summary=summarize_objects(list(objects)),
        objects=objects,
        selected_objects=selected_objects,
    )
