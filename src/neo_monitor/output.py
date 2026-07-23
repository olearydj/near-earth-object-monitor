"""Serialization and filesystem helpers for user-requested data artifacts."""

from __future__ import annotations

import csv
from io import StringIO
import json
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

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
    """Write a readable, credential-sanitized copy of the NASA response.

    Parent directories are created as needed. Analytical response fields are
    preserved before project validation or transformation, while API-key query
    values echoed in provider link metadata are redacted.

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
    """Return a readable NASA response with URL credential values redacted."""

    return (
        json.dumps(_redact_api_key_query_values(feed), indent=2, sort_keys=True) + "\n"
    )


def _redact_api_key_query_values(value: Any) -> Any:
    """Copy JSON-like data while redacting API keys embedded in URL queries."""

    if isinstance(value, dict):
        return {key: _redact_api_key_query_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_api_key_query_values(item) for item in value]
    if isinstance(value, str):
        return _redact_api_key_in_url(value)
    return value


def _redact_api_key_in_url(value: str) -> str:
    """Replace an ``api_key`` URL query value without changing other fields."""

    parsed = urlsplit(value)
    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    if not any(key.lower() == "api_key" for key, _ in query_items):
        return value

    redacted_query = urlencode(
        [
            (key, "[REDACTED]" if key.lower() == "api_key" else item)
            for key, item in query_items
        ]
    )
    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, redacted_query, parsed.fragment)
    )


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
