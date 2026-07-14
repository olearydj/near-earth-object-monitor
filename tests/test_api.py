from datetime import date
from unittest.mock import Mock

import pytest
import requests

from neo_monitor.api import NASA_NEO_FEED_URL, NasaApiError, fetch_neo_feed


def test_fetch_neo_feed_returns_a_json_object_and_passes_expected_request_values(
    monkeypatch,
):
    response = Mock()
    response.json.return_value = {"near_earth_objects": {}}
    get = Mock(return_value=response)
    monkeypatch.setattr("neo_monitor.api.requests.get", get)

    data = fetch_neo_feed("test-key", date(2026, 7, 2), date(2026, 7, 3))

    assert data == {"near_earth_objects": {}}
    get.assert_called_once_with(
        NASA_NEO_FEED_URL,
        params={
            "start_date": "2026-07-02",
            "end_date": "2026-07-03",
            "api_key": "test-key",
        },
        timeout=15.0,
    )
    response.raise_for_status.assert_called_once_with()


def test_fetch_neo_feed_rejects_a_missing_api_key():
    with pytest.raises(NasaApiError, match="NASA_API_KEY is required"):
        fetch_neo_feed("  ", date(2026, 7, 2))


def test_fetch_neo_feed_explains_an_http_error(monkeypatch):
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError(
        response=Mock(status_code=429)
    )
    monkeypatch.setattr("neo_monitor.api.requests.get", Mock(return_value=response))

    with pytest.raises(NasaApiError, match="status 429"):
        fetch_neo_feed("test-key", date(2026, 7, 2))


def test_fetch_neo_feed_explains_a_connection_failure(monkeypatch):
    monkeypatch.setattr(
        "neo_monitor.api.requests.get",
        Mock(side_effect=requests.ConnectionError("network unavailable")),
    )

    with pytest.raises(NasaApiError, match="network unavailable"):
        fetch_neo_feed("test-key", date(2026, 7, 2))


def test_fetch_neo_feed_rejects_invalid_json(monkeypatch):
    response = Mock()
    response.json.side_effect = ValueError("not json")
    monkeypatch.setattr("neo_monitor.api.requests.get", Mock(return_value=response))

    with pytest.raises(NasaApiError, match="not valid JSON"):
        fetch_neo_feed("test-key", date(2026, 7, 2))


def test_fetch_neo_feed_rejects_an_unexpected_top_level_shape(monkeypatch):
    response = Mock()
    response.json.return_value = ["not", "an", "object"]
    monkeypatch.setattr("neo_monitor.api.requests.get", Mock(return_value=response))

    with pytest.raises(NasaApiError, match="unexpected shape"):
        fetch_neo_feed("test-key", date(2026, 7, 2))
