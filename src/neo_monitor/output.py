from __future__ import annotations

import csv
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
        output_path.write_text(
            json.dumps(feed, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise OutputWriteError(f"Could not write raw JSON to {output_path}.") from exc


def write_objects_csv(objects: Sequence[NeoObject], output_path: Path) -> None:
    """Write extracted near-earth object rows to a CSV file."""

    fieldnames = [
        "approach_date",
        "name",
        "hazardous",
        "diameter_meters",
        "miss_distance_km",
        "miss_distance_lunar",
        "velocity_kph",
    ]

    try:
        _ensure_parent_dir(output_path)
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
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
    except OSError as exc:
        raise OutputWriteError(
            f"Could not write processed CSV to {output_path}."
        ) from exc


def _ensure_parent_dir(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
