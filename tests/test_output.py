import json
from pathlib import Path

from neo_monitor.output import objects_csv_text, raw_json_text
from neo_monitor.summarize import extract_objects


FIXTURE = Path(__file__).parent / "fixtures" / "neo-feed-sample.json"


def load_fixture():
    return json.loads(FIXTURE.read_text())


def test_raw_json_text_is_suitable_for_a_browser_download():
    assert json.loads(raw_json_text(load_fixture()))["element_count"] == 3


def test_raw_json_text_redacts_api_key_values_without_mutating_feed():
    feed = load_fixture()

    saved_feed = json.loads(raw_json_text(feed))

    assert "DEMO_KEY" not in raw_json_text(feed)
    assert "%5BREDACTED%5D" in saved_feed["links"]["self"]
    assert "DEMO_KEY" in feed["links"]["self"]


def test_objects_csv_text_is_suitable_for_a_browser_download():
    csv_text = objects_csv_text(extract_objects(load_fixture()))

    assert "approach_date,name,hazardous,diameter_meters" in csv_text
    assert "2026-07-02,Example Asteroid Beta,true,50.000" in csv_text
