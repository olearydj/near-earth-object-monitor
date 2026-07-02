import json
from pathlib import Path

from neo_monitor.summarize import extract_objects, format_summary, summarize_feed


FIXTURE = Path(__file__).parent / "fixtures" / "neo-feed-sample.json"


def load_fixture():
    return json.loads(FIXTURE.read_text())


def test_extract_objects_returns_selected_fields():
    objects = extract_objects(load_fixture())

    assert len(objects) == 3
    assert objects[0].name == "Example Asteroid Alpha"
    assert objects[0].diameter_meters == 200


def test_summarize_feed_identifies_key_objects():
    summary = summarize_feed(load_fixture())

    assert summary.total_objects == 3
    assert summary.hazardous_count == 1
    assert summary.closest is not None
    assert summary.closest.name == "Example Asteroid Beta"
    assert summary.fastest is not None
    assert summary.fastest.name == "Example Asteroid Beta"
    assert summary.largest is not None
    assert summary.largest.name == "Example Asteroid Gamma"


def test_format_summary_includes_report_values():
    summary = summarize_feed(load_fixture())

    report = format_summary(summary, "2026-07-02")

    assert "Near-Earth Object Summary" in report
    assert "Objects observed: 3" in report
    assert "Potentially hazardous: 1" in report
    assert "Example Asteroid Beta" in report
