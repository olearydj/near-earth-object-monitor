from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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


def extract_objects(feed: dict[str, Any]) -> list[NeoObject]:
    """Extract the fields this project currently cares about."""

    # External JSON is messy compared with normal Python objects. This function
    # converts the nested API response into a predictable list of NeoObject
    # values. That conversion step is a common pattern in real data projects.
    by_date = feed.get("near_earth_objects", {})
    if not isinstance(by_date, dict):
        return []

    objects: list[NeoObject] = []

    # The API groups objects by date. Sorting makes the output deterministic,
    # which is useful for tests and for comparing runs.
    for approach_date, daily_objects in sorted(by_date.items()):
        if not isinstance(daily_objects, list):
            continue

        for raw_object in daily_objects:
            if not isinstance(raw_object, dict):
                continue

            close_approaches = raw_object.get("close_approach_data", [])
            if not close_approaches:
                continue

            # Many NEOs only have one close approach in the requested feed. For
            # this first version, use the first approach and keep the behavior
            # simple rather than modeling every possible approach.
            close_approach = close_approaches[0]
            if not isinstance(close_approach, dict):
                continue

            objects.append(
                NeoObject(
                    name=str(raw_object.get("name", "unknown object")),
                    approach_date=str(
                        close_approach.get("close_approach_date", approach_date)
                    ),
                    hazardous=bool(
                        raw_object.get("is_potentially_hazardous_asteroid", False)
                    ),
                    diameter_meters=_estimated_diameter_meters(raw_object),
                    miss_distance_km=_float_from_nested(
                        close_approach, "miss_distance", "kilometers"
                    ),
                    miss_distance_lunar=_float_from_nested(
                        close_approach, "miss_distance", "lunar"
                    ),
                    velocity_kph=_float_from_nested(
                        close_approach,
                        "relative_velocity",
                        "kilometers_per_hour",
                    ),
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


def _estimated_diameter_meters(raw_object: dict[str, Any]) -> float:
    # NASA provides a min and max estimated diameter. Using the midpoint gives
    # us one number to compare when we report the largest object.
    diameter = raw_object.get("estimated_diameter", {})
    if not isinstance(diameter, dict):
        return 0.0

    kilometers = diameter.get("kilometers", {})
    if not isinstance(kilometers, dict):
        return 0.0

    min_km = _float_value(kilometers.get("estimated_diameter_min"))
    max_km = _float_value(kilometers.get("estimated_diameter_max"))
    return ((min_km + max_km) / 2) * 1000


def _float_from_nested(data: dict[str, Any], section: str, key: str) -> float:
    # Several useful values are nested two levels deep in the API response.
    # This helper keeps the repeated dictionary lookup code in one place.
    section_value = data.get(section, {})
    if not isinstance(section_value, dict):
        return 0.0
    return _float_value(section_value.get(key))


def _float_value(value: object) -> float:
    # JSON values often arrive as strings, even when they represent numbers.
    # Invalid or missing values become 0.0 so one bad field does not crash the
    # whole summary.
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return 0.0
