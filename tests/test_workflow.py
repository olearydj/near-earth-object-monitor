import json
from datetime import date
from pathlib import Path
from unittest.mock import Mock

import pytest

from neo_monitor import workflow
from neo_monitor.workflow import (
    MonitorRequest,
    build_monitor_result,
    fetch_monitor_feed,
)


FIXTURE = Path(__file__).parent / "fixtures" / "neo-feed-sample.json"


def load_fixture():
    return json.loads(FIXTURE.read_text())


def test_build_monitor_result_reuses_validation_summary_filtering_and_ranking():
    result = build_monitor_result(
        load_fixture(),
        MonitorRequest(
            start_date=date(2026, 7, 2),
            hazardous_only=False,
            sort_by="closest",
            top=1,
        ),
    )

    assert result.label == "2026-07-02"
    assert result.summary.total_objects == 3
    assert [obj.name for obj in result.objects] == [
        "Example Asteroid Alpha",
        "Example Asteroid Beta",
        "Example Asteroid Gamma",
    ]
    assert [obj.name for obj in result.selected_objects] == ["Example Asteroid Beta"]


def test_fetch_monitor_feed_uses_the_request_dates_at_the_existing_api_boundary(
    monkeypatch,
):
    request = MonitorRequest(start_date=date(2026, 7, 2), end_date=date(2026, 7, 3))
    fetch = Mock(return_value={"near_earth_objects": {}})
    monkeypatch.setattr(workflow, "fetch_neo_feed", fetch)

    feed = fetch_monitor_feed("test-key", request)

    assert feed == {"near_earth_objects": {}}
    fetch.assert_called_once_with(
        api_key="test-key",
        start_date=date(2026, 7, 2),
        end_date=date(2026, 7, 3),
    )


def test_build_monitor_result_can_report_no_matching_selected_objects():
    result = build_monitor_result(
        load_fixture(),
        MonitorRequest(
            start_date=date(2026, 7, 2),
            hazardous_only=True,
            min_diameter_meters=100,
            sort_by="largest",
            top=10,
        ),
    )

    assert result.summary.total_objects == 3
    assert result.selected_objects == ()


def test_monitor_request_rejects_an_invalid_date_range():
    with pytest.raises(ValueError, match="end date cannot be before start date"):
        MonitorRequest(start_date=date(2026, 7, 3), end_date=date(2026, 7, 2))


def test_monitor_request_requires_a_ranking_when_limiting_rows():
    with pytest.raises(ValueError, match="top requires a ranking"):
        MonitorRequest(start_date=date(2026, 7, 2), top=1)
