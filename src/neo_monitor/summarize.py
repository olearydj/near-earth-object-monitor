from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging
from typing import Any
from typing import Literal
from typing import Sequence

from pydantic import BaseModel, Field, StrictBool, ValidationError


logger = logging.getLogger(__name__)
SortBy = Literal["closest", "fastest", "largest"]


class NeoDataValidationError(ValueError):
    """Raised when required NASA API data cannot be safely used."""


@dataclass(frozen=True)
class NeoObject:
    """Selected fields for one near-earth object close approach."""

    # A dataclass is a lightweight way to name the fields we care about. The
    # NASA response contains much more data, but keeping a smaller shape makes
    # the rest of the code easier to read and test.
    name: str
    approach_date: str
    hazardous: bool
    diameter_meters: float
    miss_distance_km: float
    miss_distance_lunar: float
    velocity_kph: float


@dataclass(frozen=True)
class NeoSummary:
    """Summary values for a NASA near-earth object feed response."""

    # These are the values the CLI currently reports. Storing them together
    # keeps formatting separate from the calculations that produce the summary.
    total_objects: int
    hazardous_count: int
    closest: NeoObject | None
    fastest: NeoObject | None
    largest: NeoObject | None


class _DiameterKilometersInput(BaseModel):
    estimated_diameter_min: float
    estimated_diameter_max: float


class _EstimatedDiameterInput(BaseModel):
    kilometers: _DiameterKilometersInput


class _MissDistanceInput(BaseModel):
    kilometers: float
    lunar: float


class _RelativeVelocityInput(BaseModel):
    kilometers_per_hour: float


class _CloseApproachInput(BaseModel):
    close_approach_date: date
    miss_distance: _MissDistanceInput
    relative_velocity: _RelativeVelocityInput


class _NeoObjectInput(BaseModel):
    """Only the external fields needed to create one trusted NeoObject."""

    name: str
    is_potentially_hazardous_asteroid: StrictBool
    estimated_diameter: _EstimatedDiameterInput
    close_approach_data: list[_CloseApproachInput] = Field(min_length=1)


class _NeoFeedInput(BaseModel):
    near_earth_objects: dict[date, list[_NeoObjectInput]]


def extract_objects(feed: dict[str, Any]) -> list[NeoObject]:
    """Extract the fields this project currently cares about."""

    # External JSON is not yet a trusted project record. Pydantic checks only
    # the fields used here; after validation, this function converts them into
    # the small immutable NeoObject dataclass used by the rest of the project.
    try:
        validated_feed = _NeoFeedInput.model_validate(feed)
    except ValidationError as exc:
        first_problem = exc.errors(include_url=False)[0]
        location = ".".join(str(part) for part in first_problem["loc"])
        message = first_problem["msg"]
        logger.warning("NASA data validation failed at %s: %s", location, message)
        raise NeoDataValidationError(
            f"NASA data could not be used at {location}: {message}"
        ) from exc

    objects: list[NeoObject] = []
    for _, daily_objects in sorted(validated_feed.near_earth_objects.items()):
        for raw_object in daily_objects:
            # The feed's first close approach is the one this introductory
            # project currently summarizes. The validated list is non-empty.
            close_approach = raw_object.close_approach_data[0]
            diameter = raw_object.estimated_diameter.kilometers
            objects.append(
                NeoObject(
                    name=raw_object.name,
                    approach_date=close_approach.close_approach_date.isoformat(),
                    hazardous=raw_object.is_potentially_hazardous_asteroid,
                    diameter_meters=(
                        (
                            diameter.estimated_diameter_min
                            + diameter.estimated_diameter_max
                        )
                        / 2
                        * 1000
                    ),
                    miss_distance_km=close_approach.miss_distance.kilometers,
                    miss_distance_lunar=close_approach.miss_distance.lunar,
                    velocity_kph=close_approach.relative_velocity.kilometers_per_hour,
                )
            )

    return objects


def summarize_objects(objects: list[NeoObject]) -> NeoSummary:
    """Create the current high-level report summary."""

    # This is a pure function: the result depends only on the objects passed in.
    # It does not read files, call an API, print output, or modify global state.
    # That makes it straightforward to unit test.
    if not objects:
        return NeoSummary(
            total_objects=0,
            hazardous_count=0,
            closest=None,
            fastest=None,
            largest=None,
        )

    return NeoSummary(
        total_objects=len(objects),
        hazardous_count=sum(1 for obj in objects if obj.hazardous),
        closest=min(objects, key=lambda obj: obj.miss_distance_km),
        fastest=max(objects, key=lambda obj: obj.velocity_kph),
        largest=max(objects, key=lambda obj: obj.diameter_meters),
    )


def summarize_feed(feed: dict[str, Any]) -> NeoSummary:
    """Extract objects from a NASA feed and summarize them."""

    # This small wrapper names the full operation for callers: take the raw feed
    # shape from NASA and return the smaller summary shape used by the CLI.
    return summarize_objects(extract_objects(feed))


def filter_objects(
    objects: Sequence[NeoObject],
    *,
    hazardous_only: bool = False,
    min_diameter_meters: float | None = None,
    max_miss_distance_lunar: float | None = None,
) -> list[NeoObject]:
    """Filter extracted near-earth objects for row-level outputs."""

    filtered: list[NeoObject] = []
    for obj in objects:
        if hazardous_only and not obj.hazardous:
            continue
        if (
            min_diameter_meters is not None
            and obj.diameter_meters < min_diameter_meters
        ):
            continue
        if (
            max_miss_distance_lunar is not None
            and obj.miss_distance_lunar > max_miss_distance_lunar
        ):
            continue
        filtered.append(obj)

    return filtered


def rank_objects(
    objects: Sequence[NeoObject], sort_by: SortBy, top: int | None = None
) -> list[NeoObject]:
    """Rank objects by one useful field and optionally keep the first rows."""

    if top is not None and top < 1:
        raise ValueError("top must be at least 1")

    if sort_by == "closest":
        ranked = sorted(objects, key=lambda obj: obj.miss_distance_lunar)
    elif sort_by == "fastest":
        ranked = sorted(objects, key=lambda obj: obj.velocity_kph, reverse=True)
    else:
        ranked = sorted(objects, key=lambda obj: obj.diameter_meters, reverse=True)

    return ranked[:top]


def format_summary(summary: NeoSummary, label: str) -> str:
    """Format the summary for terminal output."""

    # Formatting is kept separate from printing. Returning a string lets tests
    # check the text without capturing stdout.
    lines = [
        "Near-Earth Object Summary",
        f"Date range: {label}",
        f"Objects observed: {summary.total_objects}",
        f"Potentially hazardous: {summary.hazardous_count}",
    ]

    if summary.closest is not None:
        lines.append(
            "Closest approach: "
            f"{summary.closest.name} "
            f"({summary.closest.miss_distance_lunar:.2f} lunar distances, "
            f"{summary.closest.miss_distance_km:,.0f} km)"
        )

    if summary.fastest is not None:
        lines.append(
            "Fastest object: "
            f"{summary.fastest.name} "
            f"({summary.fastest.velocity_kph:,.0f} km/h)"
        )

    if summary.largest is not None:
        lines.append(
            "Largest estimated diameter: "
            f"{summary.largest.name} "
            f"({summary.largest.diameter_meters:.0f} m)"
        )

    return "\n".join(lines)


def format_object_listing(objects: Sequence[NeoObject]) -> str:
    """Format extracted objects as a readable terminal listing."""

    if not objects:
        return "No near-earth objects matched."

    rows = [
        "Near-Earth Object Listing",
        (
            "Approach Date | Name | Hazardous | Diameter (m) | "
            "Miss Distance (LD) | Velocity (km/h)"
        ),
        "-" * 86,
    ]

    for obj in objects:
        rows.append(
            " | ".join(
                [
                    obj.approach_date,
                    obj.name,
                    "yes" if obj.hazardous else "no",
                    f"{obj.diameter_meters:.0f}",
                    f"{obj.miss_distance_lunar:.2f}",
                    f"{obj.velocity_kph:.0f}",
                ]
            )
        )

    return "\n".join(rows)
