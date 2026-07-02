from __future__ import annotations

from datetime import date
from typing import Any

import requests


NASA_NEO_FEED_URL = "https://api.nasa.gov/neo/rest/v1/feed"


class NasaApiError(RuntimeError):
    """Raised when the NASA API request or response is not usable."""


def fetch_neo_feed(
    api_key: str,
    start_date: date,
    end_date: date | None = None,
    timeout: float = 15.0,
) -> dict[str, Any]:
    """Fetch near-earth object close-approach data from NASA."""

    if not api_key.strip():
        raise NasaApiError("NASA_API_KEY is required.")

    params = {
        "start_date": start_date.isoformat(),
        "end_date": (end_date or start_date).isoformat(),
        "api_key": api_key,
    }

    try:
        response = requests.get(NASA_NEO_FEED_URL, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise NasaApiError(f"NASA API request failed with status {status}.") from exc
    except requests.RequestException as exc:
        raise NasaApiError(f"NASA API request failed: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise NasaApiError("NASA API response was not valid JSON.") from exc

    if not isinstance(data, dict):
        raise NasaApiError("NASA API response had an unexpected shape.")

    return data
