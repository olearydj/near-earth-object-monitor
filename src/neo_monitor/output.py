from __future__ import annotations

import csv
from io import StringIO
import json
from pathlib import Path
from typing import Any, Sequence

from neo_monitor.summarize import NeoObject


class OutputWriteError(RuntimeError):
    """Raised when a requested output artifact cannot be written."""


def write_raw_json(feed: dict[str, Any], output_path: Path) -> None:
    """Write the raw NASA feed response to a JSON file."""

    try:
        _ensure_parent_dir(output_path)
        output_path.write_text(raw_json_text(feed), encoding="utf-8")
    except OSError as exc:
        raise OutputWriteError(f"Could not write raw JSON to {output_path}.") from exc


def write_objects_csv(objects: Sequence[NeoObject], output_path: Path) -> None:
    """Write extracted near-earth object rows to a CSV file."""

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
    """Return extracted records as CSV for file or browser download."""

    fieldnames = [
        "approach_date",
        "name",
        "hazardous",
        "diameter_meters",
        "miss_distance_km",
        "miss_distance_lunar",
        "velocity_kph",
    ]
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
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
