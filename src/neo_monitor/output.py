"""Serialization and filesystem helpers for user-requested data artifacts."""

from __future__ import annotations

import csv
from io import StringIO
import json
from pathlib import Path
from typing import Any, Sequence

from neo_monitor.summarize import NeoObject


PROCESSED_CSV_FIELDS = (
    "approach_date",
    "name",
    "hazardous",
    "diameter_meters",
    "miss_distance_km",
    "miss_distance_lunar",
    "velocity_kph",
)
"""Stable column names and order for the processed CSV artifact."""


class OutputWriteError(RuntimeError):
    """Raised when a requested output artifact cannot be written."""


def write_raw_json(feed: dict[str, Any], output_path: Path) -> None:
    """Write a readable copy of the raw NASA response.

    Parent directories are created as needed. The raw response is intentionally
    preserved before project validation or transformation.

    Raises:
        OutputWriteError: If the destination cannot be created or written.
    """

    try:
        _ensure_parent_dir(output_path)
        output_path.write_text(raw_json_text(feed), encoding="utf-8")
    except OSError as exc:
        raise OutputWriteError(f"Could not write raw JSON to {output_path}.") from exc


def write_objects_csv(objects: Sequence[NeoObject], output_path: Path) -> None:
    """Write validated project records using the documented CSV schema.

    Parent directories are created as needed. See ``docs/data-dictionary.md``
    for field meanings, units, and transformation rules.

    Raises:
        OutputWriteError: If the destination cannot be created or written.
    """

    try:
        _ensure_parent_dir(output_path)
        output_path.write_text(objects_csv_text(objects), encoding="utf-8")
    except OSError as exc:
        raise OutputWriteError(
            f"Could not write processed CSV to {output_path}."
        ) from exc


def _ensure_parent_dir(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)


def raw_json_text(feed: dict[str, Any]) -> str:
    """Return a readable raw NASA response for file or browser download."""

    return json.dumps(feed, indent=2, sort_keys=True) + "\n"


def objects_csv_text(objects: Sequence[NeoObject]) -> str:
    """Serialize validated records as CSV for a file or browser download."""

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=PROCESSED_CSV_FIELDS)
    writer.writeheader()
    for obj in objects:
        writer.writerow(
            {
                "approach_date": obj.approach_date,
                "name": obj.name,
                "hazardous": str(obj.hazardous).lower(),
                "diameter_meters": f"{obj.diameter_meters:.3f}",
                "miss_distance_km": f"{obj.miss_distance_km:.3f}",
                "miss_distance_lunar": f"{obj.miss_distance_lunar:.3f}",
                "velocity_kph": f"{obj.velocity_kph:.3f}",
            }
        )
    return buffer.getvalue()
