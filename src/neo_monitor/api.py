"""NASA NEO Feed client and the project's external network boundary."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

import requests


NASA_NEO_FEED_URL = "https://api.nasa.gov/neo/rest/v1/feed"
logger = logging.getLogger(__name__)


class NasaApiError(RuntimeError):
    """Raised when the NASA API request or response is not usable."""


def fetch_neo_feed(
    api_key: str,
    start_date: date,
    end_date: date | None = None,
    timeout: float = 15.0,
) -> dict[str, Any]:
    """Fetch one date range from NASA's NEO Feed API.

    Args:
        api_key: NASA API key. Blank values are rejected before any request.
        start_date: First close-approach date to request.
        end_date: Last date to request; defaults to ``start_date``.
        timeout: Maximum seconds to wait for the HTTP request.

    Returns:
        The decoded top-level JSON object. Its domain fields are validated at
        the later transformation boundary in `neo_monitor.summarize`.

    Raises:
        NasaApiError: If configuration, transport, HTTP status, JSON decoding,
        or the top-level response shape is unusable.
    """

    # This function is the network boundary of the program. Keeping the live
    # HTTP request here makes the rest of the project easier to test with saved
    # fixture data instead of calling NASA during every test run.
    if not api_key.strip():
        raise NasaApiError("NASA_API_KEY is required.")

    # The API expects dates as strings in YYYY-MM-DD format. The rest of the
    # program uses real date objects so invalid dates can be caught earlier.
    params = {
        "start_date": start_date.isoformat(),
        "end_date": (end_date or start_date).isoformat(),
        "api_key": api_key,
    }

    try:
        logger.info(
            "Requesting NASA NEO feed for %s through %s.",
            params["start_date"],
            params["end_date"],
        )
        logger.debug("Using a request timeout of %.1f seconds.", timeout)
        # Always include a timeout for external requests. Without one, a CLI can
        # hang indefinitely if the network or remote server stalls.
        response = requests.get(NASA_NEO_FEED_URL, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        logger.warning("NASA API request failed with HTTP status %s.", status)
        raise NasaApiError(f"NASA API request failed with status {status}.") from exc
    except requests.RequestException as exc:
        logger.warning("NASA API request failed: %s", exc)
        raise NasaApiError(f"NASA API request failed: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.warning("NASA API response was not valid JSON.")
        raise NasaApiError("NASA API response was not valid JSON.") from exc

    # Type hints describe what we expect, but API responses come from outside
    # Python. We still need a runtime check before returning the parsed data.
    if not isinstance(data, dict):
        logger.warning("NASA API response had an unexpected top-level shape.")
        raise NasaApiError("NASA API response had an unexpected shape.")

    logger.debug("NASA API response parsed as a JSON object.")
    return data
